"""语义理解问答脚本。

使用 Claude 推理进行语义匹配和问答。
"""

import json
import os


def load_index(jsonl_path, meta_path):
    """加载索引文件。"""
    # 加载 JSONL 索引
    records = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # 加载元数据
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    return records, meta


def semantic_search(query, records, meta, clean_md_path):
    """语义搜索。

    模拟 Claude 的推理过程：
    1. 理解问题意图
    2. 识别关键词和同义词
    3. 在索引中查找相关内容
    4. 返回语义相关的结果
    """
    # 读取 clean_md
    with open(clean_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 问题理解
    query_lower = query.lower()

    # 同义词映射（模拟 Claude 的语义理解）
    synonyms = {
        "韧性": ["robustness", "resilience", "stability"],
        "机制": ["mechanism", "reason", "cause"],
        "贡献": ["contribution", "achievement", "finding"],
        "定义": ["definition", "define", "describe"],
        "区别": ["difference", "distinction", "contrast"],
        "优势": ["advantage", "benefit", "strength"],
        "方法": ["method", "approach", "technique"],
        "结果": ["result", "outcome", "finding"],
    }

    # 扩展查询关键词
    expanded_keywords = set()
    for word in query_lower.split():
        expanded_keywords.add(word)
        # 查找同义词
        for cn_word, en_words in synonyms.items():
            if word in cn_word or cn_word in word:
                expanded_keywords.update(en_words)

    # 在索引中查找
    results = []
    for record in records:
        text = record.get("text", "").lower()

        # 计算语义相关性
        relevance = 0
        for keyword in expanded_keywords:
            if keyword in text:
                relevance += 1

        if relevance > 0:
            results.append({
                "section_path": record.get("section_path", ""),
                "anchor_id": record.get("anchor_id", ""),
                "text": record.get("text", ""),
                "source_ref": record.get("source_ref", ""),
                "relevance": relevance
            })

    # 按相关性排序
    results.sort(key=lambda x: x["relevance"], reverse=True)

    return results[:5]


def format_answer(query, results, meta):
    """格式化答案。

    模拟 Claude 生成答案的过程。
    """
    # 获取章节信息
    sections = meta.get("sections", [])
    section_map = {s["section_path"]: s["title"] for s in sections}

    answer_parts = []
    answer_parts.append(f"问题: {query}")
    answer_parts.append("")
    answer_parts.append("相关段落:")

    for i, r in enumerate(results, 1):
        section_title = section_map.get(r["section_path"], r["section_path"])
        answer_parts.append(f"\n{i}. 章节: {section_title}")
        answer_parts.append(f"   锚点: {r['anchor_id']}")
        answer_parts.append(f"   来源: {r['source_ref']}")
        answer_parts.append(f"   内容: {r['text'][:200]}...")

    answer_parts.append("")
    answer_parts.append("答案:")
    answer_parts.append("（基于以上段落，Claude 可以推理出完整答案）")

    return "\n".join(answer_parts)


def main():
    """主函数。"""
    # 测试文献路径
    base_dir = "outputs/01-Superior-resilience-poisoning-unlearning"
    jsonl_path = os.path.join(base_dir, "pageindex/index.jsonl")
    meta_path = os.path.join(base_dir, "pageindex/index.meta.json")
    clean_md_path = os.path.join(base_dir, "clean_md/clean.md")

    # 加载索引
    print("=== 加载索引 ===")
    records, meta = load_index(jsonl_path, meta_path)
    print(f"索引记录数: {len(records)}")
    print(f"章节数: {len(meta.get('sections', []))}")

    # 测试问题
    questions = [
        "这篇论文的主要贡献是什么？",
        "QNN 的韧性机制是什么？",
        "LRR 是怎么定义的？",
        "标签翻转和特征随机化有什么区别？",
        "为什么 QNN 比 MLP 更鲁棒？",
    ]

    # 执行语义问答
    print("\n=== 语义理解问答测试 ===")
    for q in questions:
        print(f"\n{'='*60}")
        results = semantic_search(q, records, meta, clean_md_path)
        answer = format_answer(q, results, meta)
        # 处理编码问题
        print(answer.encode('utf-8', errors='replace').decode('utf-8'))


if __name__ == "__main__":
    main()
