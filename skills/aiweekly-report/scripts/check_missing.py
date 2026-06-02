#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_missing.py - 漏检检测脚本

通过对比"人名配置清单"与"已评审人员名单"，输出本周未提交者。
遵循"确定的事应该由脚本完成"原则：漏检 = 纯 set 差集，无需模型判断。

Usage:
    python check_missing.py --members <path> --reviewed <path>

Output:
    - 控制台：可读格式的漏检名单
    - stdout JSON: {"missing": [...], "count": N, "total_members": M, "reviewed_count": K}
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


def read_reviewed_names(path: Path) -> list[str]:
    if not path.exists():
        print(f"[ERROR] 评审结果文件不存在: {path}", file=sys.stderr)
        sys.exit(2)
    data = json.loads(path.read_text(encoding="utf-8"))
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
    parser = argparse.ArgumentParser(description="漏检检测：人名清单 - 已评审名单")
    parser.add_argument(
        "--members",
        required=True,
        help="人名配置清单路径（每行一个姓名）",
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
    reviewed_path = Path(args.reviewed)

    should = set(read_members(members_path))
    reviewed = set(read_reviewed_names(reviewed_path))
    missing = sorted(should - reviewed)

    result = {
        "missing": missing,
        "count": len(missing),
        "total_members": len(should),
        "reviewed_count": len(reviewed),
    }

    print(f"应到 {len(should)} 人，已评审 {len(reviewed)} 人，漏检 {len(missing)} 人")
    if missing:
        print("漏检名单:")
        for name in missing:
            print(f"  - {name}")
    else:
        print("无漏检")

    if args.output_json:
        Path(args.output_json).write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"已写入: {args.output_json}")

    print("---JSON-BEGIN---")
    print(json.dumps(result, ensure_ascii=False))
    print("---JSON-END---")

    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
