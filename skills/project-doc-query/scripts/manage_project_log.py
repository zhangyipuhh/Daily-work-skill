#!/usr/bin/python
# -*- coding:utf-8 -*-
r"""
manage_project_log.py

WHY NOT `from DocumentLoader import ...` IN YOUR OWN SCRIPT?
============================================================
常见反模式：嫌 PowerShell 引号转义麻烦 → 写临时 .py → from DocumentLoader import ...
本 SKILL 反模式红线段明令禁止（见 ../SKILL.md §反模式红线）。

本 CLI 用途：管理 .project/<项目号>/ 下的日志文件。
  - init: 首次创建 .project 目录 + project_log.md + clarification_log.md
  - append-clarification: 追加一条澄清记录到 clarification_log.md
  - append-operation: 追加一条主操作记录到 project_log.md
  - read: 打印主日志内容

退出码：0 成功 / 1 项目根或工作根不存在 / 2 文件读写异常

------------------------------------------------------------
所有过程文件（project_log.md / clarification_log.md / drafts/）都放在
<用户工作根>/.project/<项目号>/ 下，**不在 skill 内**。
由 query skill 的 dump_paths.py 自动生成路径变量。

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
from datetime import datetime


PROJECT_HEADER = """# Project Log · {project_id}

> 项目根：{project_root}
> 初始化时间：{timestamp}
> 初始化 skill：{init_skill}

## 操作记录

| 时间戳 | skill | 操作类型 | 修改内容 | 证据/路径 |
|---|---|---|---|---|
"""

CLARIFICATION_HEADER = """# Clarification Log · {project_id}

> 配套 project_log.md 使用。
> 每次模型向用户询问并得到回答后追加一行。

