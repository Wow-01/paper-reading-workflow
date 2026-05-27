"""JSONL 查询脚本测试。

使用 JSONL 索引进行问答。
"""

import json
import os


def load_jsonl_index(jsonl_path):
    """加载 JSONL 索引。"""
    records = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def search_jsonl(records, query):
    """在 JSONL 索引中搜索。

    遍历所有记录，查找包含查询关键词的记录。
    """
    query_lower = query.lower()
    keywords = query_lower.split()

    results = []

    for record in records:
        text = record.get("text", "").lower()

        # 计算关键词匹配数
        matches = sum(1 for kw in keywords if kw in text)

        if matches > 0:
            relevance = matches / len(keywords)
            results.append({
                "section_path": record.get("section_path", ""),
                "anchor_id": record.get("anchor_id", ""),
                "text": record.get("text", "")[:300],  # 限制长度
                "source_ref": record.get("source_ref", ""),
                "relevance": relevance
            })

    # 按相关性排序
    results.sort(key=lambda x: x["relevance"], reverse=True)

    return results[:3]  # 返回 top 3


def main():
    """主函数。"""
    # 测试文献路径
    base_dir = "outputs/01-Superior-resilience-poisoning-unlearning"
    jsonl_path = os.path.join(base_dir, "pageindex/index.jsonl")

    # 加载索引
    print("=== 加载 JSONL 索引 ===")
    records = load_jsonl_index(jsonl_path)
    print(f"索引记录数: {len(records)}")

    # 测试问题
    questions = [
        "这篇论文的主要贡献是什么？",
        "QNN 的韧性机制是什么？",
        "LRR 是怎么定义的？",
        "标签翻转和特征随机化有什么区别？",
    ]

    # 执行查询
    print("\n=== JSONL 查询测试 ===")
    for q in questions:
        print(f"\n问题: {q}")
        results = search_jsonl(records, q)
        for i, r in enumerate(results, 1):
            print(f"  结果{i}: [{r['section_path']}] {r['anchor_id']}")
            print(f"    相关性: {r['relevance']:.2f}")
            print(f"    来源: {r['source_ref']}")
            print(f"    内容: {r['text'][:100]}...")


if __name__ == "__main__":
    main()
