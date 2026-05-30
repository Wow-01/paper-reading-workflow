# 论文阅读工作流

将论文从「拿到 PDF」推进到「真正读懂」的自动化工作流。

## 功能概述

- **PDF 提取**：使用 MinerU 提取论文正文、公式、图片、表格
- **Markdown 清洗**：规范化章节结构、图注、公式格式
- **PageIndex 构建**：生成可检索的 JSONL 索引，支持问答定位
- **中英文混合查询**：支持中英文混合关键词搜索
- **结构化总结**：一页纸总结、章节笔记、术语表、追问清单
- **公式推导补全**：补全作者省略的中间推导步骤

---

## 快速开始

### 环境要求

- **Python**: 3.10+（推荐 3.11）
- **磁盘空间**: 约 60GB（用于 MinerU 模型）
- **Claude Code**: 用于调用 skill 生成总结（可选）

### 完整安装步骤

#### 步骤 1：克隆项目

```bash
git clone <repo-url>
cd paper-reading-workflow
```

#### 步骤 2：创建虚拟环境

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

#### 步骤 3：安装 PyTorch（CPU 版本）

```bash
# 必须先安装 CPU 版本，避免 DLL 问题
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

#### 步骤 4：安装其他依赖

```bash
pip install -r requirements.txt
```

#### 步骤 5：下载 MinerU 模型（约 52GB）

```bash
# 使用镜像加速（可选）
set HF_ENDPOINT=https://hf-mirror.com  # Windows
# export HF_ENDPOINT=https://hf-mirror.com  # Linux/Mac

# 下载模型
python -c "from magic_pdf.model.download import download_models; download_models()"
```

#### 步骤 6：修复模型目录结构

```bash
# 进入模型目录（根据实际路径修改）
cd ~/.cache/huggingface/hub/models--opendatalab--PDF-Extract-Kit-1.0/snapshots/<hash>

# 或者使用默认路径
# Windows: %USERPROFILE%\.cache\huggingface\hub\models--opendatalab--PDF-Extract-Kit-1.0\snapshots\<hash>
# Linux/Mac: ~/.cache/huggingface/hub/models--opendatalab--PDF-Extract-Kit-1.0/snapshots/<hash>

# 复制 models 目录下的内容到当前目录
# Windows
xcopy /E /I models\* .

