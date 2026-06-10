#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
list_sheets.py

列出 skill 包内所有表名 + 业务说明 + 主键, 给 LLM 选表用。

调用:
  python list_sheets.py
  python list_sheets.py --filter ZZ
  python list_sheets.py --format json
"""
import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
TABLES_DIR = SKILL_DIR / "tables"


def parse_table_md(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    code_match = re.search(r"^#\s+(\S+)\s+-\s+(.+)$", text, re.MULTILINE)
    if not code_match:
        return {"code": md_path.stem, "business_name": "", "primary_key": ""}
    code = code_match.group(1).strip()
    business = code_match.group(2).strip()
    pk_match = re.search(r"主键\*\*:\s*`(\S+?)`", text)
    pk = pk_match.group(1) if pk_match else ""
    return {"code": code, "business_name": business, "primary_key": pk}


def main():
    parser = argparse.ArgumentParser(description="列出所有表")
    parser.add_argument("--filter", default="", help="按 code 子串过滤")
    parser.add_argument("--format", default="json", choices=["json", "text"])
    args = parser.parse_args()

    if not TABLES_DIR.exists():
        print(json.dumps({"ok": False, "errors": [f"tables 目录不存在: {TABLES_DIR}"]}, ensure_ascii=False))
        sys.exit(1)

    tables = []
    for md in sorted(TABLES_DIR.glob("*.md")):
        info = parse_table_md(md)
        if args.filter and args.filter.upper() not in info["code"].upper():
            continue
        tables.append(info)

    if args.format == "json":
        print(json.dumps({"ok": True, "count": len(tables), "tables": tables}, ensure_ascii=False, indent=2))
    else:
        for t in tables:
            print(f"- {t['code']}: {t['business_name']} (主键: {t['primary_key']})")


if __name__ == "__main__":
    main()
