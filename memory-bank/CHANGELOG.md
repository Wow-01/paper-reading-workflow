# 更新日志

本文件记录论文阅读工作流的所有重要更新和改进。

---

## 2026-05-27

### 改进

#### 查询功能增强（基于 PageIndex 思路）

**改进1：索引添加摘要和关键词**
- **新增**：`build_pageindex.py` 添加 `extract_keywords()` 和 `generate_auto_summary()` 函数
- **新增**：索引记录新增 `keywords` 和 `summary` 字段
- **效果**：平均 Top1 分数从 12.5 提升到 21.0（+68.2%）

**改进2：语义重排序优化**
- **优化**：`query_index.py` 的 `_semantic_rank()` 函数
- **新增**：多因素综合评分（位置、密度、连续性、覆盖度）
- **效果**：平均 Top1 分数从 21.0 提升到 32.9（+56.7%）

**改进3：章节上下文支持**
- **新增**：`IndexSearcher.add_context()` 方法
- **功能**：为搜索结果添加前后文，帮助理解完整内容
- **使用**：`search_index(index_path, query, with_context=True)`

**改进4：多轮对话支持**
- **新增**：对话历史功能
- **新增**：`_is_followup()` 和 `_expand_query()` 方法
- **功能**：支持追问，自动扩展查询
- **使用**：连续查询时自动结合历史

**测试结果汇总**：
| 改进项 | 平均分数 | 提升幅度 |
|--------|----------|----------|
| 基础版本 | 12.5 | - |
| 改进1（关键词+摘要） | 21.0 | +68.2% |
| 改进2（语义重排序） | 32.9 | +163.2% |
| 改进3（上下文） | - | 功能增强 |
| 改进4（多轮对话） | - | 功能增强 |

#### 公式渲染改进
- **方案**：使用 VS Code + Markdown Preview Enhanced 插件
- **安装**：`code --install-extension shd101wyy.markdown-preview-enhanced`
- **使用**：按 `Ctrl+Shift+V` 或 `Ctrl+K V` 预览公式
- **效果**：公式渲染为数学符号，支持 LaTeX 语法

#### 翻译规则改进
- **优化**：在交付指引中添加翻译要求，避免中英混杂
- **规则**：专有名词保留英文，描述性词汇必须翻译
- **效果**：生成的中文总结将更加规范

#### 扁平JSONL + LLM分层检索功能
- **新增**：创建 `scripts/query_index.py` 索引查询模块
  - 支持中英文混合查询（如"量子 Monte Carlo"）
  - 关键词匹配（正文权重1，章节权重3）
  - 语义排序（完全匹配、关键词密度、连续性）
  - 命令行接口
- **新增**：创建 `scripts/test_retrieval_comparison.py` 检索方案对比测试
- **优化**：`scripts/run_workflow.py` 交付指引添加查询示例
- **测试结果**：
  - 平均响应时间：0.00025秒（<1ms）
  - 平均结果数：4.4个
  - 结果全面性：高
  - 结果精准性：中

#### 语义理解问答功能
- **新增**：在 CLAUDE.md 中添加语义理解问答规则
- **新增**：创建 `scripts/semantic_qa.py` 语义问答脚本
- **优化**：关键词匹配算法，支持同义词扩展
  - "韧性" → ["robustness", "resilience", "stability"]
  - "QNN" → ["quantum neural network"]
  - "贡献" → ["contribution", "achievement", "finding"]
- **效果**：问题覆盖率从 40% 提升到 100%

#### 查询方式对比测试
- **新增**：创建 `scripts/test_query_tree.py` 树结构查询脚本
- **新增**：创建 `scripts/test_query_jsonl.py` JSONL 查询脚本
- **新增**：创建 `scripts/test_comparison.py` 对比测试脚本
- **结论**：JSONL 方式更适合当前项目（速度快 37.5 倍，定位更精确）

### 文档

- **新增**：创建 `outputs/comparison_report.md` 查询方式对比报告
- **新增**：创建 `outputs/semantic_qa_report.md` 语义理解测试报告
- **新增**：创建 `outputs/retrieval_comparison_analysis.md` 检索方案对比分析

