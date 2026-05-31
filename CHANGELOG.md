# 更新日志

本文件记录论文阅读工作流的所有重要更新和改进。

---

## 2026-05-31

### 改进

#### 项目初始化脚本
- **新增**：创建 `scripts/init_project.py` 初始化脚本
- **功能**：一键创建新的论文分析项目目录
- **用法**：`python scripts/init_project.py "项目名称"`
- **默认位置**：D 盘根目录
- **测试结果**：
  - 创建项目：D:\test-workflow ✅
  - 复制论文：02-Imaginary-time-Mpemba-effect.pdf ✅
  - PDF 提取：MinerU 成功，11 章节，107 条索引 ✅
  - 总结生成：one-pager、section-notes、glossary、followups ✅
  - 公式推导：formula-notes.md 生成 ✅
  - 语义问答：query_index.py 正常工作 ✅

#### 公式渲染改进
- **方案**：使用 VS Code + Markdown Preview Enhanced 插件
- **安装**：`code --install-extension shd101wyy.markdown-preview-enhanced`
- **使用**：按 `Ctrl+Shift+V` 或 `Ctrl+K V` 预览公式

#### 翻译规则改进
- **优化**：在交付指引中添加翻译要求，避免中英混杂
- **规则**：专有名词保留英文，描述性词汇必须翻译

---

## 2026-05-27

### 改进

#### 扁平JSONL + LLM分层检索功能
- **新增**：创建 `scripts/query_index.py` 索引查询模块
- **功能**：支持中英文混合查询、关键词匹配、语义排序

#### 语义理解问答功能
- **新增**：在 CLAUDE.md 中添加语义理解问答规则
- **新增**：创建 `scripts/semantic_qa.py` 语义问答脚本

---

## 2026-05-26

### 完成里程碑

#### M1：环境准备 ✅
- Python 3.11.9 虚拟环境创建
- magic-pdf 1.3.12 安装成功
- pdfplumber 安装成功

#### M2：基础功能开发 ✅
- 创建所有核心脚本（run_workflow.py 等）

#### M3：Skill 调用与结果生成 ✅
- 实现 academic-researcher 和 math-reasoning skill 调用

#### M4：联调与验证 ✅
- 单篇、批量处理测试通过
- 失败场景验证通过

---

## 2026-05-25

### 项目初始化

- 创建项目目录结构
- 初始化 Git 仓库
- 编写产品需求文档
- 编写技术栈文档
- 编写实施计划文档
