# 项目指令

## 文档阅读

写任何代码前都应完整阅读 D:\paper-reading workflow\memory-bank\工作流产品需求.md 和 D:\paper-reading workflow\memory-bank\architt.md，每完成一个重大功能或者里程碑后必须更新 D:\paper-reading workflow\memory-bank\architt.md

## Git 提交规则

### 自动提交时机

每次完成以下操作后，**必须自动执行 git 提交**：

1. **功能开发完成** - 实现了某个模块或函数
2. **文件创建/修改** - 创建或修改了重要文件
3. **问题修复** - 修复了 bug 或错误
4. **配置变更** - 修改了配置文件、依赖等
5. **文档更新** - 更新了 README、需求文档等
6. **里程碑达成** - 达到了产品需求中的里程碑

### 提交信息格式

```
<类型>(<范围>): <描述>

[可选] 详细说明
```

**类型说明：**
- `feat`: 新功能
- `fix`: 修复 bug
- `config`: 配置变更
- `docs`: 文档更新
- `refactor`: 重构
- `test`: 测试相关
- `milestone`: 里程碑
- `init`: 初始化

**示例：**
```
feat(extract): 实现 MinerU PDF 提取模块
fix(clean): 修复 Markdown 清洗时公式丢失问题
config: 添加 requirements.txt 依赖
milestone(M1): PDF 提取与 clean_md 稳定生成
```

### 自动提交脚本

在执行 git 提交时，使用以下命令格式：

```bash
# 添加相关文件
git add <修改的文件>

# 提交（使用 HEREDOC 格式确保格式正确）
git commit -m "$(cat <<'EOF'
<类型>(<范围>): <描述>

[可选详细说明]
EOF
)"

# 达到里程碑时打标签
git tag -a <标签名> -m "<里程碑描述>"
```

### 里程碑标签规范

- M1: PDF 提取与 clean_md 稳定生成
- M2: PageIndex 构建与基础查询通过
- M3: 一页纸结构化总结输出稳定
- M4: 公式推导补全按需触发稳定
- M5: 批量模式与失败恢复稳定

### 提交检查清单

在提交前，确认：
- [ ] 代码可以正常运行（无语法错误）
- [ ] 相关文件已添加到 git
- [ ] 提交信息格式正确
- [ ] 达到里程碑时已打标签

### 回退指令

如果需要回退，使用以下命令：

```bash
# 查看提交历史
git log --oneline

# 回退到某个提交
git reset --hard <commit-hash>

# 回退到某个里程碑
git reset --hard <tag-name>
```
