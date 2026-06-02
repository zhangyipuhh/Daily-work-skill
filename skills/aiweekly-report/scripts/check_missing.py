#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_missing.py - 漏检检测脚本（V2.2）

通过对比三方集合，输出两类漏检：
  1. 真未提交 (not_submitted)：人名清单有，但周目录无子目录
  2. 漏评审 (not_reviewed)：周目录有子目录，但 review_results.json 缺该名字

遵循"确定的事应该由脚本完成"原则：漏检 = 纯 set 运算，无需模型判断。

Usage:
    python check_missing.py --members <path> --attended <week_dir> --reviewed <path>
    python check_missing.py --members <path> --attended <week_dir> --reviewed <path> --output-json <path>

Output:
    - 控制台：可读格式的两类漏检名单
    - stdout JSON:
        {
          "total_members": 40,
          "actually_attended": 35,
          "reviewed_count": 33,
          "not_submitted": [...],   # 情况 A：真未提交
          "not_submitted_count": 5,
          "not_reviewed": [...],    # 情况 B：漏评审（需补件）
          "not_reviewed_count": 2,
          "missing": [...],         # 兼容旧字段
          "missing_count": 7
        }
    - 返回码: 0 = 无漏检, 1 = 有漏检（仅返回码，不阻断流程）
"""
import argparse
import json
import sys
from pathlib import Path


def read_members(path: Path) -> list[str]:
    if not path.exists():
        print(f"[ERROR] 人名清单不存在: {path}", file=sys.stderr)
        sys.exit(2)
    members = []
    for line in path.read_text(encoding="utf-8").splitlines():
        name = line.strip()
        if name and not name.startswith("#"):
            members.append(name)
    return members


def scan_attended_subdirs(week_dir: Path) -> list[str]:
    """扫描周目录下所有子目录名（仅目录）"""
    if not week_dir.exists():
        print(f"[ERROR] 周目录不存在: {week_dir}", file=sys.stderr)
        sys.exit(2)
    if not week_dir.is_dir():
        print(f"[ERROR] 周目录不是目录: {week_dir}", file=sys.stderr)
        sys.exit(2)
    names = []
    for child in sorted(week_dir.iterdir()):
        if child.is_dir():
            names.append(child.name)
    return names


def read_reviewed_names(path: Path) -> list[str]:
    if not path.exists():
        print(f"[ERROR] 评审结果文件不存在: {path}", file=sys.stderr)
        sys.exit(2)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 解析失败: {e}", file=sys.stderr)
        sys.exit(2)
    names = []
    for item in data:
        if not isinstance(item, dict):
            continue
        d = item.get("data", {})
        if not isinstance(d, dict):
            continue
        name = d.get("name")
        if name:
            names.append(name)
    return names


def main() -> None:
    parser = argparse.ArgumentParser(
        description="漏检检测：拆分真未提交与漏评审"
    )
    parser.add_argument(
        "--members",
        required=True,
        help="人名配置清单路径（每行一个姓名）",
    )
    parser.add_argument(
        "--attended",
        required=True,
        help="周目录路径（扫描其下子目录名作为实际提交者）",
    )
    parser.add_argument(
        "--reviewed",
        required=True,
        help="review_results.json 路径",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="可选：把漏检结果同时写入此 JSON 文件",
    )
    args = parser.parse_args()

    members_path = Path(args.members)
    week_dir = Path(args.attended)
    reviewed_path = Path(args.reviewed)

    should = set(read_members(members_path))
    attended = set(scan_attended_subdirs(week_dir))
    reviewed = set(read_reviewed_names(reviewed_path))

    not_submitted = sorted(should - attended)
    not_reviewed = sorted(attended - reviewed)
    missing = sorted(set(not_submitted) | set(not_reviewed))

    result = {
        "total_members": len(should),
        "actually_attended": len(attended),
        "reviewed_count": len(reviewed),
        "not_submitted": not_submitted,
        "not_submitted_count": len(not_submitted),
        "not_reviewed": not_reviewed,
        "not_reviewed_count": len(not_reviewed),
        "missing": missing,
        "missing_count": len(missing),
    }

    print(f"应到 {len(should)} 人，周目录实到 {len(attended)} 人，已评审 {len(reviewed)} 人")
    if not_submitted:
        print(f"真未提交 (A) {len(not_submitted)} 人（需补 0 分）:")
        for name in not_submitted:
            print(f"  A - {name}")
    if not_reviewed:
        print(f"漏评审 (B) {len(not_reviewed)} 人（需补件: 重新派 subagent 评审）:")
        for name in not_reviewed:
            print(f"  B - {name}")
    if not not_submitted and not not_reviewed:
        print("无漏检，全员已评审。")

    if args.output_json:
        Path(args.output_json).write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"已写入: {args.output_json}")

    print("---JSON-BEGIN---")
    print(json.dumps(result, ensure_ascii=False))
    print("---JSON-END---")

    has_missing = bool(not_submitted or not_reviewed)
    sys.exit(1 if has_missing else 0)


if __name__ == "__main__":
    main()
