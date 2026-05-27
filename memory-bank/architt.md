# Architecture Notes

## Environment
- Python: 3.11.9 in .venv
- Packages: magic-pdf 1.3.12, pdfplumber, pyyaml installed
- magic-pdf config: C:\Users\菌子王\magic-pdf.json
- Models dir: D:\MinerU\models\magic-pdf-1.3.12
- HF mirror: https://hf-mirror.com (session env)

## 项目结构

```
paper-reading workflow/
├── projects/                    # PDF 输入目录
│   ├── 01-*.pdf
│   ├── ...
│   └── 10-*.pdf
├── outputs/                     # 输出目录
│   ├── <pdf_stem>/
│   │   ├── raw_md/              # MinerU 原始提取
│   │   │   ├── raw.md           # 主 Markdown（重命名）
│   │   │   └── auto/            # MinerU 原始输出
│   │   ├── clean_md/            # 清洗后的 Markdown
│   │   │   └── clean.md
│   │   ├── pageindex/           # 索引文件
│   │   │   ├── index.jsonl
│   │   │   └── index.meta.json
│   │   ├── summary/             # 总结相关
│   │   │   ├── input-for-summary.md
│   │   │   ├── input-for-formula.md
│   │   │   ├── one-pager.md     # (阶段3生成)
│   │   │   ├── section-notes.md
│   │   │   ├── glossary.md
│   │   │   └── followups.md
│   │   ├── logs/                # 日志
│   │   │   └── run.log
│   │   ├── 交付指引.md           # 自动生成
│   │   └── failure.md           # (失败时生成)
│   └── failure-summary.md       # (批量失败时生成)
├── scripts/                     # 脚本目录
│   ├── run_workflow.py          # 统一入口
│   ├── extract_mineru.py        # MinerU 提取
│   ├── extract_pdfplumber.py    # pdfplumber 提取
│   ├── clean_markdown.py        # Markdown 清洗
│   ├── build_pageindex.py       # PageIndex 构建
│   ├── prepare_summary_input.py # 总结输入准备
│   ├── prepare_formula_input.py # 公式输入准备
│   └── write_failure_report.py  # 失败报告
├── memory-bank/                 # 文档目录
├── config.yaml                  # 配置文件
└── requirements.txt             # 依赖清单
```

## 模块职责

### run_workflow.py - 统一入口
- 解析 CLI 参数（--file, --dir, --config, --verbose）
- 加载配置文件
- 协调各模块执行
- 生成交付指引.md

### extract_mineru.py - MinerU 提取
- 调用 `magic-pdf -p <pdf> -o <dir> -m auto`
- 查找并复制主 Markdown 为 raw.md
- 返回 raw.md 路径

### extract_pdfplumber.py - pdfplumber 提取
- 补充提取文本和表格
- 降级方案：MinerU 失败或过短时使用

### clean_markdown.py - Markdown 清洗
- 规范化章节标题
- 保留图注（Figure/Fig./图）
- 规范化公式块（$$/$$/\\[\\]）
- 合并 MinerU 和 pdfplumber 结果

### build_pageindex.py - PageIndex 构建
- 解析章节结构
- 生成段落/公式/图/表锚点
- 输出 index.jsonl 和 index.meta.json

### prepare_summary_input.py - 总结输入准备
- 读取 clean.md 和 index.meta.json
- 生成结构化输入文件供 Claude 调用 skill

### prepare_formula_input.py - 公式输入准备
- 提取公式块和上下文
- 生成输入文件供 math-reasoning skill 使用

### write_failure_report.py - 失败报告
- 记录错误原因和建议
- 支持单篇和批量失败汇总

## 关键设计决策

1. **脚本调用方式**：import 调用（非子进程）
2. **MinerU 输出处理**：查找 `<stem>.md` 并复制为 `raw.md`
3. **降级策略**：MinerU 为主，pdfplumber 补充
4. **Skill 调用**：脚本准备数据 + Claude 手动调用
5. **PageIndex 查询**：V1 不实现独立查询脚本
6. **批量处理**：V1 顺序处理，单篇失败不影响其他

## 数据流

```
PDF → extract_mineru → raw_md/raw.md
                         ↓
                   clean_markdown → clean_md/clean.md
                         ↓
                   build_pageindex → pageindex/index.jsonl + index.meta.json
                         ↓
                   prepare_summary_input → summary/input-for-summary.md
                   prepare_formula_input → summary/input-for-formula.md
                         ↓
                   生成交付指引.md
                         ↓
                   [Claude 手动调用 skill]
                         ↓
                   summary/one-pager.md + section-notes.md + ...
```

