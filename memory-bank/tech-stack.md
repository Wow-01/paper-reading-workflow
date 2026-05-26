# 技术栈推荐（简单且健壮）

以下技术栈以“能跑通、易维护、低复杂度”为优先，覆盖单篇/批量、可追溯、可扩展、多模态路由与公式推导补全等能力。

## 1. 语言与运行环境

- 语言：Python 3.10+
  - 生态成熟，PDF/文本处理库丰富。
  - 便于在 VS Code + Claude Code 中执行脚本与调试。
- 运行方式：CLI 脚本 + 约定目录
  - 适配 Windows 本地工作流，避免服务化复杂度。

## 2. 处理链路与组件位置

推荐顺序（单篇与批量一致）：
PDF 判定 → 提取 → 清洗 → PageIndex → 一页纸总结 → 公式推导补全 → 汇总输出

- PDF 判定（轻量规则）
  - 若抽取的纯文本占比低、图像页占比高，则判为图片型。
  - 其余按文本型处理。
- MinerU（优先用于图片型）
  - 输入：PDF
  - 输出：raw_md
  - 失败或过短时触发降级。
- pdfplumber（文本型与降级补充）
  - 输入：PDF
  - 输出：正文与表格片段（合并到 clean_md）。
  - 与 MinerU 结果合并时保留章节与图注线索。
- Markdown 清洗（脚本）
  - 输入：raw_md + pdfplumber 补充
  - 输出：clean_md（保留图注、公式、章节层级、引用线索）。
- PageIndex（索引与定位）
  - 输入：clean_md + 章节结构映射
  - 输出：outputs/<pdf_stem>/pageindex/index.jsonl 与 index.meta.json
  - 查询：V1 不实现独立查询脚本，Claude 直接读取 JSONL 定位
- Academic Researcher Skill（一页纸结构化总结）
  - 位置：PageIndex 之后。
  - 输入：prepare_summary_input.py 生成的结构化输入文件
  - 输出：outputs/<pdf_stem>/summary/one-pager.md
  - 调用方式：脚本准备数据 + Claude 手动调用 skill
  - 安装：`npx skills add shubhamsaboo/awesome-llm-apps@academic-researcher -g -y`
- math-reasoning skill（公式推导补全）
  - 位置：一页纸总结之后，可按需触发。
  - 输入：prepare_formula_input.py 生成的公式块 + 上下文文件
  - 输出：outputs/<pdf_stem>/summary/formula-notes.md
  - 调用方式：脚本准备数据 + Claude 手动调用 skill
  - 安装：`npx skills add lingzhi227/agent-research-skills@math-reasoning -g -y`

### 2.1 关键输入输出契约

- raw_md
  - 来源：MinerU
  - 目标：保留最大信息量，允许噪声。
- clean_md
  - 来源：raw_md + pdfplumber 补充
  - 目标：保留章节、图注、公式与引用线索，作为后续所有生成的唯一输入。
- PageIndex 索引
  - 主要字段：`section_path`, `anchor_id`, `text`, `source_ref`。
  - 目标：支持定位与追问。
- 一页纸总结
  - 来源：clean_md + 章节映射 + 可选 index.meta。
  - 目标：动机/方法/结果/意义四模块齐全。
- 公式推导补全
  - 来源：公式块 + 上下文段落。
  - 目标：分步推导 + 假设/近似标注。

## 3. 交互与入口

- CLI：Python 标准库 argparse
  - 简单、零依赖、稳定。
  - 支持“单篇/批量”显式口令参数。
- 目录约定
  - 输入：projects/
  - 输出：outputs/<pdf_stem>/

## 4. 多模态图像路由（可选）

- 能力判断（配置驱动）
  - 在配置中声明 `vision.enabled=true/false` 或提供模型名。
  - 未配置或模型不可用时自动降级。
