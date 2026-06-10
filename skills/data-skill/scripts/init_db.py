#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
init_db.py

根据 skill 包内 tables/<表 code>.md 的字段定义, 在 ~/.data-skill/data.db
执行 CREATE TABLE IF NOT EXISTS。

构建期生成的 tables/*.md 是 schema 唯一来源, 运行时不再读 xlsx。
"""
import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

import yaml


def user_dir() -> Path:
    return Path.home() / ".data-skill"


def load_config() -> dict:
    cfg_path = user_dir() / "config.yml"
    if not cfg_path.exists():
        print(json.dumps({"ok": False, "errors": [f"config.yml 不存在: {cfg_path}, 请先跑 init_config.py"]}, ensure_ascii=False))
        sys.exit(1)
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_table_md(md_path: Path) -> tuple[str, list[dict]]:
    """
    解析 tables/<code>.md, 返回 (code, fields)。
    fields: [{code, type, length, decimal, constraint, primary_key}]
    """
    text = md_path.read_text(encoding="utf-8")
    code_match = re.search(r"^#\s+(\S+)\s+-\s+", text, re.MULTILINE)
    if not code_match:
        raise ValueError(f"无法从 {md_path} 解析表代码")
    code = code_match.group(1).strip()

    fields: list[dict] = []
    in_table = False
    for line in text.splitlines():
        if line.strip().startswith("| 序号"):
            in_table = True
            continue
        if in_table and line.strip().startswith("|---"):
            continue
        if in_table and line.strip() == "":
            break
        if in_table and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 7:
                continue
            seq, name, fcode_cell, ftype, flen, fdec, constraint, *_ = cells
            fcode = fcode_cell.strip("`").strip()
            fields.append({
                "seq": seq,
                "name": name,
                "code": fcode,
                "type": ftype,
                "length": int(flen) if flen and flen.isdigit() else None,
                "decimal": int(fdec) if fdec and fdec.isdigit() else None,
                "constraint": constraint,
            })
        elif in_table and not line.strip().startswith("|"):
            in_table = False

    if fields:
        fields[0]["primary_key"] = True
    return code, fields


def sqlite_type(field: dict) -> str:
    t = field["type"].lower()
    if t in ("char", "clob", "text", "varchar"):
        if field.get("length") and field["length"] > 0:
            return f"VARCHAR({field['length']})"
        return "TEXT"
    if t in ("int", "integer", "bigint"):
        return "INTEGER"
    if t in ("float", "double", "decimal", "number"):
        return "REAL"
    if t in ("date", "datetime", "timestamp"):
        return "TEXT"
    return "TEXT"


def build_ddl(code: str, fields: list[dict]) -> str:
    cols = []
    for f in fields:
        col_def = f'"{f["code"]}" {sqlite_type(f)}'
        if f.get("primary_key"):
            col_def += " PRIMARY KEY"
        cols.append(col_def)
    return f'CREATE TABLE IF NOT EXISTS "{code}" (\n  ' + ",\n  ".join(cols) + "\n);"


def main():
    parser = argparse.ArgumentParser(description="建库脚本, 按 tables/*.md 在 SQLite 中建表")
    parser.add_argument("--skill-dir", default=str(Path(__file__).resolve().parents[1]),
                        help="skill 包根目录, 含 tables/")
    args = parser.parse_args()

    cfg = load_config()
    db_path = Path(cfg["db_path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)

    tables_dir = Path(args.skill_dir) / "tables"
    if not tables_dir.exists():
        print(json.dumps({"ok": False, "errors": [f"tables 目录不存在: {tables_dir}"]}, ensure_ascii=False))
        sys.exit(1)

    md_files = sorted(tables_dir.glob("*.md"))
    if not md_files:
        print(json.dumps({"ok": False, "errors": [f"tables 目录无 md: {tables_dir}"]}, ensure_ascii=False))
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    created = []
    errors = []
    for md in md_files:
        try:
            code, fields = parse_table_md(md)
            ddl = build_ddl(code, fields)
            cur.execute(ddl)
            created.append({"code": code, "fields": len(fields)})
        except Exception as e:
            errors.append({"file": md.name, "error": str(e)})
    conn.commit()
    conn.close()

    print(json.dumps({
        "ok": len(errors) == 0,
        "db_path": str(db_path),
        "created": created,
        "errors": errors,
    }, ensure_ascii=False, indent=2))

    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
