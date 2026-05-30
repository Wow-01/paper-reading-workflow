"""PageIndex 构建模块。

生成 index.jsonl 与 index.meta.json 索引文件。
支持关键词提取和摘要生成。
"""

import json
import logging
import os
import re
from typing import List

logger = logging.getLogger(__name__)


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """从文本中提取关键词。

    提取规则：
    - 英文术语（大写开头的词组，最多3个单词）
    - 中文词汇（2-4字）
    - 缩写（全大写或大写+数字）
    - 关键概念词

    Args:
        text: 输入文本
        max_keywords: 最大关键词数量

    Returns:
        关键词列表
    """
    keywords = []

    # 1. 提取英文术语（大写开头的词组，最多3个单词）
    en_terms = re.findall(r'[A-Z][a-zA-Z]+(?:\s+[a-z]+){0,2}', text)
    for term in en_terms:
        term = term.strip()
        # 过滤太长的术语
        if 2 < len(term) < 30 and term not in keywords:
            keywords.append(term)

    # 2. 提取缩写（全大写或大写+数字，如 QMC, MBL, AFM）
    abbreviations = re.findall(r'\b[A-Z]{2,}(?:\d+)?\b', text)
    for abbr in abbreviations:
        if abbr not in keywords and len(abbr) < 10:
            keywords.append(abbr)

    # 3. 提取中文词汇（2-4字，更有意义）
    cn_terms = re.findall(r'[一-鿿]{2,4}', text)
    for term in cn_terms:
        if term not in keywords:
            keywords.append(term)

    # 4. 提取关键概念词（常见学术词汇）
    concept_patterns = [
        r'(?:quantum|classical)\s+\w+',
        r'(?:ground|excited)\s+state',
        r'(?:phase|quantum)\s+transition',
        r'(?:fermion|boson|spin)\s+model',
    ]
    for pattern in concept_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if match.lower() not in [kw.lower() for kw in keywords]:
                keywords.append(match)

    return keywords[:max_keywords]


def generate_summary_prompt(text: str, max_length: int = 200) -> str:
    """生成摘要提示词（由 Claude 处理）。

    Args:
        text: 输入文本
        max_length: 提示词最大长度

    Returns:
        摘要提示词
    """
    # 限制输入长度
    text_preview = text[:max_length]

    prompt = f"""请用 1-2 句话概括以下内容的核心要点，只返回概括，不要其他内容：

{text_preview}"""

    return prompt


def generate_auto_summary(text: str, max_length: int = 100) -> str:
    """自动生成简单摘要（基于规则，无需 LLM）。

    提取文本的前几句话作为摘要。

    Args:
        text: 输入文本
        max_length: 摘要最大长度

    Returns:
        自动生成的摘要
    """
    # 按句子分割（英文句号、中文句号、问号、感叹号）
    sentences = re.split(r'[.!?。！？]', text)

    # 取前2句话
    summary_parts = []
    for sentence in sentences[:2]:
        sentence = sentence.strip()
        if len(sentence) > 10:  # 过滤太短的句子
            summary_parts.append(sentence)

    summary = '. '.join(summary_parts)

    # 限制长度
    if len(summary) > max_length:
        summary = summary[:max_length] + '...'

    return summary if summary else text[:max_length]


