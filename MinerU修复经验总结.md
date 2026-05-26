# MinerU (magic-pdf) 安装与修复经验总结

## 背景说明

MinerU 和 magic-pdf 是**同一个工具**的两种称呼：
- **MinerU**：项目名称（GitHub 仓库名）
- **magic-pdf**：pip 包名（安装命令：`pip install magic-pdf[full]`）

本文档记录在 Windows 11 环境下安装和配置 magic-pdf 1.3.12 过程中遇到的所有问题及解决方案。

---

## 环境信息

| 项目 | 值 |
|------|-----|
| 操作系统 | Windows 11 Home China 10.0.26200 |
| Python 版本 | 3.11.9（.venv 环境） |
| magic-pdf 版本 | 1.3.12 |
| 模型目录 | `D:\MinerU\models\magic-pdf-1.3.12` |
| 配置文件 | `~/.magic-pdf.json` |

---

## 问题与解决方案

### 问题1：PyTorch DLL 加载失败 (c10.dll)

**现象**：
```
ImportError: DLL load failed while importing _C: 找不到指定的模块。
```

**原因**：
Windows 上 PyTorch GPU 版本的 DLL 依赖缺失，系统没有 NVIDIA GPU 或 CUDA 驱动不完整。

**解决方案**：
安装 CPU 版本的 PyTorch：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

**关键点**：
- 必须使用 `--index-url` 指定 CPU 版本的 wheel 源
- 安装后需要重启 Python 环境

---

### 问题2：Python 环境混乱

**现象**：
系统中有多个 Python 版本，导致包安装位置混乱：
- Anaconda Python 3.13
- 系统 Python 3.11
- .venv Python 3.11

**解决方案**：
统一使用 `.venv` 环境，所有命令都通过 `.venv` 执行：
```bash
# 激活环境
.venv\Scripts\activate

# 或直接使用 .venv 中的 Python
.venv\Scripts\python.exe script.py
```

**关键点**：
- 在 VS Code 中选择正确的 Python 解释器
- 确保终端激活的是 `.venv` 环境

---

### 问题3：OCR 模型 v3/v5 不匹配

**现象**：
```
FileNotFoundError: [Errno 2] No such file or directory: '.../ch_PP-OCRv3_det_infer.pth'
```

**原因**：
magic-pdf 代码期望使用 v3 模型，但 HuggingFace 上只有 v5 版本的模型文件。

**解决方案**：
修改 OCR 模型配置文件，将 v3 改为 v5：

**配置文件位置**：
```
.venv\Lib\site-packages\magic_pdf\model\sub_modules\ocr\paddleocr2pytorch\pytorchocr\utils\resources\models_config.yml
```

**修改内容**：
```yaml
# 修改前
lang:
  ch_lite:
    det: ch_PP-OCRv3_det_infer.pth
    rec: ch_PP-OCRv3_rec_infer.pth

# 修改后
lang:
  ch_lite:
    det: ch_PP-OCRv5_det_infer.pth
    rec: ch_PP-OCRv5_rec_infer.pth
```

**需要修改的语言配置**：
- `ch_lite`：中文轻量版
- `ch_server`：中文服务器版
- `en`：英文版
- `Multilingual_*`：多语言版

**关键点**：
- 所有 `PP-OCRv3` 都要改为 `PP-OCRv5`
- `Multilingual_PP-OCRv3` 改为 `Multilingual_PP-OCRv5`
- `en_PP-OCRv3` 改为 `en_PP-OCRv5`

---

### 问题4：onnxruntime DLL 加载失败

**现象**：
```
ImportError: DLL load failed while importing onnxruntime_pybind11_state
```

**原因**：
onnxruntime 1.26.0 与 Python 3.11 不兼容。

**解决方案**：
降级 onnxruntime 版本：
```bash
pip install onnxruntime==1.19.2
```

**关键点**：
- 版本 1.19.2 经测试可用
- 不要使用最新版本

---

### 问题5：ultralytics SSL 错误

**现象**：
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**原因**：
ultralytics（YOLO 模型依赖）在下载模型时需要访问 GitHub API，SSL 证书验证失败。

**解决方案**：
Monkey-patch 禁用 SSL 验证（临时方案）：

