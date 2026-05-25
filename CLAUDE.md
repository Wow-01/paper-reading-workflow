# 项目指令

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
