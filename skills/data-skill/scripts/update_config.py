#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
update_config.py

修改 ~/.data-skill/config.yml 中的某个 key。
LLM 从用户自然语言中抽取 (key, value), 调用本脚本落盘。

支持的 key:
  - file_parser_server_url
  - file_parser_api_url
  - db_path
  - parser_output_format
  - parser_lang_list
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

ALLOWED_KEYS = {
    "file_parser_server_url",
    "file_parser_api_url",
    "db_path",
    "parser_output_format",
    "parser_lang_list",
}


def main():
    parser = argparse.ArgumentParser(description="修改 ~/.data-skill/config.yml")
    parser.add_argument("--key", required=True, help=f"配置 key, 允许: {sorted(ALLOWED_KEYS)}")
    parser.add_argument("--value", required=True, help="新值")
    args = parser.parse_args()

    if args.key not in ALLOWED_KEYS:
        print(json.dumps({"ok": False, "errors": [f"不支持的 key: {args.key}, 允许: {sorted(ALLOWED_KEYS)}"]}, ensure_ascii=False))
        sys.exit(1)

    cfg_path = Path.home() / ".data-skill" / "config.yml"
    if not cfg_path.exists():
        print(json.dumps({"ok": False, "errors": [f"config.yml 不存在: {cfg_path}"]}, ensure_ascii=False))
        sys.exit(1)

    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    old = cfg.get(args.key)
    cfg[args.key] = args.value

    with open(cfg_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)

    print(json.dumps({
        "ok": True,
        "key": args.key,
        "old": old,
        "new": args.value,
        "config_path": str(cfg_path),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