在调用 magic-pdf 之前添加：
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 或者
import requests
requests.packages.urllib3.disable_warnings()
```

**关键点**：
- 这是临时方案，存在安全风险
- 只在开发/测试环境使用
- 生产环境应修复 SSL 证书问题

---

### 问题5.1：layoutreader 模型 SSL 错误

**现象**：
```
'(MaxRetryError("HTTPSConnectionPool(host='huggingface.co', port=443): Max retries exceeded with url: /hantian/layoutreader/resolve/main/config.json (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)')))")
```

**原因**：
magic-pdf 在 auto 模式下会尝试下载 layoutreader 模型（用于优化阅读顺序），但访问 huggingface.co 时 SSL 证书验证失败。

**影响**：
- auto 模式会卡在 Processing pages 阶段
- 其他步骤（Layout、MFD、MFR、OCR）都已完成

**解决方案**：
在调用 do_parse 之前禁用 SSL 验证：

```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

**关键点**：
- 必须在导入 magic_pdf 之前设置
- txt 模式不需要 layoutreader，可以正常工作
- auto 模式质量更好（公式格式正确），建议使用

---

### 问题6：模型目录结构不匹配

**现象**：
```
FileNotFoundError: [Errno 2] No such file or directory: 'D:/MinerU/models/magic-pdf-1.3.12/MFD/...'
```

**原因**：
magic-pdf 期望模型目录结构为：
```
magic-pdf-1.3.12/
├── MFD/
├── MFR/
├── Layout/
└── ...
```

但实际下载的模型结构为：
```
magic-pdf-1.3.12/
└── models/
    ├── MFD/
    ├── MFR/
    ├── Layout/
    └── ...
```

**解决方案**：
将 `models/` 下的内容复制到根目录：
```bash
# 进入模型目录
cd D:\MinerU\models\magic-pdf-1.3.12

# 复制 models 目录下的内容到当前目录
xcopy /E /I models\* .
```

**最终目录结构**：
```
magic-pdf-1.3.12/
├── MFD/
├── MFR/
├── Layout/
├── OCR/
├── Table/
├── models/  # 原始目录，可保留或删除
└── ...
```

**关键点**：
- 确保所有子目录（MFD、MFR、Layout 等）都在根目录下
- 可以删除空的 `models/` 目录节省空间

---

### 问题7：MFR 公式识别 transformers 不兼容

**现象**：
```
TypeError: forward() got an unexpected keyword argument 'cache_position'
```

**原因**：
transformers 4.57.6 的 `cache_position` 参数与 MFR 模型不兼容。

**解决方案**：
降级 transformers 版本：
```bash
pip install transformers==4.51.3
```

**关键点**：
- 版本 4.51.3 经测试可用
- 不要使用最新版本
- 降级后需要重启 Python 环境

---

### 问题8：D 盘空间满

**现象**：
下载模型后 D 盘空间不足，导致下载失败或系统异常。

**原因**：
模型文件占用约 52GB 空间。

**解决方案**：
1. 删除旧的模型目录：
   ```bash
   rmdir /S /Q D:\MinerU\models\magic-pdf-1.3.12
   ```

2. 清理磁盘空间后重新下载：
   ```bash
   # 设置 HuggingFace 镜像（可选，加速下载）
   set HF_ENDPOINT=https://hf-mirror.com

   # 重新下载模型
   python -c "from magic_pdf.model.download import download_models; download_models()"
   ```

**关键点**：
- 模型文件很大，确保有足够空间（建议 60GB+）
- 可以使用 HuggingFace 镜像加速下载
- 下载完成后可以删除临时文件

---

## 配置文件

### magic-pdf.json

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

---

## 模型模式配置

### __init__.py 配置

**位置**：
```
.venv\Lib\site-packages\magic_pdf\model\__init__.py
```

**配置内容**：
```python
__use_inside_model__ = True
__model_mode__ = 'full'
```

**说明**：
- `__use_inside_model__ = True`：使用内置模型
- `__model_mode__ = 'full'`：使用完整模式（包含 OCR、MFR 等）

**其他模式**：
- `'lite'`：轻量模式（仅 PaddleOCR，无公式识别）

---

## 验证安装