# Linux/Mac
cp -r models/* .
```

#### 步骤 7：修改 OCR 模型配置

编辑文件：
```
.venv/Lib/site-packages/magic_pdf/model/sub_modules/ocr/paddleocr2pytorch/pytorchocr/utils/resources/models_config.yml
```

将所有 `PP-OCRv3` 改为 `PP-OCRv5`：

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

#### 步骤 8：创建 MinerU 配置文件

创建 `~/.magic-pdf.json`：

```json
{
  "models-dir": "~/.cache/huggingface/hub/models--opendatalab--PDF-Extract-Kit-1.0/snapshots/<hash>",
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

> 注意：将 `models-dir` 替换为实际的模型目录路径。

#### 步骤 9：验证安装

```bash
# 验证 MinerU
magic-pdf --version
# 预期输出: magic-pdf version 1.3.12

# 验证 Python 模块
python -c "import magic_pdf; print('OK')"
# 预期输出: OK

# 验证 pdfplumber
python -c "import pdfplumber; print('OK')"
# 预期输出: OK
```

#### 步骤 10：安装 Claude Code Skills（可选）

```bash
# 安装 academic-researcher skill（用于生成一页纸总结）
npx skills add shubhamsaboo/awesome-llm-apps@academic-researcher -g -y

# 安装 math-reasoning skill（用于公式推导补全）
npx skills add lingzhi227/agent-research-skills@math-reasoning -g -y
```

---

## 使用方法

### 单篇处理

```bash
# 将 PDF 放入 projects/ 目录
cp your-paper.pdf projects/

# 运行工作流
python scripts/run_workflow.py --file your-paper.pdf
```

### 批量处理

```bash
# 处理整个目录
python scripts/run_workflow.py --dir projects/

# 处理指定的多篇论文
python scripts/run_workflow.py --file paper1.pdf --file paper2.pdf --file paper3.pdf
```

### 可选参数

```bash
# 指定配置文件
python scripts/run_workflow.py --file paper.pdf --config config.yaml

# 详细日志
python scripts/run_workflow.py --file paper.pdf --verbose
```

### 查询索引

处理完成后，可以查询索引：

```bash
# 基本查询
python scripts/query_index.py outputs/paper/pageindex/index.jsonl "Mpemba effect"

# 中英文混合查询
python scripts/query_index.py outputs/paper/pageindex/index.jsonl "量子 Monte Carlo"

# 指定返回结果数量
python scripts/query_index.py outputs/paper/pageindex/index.jsonl "Hubbard model" 10
```

---

## 输出结构

每篇论文处理后，会在 `outputs/<pdf_stem>/` 目录下生成：

```
outputs/<pdf_stem>/
├── raw_md/                    # MinerU 原始提取
│   ├── raw.md                 # 主 Markdown 文件
│   └── auto/                  # MinerU 原始输出
│       ├── <stem>.md
│       ├── images/            # 提取的图片
│       └── content_list.json
├── clean_md/                  # 清洗后的 Markdown
│   └── clean.md
├── pageindex/                 # 索引文件
│   ├── index.jsonl            # JSONL 格式索引
│   └── index.meta.json        # 索引元数据
├── summary/                   # 总结文件
│   ├── input-for-summary.md   # 总结输入（脚本生成）
│   ├── input-for-formula.md   # 公式输入（脚本生成）
│   ├── one-pager.md           # 一页纸总结（Claude 生成）
│   ├── section-notes.md       # 章节笔记（Claude 生成）
│   ├── glossary.md            # 术语表（Claude 生成）
│   ├── followups.md           # 追问清单（Claude 生成）
│   └── formula-notes.md       # 公式推导（Claude 生成）
├── logs/                      # 日志
│   └── run.log
└── 交付指引.md                 # 自动生成的 Claude 执行指引
```

---

## 工作流程

### 阶段 1：脚本自动处理

```bash
python scripts/run_workflow.py --file paper.pdf
```

脚本会自动完成：
1. MinerU 提取 PDF → `raw_md/raw.md`
2. Markdown 清洗 → `clean_md/clean.md`
3. PageIndex 构建 → `pageindex/index.jsonl`
4. 准备总结输入 → `summary/input-for-summary.md`
5. 准备公式输入 → `summary/input-for-formula.md`
6. 生成交付指引 → `交付指引.md`

### 阶段 2：Claude 调用 Skill 生成总结

脚本完成后，读取 `交付指引.md`，Claude 会：

1. 调用 `academic-researcher` skill 生成 **one-pager.md**
2. 调用 `math-reasoning` skill 生成 **formula-notes.md**
3. 直接生成 **section-notes.md**、**glossary.md**、**followups.md**

---

## 配置说明

配置文件 `config.yaml`：

```yaml
# 论文阅读工作流配置

vision:
  enabled: true  # 是否启用视觉能力（分析图片）

mineru:
  path: magic-pdf  # MinerU 命令路径

outputs:
  dir: outputs/  # 输出根目录

thresholds:
  clean_md_min_chars: 800  # clean_md 最少字符数（低于此值触发降级）

logging:
  level: INFO  # 日志级别：DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
```

---

## 输出文件说明

### one-pager.md

一页纸结构化总结，包含四个模块：
- **动机**：要解决什么问题？现有方法的不足？
- **方法**：核心思路、关键创新点、技术路线
- **结果**：主要实验结论、对比基线的优势
- **意义**：学术贡献、应用价值、局限性

### section-notes.md

章节级精读笔记，每个一级标题至少 3 条要点，每条包含「结论 + 来源」。

### glossary.md

关键符号与术语表，表格格式：符号/术语、含义、单位、出处。

### followups.md

可继续追问的问题清单，3-8 条问题，覆盖动机、方法、假设与结论。

### formula-notes.md

公式推导补全，补全作者省略的中间推导步骤，标注使用的假设/近似。

### index.jsonl

PageIndex 索引文件，每行一个 JSON 记录：

```json
{"section_path": "sec2.1", "anchor_id": "para-2-1-3", "text": "原文片段...", "source_ref": "p3#sec2.1"}
```

字段说明：
- `section_path`：章节路径（如 `sec2.1`、`introduction`）
- `anchor_id`：段落/公式/图/表锚点（如 `para-2-1-3`、`eq5`、`fig3`）
- `text`：原文片段
- `source_ref`：页码定位线索

---

## 错误处理

### 降级策略

- **MinerU 失败**：自动降级到 pdfplumber 提取
- **MinerU 成功但内容过短**（< 800 字）：用 pdfplumber 补充
- **MinerU + pdfplumber 都失败**：生成 failure.md 失败报告

### 批量处理

- 单篇失败不影响其他论文继续处理
- 批量处理完成后生成 `outputs/failure-summary.md` 汇总失败情况

### 失败报告

单篇失败：`outputs/<pdf_stem>/failure.md`
批量失败：`outputs/failure-summary.md`

---

## 目录结构

```
paper-reading-workflow/
├── projects/                    # PDF 输入目录
│   ├── paper1.pdf
│   ├── paper2.pdf
│   └── ...
├── outputs/                     # 输出目录
│   ├── <pdf_stem>/             # 每篇论文独立目录
│   └── failure-summary.md      # 批量失败汇总
├── scripts/                     # 脚本目录
│   ├── run_workflow.py          # 统一入口
│   ├── extract_mineru.py        # MinerU 提取
│   ├── extract_pdfplumber.py    # pdfplumber 提取
│   ├── clean_markdown.py        # Markdown 清洗
│   ├── build_pageindex.py       # PageIndex 构建
│   ├── query_index.py           # 索引查询
│   ├── prepare_summary_input.py # 总结输入准备
│   ├── prepare_formula_input.py # 公式输入准备
│   └── write_failure_report.py  # 失败报告
├── memory-bank/                 # 项目文档
├── config.yaml                  # 配置文件
├── requirements.txt             # 依赖清单
├── CHANGELOG.md                 # 更新日志
└── README.md                    # 本文件
```

---

## 技术栈

- **语言**：Python 3.10+
- **PDF 提取**：MinerU (magic-pdf 1.3.12)、pdfplumber
- **Markdown 清洗**：自定义脚本
- **索引**：PageIndex（JSONL 结构）
- **查询**：扁平 JSONL + LLM 分层检索
- **总结生成**：academic-researcher skill
- **公式推导**：math-reasoning skill
- **日志**：Python logging
- **CLI**：argparse

---

## 使用场景

- **快速判断**：这篇文章值不值得读？
- **论文初读**：先看摘要、结论、图表和公式结构，建立整体认知
- **论文精读**：逐节理解方法、推导、假设和结论
- **公式理解**：补全作者省略的中间推导步骤
- **批量阅读**：对某个文件夹下的一批相关文献进行连续分析
- **语义查询**：使用中英文混合关键词查询论文内容

---

## 验收标准

- ✅ 单篇流程可完整跑通并生成 `outputs/<pdf_stem>/`
- ✅ one-pager 四模块齐全，每模块不少于 2 句话
- ✅ PageIndex 可定位至少 3 个问题的答案片段
- ✅ 章节级理解笔记覆盖一级标题不少于 80%
- ✅ 批量模式单篇失败不影响其他论文
- ✅ 支持中英文混合查询

---

## 已知限制

- MinerU 处理速度较慢（16 页 PDF 约 3-5 分钟）
- 公式识别依赖 MinerU 的公式检测能力
- 图片分析依赖 Claude Code 的视觉能力
- V1 版本不支持跨论文对比
- 模型下载需要约 52GB 磁盘空间

---

## 常见问题

### Q1: MinerU 安装失败怎么办？

参考 `MinerU完整配置与修复指南.md`，常见问题包括：
- PyTorch DLL 问题：安装 CPU 版本
- OCR 模型不匹配：修改 models_config.yml
- transformers 不兼容：降级到 4.51.3

### Q2: 如何加速 MinerU？

- 使用 GPU 模式（需要 CUDA）
- 使用 lite 模式（牺牲公式识别）
- 减少 PDF 页数

### Q3: 查询支持哪些语言？

支持中英文混合查询，如：
- "Mpemba effect 量子"
- "Hubbard model 反铁磁"
- "quantum Monte Carlo 符号问题"

### Q4: 如何自定义输出目录？

修改 `config.yaml` 中的 `outputs.dir` 配置项。

---

## 后续迭代方向

- 多模态图片理解增强
- 跨论文对比功能
- 概念图谱生成
- 更智能的批量文献管理
- Web UI 界面

---

## 许可证

[待定]

---

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)
