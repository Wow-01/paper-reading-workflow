#!/bin/bash

# Git 提交脚本
# 用法: ./git-commit.sh <类型> <范围> <描述> [详细说明]

# 检查参数
if [ $# -lt 3 ]; then
    echo "用法: $0 <类型> <范围> <描述> [详细说明]"
    echo ""
    echo "类型:"
    echo "  feat      - 新功能"
    echo "  fix       - 修复 bug"
    echo "  config    - 配置变更"
    echo "  docs      - 文档更新"
    echo "  refactor  - 重构"
    echo "  test      - 测试相关"
    echo "  milestone - 里程碑"
    echo "  init      - 初始化"
    echo ""
    echo "示例:"
    echo "  $0 feat extract 实现MinerU PDF提取模块"
    echo "  $0 milestone M1 PDF提取与clean_md稳定生成"
    exit 1
fi

TYPE=$1
SCOPE=$2
DESCRIPTION=$3
DETAIL=$4

# 构建提交信息
if [ -n "$DETAIL" ]; then
    COMMIT_MSG="$TYPE($SCOPE): $DESCRIPTION

$DETAIL"
else
    COMMIT_MSG="$TYPE($SCOPE): $DESCRIPTION"
fi

# 添加所有修改的文件
git add .

# 执行提交
git commit -m "$COMMIT_MSG"

# 如果是里程碑，打标签
if [ "$TYPE" = "milestone" ]; then
    git tag -a "$SCOPE" -m "$DESCRIPTION"
    echo "已创建里程碑标签: $SCOPE"
fi

echo "提交完成: $COMMIT_MSG"
