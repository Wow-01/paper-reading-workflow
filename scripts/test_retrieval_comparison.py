"""检索方案对比测试。

对比两种方案：
1. 扁平JSONL + LLM分层检索
2. 树形结构 + LLM检索
"""

import json
import os
import re
import time
from pathlib import Path
from typing import List, Dict, Optional


# ============================================================================
# 方案1：扁平JSONL + LLM分层检索
# ============================================================================

class FlatJSONLSearcher:
    """扁平JSONL检索器"""

    def __init__(self, index_path: str):
        self.records = self._load_index(index_path)
        print(f"加载索引: {len(self.records)} 条记录")

    def _load_index(self, path: str) -> List[Dict]:
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def keyword_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """关键词搜索"""
        query_lower = query.lower()
        keywords = self._extract_keywords(query_lower)

        scored = []
        for record in self.records:
            text = record.get("text", "").lower()
            section = record.get("section_path", "").lower()

            # 计算匹配分数
            score = 0
            matched_kw = []

            for kw in keywords:
                if kw in text:
                    score += 1
                    matched_kw.append(kw)
                if kw in section:
                    score += 2  # 章节匹配权重更高
                    if kw not in matched_kw:
                        matched_kw.append(kw)

            if score > 0:
                scored.append({
                    **record,
                    "match_score": score,
                    "matched_keywords": matched_kw,
                    "method": "flat_jsonl"
                })

        scored.sort(key=lambda x: x["match_score"], reverse=True)
        return scored[:top_k]

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（中英文混合）"""
        keywords = []
        # 英文单词
        en_words = re.findall(r'[a-zA-Z]+(?:[-\'][a-zA-Z]+)*', text)
        keywords.extend([w.lower() for w in en_words if len(w) > 2])
        # 中文词汇
        cn_chars = re.findall(r'[一-鿿]+', text)
        keywords.extend(cn_chars)
        return keywords

    def llm_rerank(self, query: str, candidates: List[Dict], top_k: int = 5) -> List[Dict]:
        """LLM语义重排序（模拟）"""
        # 这里模拟LLM重排序，实际应调用LLM API
        # 根据文本与查询的语义相关性重新打分

        query_keywords = set(self._extract_keywords(query.lower()))

        for candidate in candidates:
            text = candidate.get("text", "").lower()
            # 计算语义相关性分数（简化版）
            semantic_score = 0

            # 检查关键词密度
            for kw in query_keywords:
                if kw in text:
                    semantic_score += text.count(kw)

            # 检查是否包含完整短语
            if query.lower() in text:
                semantic_score += 10

            candidate["semantic_score"] = semantic_score

        # 按语义分数排序
        candidates.sort(key=lambda x: x.get("semantic_score", 0), reverse=True)
        return candidates[:top_k]


# ============================================================================
# 方案2：树形结构 + LLM检索
# ============================================================================

class TreeIndexSearcher:
    """树形索引检索器"""

    def __init__(self, index_path: str, meta_path: str):
        self.records = self._load_index(index_path)
        self.meta = self._load_meta(meta_path)
        self.tree = self._build_tree()
        print(f"加载树形索引: {len(self.tree)} 个根节点")

    def _load_index(self, path: str) -> List[Dict]:
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def _load_meta(self, path: str) -> Dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_tree(self) -> List[Dict]:
        """从扁平记录构建树形结构"""
        # 按section_path分组
        sections = {}
        for record in self.records:
            section = record.get("section_path", "unknown")
            if section not in sections:
                sections[section] = {
                    "title": section,
                    "section_path": section,
                    "records": [],
                    "summary": ""
                }
            sections[section]["records"].append(record)

        # 为每个section生成摘要
        tree = []
        for section_path, section_data in sections.items():
            # 生成摘要（取前3个段落的前100字符）
            summaries = []
            for r in section_data["records"][:3]:
                text = r.get("text", "")[:100]
                if text:
                    summaries.append(text)
            section_data["summary"] = " | ".join(summaries)

            # 构建子节点
            nodes = []
            for r in section_data["records"]:
                nodes.append({
                    "anchor_id": r.get("anchor_id"),
                    "text": r.get("text", "")[:200],
                    "source_ref": r.get("source_ref")
                })
            section_data["nodes"] = nodes

            tree.append(section_data)

        return tree

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """树形检索：先定位section，再找具体内容"""
        query_lower = query.lower()
        keywords = self._extract_keywords(query_lower)

        # 第一步：定位相关section
        section_scores = []
        for section in self.tree:
            score = 0
            title = section.get("title", "").lower()
            summary = section.get("summary", "").lower()

            for kw in keywords:
                if kw in title:
                    score += 3
                if kw in summary:
                    score += 1

            if score > 0:
                section_scores.append((score, section))

        section_scores.sort(key=lambda x: x[0], reverse=True)

        # 第二步：在相关section内搜索具体内容
        results = []
        for _, section in section_scores[:3]:  # 只看前3个最相关的section
            for node in section.get("nodes", []):
                text = node.get("text", "").lower()
                score = sum(1 for kw in keywords if kw in text)

                if score > 0:
                    results.append({
                        "section_path": section.get("section_path"),
                        "anchor_id": node.get("anchor_id"),
                        "text": node.get("text"),
                        "source_ref": node.get("source_ref"),
                        "match_score": score,
                        "method": "tree_index"
                    })

        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:top_k]

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        en_words = re.findall(r'[a-zA-Z]+(?:[-\'][a-zA-Z]+)*', text)
        keywords.extend([w.lower() for w in en_words if len(w) > 2])
        cn_chars = re.findall(r'[一-鿿]+', text)
        keywords.extend(cn_chars)
        return keywords

    def get_toc(self) -> str:
        """获取目录结构"""
        toc_lines = []
        for section in self.tree:
            title = section.get("title", "Unknown")
            record_count = len(section.get("records", []))
            toc_lines.append(f"- {title} ({record_count} 段落)")
        return "\n".join(toc_lines)


# ============================================================================
# 测试框架
# ============================================================================

class RetrievalTester:
    """检索测试框架"""

    def __init__(self, index_path: str, meta_path: str):
        self.flat_searcher = FlatJSONLSearcher(index_path)
        self.tree_searcher = TreeIndexSearcher(index_path, meta_path)

    def run_test(self, queries: List[str], top_k: int = 5) -> Dict:
        """运行对比测试"""
        results = {
            "flat_jsonl": [],
            "tree_index": [],
            "comparison": []
        }

        for query in queries:
            print(f"\n{'='*60}")
            print(f"查询: {query}")
            print(f"{'='*60}")

            # 方案1：扁平JSONL
            start_time = time.time()
            flat_results = self.flat_searcher.keyword_search(query, top_k)
            flat_time = time.time() - start_time

            # 方案2：树形索引
            start_time = time.time()
            tree_results = self.tree_searcher.search(query, top_k)
            tree_time = time.time() - start_time

            # 记录结果
            results["flat_jsonl"].append({
                "query": query,
                "results": flat_results,
                "time": flat_time,
                "count": len(flat_results)
            })

            results["tree_index"].append({
                "query": query,
                "results": tree_results,
                "time": tree_time,
                "count": len(tree_results)
            })

            # 对比分析
            comparison = self._compare_results(flat_results, tree_results, query)
            results["comparison"].append({
                "query": query,
                **comparison
            })

            # 打印结果
            self._print_results(query, flat_results, tree_results, flat_time, tree_time)

        return results

    def _compare_results(self, flat_results: List[Dict], tree_results: List[Dict], query: str) -> Dict:
        """对比两种方案的结果"""
        # 提取锚点ID
        flat_anchors = set(r.get("anchor_id") for r in flat_results)
        tree_anchors = set(r.get("anchor_id") for r in tree_results)

        # 计算重叠度
        overlap = flat_anchors & tree_anchors
        overlap_ratio = len(overlap) / max(len(flat_anchors), len(tree_anchors), 1)

        return {
            "flat_count": len(flat_results),
            "tree_count": len(tree_results),
            "overlap_count": len(overlap),
            "overlap_ratio": overlap_ratio,
            "flat_anchors": list(flat_anchors),
            "tree_anchors": list(tree_anchors)
        }

    def _print_results(self, query: str, flat_results: List[Dict], tree_results: List[Dict],
                       flat_time: float, tree_time: float):
        """打印测试结果"""
        print(f"\n方案1 - 扁平JSONL ({flat_time:.3f}秒):")
        for i, r in enumerate(flat_results[:3], 1):
            print(f"  [{i}] 分数:{r.get('match_score', 0)} 章节:{r.get('section_path', 'N/A')}")
            text = r.get('text', '')[:80].encode('gbk', 'ignore').decode('gbk', 'ignore')
            print(f"      {text}...")

        print(f"\n方案2 - 树形索引 ({tree_time:.3f}秒):")
        for i, r in enumerate(tree_results[:3], 1):
            print(f"  [{i}] 分数:{r.get('match_score', 0)} 章节:{r.get('section_path', 'N/A')}")
            text = r.get('text', '')[:80].encode('gbk', 'ignore').decode('gbk', 'ignore')
            print(f"      {text}...")

    def generate_report(self, results: Dict, output_path: str):
        """生成测试报告"""
        report = {
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_queries": len(results["comparison"]),
            "summary": {
                "avg_flat_time": sum(r["time"] for r in results["flat_jsonl"]) / len(results["flat_jsonl"]),
                "avg_tree_time": sum(r["time"] for r in results["tree_index"]) / len(results["tree_index"]),
                "avg_overlap_ratio": sum(r["overlap_ratio"] for r in results["comparison"]) / len(results["comparison"])
            },
            "details": results["comparison"]
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n报告已保存到: {output_path}")
        return report


# ============================================================================
# 主函数
# ============================================================================

def main():
    # 测试查询（中英文混合）
    test_queries = [
        "Mpemba effect 量子",
        "Hubbard model 反铁磁",
        "quantum Monte Carlo 符号问题",
        "entanglement 纠缠熵",
        "phase transition 相变",
        "ground state 基态能量",
        "imaginary time 虚时间演化",
        "Dirac fermion 狄拉克费米子"
    ]

    # 索引路径
    index_path = "outputs/02-Imaginary-time-Mpemba-effect/pageindex/index.jsonl"
    meta_path = "outputs/02-Imaginary-time-Mpemba-effect/pageindex/index.meta.json"

    # 检查文件是否存在
    if not os.path.exists(index_path):
        print(f"错误: 索引文件不存在: {index_path}")
        return

    # 创建测试器
    tester = RetrievalTester(index_path, meta_path)

    # 运行测试
    print("\n" + "="*60)
    print("开始检索方案对比测试")
    print("="*60)

    results = tester.run_test(test_queries, top_k=5)

    # 生成报告
    report_path = "outputs/retrieval_comparison_report.json"
    report = tester.generate_report(results, report_path)

    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"总查询数: {report['total_queries']}")
    print(f"平均响应时间 - 扁平JSONL: {report['summary']['avg_flat_time']:.3f}秒")
    print(f"平均响应时间 - 树形索引: {report['summary']['avg_tree_time']:.3f}秒")
    print(f"平均结果重叠率: {report['summary']['avg_overlap_ratio']:.2%}")

    # 显示树形结构目录
    print("\n" + "="*60)
    print("树形索引目录结构")
    print("="*60)
    print(tester.tree_searcher.get_toc())


if __name__ == "__main__":
    main()
