#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
verify_inventory.py

核验 inventory.json, 找出未处理的文件, 输出 verify_report.json。
本脚本只做"清单比对", 不直接补跑 - 补跑由 SKILL.md 决定 (重跑 LLM 流程)。

调用:
  python verify_inventory.py --dir <path>
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="核验 inventory")
    parser.add_argument("--dir", required=True, help="目标目录")
    args = parser.parse_args()

    target_dir = Path(args.dir).resolve()
    inv_path = target_dir / ".data-skill" / "inventory.json"
    if not inv_path.exists():
        print(json.dumps({"ok": False, "errors": [f"inventory.json 不存在: {inv_path}"]}, ensure_ascii=False))
        sys.exit(1)

    with open(inv_path, "r", encoding="utf-8") as f:
        inventory = json.load(f)

    pending = [x for x in inventory["items"] if x["status"] == "pending"]
    processing = [x for x in inventory["items"] if x["status"] == "processing"]
    failed = [x for x in inventory["items"] if x["status"] == "failed" and x.get("errors")]
    skipped_no_match = [
        x for x in inventory["items"]
        if x["status"] == "skipped" and any("no_match" in (e or "") for e in x.get("errors", []))
    ]
    done = [x for x in inventory["items"] if x["status"] == "done"]
    skipped_other = [
        x for x in inventory["items"]
        if x["status"] == "skipped" and x not in skipped_no_match
    ]

    missing = pending + processing
    needs_retry = skipped_no_match

    report = {
        "version": 1,
        "target_dir": str(target_dir),
        "total": len(inventory["items"]),
        "summary": {
            "done": len(done),
            "skipped_no_match": len(skipped_no_match),
            "skipped_other": len(skipped_other),
            "failed": len(failed),
            "pending": len(pending),
            "processing": len(processing),
        },
        "missing": missing,
        "needs_retry": needs_retry,
        "failed_items": failed,
    }

    out_path = target_dir / ".data-skill" / "verify_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    need_action = bool(missing or needs_retry)
    print(json.dumps({
        "ok": True,
        "report_path": str(out_path),
        "need_action": need_action,
        "missing_count": len(missing),
        "needs_retry_count": len(needs_retry),
        "failed_count": len(failed),
        "done_count": len(done),
    }, ensure_ascii=False, indent=2))

    sys.exit(2 if need_action else 0)


if __name__ == "__main__":
    main()
