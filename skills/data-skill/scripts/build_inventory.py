#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_inventory.py

扫描指定目录, 产出 .data-skill/inventory.json。
支持的文件类型与 file_parser_client 一致。

调用:
  python build_inventory.py --dir <path> [--force-rebuild]
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

SUPPORTED_EXTS = {
    ".pdf", ".docx", ".doc", ".txt", ".md",
    ".csv", ".xlsx", ".xls",
    ".png", ".jpg", ".jpeg",
}


def file_hash(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="扫描目录建 inventory")
    parser.add_argument("--dir", required=True, help="目标目录")
    parser.add_argument("--force-rebuild", action="store_true", help="忽略已存在 inventory, 重建")
    args = parser.parse_args()

    target_dir = Path(args.dir).resolve()
    if not target_dir.exists() or not target_dir.is_dir():
        print(json.dumps({"ok": False, "errors": [f"目录不存在: {target_dir}"]}, ensure_ascii=False))
        sys.exit(1)

    inv_dir = target_dir / ".data-skill"
    inv_path = inv_dir / "inventory.json"

    if inv_path.exists() and not args.force_rebuild:
        with open(inv_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        print(json.dumps({
            "ok": True,
            "reused": True,
            "inventory_path": str(inv_path),
            "pending": sum(1 for x in existing["items"] if x["status"] == "pending"),
            "done": sum(1 for x in existing["items"] if x["status"] == "done"),
            "total": len(existing["items"]),
        }, ensure_ascii=False, indent=2))
        return

    items = []
    for root, _, files in os.walk(target_dir):
        if ".data-skill" in Path(root).parts:
            continue
        for name in files:
            p = Path(root) / name
            if p.suffix.lower() in SUPPORTED_EXTS:
                items.append({
                    "file": str(p.relative_to(target_dir)),
                    "absolute": str(p),
                    "size": p.stat().st_size,
                    "md5": file_hash(p),
                    "status": "pending",
                    "matched_table": None,
                    "primary_key": None,
                    "errors": [],
                    "retry": 0,
                })

    inv_dir.mkdir(parents=True, exist_ok=True)
    inventory = {
        "version": 1,
        "target_dir": str(target_dir),
        "created_at": __import__("datetime").datetime.now().isoformat(),
        "items": items,
    }
    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "ok": True,
        "reused": False,
        "inventory_path": str(inv_path),
        "total": len(items),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
