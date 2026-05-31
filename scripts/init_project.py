"""初始化新论文分析项目。

复制工作流模板到新目录，清理 outputs 和 projects。
"""

import argparse
import os
import shutil
from pathlib import Path


# 需要复制的文件和目录
FILES_TO_COPY = [
    "scripts/",
    "memory-bank/",
    "config.yaml",
    "requirements.txt",
    "CLAUDE.md",
    "README.md",
    "CHANGELOG.md",
]

# 需要创建的空目录
DIRS_TO_CREATE = [
    "projects/",
    "outputs/",
]


def init_project(project_name: str, target_dir: str = None) -> str:
    """初始化新项目。

    Args:
        project_name: 项目名称
        target_dir: 目标目录（默认 D:\）

    Returns:
        项目目录路径
    """
    # 确定源目录（当前工作流目录）
    source_dir = Path(__file__).parent.parent

    # 确定目标目录
    if target_dir is None:
        target_dir = Path("D:/")
    else:
        target_dir = Path(target_dir)

    # 创建项目目录
    project_dir = target_dir / project_name

    if project_dir.exists():
        print(f"错误：目录已存在 {project_dir}")
        print("请选择其他名称或删除现有目录")
        return None

    print(f"创建项目：{project_dir}")
    project_dir.mkdir(parents=True)

    # 复制文件和目录
    for item in FILES_TO_COPY:
        source = source_dir / item
        target = project_dir / item

        if source.is_dir():
            # 复制目录（排除 __pycache__）
            shutil.copytree(
                source,
                target,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"),
            )
            print(f"  复制目录：{item}")
        elif source.is_file():
            # 复制文件
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            print(f"  复制文件：{item}")

    # 创建空目录
    for dir_name in DIRS_TO_CREATE:
        dir_path = project_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"  创建目录：{dir_name}")

    # 创建 .gitignore
    gitignore_content = """# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# 项目特定
outputs/*/raw_md/
outputs/*/clean_md/
outputs/*/pageindex/
outputs/*/summary/
outputs/*/logs/
outputs/*/*.md
projects/*.pdf
"""
    gitignore_path = project_dir / ".gitignore"
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    print("  创建文件：.gitignore")

    # 创建空的 README 模板
    readme_template = f"""# {project_name}

论文分析项目，使用论文阅读工作流。

## 使用方法

1. 将 PDF 文件放入 `projects/` 目录
2. 运行分析：
   ```bash
   python scripts/run_workflow.py --file your-paper.pdf
   ```
3. 查看结果：`outputs/<pdf_stem>/`

## 目录结构

```
{project_name}/
├── projects/          # PDF 输入目录
├── outputs/           # 输出目录
├── scripts/           # 工作流脚本
├── memory-bank/       # 文档
├── config.yaml        # 配置文件
└── README.md          # 本文件
```

## 详细说明

参考 `memory-bank/` 目录下的文档。
"""
    readme_path = project_dir / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_template)
    print("  更新文件：README.md")

    # 创建项目说明文件
    project_info = f"""# 项目信息

- **项目名称**：{project_name}
- **创建时间**：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **模板来源**：论文阅读工作流

## 快速开始

1. 将 PDF 文件复制到 `projects/` 目录
2. 运行：`python scripts/run_workflow.py --file <filename>.pdf`
3. 查看结果：`outputs/<filename>/`
"""
    info_path = project_dir / "PROJECT.md"
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(project_info)
    print("  创建文件：PROJECT.md")

    print(f"\n项目初始化完成：{project_dir}")
    print(f"\n下一步：")
    print(f"  1. cd {project_dir}")
    print(f"  2. 将 PDF 文件复制到 projects/ 目录")
    print(f"  3. 运行：python scripts/run_workflow.py --file <filename>.pdf")

    return str(project_dir)


def main():
    """主函数。"""
    parser = argparse.ArgumentParser(
        description="初始化新论文分析项目",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 在 D:\ 创建新项目
  python scripts/init_project.py my-paper-analysis

  # 指定目标目录
  python scripts/init_project.py my-paper-analysis --dir E:/projects

  # 查看帮助
  python scripts/init_project.py --help
        """,
    )

    parser.add_argument("name", help="项目名称")
    parser.add_argument("--dir", default="D:/", help="目标目录（默认 D:/）")

    args = parser.parse_args()

    init_project(args.name, args.dir)


if __name__ == "__main__":
    main()
