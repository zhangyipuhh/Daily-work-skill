#!/usr/bin/python
# -*- coding:utf-8 -*-
r"""
read_doc.py

WHY NOT `from DocumentLoader import ...` IN YOUR OWN SCRIPT?
============================================================
常见反模式：嫌 PowerShell 引号转义麻烦 → 写临时 .py → from DocumentLoader import ...
本 SKILL 反模式红线段明令禁止（见 ../SKILL.md §反模式红线）。

正确做法（任选其一）：
  1. 直接调本 CLI：
     python scripts/read_doc.py --file <path> [--sheet ...] [--keyword ...] [--max-rows N]
  2. 路径长/转义麻烦 → 用 dump_paths.py 生成 PowerShell 变量：
     . (python scripts/dump_paths.py --project-root "<项目根>" --format ps1)
     python scripts/read_doc.py --file $PLANNING_SHEET_LATEST --output json
  3. 输出乱码 → 写到文件：
     python scripts/read_doc.py --file ... --output json --output-file D:\out.json
  4. 想用 Select-Object 截断 → 用 --max-rows：
     python scripts/read_doc.py --file ... --max-rows 20
  5. 想用 Where-Object 过滤 → 用 --keyword：
     python scripts/read_doc.py --file ... --keyword 张三

退出码：0 成功 / 1 文件不存在 / 2 不支持的扩展名 / 3 加载异常 / 4 无匹配结果

------------------------------------------------------------
万能文件读取 CLI：自动按扩展名分发到 DocumentLoader 下的 8 个 Loader。
支持：xlsx / xlsm / docx / doc / pdf / txt / md / csv / json / eml

Date: 2026-06-11
Author: project-doc-query skill
"""

import sys
from pathlib import Path

# 绕开 Windows PowerShell 5.1 GBK 默认编码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

_SKILL_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SKILL_SCRIPTS))

import argparse
import json
from typing import Any, Dict, List, Optional

from DocumentLoader import DocumentLoader, LOADER_MAPPING, LOADER_DEFAULT_KWARGS  # noqa: E402


EXT_FORMAT_PARAM: Dict[str, Dict[str, str]] = {
    ".xlsx": {"sheet": "--sheet", "kw": "--keyword", "row": "--row-range", "hidden": "--include-hidden"},
    ".xlsm": {"sheet": "--sheet", "kw": "--keyword", "row": "--row-range", "hidden": "--include-hidden"},
    ".docx": {"kw": "--keyword"},
    ".doc": {"kw": "--keyword"},
    ".pdf": {"kw": "--keyword"},
    ".txt": {"enc": "--encoding", "kw": "--keyword"},
    ".md": {"kw": "--keyword"},
    ".markdown": {"kw": "--keyword"},
    ".csv": {"enc": "--encoding", "kw": "--keyword"},
    ".json": {"jq": "--jq-schema", "kw": "--keyword"},
    ".eml": {"enc": "--prefer-encoding", "kw": "--keyword"},
}


def build_kwargs(args: argparse.Namespace, ext: str) -> Dict[str, Any]:
    """根据文件扩展名，从 CLI 参数构造 Loader 入参。"""
    ext = ext.lower()
    kwargs: Dict[str, Any] = dict(LOADER_DEFAULT_KWARGS.get(ext, {}))

    if ext in (".xlsx", ".xlsm"):
        if getattr(args, "sheet", None):
            kwargs["sheet_name"] = args.sheet
        if getattr(args, "row_range", None):
            kwargs["row_range"] = args.row_range
        if getattr(args, "include_hidden", False):
            kwargs["include_hidden"] = True
    elif ext == ".json":
        if getattr(args, "jq_schema", None):
            kwargs["jq_schema"] = args.jq_schema
        if getattr(args, "text_content", False):
            kwargs["text_content"] = True
    elif ext in (".txt", ".csv"):
        if getattr(args, "encoding", None):
            kwargs["encoding"] = args.encoding
    elif ext == ".eml":
        if getattr(args, "prefer_encoding", None):
            kwargs["prefer_encoding"] = args.prefer_encoding

    if getattr(args, "keyword", None):
        kwargs["keyword"] = args.keyword

    return kwargs


def render_text(docs: List[Any], max_rows: int, keyword: Optional[str]) -> str:
    out: List[str] = []
    for i, doc in enumerate(docs[:max_rows] if max_rows > 0 else docs):
        meta = getattr(doc, "metadata", {}) or {}
        head = f"--- 片段 {i + 1} ---"
        meta_str = " | ".join(f"{k}={v}" for k, v in meta.items() if k not in ("source", "file_type", "loader_used"))
        if meta_str:
            head += f"  [{meta_str}]"
        out.append(head)
        out.append(getattr(doc, "page_content", "") or "")
        out.append("")
    return "\n".join(out)