### 1. 验证 magic-pdf 版本
```bash
magic-pdf --version
```
预期输出：`magic-pdf version 1.3.12`

### 2. 验证 Python 模块
```bash
python -c "import magic_pdf; print('OK')"
```
预期输出：`OK`

### 3. 验证模型可用性
```bash
python -c "from magic_pdf.model.download import download_models; print('Models dir exists')"
```
预期输出：`Models dir exists`

### 4. 测试 PDF 提取
```bash
magic-pdf -p projects/test.pdf -o outputs/test/ -m auto
```

**预期结果**：
- 生成 `outputs/test/auto/` 目录
- 包含 `*.md` 文件（Markdown 输出）
- 包含 `images/` 目录（提取的图片）

---

## 常见问题 FAQ

### Q1：magic-pdf 和 MinerU 是什么关系？
**A**：同一个工具的两种称呼。MinerU 是项目名，magic-pdf 是 pip 包名。

### Q2：为什么选择 auto 模式？
**A**：auto 模式会自动检测 PDF 类型（图片型/文本型），并选择最佳提取策略。同时会自动识别公式。

### Q3：提取速度很慢怎么办？
**A**：
- 使用 GPU 模式（需要 CUDA 支持）
- 使用 lite 模式（牺牲公式识别）
- 减少 PDF 页数

### Q4：如何提高章节识别准确率？
**A**：
- 使用 MinerU 的 auto 模式（比 pdfplumber 更好）
- 确保 PDF 有标准的章节标题格式
- 后续可通过 clean_markdown.py 脚本优化

### Q5：公式识别失败怎么办？
**A**：
- 确保 `formula-config.enable = true`
- 确保 transformers 版本为 4.51.3
- 检查模型目录是否完整

---

## 版本兼容性矩阵

| 组件 | 推荐版本 | 不兼容版本 | 备注 |
|------|----------|------------|------|
| magic-pdf | 1.3.12 | - | 当前稳定版 |
| torch | CPU 最新版 | GPU 版本（无 CUDA） | 使用 CPU 版本 |
| transformers | 4.51.3 | 4.57.6+ | MFR 模型不兼容 |
| onnxruntime | 1.19.2 | 1.26.0 | DLL 加载问题 |
| pdfplumber | 最新版 | - | 无特殊要求 |

---

## 总结

### 安装步骤（推荐顺序）

1. **创建虚拟环境**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **安装 CPU 版 PyTorch**
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   ```

3. **安装 magic-pdf**
   ```bash
   pip install magic-pdf[full]
   ```

4. **降级不兼容的包**
   ```bash
   pip install transformers==4.51.3
   pip install onnxruntime==1.19.2
   ```

5. **下载模型**
   ```bash
   set HF_ENDPOINT=https://hf-mirror.com
   python -c "from magic_pdf.model.download import download_models; download_models()"
   ```

6. **修复模型目录结构**
   ```bash
   cd D:\MinerU\models\magic-pdf-1.3.12
   xcopy /E /I models\* .
   ```

7. **修改 OCR 模型配置**
   - 编辑 `.venv\Lib\site-packages\magic_pdf\model\sub_modules\ocr\paddleocr2pytorch\pytorchocr\utils\resources\models_config.yml`
   - 将所有 `v3` 改为 `v5`

8. **配置 magic-pdf.json**
   - 创建 `~/.magic-pdf.json`
   - 填入上述配置

9. **验证安装**
   ```bash
   magic-pdf --version
   python -c "import magic_pdf; print('OK')"
   ```

### 关键教训

1. **环境隔离很重要**：统一使用 `.venv` 避免版本冲突
2. **版本锁定**：记录所有依赖版本，避免升级导致不兼容
3. **模型目录结构**：确保与代码期望的结构一致
4. **镜像加速**：使用 HuggingFace 镜像加速模型下载
5. **磁盘空间**：模型文件很大，提前规划存储空间

---

## 参考链接

- [MinerU GitHub](https://github.com/opendatalab/MinerU)
- [magic-pdf PyPI](https://pypi.org/project/magic-pdf/)
- [HuggingFace 模型下载](https://huggingface.co/open-magic-pdf)
- [PyTorch CPU 版本](https://download.pytorch.org/whl/cpu)