def build_index(clean_md_path: str, output_dir: str) -> tuple[str, str]:
    """构建 PageIndex 索引。

    Args:
        clean_md_path: clean.md 文件路径
        output_dir: pageindex 输出目录

    Returns:
        (index.jsonl 路径, index.meta.json 路径)
    """
    logger.info("开始构建 PageIndex")

    # 读取 clean_md
    with open(clean_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 解析章节结构
    sections = _parse_sections(content)
    logger.info("识别到 %d 个章节", len(sections))

    # 构建索引记录
    records = _build_records(content, sections)

    # 保存文件
    os.makedirs(output_dir, exist_ok=True)

    jsonl_path = os.path.join(output_dir, "index.jsonl")
    meta_path = os.path.join(output_dir, "index.meta.json")

    # 保存 index.jsonl
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # 保存 index.meta.json
    meta = _build_meta(sections, records, content)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    logger.info("PageIndex 构建完成: %d 条记录", len(records))
    return jsonl_path, meta_path


def _parse_sections(content: str) -> list[dict]:
    """解析章节结构。

    识别格式：
    - # 1. Introduction → sec1
    - ## 2.1 Method → sec2.1
    - ### 3.2.1 Details → sec3.2.1
    - # Abstract → abstract
    - # Introduction → introduction
    """
    sections = []
    current_section = None

    for line in content.split("\n"):
        # 匹配标题
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()

            # 生成 section_path
            section_path = _generate_section_path(title)

            current_section = {
                "level": level,
                "title": title,
                "section_path": section_path,
            }
            sections.append(current_section)

    return sections


def _generate_section_path(title: str) -> str:
    """生成 section_path。

    规则：
    - 有编号 → sec + 编号（如 2.1 Method → sec2.1）
    - 无编号 → 标题小写，空格替换为连字符（如 Abstract → abstract）
    """
    # 尝试提取编号
    match = re.match(r'^(\d+(?:\.\d+)*)\s+', title)
    if match:
        return "sec" + match.group(1)

    # 无编号，转换为小写连字符格式
    title_lower = title.lower().strip()
    title_slug = re.sub(r'[^a-z0-9]+', '-', title_lower)
    title_slug = title_slug.strip('-')
    return title_slug if title_slug else "unknown"


def _build_records(content: str, sections: list[dict]) -> list[dict]:
    """构建索引记录。

    字段：
    - section_path: 章节路径
    - anchor_id: 段落/公式锚点
    - text: 原文片段
    - source_ref: 页码定位线索
    - keywords: 关键词列表（新增）
    - summary: 摘要（新增）
    """
    records = []
    current_section = "unknown"
    paragraph_index = 0
    equation_counter = 0
    figure_counter = 0
    table_counter = 0

    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # 检测章节标题
        section_match = re.match(r'^#{1,6}\s+(.+)$', line)
        if section_match:
            title = section_match.group(1).strip()
            current_section = _generate_section_path(title)
            paragraph_index = 0
            i += 1
            continue

        # 检测公式块
        if line.strip().startswith("$$") or line.strip().startswith("\\["):
            equation_counter += 1
            formula_text = _extract_formula_block(lines, i)
            record = {
                "section_path": current_section,
                "anchor_id": f"eq{equation_counter}",
                "text": formula_text[:500],  # 限制长度
                "source_ref": f"#{current_section}",
                "keywords": extract_keywords(formula_text, max_keywords=3),
                "summary": generate_auto_summary(formula_text, max_length=50),
            }
            records.append(record)
            # 跳过公式块
            while i < len(lines) and not (lines[i].strip().endswith("$$") or lines[i].strip().endswith("\\]")):
                i += 1
            i += 1
            continue

        # 检测图注
        fig_match = re.match(r'^(Figure|Fig\.?)\s+(\d+)', line, re.IGNORECASE)
        if fig_match:
            figure_counter += 1
            fig_id = fig_match.group(2)
            record = {
                "section_path": current_section,
                "anchor_id": f"fig{fig_id}",
                "text": line.strip()[:500],
                "source_ref": f"#{current_section}",
                "keywords": extract_keywords(line, max_keywords=3),
                "summary": generate_auto_summary(line, max_length=50),
            }
            records.append(record)
            i += 1
            continue

        # 检测表格标题
        table_match = re.match(r'^Table\s+(\d+)', line, re.IGNORECASE)
        if table_match:
            table_counter += 1
            table_id = table_match.group(1)
            record = {
                "section_path": current_section,
                "anchor_id": f"table{table_id}",
                "text": line.strip()[:500],
                "source_ref": f"#{current_section}",
                "keywords": extract_keywords(line, max_keywords=3),
                "summary": generate_auto_summary(line, max_length=50),
            }
            records.append(record)
            i += 1
            continue

        # 普通段落
        if line.strip() and not line.startswith("#"):
            paragraph_index += 1
            # 合并连续非空行作为段落
            para_lines = [line]
            while i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].startswith("#"):
                i += 1
                para_lines.append(lines[i])

            para_text = " ".join(para_lines).strip()
            if len(para_text) > 20:  # 过滤太短的行
                # 生成段落锚点
                section_parts = re.findall(r'\d+', current_section)
                if section_parts:
                    section_id = "-".join(section_parts)
                else:
                    section_id = "0"

                record = {
                    "section_path": current_section,
                    "anchor_id": f"para-{section_id}-{paragraph_index}",
                    "text": para_text[:500],  # 限制长度
                    "source_ref": f"#{current_section}",
                    "keywords": extract_keywords(para_text, max_keywords=5),
                    "summary": generate_auto_summary(para_text, max_length=100),
                }
                records.append(record)

        i += 1

    return records


def _extract_formula_block(lines: list[str], start: int) -> str:
    """提取公式块内容。"""
    block_lines = [lines[start]]
    i = start + 1

    while i < len(lines):
        block_lines.append(lines[i])
        if lines[i].strip().endswith("$$") or lines[i].strip().endswith("\\]"):
            break
        i += 1

    return "\n".join(block_lines)


def _build_meta(sections: list[dict], records: list[dict], content: str) -> dict:
    """构建索引元数据。"""
    # 统计信息
    stats = {
        "total_chars": len(content),
        "total_sections": len(sections),
        "total_records": len(records),
        "equations": len([r for r in records if r["anchor_id"].startswith("eq")]),
        "figures": len([r for r in records if r["anchor_id"].startswith("fig")]),
        "tables": len([r for r in records if r["anchor_id"].startswith("table")]),
        "paragraphs": len([r for r in records if r["anchor_id"].startswith("para")]),
    }

    # 章节树
    section_tree = []
    for sec in sections:
        section_tree.append({
            "level": sec["level"],
            "title": sec["title"],
            "section_path": sec["section_path"],
        })

    return {
        "sections": section_tree,
        "stats": stats,
    }
