"""总结输入准备模块。

读取 clean_md 和 index.meta.json，生成结构化输入文件供 Claude 调用 skill。
"""

import json
import logging
import os

logger = logging.getLogger(__name__)


def prepare_summary_input(clean_md_path: str, meta_path: str, output_path: str) -> str:
    """准备总结输入文件。

    Args:
        clean_md_path: clean.md 文件路径
        meta_path: index.meta.json 文件路径
        output_path: 输出文件路径

    Returns:
        生成的输入文件路径
    """
    logger.info("开始准备总结输入")

    # 读取 clean_md
    with open(clean_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 读取元数据
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # 构建输入文件
    sections = meta.get("sections", [])
    stats = meta.get("stats", {})

    input_content = _build_input_content(content, sections, stats)

    # 保存文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(input_content)

    logger.info("总结输入文件已生成: %s", output_path)
    return output_path


def _build_input_content(content: str, sections: list, stats: dict) -> str:
    """构建输入文件内容。"""
    lines = [
        "# 论文总结输入",
        "",
        "## 章节结构",
        "",
    ]

    # 添加章节结构
    for sec in sections:
        level = sec.get("level", 1)
        title = sec.get("title", "")
        section_path = sec.get("section_path", "")
        indent = "  " * (level - 1)
        lines.append(f"{indent}- {title} (`{section_path}`)")

    lines.extend([
        "",
        "## 统计信息",
        "",
        f"- 总字符数: {stats.get('total_chars', 0)}",
        f"- 章节数: {stats.get('total_sections', 0)}",
        f"- 段落数: {stats.get('paragraphs', 0)}",
        f"- 公式数: {stats.get('equations', 0)}",
        f"- 图片数: {stats.get('figures', 0)}",
        f"- 表格数: {stats.get('tables', 0)}",
        "",
        "## 论文正文",
        "",
        content,
    ])

    return "\n".join(lines)
