#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
parse_file.py

包装 file_parser_client.py 调用 MinerU 解析服务, 产出 json + md 双格式。
本脚本是"确定的事脚本做" - 解析流程固定, 不涉及语义判断。

输出:
  <output_dir>/<原文件名 stem>.json
  <output_dir>/<原文件名 stem>.md

调用:
  python parse_file.py --file <path> --output-dir <dir> [--format json|md|both]
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_REF = Path(r"D:\项目文档\AIAssistive\data_skill_tmp\file_parser_client.py")


def load_config() -> dict:
    cfg_path = Path.home() / ".data-skill" / "config.yml"
    if not cfg_path.exists():
        raise FileNotFoundError(f"config.yml 不存在: {cfg_path}")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def _do_parse(client, file_path: Path, output_dir: Path, api_url: str, output_format: str) -> str:
    return await asyncio.to_thread(
        client.parse,
        file_path=str(file_path),
        output_dir=str(output_dir),
        api_url=api_url,
        output_format=output_format,
    )


async def parse_one(file_path: Path, output_dir: Path, output_format: str, cfg: dict) -> dict:
    sys.path.insert(0, str(REPO_REF.parent))
    from file_parser_client import FileParserClient

    output_dir.mkdir(parents=True, exist_ok=True)
    client = FileParserClient(
        server_url=cfg["file_parser_server_url"],
        max_retries=int(cfg.get("parser_max_retries", 60)),
        poll_interval=float(cfg.get("parser_poll_interval", 2.0)),
        timeout=int(cfg.get("parser_timeout", 300)),
    )

    results = {"file": str(file_path), "outputs": {}}
    formats = ["json", "md"] if output_format == "both" else [output_format]
    for fmt in formats:
        try:
            out = await _do_parse(
                client,
                file_path,
                output_dir,
                cfg["file_parser_api_url"],
                fmt,
            )
            results["outputs"][fmt] = out
        except Exception as e:
            results["outputs"][fmt] = {"error": str(e)}
            results["error"] = str(e)
    return results


def main():
    parser = argparse.ArgumentParser(description="解析文件 -> json/md")
    parser.add_argument("--file", required=True, help="待解析文件路径")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--format", default="json", choices=["json", "md", "both"])
    args = parser.parse_args()

    file_path = Path(args.file).resolve()
    if not file_path.exists():
        print(json.dumps({"ok": False, "errors": [f"文件不存在: {file_path}"]}, ensure_ascii=False))
        sys.exit(1)

    output_dir = Path(args.output_dir).resolve()

    try:
        cfg = load_config()
    except Exception as e:
        print(json.dumps({"ok": False, "errors": [f"加载配置失败: {e}"]}, ensure_ascii=False))
        sys.exit(1)

    try:
        result = asyncio.run(parse_one(file_path, output_dir, args.format, cfg))
    except Exception as e:
        print(json.dumps({"ok": False, "errors": [f"解析失败: {e}"]}, ensure_ascii=False))
        sys.exit(1)

    has_error = any("error" in v for v in result["outputs"].values() if isinstance(v, dict))
    print(json.dumps({"ok": not has_error, **result}, ensure_ascii=False, indent=2))
    sys.exit(0 if not has_error else 1)


if __name__ == "__main__":
    main()
