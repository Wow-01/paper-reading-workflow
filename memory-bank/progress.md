# Progress

## 2026-05-26
- M1 complete: .venv created, magic-pdf and pdfplumber installed.
- Checks: magic-pdf --version, import pdfplumber.
- MinerU auto模式验证成功（含公式识别），16页PDF约5分钟。
- Git仓库初始化完成，初始提交已创建。

## 澄清问题解决（5个）
1. **Skill调用方式**：V1采用"脚本准备 + Claude手动调用"模式，脚本负责数据准备，Claude负责调用skill
2. **PageIndex查询**：V1不实现独立查询脚本，Claude直接读取JSONL定位
3. **多模态实现**：V1采用最简方案，脚本列出图片路径，Claude Code原生支持图片查看
4. **降级链路**：明确合并策略，MinerU为主，pdfplumber补充表格和缺失段落
5. **测试路径**：统一使用`projects/`目录（以16.8节为准）

**更新文件**：
- memory-bank/实施计划.md（12.1、15.2、15.3、15.9、15.10、16.4节）
- memory-bank/tech-stack.md（2、4、5、10节）

**下一步**：阶段2基础功能开发 - 创建scripts/run_workflow.py
