#!/usr/bin/python
# -*- coding:utf-8 -*-
r"""
scan_project_root.py

WHY NOT `from DocumentLoader import ...` IN YOUR OWN SCRIPT?
============================================================
常见反模式：嫌 PowerShell 引号转义麻烦 → 写临时 .py → from DocumentLoader import ...
本 SKILL 反模式红线段明令禁止（见 ../SKILL.md §反模式红线）。

正确做法：
  1. 直接调本 CLI：
     python scripts/scan_project_root.py --project-root "<项目根>" [--subdir NAME] [--ext .docx,.pdf] [--output list|json|table]
  2. 想列文件后用 PowerShell 截断 → 用 --output json --output-file 写到文件：
     python scripts/scan_project_root.py --project-root "..." --output json --output-file D:\out.json
  3. 想列文件后用 grep 过滤 → 表格输出 + 重定向：
     python scripts/scan_project_root.py --project-root "..." --output table --output-file D:\out.md

退出码：0 成功 / 1 项目根或子目录不存在

------------------------------------------------------------
扫描项目根目录，按子目录名/扩展名过滤列出文件清单。

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


def parse_ext_list(ext_str: str) -> list:
    if not ext_str:
        return []
    parts = [p.strip().lower() for p in ext_str.split(",") if p.strip()]
    return [p if p.startswith(".") else f".{p}" for p in parts]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="扫描项目根目录，按子目录/扩展名过滤列文件清单",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python scan_project_root.py --project-root \"D:\\\\项目文档\\\\202410-C0008-...\"\n"
            "  python scan_project_root.py --project-root \"D:\\\\...\" --subdir 01_项目策划\n"
            "  python scan_project_root.py --project-root \"D:\\\\...\" --ext .docx,.pdf --output json\n"
        ),
    )
    parser.add_argument("--project-root", required=True, help="项目根目录绝对路径")
    parser.add_argument("--subdir", default=None, help="子目录名（如 01_项目策划 / 03_技术文档及评审/01_实施方案）")
    parser.add_argument("--ext", default=None, help="扩展名过滤，逗号分隔（如 .docx,.pdf）")
    parser.add_argument("--output", choices=["list", "json", "table"], default="list",
                        help="list=逐行 / json=结构化 / table=markdown 表格")
    parser.add_argument("--output-file", default=None, help="写入文件路径（绕开 Windows 控制台编码）")
    args = parser.parse_args()

    project_root = Path(args.project_root)
    if not project_root.exists():
        print(f"[ERR] 项目根目录不存在: {project_root}", file=sys.stderr)
        return 1

    target_dir = project_root
    if args.subdir:
        target_dir = project_root / args.subdir
        if not target_dir.exists():
            print(f"[ERR] 子目录不存在: {target_dir}", file=sys.stderr)
            return 1

    exts = parse_ext_list(args.ext)

    files: list = []
    for p in target_dir.rglob("*"):
        if not p.is_file():
            continue
        if p.name.startswith("~$"):  # 跳过 Excel 临时锁文件
            continue
        if exts and p.suffix.lower() not in exts:
            continue
        files.append(p)

    files.sort(key=lambda p: str(p).lower())

    if args.output == "json":
        import json
        payload = [{
            "absolute_path": str(f),
            "relative_path": str(f.relative_to(project_root)),
            "name": f.name,
            "suffix": f.suffix.lower(),
            "size_kb": round(f.stat().st_size / 1024, 1),
        } for f in files]
        text = json.dumps(payload, ensure_ascii=False, indent=2)
    elif args.output == "table":
        lines = ["| 相对路径 | 扩展名 | 大小(KB) |", "|---|---|---|"]
        for f in files:
            rel = str(f.relative_to(project_root))
            lines.append(f"| {rel} | {f.suffix.lower()} | {round(f.stat().st_size / 1024, 1)} |")
        text = "\n".join(lines)
    else:
        text = "\n".join(str(f.relative_to(project_root)) for f in files)

    if args.output_file:
        out_path = Path(args.output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"[OK] 找到 {len(files)} 个文件 → {out_path}")
    else:
        print(text, flush=True)
        print(f"\n[OK] 共 {len(files)} 个文件", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
