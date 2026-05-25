@echo off
REM Git 提交脚本 (Windows)
REM 用法: git-commit.bat <类型> <范围> <描述> [详细说明]

if "%~3"=="" (
    echo 用法: %0 ^<类型^> ^<范围^> ^<描述^> [详细说明]
    echo.
    echo 类型:
    echo   feat      - 新功能
    echo   fix       - 修复 bug
    echo   config    - 配置变更
    echo   docs      - 文档更新
    echo   refactor  - 重构
    echo   test      - 测试相关
    echo   milestone - 里程碑
    echo   init      - 初始化
    echo.
    echo 示例:
    echo   %0 feat extract 实现MinerU PDF提取模块
    echo   %0 milestone M1 PDF提取与clean_md稳定生成
    exit /b 1
)

set TYPE=%~1
set SCOPE=%~2
set DESCRIPTION=%~3
set DETAIL=%~4

REM 构建提交信息
if defined DETAIL (
    set COMMIT_MSG=%TYPE%(%SCOPE%): %DESCRIPTION%

%DETAIL%
) else (
    set COMMIT_MSG=%TYPE%(%SCOPE%): %DESCRIPTION%
)

REM 添加所有修改的文件
git add .

REM 执行提交
git commit -m "%COMMIT_MSG%"

REM 如果是里程碑，打标签
if "%TYPE%"=="milestone" (
    git tag -a "%SCOPE%" -m "%DESCRIPTION%"
    echo 已创建里程碑标签: %SCOPE%
)

echo 提交完成: %COMMIT_MSG%
