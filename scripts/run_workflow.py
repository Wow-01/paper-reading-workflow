"""论文阅读工作流入口脚本。

支持单篇和批量处理模式。
"""

import argparse
import logging
import os
import sys
from datetime import datetime

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extract_mineru import extract_with_mineru
from extract_pdfplumber import extract_with_pdfplumber
from clean_markdown import clean_and_merge, save_clean_md
from build_pageindex import build_index
from prepare_summary_input import prepare_summary_input
from prepare_formula_input import prepare_formula_input
from write_failure_report import write_failure_report, write_batch_failure_summary


def load_config(config_path: str) -> dict:
    """加载配置文件。"""
    import yaml

    default_config = {
        "vision": {"enabled": True},
        "mineru": {"path": "magic-pdf"},
        "outputs": {"dir": "outputs/"},
        "thresholds": {"clean_md_min_chars": 800},
        "logging": {"level": "INFO", "format": "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"},
    }

    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            # 合并默认配置
            for key in default_config:
                if key not in config:
                    config[key] = default_config[key]
            return config

    return default_config


def setup_logging(log_dir: str, level: str = "INFO") -> None:
    """配置日志。"""
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "run.log")

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def process_single(pdf_path: str, config: dict) -> dict:
    """处理单篇 PDF。

    Args:
        pdf_path: PDF 文件路径
        config: 配置字典

    Returns:
        处理结果字典
    """
    logger = logging.getLogger("run_workflow")

    pdf_stem = os.path.splitext(os.path.basename(pdf_path))[0]
    outputs_dir = config["outputs"]["dir"]
    output_base = os.path.join(outputs_dir, pdf_stem)

    logger.info("=" * 60)
    logger.info("开始处理: %s", pdf_path)
    logger.info("=" * 60)

    # 创建输出目录结构
    raw_md_dir = os.path.join(output_base, "raw_md")
    clean_md_dir = os.path.join(output_base, "clean_md")
    pageindex_dir = os.path.join(output_base, "pageindex")
    summary_dir = os.path.join(output_base, "summary")
    logs_dir = os.path.join(output_base, "logs")

    for d in [raw_md_dir, clean_md_dir, pageindex_dir, summary_dir, logs_dir]:
        os.makedirs(d, exist_ok=True)

    # 设置该论文的日志
    log_file = os.path.join(logs_dir, "run.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s"))
    logger.addHandler(file_handler)

    try:
        # 步骤1: MinerU 提取
        logger.info("[步骤1/6] MinerU 提取")
        raw_md_path = extract_with_mineru(pdf_path, raw_md_dir)

        # 步骤2: 检查是否需要 pdfplumber 补充
        logger.info("[步骤2/6] 检查提取质量")
        threshold = config["thresholds"]["clean_md_min_chars"]
        plumber_text = ""

        if raw_md_path:
            with open(raw_md_path, "r", encoding="utf-8") as f:
                raw_content = f.read()

            if len(raw_content) < threshold:
                logger.warning("MinerU 提取内容过短（%d 字），使用 pdfplumber 补充", len(raw_content))
                plumber_text = extract_with_pdfplumber(pdf_path)
        else:
            logger.warning("MinerU 提取失败，使用 pdfplumber 作为备选")
            plumber_text = extract_with_pdfplumber(pdf_path)

            # 如果 pdfplumber 成功，创建 raw.md
            if plumber_text:
                raw_md_path = os.path.join(raw_md_dir, "raw.md")
                with open(raw_md_path, "w", encoding="utf-8") as f:
                    f.write(plumber_text)
                # 清空 plumber_text，因为已经写入 raw.md，避免重复拼接
                plumber_text = ""

        # 检查是否有可用的提取结果
        if not raw_md_path or (not plumber_text and not os.path.exists(raw_md_path)):
            raise Exception("PDF 提取失败：MinerU 和 pdfplumber 均未成功")

        # 步骤3: Markdown 清洗
        logger.info("[步骤3/6] Markdown 清洗")
        clean_content = clean_and_merge(raw_md_path, plumber_text)

        if len(clean_content) < threshold:
            logger.warning("清洗后内容过短（%d 字），可能提取失败", len(clean_content))

        clean_md_path = os.path.join(clean_md_dir, "clean.md")
        save_clean_md(clean_content, clean_md_path)

        # 步骤4: 构建 PageIndex
        logger.info("[步骤4/6] 构建 PageIndex")
        jsonl_path, meta_path = build_index(clean_md_path, pageindex_dir)

        # 步骤5: 准备总结输入
        logger.info("[步骤5/6] 准备总结输入")
        summary_input_path = os.path.join(summary_dir, "input-for-summary.md")
        prepare_summary_input(clean_md_path, meta_path, summary_input_path)

        # 准备公式输入（按需）
        formula_input_path = os.path.join(summary_dir, "input-for-formula.md")
        formula_result = prepare_formula_input(clean_md_path, formula_input_path)
        if formula_result:
            logger.info("公式输入文件已生成")

        # 步骤6: 生成交付指引
        logger.info("[步骤6/6] 生成交付指引")
        delivery_guide_path = os.path.join(output_base, "交付指引.md")
        _generate_delivery_guide(
            delivery_guide_path,
            pdf_stem,
            clean_md_path,
            meta_path,
            jsonl_path,
            formula_result is not None,
            config["vision"]["enabled"],
        )

        logger.info("处理完成: %s", pdf_path)

        return {
            "file": pdf_path,
            "status": "success",
            "output_dir": output_base,
        }

    except Exception as e:
        logger.error("处理失败: %s", str(e))

        # 生成失败报告
        failure_path = os.path.join(output_base, "failure.md")
        write_failure_report(
            pdf_path=pdf_path,
            error=str(e),
            stage="workflow",
            output_path=failure_path,
        )

        return {
            "file": pdf_path,
            "status": "failed",
            "error": str(e),
            "stage": "workflow",
        }

    finally:
        logger.removeHandler(file_handler)
        file_handler.close()


