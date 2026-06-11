#!/usr/bin/python
# -*- coding:utf-8 -*-
r"""
find_planning_sheet.py

WHY NOT `from DocumentLoader import ...` IN YOUR OWN SCRIPT?
============================================================
常见反模式：嫌 PowerShell 引号转义麻烦 → 写临时 .py → from DocumentLoader import ...
本 SKILL 反模式红线段明令禁止（见 ../SKILL.md §反模式红线）。

正确做法（任选其一）：
  1. 直接调本 CLI：
     python scripts/find_planning_sheet.py --project-root "<项目根>" [--pattern GLOB] [--output path|info|json]
  2. 路径长/转义麻烦 → 用 dump_paths.py 生成 PowerShell 变量：
     . (python scripts/dump_paths.py --project-root "<项目根>" --format ps1)
     python scripts/find_planning_sheet.py --project-root $PROJECT_ROOT --output path
  3. 想在 Python 里继续处理：
     from find_planning_sheet import find_planning_sheet, extract_version
     candidates = find_planning_sheet(Path(root), "*策划表V*.xlsm")

退出码：0 成功 / 1 项目根不存在 / 4 未找到策划表

------------------------------------------------------------
在项目根的 01_项目策划/ 子目录下，按文件名 glob 定位最新版策划表 xlsm。
实现 references/评审计划_提取方法.md Step 1 的定位逻辑。

Date: 2026-06-11
Author: project-doc-query skill
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import argparse
import glob
import re


def extract_version(stem: str) -> tuple:
    """从文件名提取版本号 (major, minor)，如 策划表V1.0 -> (1, 0)"""
    m = re.search(r"V(\d+)\.(\d+)", stem, re.IGNORECASE)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    m2 = re.search(r"V(\d+)", stem, re.IGNORECASE)
    if m2:
        return (int(m2.group(1)), 0)
    return (0, 0)


def find_planning_sheet(project_root: Path, pattern: str) -> list:
    """在 <project_root>/01_项目策划/ 下按 glob 找策划表，按版本号降序。"""
    candidate_dir = project_root / "01_项目策划"
    if not candidate_dir.exists():
        return []
    candidates = glob.glob(str(candidate_dir / pattern))
    candidates = [c for c in candidates if not Path(c).name.startswith("~$")]
    candidates.sort(key=lambda p: extract_version(Path(p).stem), reverse=True)
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(
        description="在项目根目录下定位最新版策划表 xlsm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python find_planning_sheet.py --project-root \"D:\\\\项目文档\\\\202410-C0008-...\" --output path\n"
            "  python find_planning_sheet.py --project-root \"D:\\\\项目文档\\\\202410-C0008-...\" --output info\n"
        ),
    )
    parser.add_argument("--project-root", required=True, help="项目根目录绝对路径")
    parser.add_argument("--pattern", default="*策划表V*.xlsm", help="glob 模式（默认 *策划表V*.xlsm）")
    parser.add_argument("--output", choices=["path", "info", "json"], default="path",
                        help="path=输出绝对路径（管道用） / info=人类可读 / json=结构化")
    args = parser.parse_args()

    project_root = Path(args.project_root)
    if not project_root.exists():
        print(f"[ERR] 项目根目录不存在: {project_root}", file=sys.stderr)
        return 1

    candidates = find_planning_sheet(project_root, args.pattern)
    if not candidates:
        print(f"[ERR] 在 {project_root / '01_项目策划'} 下未找到匹配 {args.pattern!r} 的策划表", file=sys.stderr)
        return 4

    if args.output == "path":
        if len(candidates) > 1:
            print(f"[WARN] 找到 {len(candidates)} 个匹配项，取最新版", file=sys.stderr)
            for c in candidates[1:]:
                print(f"  - {c}", file=sys.stderr)
        print(candidates[0])
        return 0
    elif args.output == "json":
        import json
        print(json.dumps([{"path": c, "version": list(extract_version(Path(c).stem))} for c in candidates],
                         ensure_ascii=False, indent=2))
        return 0
    else:  # info
        print(f"找到 {len(candidates)} 个策划表（按版本降序）：")
        for c in candidates:
            v = extract_version(Path(c).stem)
            print(f"  V{v[0]}.{v[1]}  {c}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
