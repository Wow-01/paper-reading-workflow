"""公式输入准备模块。

从 clean_md 中提取公式块和上下文，生成输入文件供 Claude 调用 skill。
"""

import logging
import os
import re

logger = logging.getLogger(__name__)


def prepare_formula_input(clean_md_path: str, output_path: str) -> str | None:
    """准备公式输入文件。

    Args:
        clean_md_path: clean.md 文件路径
        output_path: 输出文件路径

    Returns:
        生成的输入文件路径，如果没有公式则返回 None
    """
    logger.info("开始准备公式输入")

    # 读取 clean_md
    with open(clean_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取公式块和上下文
    formulas = _extract_formulas_with_context(content)

    if not formulas:
        logger.info("未发现公式块，跳过公式输入准备")
        return None

    # 构建输入文件
    input_content = _build_formula_input(formulas)

    # 保存文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(input_content)

    logger.info("公式输入文件已生成: %s，共 %d 个公式", output_path, len(formulas))
    return output_path


def _extract_formulas_with_context(content: str) -> list[dict]:
    """提取公式块及其上下文。"""
    formulas = []
    lines = content.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]

        # 检测公式块开始
        if line.strip().startswith("$$") or line.strip().startswith("\\["):
            formula_lines = [line]
            formula_start = i

            # 收集公式块
            j = i + 1
            while j < len(lines):
                formula_lines.append(lines[j])
                if lines[j].strip().endswith("$$") or lines[j].strip().endswith("\\]"):
                    break
                j += 1

            # 获取上下文（前后各3段）
            context_before = _get_context_before(lines, formula_start, 3)
            context_after = _get_context_after(lines, j + 1, 3)

            formulas.append({
                "formula": "\n".join(formula_lines),
                "context_before": context_before,
                "context_after": context_after,
                "line_number": formula_start + 1,
            })

            i = j + 1
        else:
            i += 1

    return formulas


def _get_context_before(lines: list[str], index: int, count: int) -> str:
    """获取指定位置之前的上下文。"""
    context = []
    found = 0

    for i in range(index - 1, -1, -1):
        if found >= count:
            break
        line = lines[i].strip()
        if line and not line.startswith("#"):
            context.insert(0, line)
            found += 1

    return "\n".join(context)


def _get_context_after(lines: list[str], index: int, count: int) -> str:
    """获取指定位置之后的上下文。"""
    context = []
    found = 0

    for i in range(index, len(lines)):
        if found >= count:
            break
        line = lines[i].strip()
        if line and not line.startswith("#"):
            context.append(line)
            found += 1

    return "\n".join(context)


def _build_formula_input(formulas: list[dict]) -> str:
    """构建公式输入文件内容。"""
    lines = [
        "# 公式推导补全输入",
        "",
        "以下是从论文中提取的公式块及其上下文，请对每个公式进行推导补全。",
        "",
        "**要求**：",
        "1. 补全作者省略的中间推导步骤",
        "2. 标明使用的数学技巧、边界条件、近似或物理假设",
        "3. 如果某一步无法可靠补全，明确说明不确定性",
        "",
        "---",
        "",
    ]

    for i, formula in enumerate(formulas, 1):
        lines.extend([
            f"## 公式 {i}",
            "",
            "**上下文（之前）**：",
            "",
            formula["context_before"] if formula["context_before"] else "（无）",
            "",
            "**公式**：",
            "",
            formula["formula"],
            "",
            "**上下文（之后）**：",
            "",
            formula["context_after"] if formula["context_after"] else "（无）",
            "",
            "**推导补全**：",
            "",
            "（请在此处填写推导过程）",
            "",
            "---",
            "",
        ])

    return "\n".join(lines)
