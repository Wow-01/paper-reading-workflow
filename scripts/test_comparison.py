"""树结构 vs JSONL 查询对比测试。"""

import json
import os
import time


def load_jsonl_index(jsonl_path):
    """加载 JSONL 索引。"""
    records = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def build_tree_from_meta(meta_path):
    """从 index.meta.json 构建树结构。"""
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    tree = {
        "title": "root",
        "children": []
    }

    sections = meta.get("sections", [])
    for sec in sections:
        tree["children"].append({
            "title": sec.get("title", ""),
            "section_path": sec.get("section_path", ""),
            "level": sec.get("level", 1),
            "children": []
        })

    return tree


def search_tree(tree, query, clean_md_path):
    """树结构查询。"""
    with open(clean_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    results = []
    query_lower = query.lower()
    keywords = query_lower.split()

    for node in tree.get("children", []):
        section_path = node.get("section_path", "")
        title = node.get("title", "")

        # 在 clean_md 中查找该章节
        section_content = extract_section(content, title)

        if section_content:
            content_lower = section_content.lower()
            matches = sum(1 for kw in keywords if kw in content_lower)

            if matches > 0:
                relevance = matches / len(keywords)
                results.append({
                    "section_path": section_path,
                    "title": title,
                    "content": section_content[:300],
                    "relevance": relevance
                })

    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:3]


def search_jsonl(records, query):
    """JSONL 查询。"""
    query_lower = query.lower()
    keywords = query_lower.split()

    results = []

    for record in records:
        text = record.get("text", "").lower()
        matches = sum(1 for kw in keywords if kw in text)

        if matches > 0:
            relevance = matches / len(keywords)
            results.append({
                "section_path": record.get("section_path", ""),
                "anchor_id": record.get("anchor_id", ""),
                "text": record.get("text", "")[:300],
                "source_ref": record.get("source_ref", ""),
                "relevance": relevance
            })

    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:3]


def extract_section(content, title):
    """从 clean_md 中提取章节内容。"""
    lines = content.split("\n")
    in_section = False
    section_lines = []

    for line in lines:
        if title in line and line.startswith("#"):
            in_section = True
            section_lines.append(line)
            continue

        if in_section:
            if line.startswith("#") and title not in line:
                break
            section_lines.append(line)

    return "\n".join(section_lines)


def run_comparison():
    """运行对比测试。"""
    # 测试文献路径
    base_dir = "outputs/01-Superior-resilience-poisoning-unlearning"
    meta_path = os.path.join(base_dir, "pageindex/index.meta.json")
    jsonl_path = os.path.join(base_dir, "pageindex/index.jsonl")
    clean_md_path = os.path.join(base_dir, "clean_md/clean.md")

    # 加载数据
    print("=== 加载数据 ===")
    tree = build_tree_from_meta(meta_path)
    records = load_jsonl_index(jsonl_path)
    print(f"树节点数: {len(tree['children'])}")
    print(f"JSONL 记录数: {len(records)}")

    # 测试问题
    questions = [
        "这篇论文的主要贡献是什么？",
        "QNN 的韧性机制是什么？",
        "LRR 是怎么定义的？",
        "标签翻转和特征随机化有什么区别？",
        "什么是量子机器遗忘？",
    ]

    # 执行对比测试
    print("\n=== 对比测试结果 ===")
    for q in questions:
        print(f"\n问题: {q}")
        print("-" * 60)

        # 树结构查询
        start_time = time.time()
        tree_results = search_tree(tree, q, clean_md_path)
        tree_time = time.time() - start_time

        # JSONL 查询
        start_time = time.time()
        jsonl_results = search_jsonl(records, q)
        jsonl_time = time.time() - start_time

        print(f"\n树结构查询 (耗时: {tree_time:.4f}s):")
        for i, r in enumerate(tree_results, 1):
            print(f"  {i}. [{r['section_path']}] {r['title']}")
            print(f"     相关性: {r['relevance']:.2f}")

        print(f"\nJSONL 查询 (耗时: {jsonl_time:.4f}s):")
        for i, r in enumerate(jsonl_results, 1):
            print(f"  {i}. [{r['section_path']}] {r['anchor_id']}")
            print(f"     相关性: {r['relevance']:.2f}")
            print(f"     来源: {r['source_ref']}")

        # 比较结果
        print(f"\n比较:")
        print(f"  树结构返回: {len(tree_results)} 个结果")
        print(f"  JSONL 返回: {len(jsonl_results)} 个结果")
        print(f"  树结构耗时: {tree_time:.4f}s")
        print(f"  JSONL 耗时: {jsonl_time:.4f}s")


if __name__ == "__main__":
    run_comparison()
