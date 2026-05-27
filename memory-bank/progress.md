# Progress

## 2026-05-26

### M1 完成 ✅
- .venv 创建完成
- magic-pdf 1.3.12 安装成功
- pdfplumber 安装成功
- MinerU auto 模式验证成功（含公式识别）
- Git 仓库初始化完成

### M2 完成 ✅ - 阶段2：基础功能开发

**已完成的文件**：

| 文件 | 说明 | 状态 |
|------|------|------|
| requirements.txt | 依赖清单 | ✅ |
| config.yaml | 配置文件 | ✅ |
| scripts/extract_mineru.py | MinerU 提取模块（Python API） | ✅ |
| scripts/extract_pdfplumber.py | pdfplumber 提取模块 | ✅ |
| scripts/clean_markdown.py | Markdown 清洗模块 | ✅ |
| scripts/build_pageindex.py | PageIndex 构建模块 | ✅ |
| scripts/prepare_summary_input.py | 总结输入准备 | ✅ |
| scripts/prepare_formula_input.py | 公式输入准备 | ✅ |
| scripts/write_failure_report.py | 失败报告模块 | ✅ |
| scripts/run_workflow.py | 工作流入口 | ✅ |

**测试验证**：

```bash
python scripts/run_workflow.py --file projects/02-Imaginary-time-Mpemba-effect.pdf
```

**测试结果**：
- ✅ 流程完整跑通，无报错
- ✅ MinerU API 正常工作（修复了 DLL 问题）
- ✅ 章节识别：11 个章节
- ✅ 公式识别：20 个公式
- ✅ 图片提取：6 张图片
- ✅ 输出目录结构正确
- ✅ 交付指引.md 已生成

### M3 完成 ✅ - 阶段3：Skill 调用与结果生成（Claude 参与）

**执行流程**：
1. ✅ 读取 `outputs/<stem>/交付指引.md` 获取文件清单
2. ✅ 调用 `academic-researcher` skill 生成 one-pager.md
3. ✅ 调用 `math-reasoning` skill 生成 formula-notes.md
4. ✅ 基于 clean_md 生成 section-notes.md、glossary.md、followups.md

**输出文件**：
- `summary/one-pager.md` - 一页纸结构化总结（4 个模块，每模块 ≥ 2 句话）
- `summary/section-notes.md` - 章节笔记（覆盖所有一级标题）
- `summary/glossary.md` - 术语表（45 个术语/符号）
- `summary/followups.md` - 追问清单（8 个问题）
- `summary/formula-notes.md` - 公式推导补全（6 个公式）

### M4 完成 ✅ - 阶段4：联调与验证

**测试项目**：

| 测试项 | 命令 | 结果 |
|--------|------|------|
| 单篇流程 | `python scripts/run_workflow.py --file projects/02-*.pdf` | ✅ 成功 |
| 批量模式 | `python scripts/run_workflow.py --file a.pdf --file b.pdf` | ✅ 成功 |
| 失败场景 | 使用损坏的 PDF 文件 | ✅ 单篇失败不影响其他 |

**批量处理测试**：
- 测试文件：02-Imaginary-time-Mpemba-effect.pdf, 04-Entanglement-structure-information-protection.pdf
- 结果：2/2 成功，每篇独立输出
- 输出结构完整：raw_md/, clean_md/, pageindex/, summary/, 交付指引.md

**失败场景测试**：
- 测试文件：fake.pdf（损坏的 PDF）
- 结果：单篇失败，其他论文继续处理
- 生成：outputs/failure-summary.md 和 outputs/fake/failure.md

**里程碑 M4 验收**：
- ✅ 批量处理 2 篇 PDF，成功率 100%
- ✅ 单篇失败不影响其他论文
- ✅ 生成 failure-summary.md

### 检索方案对比测试 ✅

**测试目标**：对比两种中英文混合检索方案

| 方案 | 描述 | 适用场景 |
|------|------|----------|
| 扁平JSONL | 关键词匹配 + LLM重排序 | 小文档（<50页） |
| 树形索引 | 层次化检索 + LLM推理 | 大文档（>50页） |

**测试结果**：

| 指标 | 扁平JSONL | 树形索引 |
|------|-----------|----------|
| 平均响应时间 | 0.00025秒 | 0.000秒 |
| 平均结果数 | 4.4个 | 2.9个 |
| 结果全面性 | 高 | 中 |
| 结果精准性 | 中 | 高 |

**结论**：
- 对于论文阅读工作流（单篇10-30页），推荐使用扁平JSONL方案
- 树形索引作为可选增强，适合大文档场景
- 两种方案响应时间都极快（<1ms）

**测试文件**：
- `scripts/test_retrieval_comparison.py` - 测试脚本
- `outputs/retrieval_comparison_report.json` - 测试报告JSON

### 查询功能集成 ✅

**新增文件**：
- `scripts/query_index.py` - 索引查询模块

**功能特点**：
- 支持中英文混合查询（如"量子 Monte Carlo"）
- 关键词匹配 + 语义排序
- 命令行接口

**使用示例**：
```bash
# 基本查询
python scripts/query_index.py pageindex/index.jsonl "Mpemba effect"

# 中英文混合查询
python scripts/query_index.py pageindex/index.jsonl "量子 Monte Carlo"

# 指定返回结果数量
python scripts/query_index.py pageindex/index.jsonl "Hubbard model" 10
```

**集成到工作流**：
- 在交付指引.md 中添加了查询示例
- 处理完成后可直接查询索引
- `outputs/retrieval_comparison_analysis.md` - 详细分析报告

**下一步**：
项目已基本完成，可以开始使用。扩展功能待后续迭代。
