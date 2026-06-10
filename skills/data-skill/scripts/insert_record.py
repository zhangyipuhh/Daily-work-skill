#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
insert_record.py

将 LLM 抽出的字段 dict 通过 INSERT OR IGNORE 写入 SQLite。
主键冲突时跳过, 实现幂等。

调用:
  python insert_record.py --table <表 code> --record '<json>' | --record @file
"""
import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

import yaml


def load_config() -> dict:
    cfg_path = Path.home() / ".data-skill" / "config.yml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_record(arg: str) -> dict:
    if arg.startswith("@"):
        with open(arg[1:], "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(arg)


def main():
    parser = argparse.ArgumentParser(description="入库脚本 (INSERT OR IGNORE)")
    parser.add_argument("--table", required=True, help="表 code (如 ZZ_PFXX)")
    parser.add_argument("--record", required=True, help="JSON 字符串或 @file 路径")
    args = parser.parse_args()

    try:
        cfg = load_config()
    except Exception as e:
        print(json.dumps({"ok": False, "errors": [f"加载配置失败: {e}"]}, ensure_ascii=False))
        sys.exit(1)

    db_path = Path(cfg["db_path"])
    if not db_path.exists():
        print(json.dumps({"ok": False, "errors": [f"DB 不存在: {db_path}, 请先跑 init_db.py"]}, ensure_ascii=False))
        sys.exit(1)

    try:
        record = parse_record(args.record)
    except Exception as e:
        print(json.dumps({"ok": False, "errors": [f"record 解析失败: {e}"]}, ensure_ascii=False))
        sys.exit(1)

    if not record:
        print(json.dumps({"ok": False, "errors": ["record 为空"]}, ensure_ascii=False))
        sys.exit(1)

    cols = list(record.keys())
    placeholders = ", ".join(["?"] * len(cols))
    col_list = ", ".join([f'"{c}"' for c in cols])
    sql = f'INSERT OR IGNORE INTO "{args.table}" ({col_list}) VALUES ({placeholders})'

    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute(sql, [record[c] for c in cols])
        conn.commit()
        inserted = cur.rowcount > 0
        primary_key = cols[0] if cols else None
        primary_value = record.get(primary_key) if primary_key else None
        conn.close()
    except Exception as e:
        print(json.dumps({"ok": False, "errors": [f"入库失败: {e}"]}, ensure_ascii=False))
        sys.exit(1)

    print(json.dumps({
        "ok": True,
        "table": args.table,
        "primary_key": primary_key,
        "primary_value": primary_value,
        "inserted": inserted,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