def render_table(docs: List[Any], max_rows: int) -> str:
    """仅对 Excel 风格的 \\t 分隔文本友好：第一行作表头，其余作数据行。"""
    if not docs:
        return "(无数据)"
    parts: List[str] = []
    for i, doc in enumerate(docs[:max_rows] if max_rows > 0 else docs):
        meta = getattr(doc, "metadata", {}) or {}
        sheet = meta.get("sheet_name", f"片段{i + 1}")
        parts.append(f"## {sheet}")
        content = getattr(doc, "page_content", "") or ""
        lines = [ln for ln in content.split("\n") if ln and not ln.startswith("## ") and not ln.startswith("维度:")]
        if not lines:
            parts.append("(空)")
            parts.append("")
            continue
        header = lines[0].split("\t")
        parts.append("| " + " | ".join(header) + " |")
        parts.append("|" + "|".join(["---"] * len(header)) + "|")
        for row in lines[1:]:
            cells = row.split("\t")
            parts.append("| " + " | ".join(cells) + " |")
        parts.append("")
    return "\n".join(parts)


def render_json(docs: List[Any], max_rows: int) -> str:
    payload = []
    for i, doc in enumerate(docs[:max_rows] if max_rows > 0 else docs):
        meta = getattr(doc, "metadata", {}) or {}
        payload.append({
            "index": i + 1,
            "page_content": getattr(doc, "page_content", ""),
            "metadata": meta,
        })
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="万能文件读取 CLI（按扩展名自动分发到 DocumentLoader 下的 Loader）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python read_doc.py --file plan.xlsm --sheet 评审计划 --output table\n"
            "  python read_doc.py --file plan.xlsm --keyword 张三 --output json\n"
            "  python read_doc.py --file report.docx --max-rows 50\n"
            "  python read_doc.py --file mail.eml --output text\n"
        ),
    )
    parser.add_argument("--file", required=True, help="文件绝对路径")
    parser.add_argument("--output", choices=["text", "json", "table"], default="text",
                        help="输出格式：text(默认) / json / table(仅 Excel/CSV 风格数据友好)")
    parser.add_argument("--output-file", default=None, help="写入文件路径（绕开 Windows 控制台编码）")
    parser.add_argument("--max-rows", type=int, default=50, help="最大输出片段数（0=不限）")

    parser.add_argument("--sheet", default=None, help="[Excel] sheet 名（模糊匹配）")
    parser.add_argument("--row-range", default=None, help="[Excel] 行范围，如 5-20")
    parser.add_argument("--include-hidden", action="store_true", help="[Excel] 包含隐藏 sheet")

    parser.add_argument("--jq-schema", default=None, help="[JSON] jq schema 路径，如 .data.items")
    parser.add_argument("--text-content", action="store_true", help="[JSON] 把值当纯文本")

    parser.add_argument("--encoding", default=None, help="[TXT/CSV] 文本编码（默认自动检测）")
    parser.add_argument("--prefer-encoding", default=None, help="[EML] 优先编码，默认 utf-8")

    parser.add_argument("--keyword", default=None, help="对所有 Loader 的 page_content 做 substring 过滤")

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"[ERR] 文件不存在: {file_path}", file=sys.stderr)
        return 1

    ext = file_path.suffix.lower()
    if ext not in LOADER_MAPPING:
        print(f"[ERR] 不支持的扩展名: {ext}。支持: {sorted(LOADER_MAPPING.keys())}", file=sys.stderr)
        return 2

    try:
        kwargs = build_kwargs(args, ext)
        loader = DocumentLoader(file_path, custom_kwargs={ext: kwargs})
        docs = loader.load()
    except Exception as e:
        print(f"[ERR] 加载失败: {e}", file=sys.stderr)
        return 3

    if not docs:
        print(f"[WARN] 无匹配结果。扩展名={ext}，kwargs={ {k: v for k, v in kwargs.items() if k != 'keyword'} }", file=sys.stderr)
        return 4

    if args.output == "json":
        output_text = render_json(docs, args.max_rows)
    elif args.output == "table":
        output_text = render_table(docs, args.max_rows)
    else:
        output_text = render_text(docs, args.max_rows, args.keyword)

    if args.output_file:
        out_path = Path(args.output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_text, encoding="utf-8")
        print(f"[OK] 已写入 {len(docs)} 片段 → {out_path}")
    else:
        print(output_text, flush=True)
        print(f"\n[OK] 共 {len(docs)} 片段（{ext}）", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
