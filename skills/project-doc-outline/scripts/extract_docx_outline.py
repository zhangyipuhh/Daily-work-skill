#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
extract_docx_outline.py

从项目内 docx 抽取 Heading 1/2/3/4 标题，作为大纲格式范本。

Date: 2026-06-11
Author: project-doc-outline skill
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

_SKILL_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SKILL_SCRIPTS))

import argparse


def extract_headings_from_docx(docx_path: Path, max_depth: int = 4) -> str:
    """抽取 docx 的标题层级。max_depth: 1=仅 Heading 1, 4=Heading 1~4"""
    try:
        from docx import Document
    except ImportError:
        raise SystemExit("缺少依赖 python-docx，请先安装：pip install python-docx")

    if not docx_path.exists():
        raise FileNotFoundError(f"文件不存在: {docx_path}")

    doc = Document(str(docx_path))
    lines = [f"# 格式范本：{docx_path.stem}", ""]
    heading_map = {
        1: "Heading 1", 2: "Heading 2", 3: "Heading 3", 4: "Heading 4",
    }

    for p in doc.paragraphs:
        style = (p.style.name or "").strip() if p.style else ""
        text = p.text.strip()
        if not text:
            continue
        if style == "Title":
            lines.append(f"# {text}")
        else:
            for depth, name in heading_map.items():
                if style == name and depth <= max_depth:
                    prefix = "#" * (depth + 1)
                    lines.append(f"{prefix} {text}")
                    break
            else:
                continue

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从项目内 docx 抽取章节作为大纲格式范本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python extract_docx_outline.py --docx \"D:\\\\项目文档\\\\...\\\\实施方案.docx\" --output 范本.md\n"
            "  python extract_docx_outline.py --docx plan.docx --output out.md --max-depth 2\n"
        ),
    )
    parser.add_argument("--docx", required=True, help="docx 文件绝对路径")
    parser.add_argument("--output", required=True, help="输出 markdown 路径")
    parser.add_argument("--max-depth", type=int, default=4, choices=[1, 2, 3, 4],
                        help="Heading 截断深度（1-4，默认 4）")
    args = parser.parse_args()

    docx_path = Path(args.docx)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        content = extract_headings_from_docx(docx_path, max_depth=args.max_depth)
        output_path.write_text(content, encoding="utf-8")
        heading_count = sum(1 for ln in content.split("\n") if ln.startswith("#") and ln.strip() != f"# 格式范本：{docx_path.stem}")
        print(f"[OK] 抽取完成 → {output_path}")
        print(f"     共 {heading_count} 个标题（max-depth={args.max_depth}）")
        return 0
    except FileNotFoundError as e:
        print(f"[ERR] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERR] 抽取失败: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
