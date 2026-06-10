#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
init_config.py

首跑配置脚本。SKILL.md 在检测到 ~/.data-skill/config.yml 不存在时,
通过 AskUserQuestion 走人机回路收集配置, 然后调用本脚本写入 yml。

调用方式:
  python init_config.py --values '{"file_parser_server_url":"...","file_parser_api_url":"...",...}'

本脚本是"确定的事脚本做"的体现 - 语义抽取由 LLM 完成, 落盘由本脚本完成。
"""
import argparse
import json
import os
import sys
from pathlib import Path

import yaml


def default_config() -> dict:
    return {
        "file_parser_server_url": "http://Host.docker.internal:30000",
        "file_parser_api_url": "http://localhost:8000/file_parse",
        "db_path": str(Path.home() / ".data-skill" / "data.db"),
        "parser_output_format": "json",
        "parser_lang_list": "ch",
    }


def merge_with_defaults(user_values: dict) -> dict:
    cfg = default_config()
    for k, v in (user_values or {}).items():
        if v is None or (isinstance(v, str) and v.strip() == ""):
            continue
        cfg[k] = v
    return cfg


def main():
    parser = argparse.ArgumentParser(description="初始化 ~/.data-skill/config.yml")
    parser.add_argument(
        "--values",
        required=True,
        help='JSON 字符串, 含 file_parser_server_url/file_parser_api_url/db_path/parser_output_format/parser_lang_list',
    )
    args = parser.parse_args()

    try:
        user_values = json.loads(args.values)
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "errors": [f"--values 解析失败: {e}"]}, ensure_ascii=False))
        sys.exit(1)

    cfg = merge_with_defaults(user_values)

    target_dir = Path.home() / ".data-skill"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / "config.yml"

    if target_path.exists():
        backup = target_dir / f"config.yml.bak.{os.getpid()}"
        target_path.replace(backup)
        print(f"[备份] 旧配置 -> {backup}", file=sys.stderr)

    with open(target_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)

    print(json.dumps({
        "ok": True,
        "config_path": str(target_path),
        "config": cfg,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
