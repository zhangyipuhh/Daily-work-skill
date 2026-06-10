#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
extract_docx_outline.py

从 docx 中抽取章节标题（Heading 1/2/3）作为格式范本。

Usage:
    python extract_docx_outline.py --docx <path> --output <md_path>
"""

import argparse
import sys
from pathlib import Path

# 引入同 skill 内的 DocumentLoader + ExcelLoader（独立自包含）
# 本脚本位于 scripts/ 下，DocumentLoader.py 与 loader/ 是其同级（parents[0]）
_SKILL_SCRIPTS = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(_SKILL_SCRIPTS))

from DocumentLoader import DocumentLoader  # noqa: E402  同 skill 的统一入口
from loader.ExcelLoader import ExcelLoader  # noqa: E402


def extract_headings_from_docx(docx_path: Path) -> str:
    """
    直接用 python-docx 抽取标题（不依赖 langchain DocumentLoader，
    以保证 heading 层级信息被保留）。
    """
    try:
        from docx import Document
    except ImportError:
        raise SystemExit("缺少依赖 python-docx，请先安装：pip install python-docx")

    if not docx_path.exists():
        raise FileNotFoundError(f"文件不存在: {docx_path}")

    doc = Document(str(docx_path))
    lines = [f"# 格式范本：{docx_path.stem}", ""]

    for p in doc.paragraphs:
        style = (p.style.name or "").strip() if p.style else ""
        text = p.text.strip()
        if not text:
            continue
        if style in ("Title",):
            lines.append(f"# {text}")
        elif style == "Heading 1":
            lines.append(f"## {text}")
        elif style == "Heading 2":
            lines.append(f"### {text}")
        elif style == "Heading 3":
            lines.append(f"#### {text}")
        elif style == "Heading 4":
            lines.append(f"##### {text}")
        # 其他普通段落跳过（不抽取正文）

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="从 docx 抽取章节作为格式范本")
    parser.add_argument("--docx", required=True, help="docx 文件路径")
    parser.add_argument("--output", required=True, help="输出 markdown 路径")
    args = parser.parse_args()

    docx_path = Path(args.docx)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        content = extract_headings_from_docx(docx_path)
        output_path.write_text(content, encoding="utf-8")
        print(f"✅ 已抽取格式范本 → {output_path}")
        print(f"   章节行数: {content.count(chr(10) + '#') + 1 if content.startswith('#') else 0}")
        return 0
    except Exception as e:
        print(f"❌ 抽取失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
