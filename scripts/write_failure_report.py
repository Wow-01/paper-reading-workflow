"""失败报告模块。

记录失败原因与可重试建议。
"""

import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def write_failure_report(
    pdf_path: str,
    error: str,
    stage: str,
    output_path: str,
    suggestions: list[str] | None = None,
) -> str:
    """生成失败报告。

    Args:
        pdf_path: PDF 文件路径
        error: 错误信息
        stage: 失败阶段（如 extract_mineru, clean_markdown 等）
        output_path: 输出文件路径
        suggestions: 建议的解决方案

    Returns:
        生成的报告文件路径
    """
    logger.info("生成失败报告: %s", output_path)

    if suggestions is None:
        suggestions = _get_default_suggestions(stage)

    # 构建报告内容
    content = _build_report(pdf_path, error, stage, suggestions)

    # 保存文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info("失败报告已生成: %s", output_path)
    return output_path


def _build_report(pdf_path: str, error: str, stage: str, suggestions: list[str]) -> str:
    """构建报告内容。"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# 失败报告",
        "",
        "## 基本信息",
        "",
        f"- **时间**: {timestamp}",
        f"- **PDF 文件**: `{pdf_path}`",
        f"- **失败阶段**: {stage}",
        "",
        "## 错误信息",
        "",
        "```",
        error,
        "```",
        "",
        "## 建议解决方案",
        "",
    ]

    for i, suggestion in enumerate(suggestions, 1):
        lines.append(f"{i}. {suggestion}")

    lines.extend([
        "",
        "## 可重试步骤",
        "",
        f"可以尝试重新运行失败的阶段：",
        "",
        "```bash",
        f"python scripts/run_workflow.py --file {os.path.basename(pdf_path)}",
        "```",
        "",
        "如果问题持续存在，请检查：",
        "1. PDF 文件是否损坏",
        "2. MinerU 是否正确安装",
        "3. 磁盘空间是否充足",
    ])

    return "\n".join(lines)


def _get_default_suggestions(stage: str) -> list[str]:
    """根据失败阶段获取默认建议。"""
    suggestions = {
        "extract_mineru": [
            "检查 MinerU 是否正确安装：`magic-pdf --version`",
            "检查 PDF 文件是否损坏",
            "尝试使用 pdfplumber 作为备选方案",
            "检查模型文件是否完整",
        ],
        "extract_pdfplumber": [
            "检查 pdfplumber 是否安装：`pip install pdfplumber`",
            "检查 PDF 文件是否损坏",
            "尝试使用其他 PDF 阅读器打开文件",
        ],
        "clean_markdown": [
            "检查 raw.md 文件是否存在",
            "检查文件编码是否为 UTF-8",
            "检查磁盘空间是否充足",
        ],
        "build_pageindex": [
            "检查 clean.md 文件是否存在",
            "检查文件内容是否为空",
            "检查输出目录权限",
        ],
        "default": [
            "检查输入文件是否存在",
            "检查输出目录权限",
            "查看详细日志获取更多信息",
        ],
    }

    return suggestions.get(stage, suggestions["default"])


def write_batch_failure_summary(results: list[dict], output_path: str) -> str:
    """生成批量处理失败汇总。

    Args:
        results: 处理结果列表，每项包含 file, status, error 等字段
        output_path: 输出文件路径

    Returns:
        生成的汇总文件路径
    """
    logger.info("生成批量失败汇总")

    failed = [r for r in results if r.get("status") == "failed"]

    if not failed:
        logger.info("没有失败的处理任务")
        return ""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# 批量处理失败汇总",
        "",
        f"- **时间**: {timestamp}",
        f"- **总任务数**: {len(results)}",
        f"- **失败数**: {len(failed)}",
        f"- **成功率**: {(len(results) - len(failed)) / len(results) * 100:.1f}%",
        "",
        "## 失败列表",
        "",
        "| 文件 | 失败阶段 | 错误信息 |",
        "|------|----------|----------|",
    ]

    for item in failed:
        file_name = os.path.basename(item.get("file", "unknown"))
        stage = item.get("stage", "unknown")
        error = item.get("error", "unknown")[:100]  # 限制长度
        lines.append(f"| {file_name} | {stage} | {error} |")

    lines.extend([
        "",
        "## 建议",
        "",
        "1. 检查失败的 PDF 文件是否损坏",
        "2. 查看各个失败报告了解详细原因",
        "3. 尝试单独处理失败的文件",
    ])

    # 保存文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info("批量失败汇总已生成: %s", output_path)
    return output_path
