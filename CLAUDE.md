# 项目指令

## 语义理解问答规则

当用户问关于已处理论文的问题时，自动执行语义理解问答流程。

**触发条件**：
- 用户提到论文相关的关键词（如"这篇论文"、"公式"、"章节"等）
- 用户问关于特定论文的问题
- 用户引用论文中的内容

**问答执行流程**：
1. **识别问题**：理解用户问题的意图和关键词
2. **定位论文**：从 `outputs/` 目录找到对应的论文
3. **加载索引**：读取 `pageindex/index.jsonl` 和 `pageindex/index.meta.json`
4. **语义匹配**：使用 Claude 推理找到最相关的段落
5. **生成答案**：基于相关段落生成答案
6. **返回定位**：提供原文来源（section_path, anchor_id, source_ref）

**语义理解要点**：
- 理解同义词（如"韧性" = "robustness" = "resilience"）
- 理解缩写（如"QNN" = "quantum neural network"）
- 理解问题意图（不只是关键词匹配）
- 结合上下文推理答案

**示例用法**：
```
用户：这篇论文的主要贡献是什么？
Claude：[读取索引，理解问题，推理答案，返回结果]

用户：公式 3 是怎么来的？
Claude：[找到 eq3 的记录，读取上下文，解释推导]

用户：QNN 为什么比 MLP 更鲁棒？
Claude：[理解"鲁棒"="robustness"，找到相关章节，解释机制]
```

## 自动触发规则

当用户提到以下关键词时，自动执行论文阅读工作流：

**触发关键词**：
- "分析论文" + PDF 文件名
- "论文阅读" + PDF 文件名
- "读懂论文" + PDF 文件名
- "读这篇论文" + PDF 文件名

**执行流程**：
1. 从用户输入中提取 PDF 文件名
2. 检查 `projects/` 目录下是否存在该文件
3. 如果存在，自动运行：`python scripts/run_workflow.py --file <filename>`
4. 等待脚本完成后，读取 `outputs/<stem>/交付指引.md`
5. 按照交付指引生成所有总结文件（one-pager.md、section-notes.md 等）

**批量触发关键词**：
- "批量分析" + 目录名
- "分析这批论文" + 目录名
- "处理这个目录" + 目录名

**批量执行流程**：
1. 从用户输入中提取目录路径
2. 运行：`python scripts/run_workflow.py --dir <目录>`
3. 对每篇成功处理的论文，读取交付指引并生成总结

**示例用法**：
```
用户：帮我分析论文 02-Imaginary-time-Mpemba-effect.pdf
Claude：[自动执行工作流并生成总结]

用户：批量分析 projects/ 目录下的论文
Claude：[自动执行批量处理]
```

## 文档阅读（重要提示）

写任何代码前必须完整阅读以下文件：
- D:\paper-reading workflow\memory-bank\工作流产品需求.md
- D:\paper-reading workflow\memory-bank\architt.md

每完成一个重大功能或者里程碑后，必须更新以下文件：
- D:\paper-reading workflow\memory-bank\architt.md
- D:\paper-reading workflow\memory-bank\progress.md

## 执行流程

1. 使用 "Plan Mode"（shift+tab）确认满意后再执行
2. 每完成一步就提交 Git
3. 新建聊天（/new 或 /clear）继续下一步
4. 出问题时用 /rewind 回退

## 编码准则（Karpathy Guidelines）

写代码时必须遵循以下原则：

### 1. 先思考再编码
- 明确说明假设，不确定时先问
- 存在多种方案时，列出权衡，不擅自选择
- 有更简单方案时，主动提出

### 2. 简单优先
- 只写被要求的功能，不做多余的事
- 单次使用不抽象
- 不为未请求的"灵活性"写代码
- 200 行能 50 行解决就重写

### 3. 精准修改
- 只改必须改的，不顺手"改进"周边代码
- 匹配现有代码风格
- 只清理自己造成的死代码

### 4. 目标驱动
- 定义明确的成功标准
- 多步任务先列计划再执行
- 每步都要验证

## Git 提交规则

**自动提交时机**：功能完成、文件修改、问题修复、配置变更、文档更新、里程碑达成

**提交格式**：`<类型>(<范围>): <描述>`
- 类型：feat / fix / config / docs / refactor / test / milestone
- 里程碑：M1-M5，达到时自动打标签

**命令**：
```bash
git add <文件>
git commit -m "<类型>(<范围>): <描述>"
git tag -a <M1-M5> -m "<描述>"
```
