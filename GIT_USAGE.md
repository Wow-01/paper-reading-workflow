# Git 使用指南

## 自动提交方式

### 方式1：使用提交脚本

**Windows (推荐):**
```bash
# 格式
git-commit.bat <类型> <范围> <描述> [详细说明]

# 示例
git-commit.bat feat extract 实现MinerU PDF提取模块
git-commit.bat fix clean 修复Markdown清洗时公式丢失问题
git-commit.bat config 添加requirements.txt依赖
git-commit.bat milestone M1 PDF提取与clean_md稳定生成
```

**Linux/Mac:**
```bash
# 格式
./git-commit.sh <类型> <范围> <描述> [详细说明]

# 示例
./git-commit.sh feat extract 实现MinerU PDF提取模块
./git-commit.sh milestone M1 PDF提取与clean_md稳定生成
```

### 方式2：手动提交

```bash
# 添加文件
git add <文件名>

# 提交
git commit -m "feat(extract): 实现MinerU PDF提取模块"

# 打里程碑标签
git tag -a M1 -m "PDF提取与clean_md稳定生成"
```

### 方式3：Claude Code 自动提交

在开发过程中，Claude Code 会根据 CLAUDE.md 中的规则自动执行 git 提交。

## 提交类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | 实现 MinerU 提取模块 |
| `fix` | 修复 bug | 修复公式解析错误 |
| `config` | 配置变更 | 添加 requirements.txt |
| `docs` | 文档更新 | 更新 README |
| `refactor` | 重构 | 重构日志模块 |
| `test` | 测试相关 | 添加单元测试 |
| `milestone` | 里程碑 | M1 功能完成 |
| `init` | 初始化 | 项目初始化 |

## 里程碑标签

- **M1**: PDF 提取与 clean_md 稳定生成
- **M2**: PageIndex 构建与基础查询通过
- **M3**: 一页纸结构化总结输出稳定
- **M4**: 公式推导补全按需触发稳定
- **M5**: 批量模式与失败恢复稳定

## 常用 Git 命令

### 查看状态
```bash
git status              # 查看当前状态
git log --oneline       # 查看提交历史
git tag -l              # 查看所有标签
```

### 回退操作
```bash
# 回退到某个提交
git reset --hard <commit-hash>

# 回退到某个里程碑
git reset --hard M1

# 查看某个提交的详细内容
git show <commit-hash>
```

### 分支操作
```bash
# 创建开发分支
git checkout -b dev

# 切换分支
git checkout dev

# 合并分支
git merge dev
```

## 提交规范

### 提交信息格式
```
<类型>(<范围>): <描述>

[可选] 详细说明
```

### 示例
```
feat(extract): 实现 MinerU PDF 提取模块

- 支持图片型 PDF 提取
- 输出 raw_md 文件
- 添加错误处理
```

## 注意事项

1. **每个功能完成后提交** - 不要等到所有功能都完成才提交
2. **提交信息要清晰** - 说明做了什么，为什么做
3. **达到里程碑时打标签** - 方便回退和版本管理
4. **定期推送到远程** - 如果有远程仓库，定期推送备份

## 快速参考

```bash
# 开发新功能
git-commit.bat feat <模块名> <功能描述>

# 修复问题
git-commit.bat fix <模块名> <问题描述>

# 达到里程碑
git-commit.bat milestone M1 <里程碑描述>

# 查看历史
git log --oneline

# 回退到里程碑
git reset --hard M1
```
