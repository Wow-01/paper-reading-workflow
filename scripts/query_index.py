"""PageIndex 查询模块。

支持中英文混合查询，基于扁平JSONL索引。
采用关键词匹配 + LLM语义重排序的混合方案。
"""

import json
import logging
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class IndexSearcher:
    """索引查询器（支持多轮对话）"""

    def __init__(self, index_path: str):
        """初始化查询器。

        Args:
            index_path: index.jsonl 文件路径
        """
        self.index_path = index_path
        self.records = self._load_index(index_path)
        self.history = []  # 对话历史
        logger.info(f"加载索引: {len(self.records)} 条记录")

    def _load_index(self, path: str) -> List[Dict]:
        """加载索引文件"""
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def search(self, query: str, top_k: int = 5, use_history: bool = True) -> List[Dict]:
        """搜索索引（支持多轮对话）。

        Args:
            query: 查询字符串（支持中英文混合）
            top_k: 返回结果数量
            use_history: 是否使用对话历史

        Returns:
            匹配结果列表
        """
        # 分析是否是追问
        is_followup = self._is_followup(query)
        expanded_query = query

        # 如果是追问，扩展查询
        if use_history and is_followup and self.history:
            expanded_query = self._expand_query(query)
            logger.info(f"扩展查询: {expanded_query}")

        # 预处理查询
        query_normalized = self._normalize_text(expanded_query)
        keywords = self._extract_keywords(query_normalized)

        logger.info(f"查询: {query}")
        logger.info(f"关键词: {keywords}")

        # 关键词匹配
        candidates = self._keyword_match(keywords)

        # 语义排序
        results = self._semantic_rank(query_normalized, candidates)

        # 记录历史
        if use_history:
            self.history.append({
                "query": query,
                "expanded_query": expanded_query,
                "results": [r.get("anchor_id") for r in results[:3]],
                "sections": [r.get("section_path") for r in results[:3]],
            })

        return results[:top_k]

    def _is_followup(self, query: str) -> bool:
        """判断是否是追问。

        追问特征：
        - 包含代词：它、这个、那个、上述、前面
        - 包含追问词：具体、详细、更多、解释
        - 查询较短（可能是简短追问）

        Args:
            query: 查询字符串

        Returns:
            是否是追问
        """
        query_lower = query.lower()

        # 追问指示词
        followup_indicators = [
            "它", "这个", "那个", "上述", "前面", "后者", "前者",
            "具体", "详细", "更多", "解释", "为什么", "怎么", "如何",
            "then", "it", "this", "that", "more", "detail", "explain",
        ]

        # 检查是否包含追问指示词
        for indicator in followup_indicators:
            if indicator in query_lower:
                return True

        # 查询较短（<10字符）且有历史，可能是追问
        if len(query) < 10 and self.history:
            return True

        return False

    def _expand_query(self, query: str) -> str:
        """扩展追问查询。

        将追问与上一轮查询结合，形成更完整的查询。

        Args:
            query: 当前查询

        Returns:
            扩展后的查询
        """
        if not self.history:
            return query

        # 获取上一轮查询
        last_entry = self.history[-1]
        last_query = last_entry.get("query", "")
        last_sections = last_entry.get("sections", [])

        # 扩展策略1：添加上一轮查询的关键词
        last_keywords = self._extract_keywords(self._normalize_text(last_query))
        query_keywords = self._extract_keywords(self._normalize_text(query))

        # 合并关键词（去重）
        all_keywords = list(set(last_keywords + query_keywords))

        # 扩展策略2：添加上一轮命中的章节作为上下文
        expanded = " ".join(all_keywords)

        # 如果有章节信息，添加到查询中
        if last_sections:
            section_context = " ".join(last_sections[:2])
            expanded = f"{expanded} {section_context}"

        return expanded

    def clear_history(self):
        """清空对话历史"""
        self.history = []
        logger.info("对话历史已清空")

    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.history

    def add_context(self, results: List[Dict], context_count: int = 1) -> List[Dict]:
        """为搜索结果添加上下文。

        Args:
            results: 搜索结果列表
            context_count: 上下文段落数量（前后各几个）

        Returns:
            带上下文的结果列表
        """
        for result in results:
            section = result.get("section_path", "")
            anchor_id = result.get("anchor_id", "")

            # 获取同一章节的所有记录
            section_records = [r for r in self.records if r.get("section_path") == section]

            # 找到当前记录的索引
            current_idx = None
            for i, r in enumerate(section_records):
                if r.get("anchor_id") == anchor_id:
                    current_idx = i
                    break

            if current_idx is not None:
                # 获取前文
                context_before = []
                for i in range(max(0, current_idx - context_count), current_idx):
                    text = section_records[i].get("text", "")
                    if text:
                        context_before.append(text[:100])

                # 获取后文
                context_after = []
                for i in range(current_idx + 1, min(len(section_records), current_idx + context_count + 1)):
                    text = section_records[i].get("text", "")
                    if text:
                        context_after.append(text[:100])

                result["context_before"] = context_before
                result["context_after"] = context_after
            else:
                result["context_before"] = []
                result["context_after"] = []

        return results

    def _normalize_text(self, text: str) -> str:
        """文本标准化：小写、去除多余空格"""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（支持中英文混合）"""
        keywords = []

        # 英文单词（长度>2）
        en_words = re.findall(r'[a-zA-Z]+(?:[-\'][a-zA-Z]+)*', text)
        keywords.extend([w.lower() for w in en_words if len(w) > 2])

        # 中文词汇
        cn_chars = re.findall(r'[一-鿿]+', text)
        keywords.extend(cn_chars)

        # 数字和公式符号
        nums = re.findall(r'[a-zA-Z]?\d+(?:\.\d+)?', text)
        keywords.extend(nums)

        return list(set(keywords))  # 去重

    def _keyword_match(self, keywords: List[str]) -> List[Dict]:
        """关键词匹配（支持新字段：keywords, summary）"""
        scored = []

        for record in self.records:
            text = record.get("text", "").lower()
            section = record.get("section_path", "").lower()
            summary = record.get("summary", "").lower()
            record_keywords = [kw.lower() for kw in record.get("keywords", [])]

            # 计算匹配分数
            score = 0
            matched_kw = []

            for kw in keywords:
                # 正文匹配（权重1）
                if kw in text:
                    score += text.count(kw)
                    matched_kw.append(kw)

                # 章节匹配（权重3）
                if kw in section:
                    score += 3
                    if kw not in matched_kw:
                        matched_kw.append(kw)

                # 摘要匹配（权重2）
                if kw in summary:
                    score += 2
                    if kw not in matched_kw:
                        matched_kw.append(kw)

                # 索引关键词匹配（权重5）
                if kw in record_keywords:
                    score += 5
                    if kw not in matched_kw:
                        matched_kw.append(kw)

            if score > 0:
                scored.append({
                    **record,
                    "keyword_score": score,
                    "matched_keywords": matched_kw,
                })

        scored.sort(key=lambda x: x["keyword_score"], reverse=True)
        return scored

    def _semantic_rank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """语义重排序（多因素综合评分）

        评分因素：
        1. 完全匹配查询（权重最高）
        2. 关键词位置（开头匹配更重要）
        3. 关键词密度（匹配词数/总词数）
        4. 关键词连续性（相邻关键词加分）
        5. 多关键词同时命中（覆盖度）
        6. 摘要匹配加分
        """
        for candidate in candidates:
            text = candidate.get("text", "").lower()
            summary = candidate.get("summary", "").lower()

            # 语义分数
            semantic_score = 0

            # 1. 完全匹配查询（权重最高：+15）
            if query in text:
                semantic_score += 15
            elif query in summary:
                semantic_score += 10

            # 2. 关键词位置加分（开头匹配更重要）
            matched_kw = candidate.get("matched_keywords", [])
            for kw in matched_kw:
                # 在文本前100字符中匹配，加分更高
                if kw in text[:100]:
                    semantic_score += 3
                elif kw in text[:200]:
                    semantic_score += 1

            # 3. 关键词密度（匹配词数/总词数）
            keyword_score = candidate.get("keyword_score", 0)
            text_len = max(len(text), 1)
            keyword_density = keyword_score / text_len * 100
            semantic_score += keyword_density

            # 4. 关键词连续性（相邻关键词加分）
            for i in range(len(matched_kw) - 1):
                kw1, kw2 = matched_kw[i], matched_kw[i+1]
                # 在文本中检查连续性
                pattern = re.escape(kw1) + r'.{0,30}' + re.escape(kw2)
                if re.search(pattern, text):
                    semantic_score += 3
                # 在摘要中检查连续性
                if re.search(pattern, summary):
                    semantic_score += 2

            # 5. 多关键词同时命中（覆盖度加分）
            query_keywords = set(self._extract_keywords(query))
            matched_set = set(matched_kw)
            if query_keywords:
                coverage = len(matched_set) / len(query_keywords)
                if coverage >= 1.0:  # 所有关键词都命中
                    semantic_score += 5
                elif coverage >= 0.5:  # 超过一半命中
                    semantic_score += 2

            # 6. 索引关键词与查询关键词重叠
            record_keywords = set(kw.lower() for kw in candidate.get("keywords", []))
            if record_keywords and query_keywords:
                overlap = len(record_keywords & query_keywords)
                semantic_score += overlap * 2

            candidate["semantic_score"] = round(semantic_score, 2)
            candidate["final_score"] = round(keyword_score + semantic_score, 2)

        # 按最终分数排序
        candidates.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        return candidates


def search_index(index_path: str, query: str, top_k: int = 5, with_context: bool = False) -> List[Dict]:
    """便捷搜索函数。

    Args:
        index_path: index.jsonl 文件路径
        query: 查询字符串
        top_k: 返回结果数量
        with_context: 是否返回上下文

    Returns:
        匹配结果列表
    """
    searcher = IndexSearcher(index_path)
    results = searcher.search(query, top_k=top_k)

    if with_context:
        results = searcher.add_context(results)

    return results


def format_results(results: List[Dict], query: str) -> str:
    """格式化搜索结果为可读文本。

    Args:
        results: 搜索结果列表
        query: 原始查询

    Returns:
        格式化的文本
    """
    if not results:
        return f"查询 '{query}' 没有找到相关结果。"

    lines = [f"查询: {query}", f"找到 {len(results)} 个相关结果:", ""]

    for i, r in enumerate(results, 1):
        section = r.get("section_path", "N/A")
        anchor = r.get("anchor_id", "N/A")
        score = r.get("final_score", 0)
        text = r.get("text", "")[:200]
        matched = r.get("matched_keywords", [])

        lines.append(f"[{i}] 章节: {section}")
        lines.append(f"    锚点: {anchor}")
        lines.append(f"    分数: {score:.1f}")
        lines.append(f"    匹配: {', '.join(matched)}")
        lines.append(f"    内容: {text}...")
        lines.append("")

    return "\n".join(lines)


# 命令行接口
if __name__ == "__main__":
    import sys
    import os

    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    if len(sys.argv) < 3:
        print("用法: python query_index.py <index.jsonl路径> <查询> [top_k]")
        print("")
        print("示例:")
        print('  python query_index.py outputs/paper/pageindex/index.jsonl "Mpemba effect 量子"')
        print('  python query_index.py outputs/paper/pageindex/index.jsonl "Hubbard model" 10')
        sys.exit(1)

    index_path = sys.argv[1]
    query = sys.argv[2]
    top_k = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    # 检查文件是否存在
    if not os.path.exists(index_path):
        print(f"错误: 索引文件不存在: {index_path}")
        sys.exit(1)

    # 执行搜索
    results = search_index(index_path, query, top_k)

    # 打印结果
    print(format_results(results, query))
