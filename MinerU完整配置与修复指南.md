# MinerU (magic-pdf) 完整配置与修复指南

> 本文档整合了 MinerU 的安装配置、常见问题修复、Python API 调用方式以及项目中的实际使用经验。

---

## 1. 概述

### 1.1 什么是 MinerU

MinerU 和 magic-pdf 是**同一个工具**的两种称呼：
- **MinerU**：项目名称（GitHub 仓库名）
- **magic-pdf**：pip 包名（安装命令：`pip install magic-pdf[full]`）

### 1.2 功能特点

- 支持图片型和文本型 PDF 提取
- 自动检测 PDF 类型（auto 模式）
- 支持公式识别（LaTeX 格式）
- 支持 OCR 文字识别
- 支持表格识别
- 提取图片和图注

### 1.3 本项目使用方式

**推荐方式**：Python API（避免 DLL 初始化问题）

```python
from magic_pdf.tools.common import do_parse

do_parse(
    output_dir,      # 输出目录
    pdf_stem,        # PDF 文件名（不含扩展名）
    pdf_bytes,       # PDF 文件内容（bytes）
    [],              # model_list（空列表使用默认模型）
    'auto',          # parse_method: auto/txt/ocr
    # ... 其他参数
)
```

---

## 2. 环境配置

### 2.1 环境信息

| 项目 | 值 |
|------|-----|
| 操作系统 | Windows 11 Home China 10.0.26200 |
| Python 版本 | 3.11.9（.venv 环境） |
| magic-pdf 版本 | 1.3.12 |
| 模型目录 | `D:\MinerU\models\magic-pdf-1.3.12` |
| 配置文件 | `~/.magic-pdf.json` |

### 2.2 依赖版本

| 组件 | 推荐版本 | 不兼容版本 | 备注 |
|------|----------|------------|------|
| magic-pdf | 1.3.12 | - | 当前稳定版 |
| torch | CPU 最新版 | GPU 版本（无 CUDA） | 使用 CPU 版本 |
| transformers | 4.51.3 | 4.57.6+ | MFR 模型不兼容 |
| onnxruntime | 1.19.2 | 1.26.0 | DLL 加载问题 |
| pdfplumber | 最新版 | - | 无特殊要求 |

### 2.3 安装步骤（推荐顺序）

```bash
# 1. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 2. 安装 CPU 版 PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 3. 安装 magic-pdf
pip install magic-pdf[full]

# 4. 降级不兼容的包
pip install transformers==4.51.3
pip install onnxruntime==1.19.2

# 5. 下载模型（使用镜像加速）
set HF_ENDPOINT=https://hf-mirror.com
python -c "from magic_pdf.model.download import download_models; download_models()"

# 6. 修复模型目录结构
cd D:\MinerU\models\magic-pdf-1.3.12
xcopy /E /I models\* .

# 7. 修改 OCR 模型配置（v3 → v5）
# 编辑 .venv\Lib\site-packages\magic_pdf\model\sub_modules\ocr\paddleocr2pytorch\pytorchocr\utils\resources\models_config.yml
# 将所有 PP-OCRv3 改为 PP-OCRv5

# 8. 验证安装
magic-pdf --version
python -c "import magic_pdf; print('OK')"
```

---

## 3. 配置文件

### 3.1 magic-pdf.json

**位置**：`~/.magic-pdf.json`（用户主目录）

**完整配置**：
```json
{
  "models-dir": "D:\\MinerU\\models\\magic-pdf-1.3.12",
  "device-mode": "cpu",
  "table-config": {
    "is_table_recog_enable": false
  },
  "layout-config": {
    "model": "doclayout_yolo"
  },
  "formula-config": {
    "enable": true
  },
  "ocr-config": {
    "enable": true,
    "lang": "ch_lite"
  }
}
```

**配置说明**：

| 字段 | 说明 | 建议值 |
|------|------|--------|
| `models-dir` | 模型目录路径 | 根据实际路径修改 |
| `device-mode` | 设备模式 | `cpu`（无 GPU 时）或 `cuda` |
| `table-config.is_table_recog_enable` | 表格识别 | `false`（V1 暂不启用） |
| `layout-config.model` | 布局模型 | `doclayout_yolo` |
| `formula-config.enable` | 公式识别 | `true`（必须启用） |
| `ocr-config.enable` | OCR 识别 | `true`（必须启用） |
| `ocr-config.lang` | OCR 语言 | `ch_lite`（中文轻量版） |

### 3.2 模型模式配置

**位置**：`.venv\Lib\site-packages\magic_pdf\model\__init__.py`

