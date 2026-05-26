"""Markdown 清洗模块。

合并 MinerU 和 pdfplumber 的提取结果，清洗生成 clean_md。
"""

import logging
import re

logger = logging.getLogger(__name__)


def clean_and_merge(raw_md_path: str, plumber_text: str = "") -> str:
    """合并并清洗 Markdown 内容。

    Args:
        raw_md_path: raw.md 文件路径
        plumber_text: pdfplumber 补充提取的文本（可选）

    Returns:
        清洗后的 Markdown 内容
    """
    logger.info("开始 Markdown 清洗")

    # 读取 raw.md
    with open(raw_md_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # 合并内容
    if plumber_text:
        content = raw_content + "\n\n---\n\n[以下为 pdfplumber 补充提取]\n\n" + plumber_text
    else:
        content = raw_content

    # 清洗步骤
    content = _normalize_headers(content)
    content = _preserve_figure_captions(content)
    content = _normalize_formulas(content)
    content = _clean_whitespace(content)

    logger.info("Markdown 清洗完成，字符数: %d", len(content))
    return content


def _normalize_headers(content: str) -> str:
    """规范化章节标题。

    识别格式：
    - # 1. Introduction（已有 Markdown 标题）
    - Introduction—（标题后跟破折号，同行）
    - I. Introduction（罗马数字编号）
    - 1 Introduction 或 1. Introduction（数字编号）
    - Abstract、Introduction、Conclusion 等常见章节名
    """
    # 先处理已有的 Markdown 标题
    content = re.sub(r'([^\n])(#{1,6}\s)', r'\1\n\n\2', content)
    content = re.sub(r'(#{1,6}\s.+)\n([^\n])', r'\1\n\n\2', content)

    # 常见论文章节标题列表
    common_sections = [
        'Abstract', 'Introduction', 'Conclusion', 'Conclusions',
        'Methods', 'Method', 'Results', 'Discussion', 'Acknowledgments',
        'Acknowledgements', 'References', 'Appendix', 'Supplementary',
    ]

    # 格式1: 常见章节名后跟破折号（同行），如 "Introduction—"
    for section in common_sections:
        # 匹配：章节名 + 可选空格 + 破折号（— 或 --）
        pattern = r'(?<=\n)(' + section + r')\s*[—\-]{1,2}\s'
        content = re.sub(pattern, r'\n\n# \1\n\n', content, flags=re.IGNORECASE)
        # 也匹配行首的情况
        pattern = r'^(' + section + r')\s*[—\-]{1,2}\s'
        content = re.sub(pattern, r'# \1\n\n', content, flags=re.IGNORECASE)

    # 格式2: 数字编号的章节标题（如 "1 Introduction" 或 "1. Introduction"）
    # 要求：数字后跟空格，然后是至少2个字符的英文单词，再跟破折号或换行
    content = re.sub(
        r'(?<=\n)(\d+)\s*\.?\s+([A-Z][a-zA-Z]{2,}(?:\s+[a-zA-Z]+)*)\s*[—\-]{1,2}\s',
        r'\n\n# \1. \2\n\n',
        content
    )

    # 格式3: 罗马数字编号（如 "I. Introduction"）
    roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    for numeral in roman_numerals:
        content = re.sub(
            r'(?<=\n)(' + numeral + r')\.\s+([A-Z][a-zA-Z]{2,}(?:\s+[a-zA-Z]+)*)\s*[—\-]{1,2}\s',
            r'\n\n# \1. \2\n\n',
            content
        )

    # 格式4: "X.Y" 子章节（如 "2.1 Method"）
    content = re.sub(
        r'(?<=\n)(\d+\.\d+)\s+([A-Z][a-zA-Z]{2,}(?:\s+[a-zA-Z]+)*)\s*[—\-]{1,2}\s',
        r'\n\n## \1 \2\n\n',
        content
    )

    # 清理多余的空行
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content


def _preserve_figure_captions(content: str) -> str:
    """保留图注。

    识别格式：
    - Figure X: description
    - Fig. X: description
    - 图 X: description
    """
    # 确保图注段落完整
    patterns = [
        r'(Figure\s+\d+[:\.].*)',
        r'(Fig\.\s+\d+[:\.].*)',
        r'(图\s+\d+[:\.].*)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            logger.debug("保留图注: %s", match[:50])

    return content


def _normalize_formulas(content: str) -> str:
    """规范化公式块。

    识别格式：
    - $$...$$
    - \[...\]
    - \(...\)
    """
    # 确保公式块前后有空行
    content = re.sub(r'([^\n])(\$\$)', r'\1\n\n\2', content)
    content = re.sub(r'(\$\$)([^\n])', r'\1\n\n\2', content)
    content = re.sub(r'([^\n])(\\\[)', r'\1\n\n\2', content)
    content = re.sub(r'(\\\])([^\n])', r'\1\n\n\2', content)
    return content


def _clean_whitespace(content: str) -> str:
    """清理空白字符。"""
    # 将多个空行合并为两个
    content = re.sub(r'\n{3,}', '\n\n', content)
    # 移除行尾空白
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    return content


def save_clean_md(content: str, output_path: str) -> None:
    """保存 clean_md 文件。

    Args:
        content: 清洗后的 Markdown 内容
        output_path: 输出文件路径
    """
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info("clean_md 已保存: %s", output_path)
