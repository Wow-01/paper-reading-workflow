"""树结构查询脚本测试。

使用 PageIndex 树结构进行问答。
"""

import json
import os


def load_tree_index(index_path):
    """加载树结构索引。"""
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_tree_from_meta(meta_path):
    """从 index.meta.json 构建树结构。"""
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # 构建层次树
    tree = {
        "title": "root",
        "children": []
    }

    # 按 section_path 构建树
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
    """在树结构中搜索。

    模拟 PageIndex 的树搜索方式：
    1. 读取树结构
    2. 推理哪个节点最相关
    3. 定位到具体章节
    """
    # 读取 clean_md
    with open(clean_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    results = []

    # 遍历树节点
    for node in tree.get("children", []):
        section_path = node.get("section_path", "")
        title = node.get("title", "")

        # 在 clean_md 中查找该章节
        section_content = extract_section(content, title)

        if section_content:
            # 检查是否包含查询关键词
            relevance = calculate_relevance(query, section_content)
            if relevance > 0:
                results.append({
                    "section_path": section_path,
                    "title": title,
                    "content": section_content[:500],  # 限制长度
                    "relevance": relevance
                })

    # 按相关性排序
    results.sort(key=lambda x: x["relevance"], reverse=True)

    return results[:3]  # 返回 top 3


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


def calculate_relevance(query, content):
    """计算查询与内容的相关性。"""
    query_lower = query.lower()
    content_lower = content.lower()

    # 简单的关键词匹配
    keywords = query_lower.split()
    matches = sum(1 for kw in keywords if kw in content_lower)

    return matches / len(keywords) if keywords else 0


def main():
    """主函数。"""
    # 测试文献路径
    base_dir = "outputs/01-Superior-resilience-poisoning-unlearning"
    meta_path = os.path.join(base_dir, "pageindex/index.meta.json")
    clean_md_path = os.path.join(base_dir, "clean_md/clean.md")

    # 构建树结构
    print("=== 构建树结构 ===")
    tree = build_tree_from_meta(meta_path)
    print(f"树节点数: {len(tree['children'])}")

    # 测试问题
    questions = [
        "这篇论文的主要贡献是什么？",
        "QNN 的韧性机制是什么？",
        "LRR 是怎么定义的？",
        "标签翻转和特征随机化有什么区别？",
    ]

    # 执行查询
    print("\n=== 树结构查询测试 ===")
    for q in questions:
        print(f"\n问题: {q}")
        results = search_tree(tree, q, clean_md_path)
        for i, r in enumerate(results, 1):
            print(f"  结果{i}: [{r['section_path']}] {r['title']}")
            print(f"    相关性: {r['relevance']:.2f}")
            print(f"    内容: {r['content'][:100]}...")


if __name__ == "__main__":
    main()