| # | 时间戳 | 维度 | 子项 | 问题摘要 | 用户回答 | 来源 | 调用的 skill |
|---|---|---|---|---|---|---|---|
"""


def extract_project_id(project_root_name: str) -> str:
    """从项目根目录名提取项目编号，如 202410-C0008-... -> 202410-C0008"""
    parts = project_root_name.split("-")
    if len(parts) >= 2 and parts[0][:6].isdigit():
        return f"{parts[0]}-{parts[1]}"
    return project_root_name


def get_project_dir(work_root: Path, project_id: str) -> Path:
    """返回 .project/<project_id>/ 绝对路径"""
    return work_root / ".project" / project_id


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def cmd_init(args) -> int:
    work_root = Path(args.work_root)
    project_id = args.project_id
    init_skill = args.init_skill or "project-doc-overview"

    if not work_root.exists():
        print(f"[ERR] 工作根不存在: {work_root}", file=sys.stderr)
        return 1

    project_dir = get_project_dir(work_root, project_id)
    ensure_dir(project_dir)

    project_root = args.project_root or "<待用户在 query 阶段提供>"
    project_log = project_dir / "project_log.md"
    clarification_log = project_dir / "clarification_log.md"
    drafts_dir = project_dir / "drafts"
    ensure_dir(drafts_dir)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not project_log.exists():
        header = PROJECT_HEADER.format(
            project_id=project_id,
            project_root=project_root,
            timestamp=now,
            init_skill=init_skill,
        )
        first_row = f"| {now} | {init_skill} | 初始化 | 创建 .project 目录与日志 | .project/{project_id}/ |\n"
        project_log.write_text(header + first_row, encoding="utf-8")
        print(f"[OK] 创建 {project_log}")
    else:
        print(f"[SKIP] 已存在: {project_log}")

    if not clarification_log.exists():
        header = CLARIFICATION_HEADER.format(project_id=project_id)
        first_row = f"| 0 | {now} | (init) | (init) | 初始化空日志 | (init) | (init) | {init_skill} |\n"
        clarification_log.write_text(header + first_row, encoding="utf-8")
        print(f"[OK] 创建 {clarification_log}")
    else:
        print(f"[SKIP] 已存在: {clarification_log}")

    print(f"\n[OK] .project 目录就绪 → {project_dir}")
    return 0


def cmd_append_clarification(args) -> int:
    work_root = Path(args.work_root)
    project_id = args.project_id
    project_dir = get_project_dir(work_root, project_id)

    if not project_dir.exists():
        print(f"[ERR] .project/{project_id}/ 不存在，请先 init", file=sys.stderr)
        return 1

    log_path = project_dir / "clarification_log.md"
    if not log_path.exists():
        print(f"[ERR] {log_path} 不存在，请先 init", file=sys.stderr)
        return 1

    # 计算下一行编号
    with log_path.open("r", encoding="utf-8") as f:
        existing = f.readlines()
    last_num = 0
    for line in existing[3:]:  # 跳过表头 3 行
        if line.startswith("|"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) > 1 and parts[1].isdigit():
                last_num = max(last_num, int(parts[1]))

    next_num = last_num + 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = (
        f"| {next_num} | {now} | {args.dimension} | {args.item} "
        f"| {args.question} | {args.answer} | {args.source} | {args.asked_by} |\n"
    )

    with log_path.open("a", encoding="utf-8") as f:
        f.write(row)

    print(f"[OK] 澄清记录 #{next_num} 已追加 → {log_path}")
    return 0


def cmd_append_operation(args) -> int:
    work_root = Path(args.work_root)
    project_id = args.project_id
    project_dir = get_project_dir(work_root, project_id)

    if not project_dir.exists():
        print(f"[ERR] .project/{project_id}/ 不存在，请先 init", file=sys.stderr)
        return 1

    log_path = project_dir / "project_log.md"
    if not log_path.exists():
        print(f"[ERR] {log_path} 不存在，请先 init", file=sys.stderr)
        return 1

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    evidence = args.evidence or "(无)"
    row = f"| {now} | {args.skill} | {args.op_type} | {args.content} | {evidence} |\n"

    with log_path.open("a", encoding="utf-8") as f:
        f.write(row)

    print(f"[OK] 操作记录已追加 → {log_path}")
    return 0


def cmd_read(args) -> int:
    work_root = Path(args.work_root)
    project_id = args.project_id
    project_dir = get_project_dir(work_root, project_id)

    if not project_dir.exists():
        print(f"[ERR] .project/{project_id}/ 不存在", file=sys.stderr)
        return 1

    log_path = project_dir / (args.log or "project_log.md")
    if not log_path.exists():
        print(f"[ERR] {log_path} 不存在", file=sys.stderr)
        return 1

    print(log_path.read_text(encoding="utf-8"), flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="管理 .project/<项目号>/ 下的日志文件（init / append / read）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="首次创建 .project 目录与日志")
    p_init.add_argument("--work-root", required=True, help="工作根目录（项目根的父目录）")
    p_init.add_argument("--project-id", required=True, help="项目编号（如 202410-C0008）")
    p_init.add_argument("--project-root", default=None, help="项目根目录绝对路径（可选）")
    p_init.add_argument("--init-skill", default="project-doc-overview", help="初始化 skill 名")

    # append-clarification
    p_ac = subparsers.add_parser("append-clarification", help="追加一条澄清记录到 clarification_log.md")
    p_ac.add_argument("--work-root", required=True)
    p_ac.add_argument("--project-id", required=True)
    p_ac.add_argument("--dimension", required=True, help="维度（如 A.intent / B.data / C.environment / D.document_attr）")
    p_ac.add_argument("--item", required=True, help="子项（如 intent_fact_or_decision / tech_hardware）")
    p_ac.add_argument("--question", required=True, help="问题摘要")
    p_ac.add_argument("--answer", required=True, help="用户回答")
    p_ac.add_argument("--source", required=True, help="信息来源（用户口述 / 用户确认 / 文件 §X）")
    p_ac.add_argument("--asked-by", required=True, help="调用本 skill 的子 skill 名")

    # append-operation
    p_ao = subparsers.add_parser("append-operation", help="追加一条主操作记录到 project_log.md")
    p_ao.add_argument("--work-root", required=True)
    p_ao.add_argument("--project-id", required=True)
    p_ao.add_argument("--skill", required=True, help="执行操作的 skill 名")
    p_ao.add_argument("--op-type", required=True, help="操作类型（新增/更新/删除/澄清/追加）")
    p_ao.add_argument("--content", required=True, help="修改内容摘要")
    p_ao.add_argument("--evidence", default=None, help="证据/路径")

    # read
    p_read = subparsers.add_parser("read", help="读主日志/澄清日志")
    p_read.add_argument("--work-root", required=True)
    p_read.add_argument("--project-id", required=True)
    p_read.add_argument("--log", default="project_log.md", help="日志文件名（project_log.md / clarification_log.md）")

    args = parser.parse_args()

    if args.command == "init":
        return cmd_init(args)
    elif args.command == "append-clarification":
        return cmd_append_clarification(args)
    elif args.command == "append-operation":
        return cmd_append_operation(args)
    elif args.command == "read":
        return cmd_read(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
