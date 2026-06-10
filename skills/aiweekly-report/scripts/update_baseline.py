#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
update_baseline.py - Baseline 基准库维护脚本

将当前周 review_results.json 写入 SQLite 数据库 (baseline.db)。
记录每期、每个人的总分，供报告"第七章 全量比对（最近 4 次）"使用。

输入：review_results_<week>.json
输出：baseline/baseline.db (SQLite)

依赖：Python 内置 sqlite3（无需 pip install）
"""
import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS review_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  week TEXT NOT NULL,
  name TEXT NOT NULL,
  overall_score REAL,
  doc_quality REAL,
  doc_completeness REAL,
  doc_clarity REAL,
  doc_technical REAL,
  ai_adoption REAL,
  doc_code_consistency REAL,
  doc_task_consistency REAL,
  has_anti_patterns INTEGER DEFAULT 0,
  priority TEXT,
  timestamp TEXT NOT NULL,
  UNIQUE(week, name)
);

CREATE INDEX IF NOT EXISTS idx_name ON review_history(name);
CREATE INDEX IF NOT EXISTS idx_week ON review_history(week);

CREATE TABLE IF NOT EXISTS weeks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  week_no INTEGER NOT NULL UNIQUE,
  week_name TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_week_no ON weeks(week_no);
"""


def safe_get(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def to_float(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.rstrip("%")) / 100.0 if "%" in v else float(v)
        except (ValueError, AttributeError):
            return None
    return None


def to_int(v):
    if isinstance(v, bool):
        return 1 if v else 0
    if isinstance(v, (int, float)):
        return 1 if v else 0
    if isinstance(v, str):
        if v.lower() in ("true", "yes", "1", "是"):
            return 1
        if v.lower() in ("false", "no", "0", "否", ""):
            return 0
    return 0


def extract_record(item: dict, week: str, ts: str) -> dict | None:
    if not isinstance(item, dict):
        return None
    data = item.get("data")
    if not isinstance(data, dict):
        return None
    name = data.get("name") or item.get("name")
    if not name:
        return None

    # insufficient_data → 强制 0 分，确保 baseline 覆盖全员
    if item.get("insufficient_data") or data.get("insufficient_data"):
        overall = 0.0
    else:
        overall = to_float(safe_get(data, "overall_score"))
        if overall is None:
            return None  # 正常条目无分数才跳过

    return {
        "week": week,
        "name": str(name).strip(),
        "overall_score": overall,
        "doc_quality": to_float(safe_get(data, "document_quality", "overall_score")),
        "doc_completeness": to_float(safe_get(data, "document_quality", "completeness")),
        "doc_clarity": to_float(safe_get(data, "document_quality", "clarity")),
        "doc_technical": to_float(safe_get(data, "document_quality", "technical_accuracy")),
        "ai_adoption": to_float(safe_get(data, "ai_adoption_rate", "adoption_rate")),
        "doc_code_consistency": to_float(safe_get(data, "ai_adoption_rate", "doc_code_consistency", "consistency_score")),
        "doc_task_consistency": to_float(safe_get(data, "ai_adoption_rate", "doc_task_consistency", "task_consistency_score")),
        "has_anti_patterns": to_int(safe_get(data, "anti_patterns", "has_issues")),
        "priority": (safe_get(data, "improvement_priority") or "").strip() or None,
        "timestamp": ts,
    }


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(DB_SCHEMA)
        conn.commit()
    finally:
        conn.close()


def upsert_records(db_path: Path, records: list[dict]) -> tuple[int, int]:
    """返回 (新增, 覆盖) 条数"""
    if not records:
        return 0, 0
    conn = sqlite3.connect(str(db_path))
    inserted = 0
    replaced = 0
    try:
        cur = conn.cursor()
        for rec in records:
            cur.execute("SELECT id FROM review_history WHERE week = ? AND name = ?", (rec["week"], rec["name"]))
            existing = cur.fetchone()
            cur.execute(
                """
                INSERT OR REPLACE INTO review_history (
                  week, name, overall_score, doc_quality, doc_completeness,
                  doc_clarity, doc_technical, ai_adoption,
                  doc_code_consistency, doc_task_consistency,
                  has_anti_patterns, priority, timestamp
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    rec["week"], rec["name"], rec["overall_score"],
                    rec["doc_quality"], rec["doc_completeness"],
                    rec["doc_clarity"], rec["doc_technical"], rec["ai_adoption"],
                    rec["doc_code_consistency"], rec["doc_task_consistency"],
                    rec["has_anti_patterns"], rec["priority"], rec["timestamp"],
                ),
            )
            if existing:
                replaced += 1
            else:
                inserted += 1
        conn.commit()
    finally:
        conn.close()
    return inserted, replaced


def upsert_week(db_path: Path, week_name: str, ts: str) -> tuple[bool, int]:
    """写入 weeks 表，返回 (是否新插入, week_no)
    若 week_name 已存在则跳过，返回 (False, 现有week_no)
    """
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute("SELECT week_no FROM weeks WHERE week_name = ?", (week_name,))
        row = cur.fetchone()
        if row:
            conn.close()
            return False, row[0]
        cur.execute("SELECT COALESCE(MAX(week_no), 0) FROM weeks")
        max_no = cur.fetchone()[0] or 0
        new_no = max_no + 1
        cur.execute(
            "INSERT INTO weeks (week_no, week_name, created_at) VALUES (?, ?, ?)",
            (new_no, week_name, ts),
        )
        conn.commit()
        return True, new_no
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Baseline 基准库更新（SQLite）")
    parser.add_argument("--input", required=True, help="review_results_*.json 路径")
    parser.add_argument("--db", required=True, help="baseline.db 输出路径")
    parser.add_argument("--week-name", required=True, help="周名称（如 0525-0531）")
    parser.add_argument("--week", dest="legacy_week", default=None, help="已废弃，请使用 --week-name")
    args = parser.parse_args()

    input_path = Path(args.input)
    db_path = Path(args.db)
    week_name = args.week_name

    if not input_path.exists():
        print(f"[ERROR] 输入文件不存在: {input_path}", file=sys.stderr)
        return 2

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 解析失败: {e}", file=sys.stderr)
        return 2

    if not isinstance(data, list):
        print(f"[ERROR] JSON 根节点必须是数组，当前是 {type(data).__name__}", file=sys.stderr)
        return 2

    ts = datetime.now().isoformat(timespec="seconds")

    init_db(db_path)
    is_new, week_no = upsert_week(db_path, week_name, ts)

    records = []
    skipped = 0
    for item in data:
        rec = extract_record(item, week_name, ts)
        if rec is None:
            skipped += 1
        else:
            records.append(rec)

    inserted, replaced = upsert_records(db_path, records)

    print(f"[OK] Baseline 更新完成")
    print(f"     数据库: {db_path}")
    print(f"     周名称: {week_name} (第 {week_no} 周)")
    print(f"     周序号: {'新插入' if is_new else '已存在'}")
    print(f"     新增:   {inserted} 条")
    print(f"     覆盖:   {replaced} 条")
    print(f"     跳过:   {skipped} 条（无 overall_score 或缺 name）")
    print(f"     总计:   {len(records)} 条有效数据")
    return 0


if __name__ == "__main__":
    sys.exit(main())
