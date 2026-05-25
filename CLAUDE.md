# 项目指令

## 文档阅读

写任何代码前都应完整阅读 D:\paper-reading workflow\memory-bank\工作流产品需求.md 和 D:\paper-reading workflow\memory-bank\architt.md，每完成一个重大功能或者里程碑后必须更新 D:\paper-reading workflow\memory-bank\architt.md

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
