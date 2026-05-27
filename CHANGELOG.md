# 更新日志

本文件记录论文阅读工作流的所有重要更新和改进。

---

## 2026-05-27

### 改进

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

### 当前版本：v1.0.0

**核心功能**：
- PDF 提取（MinerU + pdfplumber）
- Markdown 清洗
- PageIndex 构建
- 结构化总结生成
- 公式推导补全
- 批量处理
- 语义理解问答

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

### 中期目标
- 添加多轮对话支持
- 实现跨论文对比功能
- 优化批量处理性能

### 长期愿景
- 概念图谱生成
- Web UI 界面
- 更智能的批量文献管理
