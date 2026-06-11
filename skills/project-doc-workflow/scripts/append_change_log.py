#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
append_change_log.py

按策划表子标签规整格式，向 <项目根>/06_变更及暂停/变更记录.md 追加一条记录。

Usage:
    python append_change_log.py \
        --project-root "D:\\项目文档\\202410-C0008-..." \
        --doc-type "测试方案" \
        --change-type "新增" \
        --summary "自动生成 V1.0 大纲与正文" \
        --operator "project-doc-skill"
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# 绕开 Windows PowerShell 5.1 GBK 默认编码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


CHANGE_LOG_PATH_TEMPLATE = "06_变更及暂停/变更记录.md"

CHANGE_LOG_HEADER = """| 日期 | 项目编号 | 变更类型 | 文档名 | 摘要 | 操作人（系统） |
|---|---|---|---|---|---|
"""

CHANGE_LOG_FALLBACK_HEADER = """# 变更记录

> 本文件由 project-doc-skill 自动维护。每次生成/更新文档时会追加一条记录。

""" + CHANGE_LOG_HEADER


def detect_project_id(project_root: Path) -> str:
    """从项目根目录名提取项目编号（如 202410-C0008-... → 202410-C0008）"""
    name = project_root.name
    parts = name.split("-")
    if len(parts) >= 2 and parts[0][:6].isdigit():
        return f"{parts[0]}-{parts[1]}"
    return name


def ensure_change_log(project_root: Path) -> Path:
    """确保变更记录文件存在；不存在则创建并写表头"""
    log_path = project_root / CHANGE_LOG_PATH_TEMPLATE
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text(CHANGE_LOG_FALLBACK_HEADER, encoding="utf-8")
    return log_path


def append_row(
    log_path: Path,
    date: str,
    project_id: str,
    change_type: str,
    doc_name: str,
    summary: str,
    operator: str,
) -> None:
    row = f"| {date} | {project_id} | {change_type} | {doc_name} | {summary} | {operator} |\n"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(row)


def main() -> int:
    parser = argparse.ArgumentParser(description="向项目变更记录追加一行")
    parser.add_argument("--project-root", required=True, help="项目根目录绝对路径")
    parser.add_argument("--doc-type", required=True, help="文档类型（如 测试方案）")
    parser.add_argument("--change-type", default="新增", help="变更类型：新增/更新/删除")
    parser.add_argument("--summary", default="", help="变更摘要")
    parser.add_argument("--operator", default="project-doc-skill", help="操作人/系统")
    args = parser.parse_args()

    project_root = Path(args.project_root)
    if not project_root.exists():
        print(f"[ERR] 项目根目录不存在: {project_root}")
        return 1

    log_path = ensure_change_log(project_root)
    project_id = detect_project_id(project_root)
    today = datetime.now().strftime("%Y-%m-%d")
    doc_name = f"{args.doc_type}.md"

    append_row(
        log_path,
        date=today,
        project_id=project_id,
        change_type=args.change_type,
        doc_name=doc_name,
        summary=args.summary or f"由 project-doc-skill V1 自动{args.change_type}",
        operator=args.operator,
    )

    print(f"[OK] 已追加变更记录 -> {log_path}")
    print(f"     {today} | {project_id} | {args.change_type} | {doc_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