- V1 实现方案（最简方案）
  - 脚本侧：在交付指引.md 中列出 `raw_md/images/` 目录下的图片路径
  - Claude 侧：在对话中直接查看图片（Claude Code 支持图片输入）
  - 降级方案：无法查看图片时，基于图注 + 正文推断
- 调用契约（内部接口，后续扩展用）
  - `analyze_image(image_path, caption, context)`
  - 返回：`{summary, evidence, confidence, mode}`
  - `mode` 取值：`vision` 或 `caption-only`，用于显式标注推断方式。

## 5. PageIndex 实现约定

- 索引格式：JSONL
  - 字段建议：`section_path`, `anchor_id`, `text`, `source_ref`。
- 元数据：index.meta.json
  - 记录章节树、页码映射、统计信息。
- 查询入口：V1 不实现独立查询脚本
  - JSONL 格式支持 grep/文本搜索
  - Claude 可直接读取 index.jsonl 进行定位
  - 后续扩展时可添加 `pageindex_query.py --index <path> --question "..."`

## 6. 依赖与版本管理

- 依赖管理：requirements.txt
  - 最小依赖建议：`pdfplumber`
  - 其余尽量使用标准库；如需配置文件可加 `pyyaml`。
  - 可选：`tqdm`（批量进度）、`rapidfuzz`（轻量相似度匹配）。
- 版本锁定
  - 安装验证后执行 `pip freeze > requirements.txt` 固定版本。
  - MinerU 版本记录到运行日志或版本清单。
- 虚拟环境：venv
  - 与系统环境隔离，避免冲突。

## 7. 日志与错误处理

- 日志：Python logging
  - 级别：DEBUG（细节）、INFO（里程碑）、WARNING（降级）、ERROR（失败）。
  - 格式：时间 + 级别 + 步骤 + 文件名。
  - 位置：outputs/<pdf_stem>/logs/run.log
- 错误恢复
  - MinerU 失败 → 自动使用 pdfplumber 补提取。
  - PageIndex 失败 → 终止后续总结并输出失败报告。
  - 批量模式：单篇失败不影响其他论文，生成 failure-summary.md。

## 8. 目录结构建议

- projects/
  - 原始 PDF 输入
- outputs/
  - <pdf_stem>/raw_md
  - <pdf_stem>/clean_md
  - <pdf_stem>/pageindex
  - <pdf_stem>/summary/one-pager.md
  - <pdf_stem>/summary/formula-notes.md
  - <pdf_stem>/logs/run.log
- scripts/
  - 主脚本入口与清洗工具

## 9. 配置与接口约定（用于实施）

- 配置文件：config.yaml（或 config.json）
  - `vision.enabled`: true/false
  - `mineru.path`: 本地命令或可执行路径
  - `outputs.dir`: 默认 outputs/
  - `thresholds.clean_md_min_chars`: 800

## 10. 最小脚本清单（建议）

- run_workflow.py
  - 统一入口，解析单篇/批量模式。
- extract_mineru.py
  - 调用 MinerU，输出 raw_md。
- extract_pdfplumber.py
  - 文本补提取与表格捕获。
- clean_markdown.py
  - 结构清洗与图注对齐。
- build_pageindex.py
  - 输出 index.jsonl 与 index.meta.json。
- prepare_summary_input.py
  - 读取 clean_md，生成结构化输入文件供 Claude 调用 skill。
- prepare_formula_input.py
  - 提取公式块和上下文，生成输入文件供 Claude 调用 skill。
- write_failure_report.py
  - 失败原因记录与可重试建议。

说明：V1 采用"脚本准备 + Claude 手动调用"模式，脚本负责数据准备，Claude 负责调用 skill 生成总结。

## 11. 说明与取舍

- 首选标准库实现 CLI 与日志，减少第三方依赖。
- 只在需要时引入多模态模型与额外技能，保持第一版可控。
- 不引入数据库与 Web 服务，避免复杂部署。
