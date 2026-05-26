"""pdfplumber PDF 提取模块。

补充提取正文与表格，用于 MinerU 失败或过短时的降级。
"""

import logging

logger = logging.getLogger(__name__)


def extract_with_pdfplumber(pdf_path: str) -> str:
    """使用 pdfplumber 提取 PDF 文本和表格。

    Args:
        pdf_path: PDF 文件路径

    Returns:
        提取的文本内容
    """
    logger.info("开始 pdfplumber 提取: %s", pdf_path)

    try:
        import pdfplumber
    except ImportError:
        logger.error("pdfplumber 未安装，请运行: pip install pdfplumber")
        return ""

    text_parts = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                # 提取文本
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"<!-- Page {i + 1} -->\n{page_text}")

                # 提取表格
                tables = page.extract_tables()
                for j, table in enumerate(tables):
                    if table:
                        # 转换为 Markdown 表格格式
                        md_table = _table_to_markdown(table)
                        text_parts.append(f"\n**Table {j + 1} (Page {i + 1})**\n\n{md_table}\n")

        result = "\n\n".join(text_parts)
        logger.info("pdfplumber 提取完成，字符数: %d", len(result))
        return result

    except Exception as e:
        logger.error("pdfplumber 提取失败: %s", str(e))
        return ""


def _table_to_markdown(table: list) -> str:
    """将表格数据转换为 Markdown 格式。"""
    if not table or not table[0]:
        return ""

    # 处理表头
    headers = [str(cell) if cell else "" for cell in table[0]]
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"

    # 处理数据行
    rows = []
    for row in table[1:]:
        cells = [str(cell) if cell else "" for cell in row]
        # 确保列数一致
        while len(cells) < len(headers):
            cells.append("")
        rows.append("| " + " | ".join(cells[:len(headers)]) + " |")

    return "\n".join([header_line, separator] + rows)
