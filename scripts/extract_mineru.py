"""MinerU PDF 提取模块。

调用 MinerU 提取 PDF 内容，输出 raw_md。
使用 Python API 而非 CLI，避免 DLL 初始化问题。
"""

import logging
import os
import shutil
import ssl
from pathlib import Path

logger = logging.getLogger(__name__)


def find_main_md_in_output(output_dir: str, pdf_stem: str) -> str | None:
    """在 MinerU 输出目录中查找主 md 文件。

    MinerU 输出结构：
        output_dir/
        └── pdf_stem/
            └── auto/  # 或 ocr/ txt/
                ├── pdf_stem.md  # 主 Markdown
                ├── images/
                └── content_list.json
    """
    # MinerU 会创建一个以 pdf_stem 命名的子目录
    mineru_subdir = os.path.join(output_dir, pdf_stem)
    if not os.path.exists(mineru_subdir):
        # 如果没有子目录，直接在 output_dir 中查找
        mineru_subdir = output_dir

    for method_dir in ["auto", "txt", "ocr"]:
        md_dir = os.path.join(mineru_subdir, method_dir)
        if os.path.exists(md_dir):
            for f in os.listdir(md_dir):
                if f.endswith(".md"):
                    return os.path.join(md_dir, f)
    return None


def extract_with_mineru(pdf_path: str, output_dir: str, **kwargs) -> str | None:
    """调用 MinerU Python API 提取 PDF。

    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录（outputs/<stem>/raw_md/）

    Returns:
        raw.md 文件路径，失败返回 None
    """
    logger.info("开始 MinerU 提取: %s", pdf_path)

    # 禁用 SSL 验证（解决 layoutreader 模型下载问题）
    ssl._create_default_https_context = ssl._create_unverified_context

    try:
        from magic_pdf.tools.common import do_parse
    except ImportError:
        logger.error("无法导入 magic_pdf，请确保已安装 magic-pdf")
        return None

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 读取 PDF 文件
    pdf_path_obj = Path(pdf_path)
    if not pdf_path_obj.exists():
        logger.error("PDF 文件不存在: %s", pdf_path)
        return None

    pdf_bytes = pdf_path_obj.read_bytes()
    pdf_stem = pdf_path_obj.stem

    logger.info("PDF 读取成功，大小: %d bytes", len(pdf_bytes))

    try:
        # 调用 MinerU Python API
        do_parse(
            output_dir,
            pdf_stem,
            pdf_bytes,
            [],  # model_list（空列表使用默认模型）
            'auto',  # parse_method
            False,  # debug_able
            True,  # f_draw_span_bbox
            True,  # f_draw_layout_bbox
            True,  # f_dump_md
            True,  # f_dump_middle_json
            True,  # f_dump_model_json
            True,  # f_dump_orig_pdf
            True,  # f_dump_content_list
            'mm_markdown',  # f_make_md_mode
            False,  # f_draw_model_bbox
            False,  # f_draw_line_sort_bbox
            False,  # f_draw_char_bbox
            0,  # start_page_id
            None,  # end_page_id
            None,  # lang
            None,  # layout_model
            True,  # formula_enable
            True,  # table_enable
        )

        logger.info("MinerU 执行完成")

    except Exception as e:
        logger.error("MinerU 执行失败: %s", str(e))
        return None

    # 查找生成的主 md 文件
    main_md_path = find_main_md_in_output(output_dir, pdf_stem)

    if main_md_path:
        # 复制并重命名为 raw.md
        raw_md_path = os.path.join(output_dir, "raw.md")
        shutil.copy2(main_md_path, raw_md_path)

        # 统计字符数
        with open(raw_md_path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.info("MinerU 提取完成，字符数: %d", len(content))
        return raw_md_path
    else:
        logger.error("未找到 MinerU 生成的 Markdown 文件")
        return None