---

## 2026-05-26

### 完成里程碑

#### M1：环境准备 ✅
- Python 3.11.9 虚拟环境创建
- magic-pdf 1.3.12 安装成功
- pdfplumber 安装成功
- MinerU auto 模式验证成功

#### M2：基础功能开发 ✅
- 创建 `scripts/run_workflow.py` 统一入口
- 创建 `scripts/extract_mineru.py` MinerU 提取模块
- 创建 `scripts/extract_pdfplumber.py` pdfplumber 提取模块
- 创建 `scripts/clean_markdown.py` Markdown 清洗模块
- 创建 `scripts/build_pageindex.py` PageIndex 构建模块
- 创建 `scripts/prepare_summary_input.py` 总结输入准备
- 创建 `scripts/prepare_formula_input.py` 公式输入准备
- 创建 `scripts/write_failure_report.py` 失败报告模块

#### M3：Skill 调用与结果生成 ✅
- 调用 `academic-researcher` skill 生成 one-pager.md
- 调用 `math-reasoning` skill 生成 formula-notes.md
- 生成 section-notes.md、glossary.md、followups.md

#### M4：联调与验证 ✅
- 单篇流程联调成功
- 批量模式联调成功（2/2 成功）
- 失败场景验证成功（单篇失败不影响其他）

### 新增文件

#### 配置文件
- `requirements.txt` - 依赖清单
- `config.yaml` - 配置文件

#### 文档
- `README.md` - 项目使用说明
- `memory-bank/progress.md` - 项目进度记录
- `memory-bank/architt.md` - 架构设计文档

#### 脚本
- `scripts/run_workflow.py` - 工作流入口
- `scripts/extract_mineru.py` - MinerU 提取
- `scripts/extract_pdfplumber.py` - pdfplumber 提取
- `scripts/clean_markdown.py` - Markdown 清洗
- `scripts/build_pageindex.py` - PageIndex 构建
- `scripts/prepare_summary_input.py` - 总结输入准备
- `scripts/prepare_formula_input.py` - 公式输入准备
- `scripts/write_failure_report.py` - 失败报告

### 测试验证

#### 测试文献
- 01-Superior-resilience-poisoning-unlearning.pdf
- 02-Imaginary-time-Mpemba-effect.pdf
- 04-Entanglement-structure-information-protection.pdf

#### 测试结果
- 单篇处理：100% 成功率
- 批量处理：100% 成功率（2/2）
- 失败场景：单篇失败不影响其他

---

## 2026-05-25

### 项目初始化

- 创建项目目录结构
- 初始化 Git 仓库
- 创建 memory-bank/ 文档目录
- 编写产品需求文档
- 编写技术栈文档
- 编写实施计划文档

---

## 版本说明

### 当前版本：v1.1.0

**核心功能**：
- PDF 提取（MinerU + pdfplumber）
- Markdown 清洗
- PageIndex 构建
- 结构化总结生成
- 公式推导补全
- 批量处理
- 语义理解问答
- **中英文混合查询**（扁平JSONL + LLM分层检索）

**技术栈**：
- Python 3.11.9
- MinerU (magic-pdf 1.3.12)
- pdfplumber
- Claude Code Skills (academic-researcher, math-reasoning)

**输出文件**：
- one-pager.md - 一页纸总结
- section-notes.md - 章节笔记
- glossary.md - 术语表
- followups.md - 追问清单
- formula-notes.md - 公式推导

---

## 下一步计划

### 短期改进
- 扩展同义词库，支持更多中英文映射
- 优化查询理解，支持更复杂的自然语言问题
- 增强答案生成，基于相关段落生成完整答案
- 集成LLM进行语义重排序，提升查询精准性

### 中期目标
- 添加多轮对话支持
- 实现跨论文对比功能
- 优化批量处理性能
- 实现树形索引方案，支持大文档（>50页）场景

### 长期愿景
- 概念图谱生成
- Web UI 界面
- 更智能的批量文献管理