**配置内容**：
```python
__use_inside_model__ = True
__model_mode__ = 'full'
```

**说明**：
- `__use_inside_model__ = True`：使用内置模型
- `__model_mode__ = 'full'`：使用完整模式（包含 OCR、MFR 等）
- `'lite'`：轻量模式（仅 PaddleOCR，无公式识别）

### 3.3 OCR 模型配置

**位置**：`.venv\Lib\site-packages\magic_pdf\model\sub_modules\ocr\paddleocr2pytorch\pytorchocr\utils\resources\models_config.yml`

**关键修改**：将所有 `PP-OCRv3` 改为 `PP-OCRv5`

```yaml
lang:
  ch_lite:
    det: ch_PP-OCRv5_det_infer.pth
    rec: ch_PP-OCRv5_rec_infer.pth
    dict: ppocrv5_dict.txt
  en:
    det: en_PP-OCRv5_det_infer.pth
    rec: en_PP-OCRv4_rec_infer.pth
    dict: en_dict.txt
```

### 3.4 项目配置 (config.yaml)

**位置**：项目根目录 `config.yaml`

```yaml
# 论文阅读工作流配置

vision:
  enabled: true  # V1默认开启视觉能力

mineru:
  path: magic-pdf  # MinerU命令路径

outputs:
  dir: outputs/  # 输出根目录

thresholds:
  clean_md_min_chars: 800  # clean_md最少字符数

logging:
  level: INFO  # 日志级别
  format: "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
```

---

## 4. Python API 调用

### 4.1 基本调用方式

```python
import ssl
from pathlib import Path
from magic_pdf.tools.common import do_parse

# 禁用 SSL 验证（解决 layoutreader 模型下载问题）
ssl._create_default_https_context = ssl._create_unverified_context

# 读取 PDF
pdf_path = "projects/paper.pdf"
pdf_bytes = Path(pdf_path).read_bytes()
pdf_stem = Path(pdf_path).stem

# 调用 MinerU
do_parse(
    "outputs/paper/raw_md",  # output_dir
    pdf_stem,                # pdf_stem
    pdf_bytes,               # pdf_bytes
    [],                      # model_list
    'auto',                  # parse_method
    False,                   # debug_able
    True,                    # f_draw_span_bbox
    True,                    # f_draw_layout_bbox
    True,                    # f_dump_md
    True,                    # f_dump_middle_json
    True,                    # f_dump_model_json
    True,                    # f_dump_orig_pdf
    True,                    # f_dump_content_list
    'mm_markdown',           # f_make_md_mode
    False,                   # f_draw_model_bbox
    False,                   # f_draw_line_sort_bbox
    False,                   # f_draw_char_bbox
    0,                       # start_page_id
    None,                    # end_page_id
    None,                    # lang
    None,                    # layout_model
    True,                    # formula_enable
    True,                    # table_enable
)
```

### 4.2 参数说明

| 参数 | 类型 | 说明 | 建议值 |
|------|------|------|--------|
| `output_dir` | str | 输出目录 | `outputs/<stem>/raw_md/` |
| `pdf_stem` | str | PDF 文件名（不含扩展名） | `Path(pdf_path).stem` |
| `pdf_bytes` | bytes | PDF 文件内容 | `Path(pdf_path).read_bytes()` |
| `model_list` | list | 模型列表 | `[]`（使用默认） |
| `parse_method` | str | 解析方法 | `'auto'`（推荐） |
| `debug_able` | bool | 调试模式 | `False` |
| `formula_enable` | bool | 公式识别 | `True` |
| `table_enable` | bool | 表格识别 | `True` |

### 4.3 parse_method 选项

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `auto` | 自动检测 PDF 类型 | **推荐**，质量最好 |
| `txt` | 文本提取模式 | 不需要公式识别时 |
| `ocr` | OCR 模式 | 图片型 PDF |

**关键区别**：
- `auto` 模式需要 layoutreader 模型（需禁用 SSL）
- `txt` 模式不需要 layoutreader，速度更快
- `auto` 模式公式格式正确（`$$...$$`），`txt` 模式公式格式较差

### 4.4 项目中的实现

**文件**：`scripts/extract_mineru.py`

```python
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
```

---

## 5. 输出结构

### 5.1 MinerU 原始输出

