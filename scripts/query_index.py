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
    """索引查询器"""

    def __init__(self, index_path: str):
        """初始化查询器。

        Args:
            index_path: index.jsonl 文件路径
        """
        self.index_path = index_path
        self.records = self._load_index(index_path)
        logger.info(f"加载索引: {len(self.records)} 条记录")

    def _load_index(self, path: str) -> List[Dict]:
        """加载索引文件"""
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索索引。

        Args:
            query: 查询字符串（支持中英文混合）
            top_k: 返回结果数量

        Returns:
            匹配结果列表
        """
        # 预处理查询
        query_normalized = self._normalize_text(query)
        keywords = self._extract_keywords(query_normalized)

        logger.info(f"查询: {query}")
        logger.info(f"关键词: {keywords}")

        # 关键词匹配
        candidates = self._keyword_match(keywords)

        # 语义排序
        results = self._semantic_rank(query_normalized, candidates)

        return results[:top_k]

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
        """关键词匹配"""
        scored = []

        for record in self.records:
            text = record.get("text", "").lower()
            section = record.get("section_path", "").lower()

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

            if score > 0:
                scored.append({
                    **record,
                    "keyword_score": score,
                    "matched_keywords": matched_kw,
                })

        scored.sort(key=lambda x: x["keyword_score"], reverse=True)
        return scored

    def _semantic_rank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """语义排序（基于关键词密度和位置）"""
        for candidate in candidates:
            text = candidate.get("text", "").lower()

            # 语义分数
            semantic_score = 0

            # 1. 完全匹配查询
            if query in text:
                semantic_score += 10

            # 2. 关键词密度
            keyword_score = candidate.get("keyword_score", 0)
            text_len = max(len(text), 1)
            keyword_density = keyword_score / text_len * 100
            semantic_score += keyword_density

            # 3. 关键词连续性（相邻关键词加分）
            matched_kw = candidate.get("matched_keywords", [])
            for i in range(len(matched_kw) - 1):
                kw1, kw2 = matched_kw[i], matched_kw[i+1]
                pattern = re.escape(kw1) + r'.{0,30}' + re.escape(kw2)
                if re.search(pattern, text):
                    semantic_score += 2

            candidate["semantic_score"] = semantic_score
            candidate["final_score"] = keyword_score + semantic_score

        # 按最终分数排序
        candidates.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        return candidates


def search_index(index_path: str, query: str, top_k: int = 5) -> List[Dict]:
    """便捷搜索函数。

    Args:
        index_path: index.jsonl 文件路径
        query: 查询字符串
        top_k: 返回结果数量

    Returns:
        匹配结果列表
    """
    searcher = IndexSearcher(index_path)
    return searcher.search(query, top_k=top_k)


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