def _generate_delivery_guide(
    output_path: str,
    pdf_stem: str,
    clean_md_path: str,
    meta_path: str,
    jsonl_path: str,
    has_formulas: bool,
    vision_enabled: bool,
) -> None:
    """生成交付指引文件。"""
    lines = [
        "# 交给 Claude 的文件清单",
        "",
        f"**论文**: {pdf_stem}",
        "",
        "## 必读文件",
        "",
        f"- `clean_md/clean.md`（清洗后的论文正文）",
        f"- `pageindex/index.meta.json`（章节结构与统计）",
        "",
        "## 可选文件",
        "",
        f"- `pageindex/index.jsonl`（详细索引，需要精确定位时读取）",
    ]

    if vision_enabled:
        lines.append(f"- `raw_md/images/`（图片目录，需多模态分析时查看）")

    lines.extend([
        "",
        "## 执行指令",
        "",
        "请基于 clean_md 生成：",
        "",
        "1. **一页纸总结**（one-pager.md）",
        "   - 使用 `academic-researcher` skill",
        "   - 包含：动机、方法、结果、意义四个模块",
        "   - 每个模块不少于 2 句话",
        "",
        "2. **章节笔记**（section-notes.md）",
        "   - 每个一级标题至少 3 条要点",
        "   - 要点需包含「结论 + 来源」两部分",
        "",
        "3. **术语表**（glossary.md）",
        "   - 表格格式：符号/术语、含义、单位（如有）、出处",
        "",
        "4. **追问清单**（followups.md）",
        "   - 3-8 条问题，覆盖动机、方法、假设与结论",
        "   - 每条问题附定位线索（章节或公式）",
    ])

    if has_formulas:
        lines.extend([
            "",
            "5. **公式推导补全**（formula-notes.md）",
            "   - 使用 `math-reasoning` skill",
            "   - 读取 `summary/input-for-formula.md` 获取公式列表",
            "   - 补全推导步骤，标注假设/近似",
        ])

    lines.extend([
        "",
        "## 查询功能",
        "",
        "处理完成后，可以使用以下命令查询索引：",
        "",
        "```bash",
        "# 基本查询",
        f'python scripts/query_index.py pageindex/index.jsonl "Mpemba effect"',
        "",
        "# 中英文混合查询",
        f'python scripts/query_index.py pageindex/index.jsonl "量子 Monte Carlo"',
        "",
        "# 指定返回结果数量",
        f'python scripts/query_index.py pageindex/index.jsonl "Hubbard model" 10',
        "```",
        "",
        "## 输出位置",
        "",
        "所有输出文件请保存到：`summary/` 目录",
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    """主函数。"""
    parser = argparse.ArgumentParser(
        description="论文阅读工作流",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 单篇处理
  python scripts/run_workflow.py --file 02-Imaginary-time-Mpemba-effect.pdf

  # 批量处理（整个目录）
  python scripts/run_workflow.py --dir projects/

  # 批量处理（指定多个文件）
  python scripts/run_workflow.py --file a.pdf --file b.pdf --file c.pdf

  # 指定配置文件
  python scripts/run_workflow.py --file paper.pdf --config config.yaml

  # 详细日志
  python scripts/run_workflow.py --file paper.pdf --verbose
        """,
    )

    parser.add_argument("--file", action="append", help="PDF 文件名（可多次指定）")
    parser.add_argument("--dir", help="PDF 目录（批量处理）")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--verbose", action="store_true", help="详细日志")

    args = parser.parse_args()

    # 检查参数
    if not args.file and not args.dir:
        parser.error("必须指定 --file 或 --dir")

    # 加载配置
    config = load_config(args.config)

    # 设置日志
    log_level = "DEBUG" if args.verbose else config["logging"]["level"]
    setup_logging("outputs/logs", log_level)

    logger = logging.getLogger("run_workflow")
    logger.info("论文阅读工作流启动")

    # 收集 PDF 文件
    pdf_files = []

    if args.file:
        for f in args.file:
            # 如果是完整路径
            if os.path.isabs(f):
                pdf_files.append(f)
            else:
                # 尝试在 projects/ 目录下查找
                project_path = os.path.join("projects", f)
                if os.path.exists(project_path):
                    pdf_files.append(project_path)
                elif os.path.exists(f):
                    pdf_files.append(f)
                else:
                    logger.warning("文件不存在: %s", f)

    if args.dir:
        if os.path.isdir(args.dir):
            for f in os.listdir(args.dir):
                if f.lower().endswith(".pdf"):
                    pdf_files.append(os.path.join(args.dir, f))
        else:
            logger.error("目录不存在: %s", args.dir)
            sys.exit(1)

    if not pdf_files:
        logger.error("没有找到有效的 PDF 文件")
        sys.exit(1)

    logger.info("找到 %d 个 PDF 文件", len(pdf_files))

    # 处理 PDF
    results = []

    for pdf_path in pdf_files:
        result = process_single(pdf_path, config)
        results.append(result)

    # 汇总结果
    success_count = len([r for r in results if r["status"] == "success"])
    failed_count = len([r for r in results if r["status"] == "failed"])

    logger.info("=" * 60)
    logger.info("处理完成")
    logger.info("成功: %d, 失败: %d, 总计: %d", success_count, failed_count, len(results))
    logger.info("=" * 60)

    # 如果有失败，生成汇总报告
    if failed_count > 0:
        summary_path = os.path.join(config["outputs"]["dir"], "failure-summary.md")
        write_batch_failure_summary(results, summary_path)

    # 返回退出码
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()