```
outputs/<pdf_stem>/raw_md/
└── <pdf_stem>/
    └── auto/  # 或 ocr/ txt/
        ├── <pdf_stem>.md           # 主 Markdown 文件
        ├── <pdf_stem>_content_list.json  # 内容列表
        ├── <pdf_stem>_layout.pdf   # 布局标注 PDF
        ├── <pdf_stem>_middle.json  # 中间结果
        ├── <pdf_stem>_model.json   # 模型结果
        ├── <pdf_stem>_origin.pdf   # 原始 PDF
        ├── <pdf_stem>_spans.pdf    # Spans 标注
        └── images/                 # 提取的图片
            ├── image1.jpg
            ├── image2.jpg
            └── ...
```

### 5.2 项目处理后输出

```
outputs/<pdf_stem>/
├── raw_md/
│   ├── raw.md                    # 复制并重命名的主 Markdown
│   └── <pdf_stem>/               # MinerU 原始输出（保留）
├── clean_md/
│   └── clean.md                  # 清洗后的 Markdown
├── pageindex/
│   ├── index.jsonl               # 索引文件
│   └── index.meta.json           # 索引元数据
├── summary/
│   ├── input-for-summary.md      # 总结输入
│   └── input-for-formula.md      # 公式输入
├── logs/
│   └── run.log                   # 运行日志
└── 交付指引.md                    # Claude 执行指引
```

### 5.3 Markdown 内容示例

**公式**（LaTeX 格式）：
```latex
$$
- \frac { \partial } { \partial \tau } \left| \psi ( \tau ) \right. = ( \hat { H } ( \tau ) - E _ { \tau } ) \left| \psi ( \tau ) \right. ,
$$
```

**图片引用**：
```markdown
![](images/64f73f7332b9baaa951b063b506ccbccd39592ba0bb48a888c8d83553324bd7a.jpg)
FIG. 1. The schematic illustration of imaginary-time Mpemba effect.
```

**章节标题**：
```markdown
# Imaginary-time Mpemba effect in quantum many-body systems
## Introduction
## Theoretical setup
```

---

## 6. 常见问题与解决方案

### 6.1 PyTorch DLL 加载失败 (c10.dll)

**现象**：
```
ImportError: DLL load failed while importing _C: 找不到指定的模块。
```

**原因**：Windows 上 PyTorch GPU 版本的 DLL 依赖缺失

**解决方案**：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

---

### 6.2 Python 环境混乱

**现象**：系统中有多个 Python 版本，导致包安装位置混乱

**解决方案**：统一使用 `.venv` 环境
```bash
.venv\Scripts\activate
# 或直接使用
.venv\Scripts\python.exe script.py
```

---

### 6.3 OCR 模型 v3/v5 不匹配

**现象**：
```
FileNotFoundError: [Errno 2] No such file or directory: '.../ch_PP-OCRv3_det_infer.pth'
```

**原因**：magic-pdf 代码期望 v3 模型，但 HuggingFace 只有 v5

**解决方案**：修改 `models_config.yml`，将所有 `PP-OCRv3` 改为 `PP-OCRv5`

---

### 6.4 onnxruntime DLL 加载失败

**现象**：
```
ImportError: DLL load failed while importing onnxruntime_pybind11_state
```

**解决方案**：
```bash
pip install onnxruntime==1.19.2
```

---

### 6.5 layoutreader 模型 SSL 错误

**现象**：
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**原因**：magic-pdf 在 auto 模式下下载 layoutreader 模型时 SSL 证书验证失败

**解决方案**：在调用 do_parse 之前禁用 SSL 验证
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

**关键点**：
- 必须在导入 magic_pdf 之前设置
- txt 模式不需要 layoutreader，可以正常工作
- auto 模式质量更好（公式格式正确），建议使用

---

### 6.6 模型目录结构不匹配

**现象**：
```
FileNotFoundError: [Errno 2] No such file or directory: 'D:/MinerU/models/magic-pdf-1.3.12/MFD/...'
```

**原因**：magic-pdf 期望模型在根目录，实际在 `models/` 子目录

**解决方案**：
```bash
cd D:\MinerU\models\magic-pdf-1.3.12
xcopy /E /I models\* .
```

---

### 6.7 MFR 公式识别 transformers 不兼容

**现象**：
```
TypeError: forward() got an unexpected keyword argument 'cache_position'
```

**解决方案**：
```bash
pip install transformers==4.51.3
```

---

### 6.8 D 盘空间满

**原因**：模型文件占用约 52GB 空间

**解决方案**：
1. 删除旧模型目录
2. 清理磁盘空间
3. 使用 HuggingFace 镜像重新下载

```bash
set HF_ENDPOINT=https://hf-mirror.com
python -c "from magic_pdf.model.download import download_models; download_models()"
```