## 阶段3 Skill 调用架构

### Skill 调用流程

```
input-for-summary.md → academic-researcher skill → one-pager.md
input-for-formula.md → math-reasoning skill → formula-notes.md
clean_md + index.meta.json → Claude 直接生成 → section-notes.md, glossary.md, followups.md
```

### Skill 职责

| Skill | 输入 | 输出 | 触发条件 |
|-------|------|------|----------|
| academic-researcher | 论文内容摘要 | one-pager.md | 总结输入文件存在 |
| math-reasoning | 公式列表 | formula-notes.md | 公式输入文件存在 |

### Claude 直接生成的文件

| 文件 | 内容 | 生成逻辑 |
|------|------|----------|
| section-notes.md | 章节笔记 | 遍历一级标题，每标题 ≥ 3 条要点 |
| glossary.md | 术语表 | 提取关键符号/术语、含义、出处 |
| followups.md | 追问清单 | 3-8 个问题，覆盖动机/方法/假设/结论 |

### 输出文件格式规范

**one-pager.md**：
- 四个模块：动机、方法、结果、意义
- 每模块 ≥ 2 句话
- 保留原文引用依据

**section-notes.md**：
- 每个一级标题 ≥ 3 条要点
- 每条要点包含「结论 + 来源」

**glossary.md**：
- 表格格式：符号/术语、含义、单位、出处
- 按类别分组：核心概念、物理量、模型参数等

**followups.md**：
- 3-8 个问题
- 每个问题包含：问题描述、定位线索、追问方向

**formula-notes.md**：
- 完整推导步骤
- 每步标注使用的数学技巧
- 明确说明假设/近似

## 阶段3 验证清单

| 检查项 | 验证方法 | 预期结果 |
|--------|----------|----------|
| one-pager.md 存在 | 文件检查 | 存在且非空 |
| section-notes.md 存在 | 文件检查 | 存在且非空 |
| glossary.md 存在 | 文件检查 | 存在且非空 |
| followups.md 存在 | 文件检查 | 存在且非空 |
| formula-notes.md 存在 | 文件检查 | 存在且非空 |
| one-pager 四模块 | 内容检查 | 动机/方法/结果/意义各 ≥ 2 句 |
| section-notes 覆盖率 | 章节检查 | 覆盖所有一级标题 |
| followups 问题数 | 计数检查 | 3-8 个问题 |

## 阶段4 联调与验证

### 测试项目

| 测试项 | 命令 | 结果 |
|--------|------|------|
| 单篇流程 | `python scripts/run_workflow.py --file projects/02-*.pdf` | ✅ 成功 |
| 批量模式 | `python scripts/run_workflow.py --file a.pdf --file b.pdf` | ✅ 成功 |
| 失败场景 | 使用损坏的 PDF 文件 | ✅ 单篇失败不影响其他 |

### 批量处理测试

- 测试文件：02-Imaginary-time-Mpemba-effect.pdf, 04-Entanglement-structure-information-protection.pdf
- 结果：2/2 成功，每篇独立输出
- 输出结构完整：raw_md/, clean_md/, pageindex/, summary/, 交付指引.md

### 失败场景测试

- 测试文件：fake.pdf（损坏的 PDF）
- 结果：单篇失败，其他论文继续处理
- 生成：outputs/failure-summary.md 和 outputs/fake/failure.md

### 里程碑 M4 验收

| 验收条件 | 结果 |
|----------|------|
| 批量处理成功率 ≥ 80% | ✅ 100% (2/2) |
| 单篇失败不影响其他论文 | ✅ |
| 生成 failure-summary.md | ✅ |

### CLI 接口

```bash
# 单篇处理
python scripts/run_workflow.py --file 02-Imaginary-time-Mpemba-effect.pdf

# 批量处理（指定多个文件）
python scripts/run_workflow.py --file a.pdf --file b.pdf --file c.pdf

# 批量处理（整个目录）
python scripts/run_workflow.py --dir projects/

# 可选参数
python scripts/run_workflow.py --file paper.pdf --config config.yaml
python scripts/run_workflow.py --file paper.pdf --verbose
```

### 错误处理机制

| 场景 | 行为 | 输出 |
|------|------|------|
| MinerU 失败 | 降级到 pdfplumber | 正常处理 |
| MinerU + pdfplumber 都失败 | 标记为失败 | failure.md |
| 文件不存在 | 跳过并警告 | 日志记录 |
| 批量中单篇失败 | 继续处理其他 | failure-summary.md |