---

## 7. 测试验证

### 7.1 验证安装

```bash
# 验证 magic-pdf 版本
magic-pdf --version

# 验证 Python 模块
python -c "import magic_pdf; print('OK')"

# 验证模型可用性
python -c "from magic_pdf.model.download import download_models; print('Models dir exists')"
```

### 7.2 测试 PDF 提取

```bash
# 使用 Python API 测试
python -c "
from scripts.extract_mineru import extract_with_mineru
result = extract_with_mineru('projects/test.pdf', 'outputs/test/raw_md')
print(f'成功: {result}' if result else '失败')
"
```

### 7.3 预期结果

**输出目录**：
- `raw.md` 文件存在且非空
- `images/` 目录包含提取的图片

**Markdown 内容**：
- 公式使用 `$$...$$` 格式
- 图片引用使用 `![](images/...)` 格式
- 章节标题使用 `#` 格式
- 图注完整（如 `FIG. 1.`）

---

## 8. 性能参考

### 8.1 处理时间

| PDF 页数 | 模式 | 预计时间 |
|----------|------|----------|
| 16 页 | auto | 约 5 分钟 |
| 16 页 | txt | 约 3 分钟 |

### 8.2 输出大小

| 项目 | 大小 |
|------|------|
| raw.md（16 页） | 约 70KB |
| images（6 张） | 约 800KB |
| 总输出 | 约 6MB |

---

## 9. 最佳实践

### 9.1 使用建议

1. **始终使用 auto 模式**：公式格式正确，质量最好
2. **禁用 SSL 验证**：解决 layoutreader 下载问题
3. **使用 Python API**：避免 CLI 的 DLL 问题
4. **保留原始输出**：MinerU 子目录保留，便于调试

### 9.2 错误处理

```python
try:
    result = extract_with_mineru(pdf_path, output_dir)
    if result:
        # 成功处理
        pass
    else:
        # 降级到 pdfplumber
        result = extract_with_pdfplumber(pdf_path, output_dir)
except Exception as e:
    # 记录错误
    logger.error("提取失败: %s", str(e))
```

### 9.3 降级策略

当 MinerU 失败时：
1. 检查 clean_md 字符数是否 < 800
2. 如果是，使用 pdfplumber 补充提取
3. 合并结果后继续处理

---

## 10. 参考链接

- [MinerU GitHub](https://github.com/opendatalab/MinerU)
- [magic-pdf PyPI](https://pypi.org/project/magic-pdf/)
- [HuggingFace 模型下载](https://huggingface.co/open-magic-pdf)
- [PyTorch CPU 版本](https://download.pytorch.org/whl/cpu)

---

## 附录 A：问题修复清单

| 问题 | 状态 | 解决方案 |
|------|------|----------|
| PyTorch DLL 加载失败 | ✅ | 安装 CPU 版本 |
| Python 环境混乱 | ✅ | 统一使用 .venv |
| OCR 模型 v3/v5 不匹配 | ✅ | 修改 models_config.yml |
| onnxruntime DLL 加载失败 | ✅ | 降级到 1.19.2 |
| ultralytics SSL 错误 | ✅ | 禁用 SSL 验证 |
| layoutreader SSL 错误 | ✅ | 禁用 SSL 验证 |
| 模型目录结构不匹配 | ✅ | 复制到根目录 |
| transformers 不兼容 | ✅ | 降级到 4.51.3 |
| D 盘空间满 | ✅ | 清理后重新下载 |

---

## 附录 B：版本兼容性矩阵

| 组件 | 推荐版本 | 不兼容版本 | 备注 |
|------|----------|------------|------|
| magic-pdf | 1.3.12 | - | 当前稳定版 |
| torch | CPU 最新版 | GPU 版本（无 CUDA） | 使用 CPU 版本 |
| transformers | 4.51.3 | 4.57.6+ | MFR 模型不兼容 |
| onnxruntime | 1.19.2 | 1.26.0 | DLL 加载问题 |
| pdfplumber | 最新版 | - | 无特殊要求 |

---

## 附录 C：快速检查清单

- [ ] Python 3.11+ 在 .venv 中
- [ ] PyTorch CPU 版本已安装
- [ ] magic-pdf 1.3.12 已安装
- [ ] transformers == 4.51.3
- [ ] onnxruntime == 1.19.2
- [ ] 模型目录结构正确
- [ ] OCR 配置使用 v5 模型
- [ ] magic-pdf.json 配置正确
- [ ] SSL 验证已禁用
- [ ] 测试 PDF 提取成功
