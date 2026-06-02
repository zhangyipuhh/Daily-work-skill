#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_report.py - 最终 DOCX 报告生成脚本

读取：
  - 当前周的 review_results.json
  - 当前周的 文档审查结果_*.xlsx
  - 趋势分析_*.md
  - 漏检名单 JSON（可选）

输出：AI 辅助编程报告_<week>.docx

章节：
  1. 概述
  2. 汇总统计
  3. 评审结果汇总（Top/Bottom 开发者）
  4. 改进建议汇总
  5. 不足与改进建议
  6. 本周未提交者（漏检名单）
  7. 全量比对所有历史周（最后一章）

依赖：openpyxl, python-docx
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

try:
    from openpyxl import load_workbook
except ImportError:
    print("[ERROR] 缺少 openpyxl，请先 pip install openpyxl", file=sys.stderr)
    sys.exit(1)

try:
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("[ERROR] 缺少 python-docx，请先 pip install python-docx", file=sys.stderr)
    sys.exit(1)


BLACK = RGBColor(0, 0, 0)
HEADER_FILL = "4472C4"
ALT_FILL = "F2F2F2"


def set_cell_text(cell, text, *, bold=False, color=BLACK, size=10):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(str(text) if text is not None else "")
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.bold = bold
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:eastAsia"), "微软雅黑")
    rFonts.set(qn("w:ascii"), "Arial")
    rFonts.set(qn("w:hAnsi"), "Arial")
    return cell


def set_cell_shading(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill_hex)
    tcPr.append(shd)


def add_heading(doc, text, level=1):
    h = doc.add_heading("", level=level)
    run = h.add_run(text)
    run.font.color.rgb = BLACK
    run.font.name = "Arial"
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:eastAsia"), "微软雅黑")
    rFonts.set(qn("w:ascii"), "Arial")
    rFonts.set(qn("w:hAnsi"), "Arial")
    rPr.append(rFonts)
    if level == 1:
        run.font.size = Pt(18)
    elif level == 2:
        run.font.size = Pt(14)
    else:
        run.font.size = Pt(12)
    run.bold = True
    return h


def add_paragraph(doc, text, *, bold=False, size=11):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.color.rgb = BLACK
    run.bold = bold
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:eastAsia"), "微软雅黑")
    rFonts.set(qn("w:ascii"), "Arial")
    rFonts.set(qn("w:hAnsi"), "Arial")
    rPr.append(rFonts)
    return p


def add_table(doc, headers: list[str], rows: list[list], *, header_fill=HEADER_FILL):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.autofit = True
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        set_cell_text(cell, h, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        set_cell_shading(cell, header_fill)
    for r_idx, row in enumerate(rows, 1):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx].cells[c_idx]
            set_cell_text(cell, val if val is not None else "—")
            if r_idx % 2 == 0:
                set_cell_shading(cell, ALT_FILL)
    return table


def safe_get(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_excel_rows(path: Path) -> tuple[list[str], list[list]]:
    if not path.exists():
        return [], []
    wb = load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return [], []
    headers = [str(c) if c is not None else "" for c in rows[0]]
    data = []
    for r in rows[1:]:
        data.append([("" if v is None else v) for v in r])
    return headers, data


def collect_overview(json_path: Path, week_label: str) -> dict:
    data = load_json(json_path)
    developers = []
    for item in data:
        if not isinstance(item, dict):
            continue
        d = item.get("data", {})
        if not isinstance(d, dict):
            continue
        developers.append(d)
    return {"week": week_label, "count": len(developers), "developers": developers}


def chapter_summary(doc, overview: dict, json_path: Path):
    add_heading(doc, "第一章 概述", level=1)
    add_paragraph(doc, f"本报告基于周次 {overview['week']} 的 AI 辅助编程提交材料评审。")
    add_paragraph(doc, f"评审覆盖开发者 {overview['count']} 人，数据源: {json_path.name}。")
    add_paragraph(doc, "评审聚焦于：文档质量、文档与代码/任务的一致性、AI 编程采纳率、反模式检测。")


def chapter_stats(doc, overview: dict):
    devs = overview["developers"]
    add_heading(doc, "第二章 汇总统计", level=1)
    overall = [safe_get(d, "overall_score") for d in devs if isinstance(safe_get(d, "overall_score"), (int, float))]
    docq = [safe_get(d, "document_quality", "overall_score") for d in devs if isinstance(safe_get(d, "document_quality", "overall_score"), (int, float))]
    aiad = [safe_get(d, "ai_adoption_rate", "adoption_rate") for d in devs if isinstance(safe_get(d, "ai_adoption_rate", "adoption_rate"), (int, float))]
    consis = [safe_get(d, "ai_adoption_rate", "doc_code_consistency", "consistency_score") for d in devs if isinstance(safe_get(d, "ai_adoption_rate", "doc_code_consistency", "consistency_score"), (int, float))]
    anti = [safe_get(d, "anti_patterns", "has_issues") for d in devs]

    def avg(vs):
        return sum(vs) / len(vs) if vs else 0

    def pct(n, t):
        return f"{(n / t * 100):.1f}%" if t else "0.0%"

    valid = len(overall)
    no_score = len(devs) - valid
    anti_count = sum(1 for x in anti if x is True)

    rows = [
        ["评审覆盖开发者", f"{len(devs)} 人"],
        ["有效评分人数", f"{valid} 人"],
        ["无评分/数据不足", f"{no_score} 人 ({pct(no_score, len(devs))})"],
        ["平均综合评分", f"{avg(overall):.2f}"],
        ["平均文档质量", f"{avg(docq):.2f}"],
        ["平均 AI 采纳率", f"{avg(aiad):.2%}" if aiad else "—"],
        ["平均文档代码一致性", f"{avg(consis):.2%}" if consis else "—"],
        ["反模式命中人数", f"{anti_count} 人"],
    ]
    add_table(doc, ["指标", "数值"], rows)


def chapter_top_bottom(doc, overview: dict, excel_headers: list[str], excel_rows: list[list]):
    add_heading(doc, "第三章 评审结果汇总", level=1)
    devs = overview["developers"]
    scored = [
        (safe_get(d, "name", default="未知"), safe_get(d, "overall_score"))
        for d in devs
        if isinstance(safe_get(d, "overall_score"), (int, float))
    ]
    scored.sort(key=lambda x: x[1] if x[1] is not None else -1, reverse=True)

    add_paragraph(doc, "### Top 10 高分开发者", bold=True, size=12)
    if scored:
        rows = [[n, f"{s:.2f}"] for n, s in scored[:10]]
        add_table(doc, ["开发者", "综合评分"], rows)
    else:
        add_paragraph(doc, "本周无有效评分数据。")

    if len(scored) > 10:
        add_paragraph(doc, "### Bottom 5 低分开发者", bold=True, size=12)
        rows = [[n, f"{s:.2f}"] for n, s in scored[-5:]]
        add_table(doc, ["开发者", "综合评分"], rows)

    if excel_headers and excel_rows:
        name_col = None
        for i, h in enumerate(excel_headers):
            if "开发者" in h or "name" in h.lower():
                name_col = i
                break
        score_col = None
        for i, h in enumerate(excel_headers):
            if "综合评分" in h:
                score_col = i
                break
        if name_col is not None and score_col is not None:
            add_paragraph(doc, "### Excel 数据样本（前 5 条）", bold=True, size=12)
            sample = []
            for r in excel_rows[:5]:
                if len(r) > max(name_col, score_col):
                    sample.append([str(r[name_col]), str(r[score_col])])
            if sample:
                add_table(doc, ["开发者", "综合评分"], sample)


def chapter_improvements(doc, overview: dict):
    add_heading(doc, "第四章 改进建议汇总", level=1)
    devs = overview["developers"]
    buckets = {
        "文档结构优化": [],
        "内容完整性补充": [],
        "反模式纠正": [],
        "AI 采纳率优化": [],
        "AI 使用优化": [],
    }
    keys_map = {
        "文档结构优化": "document_structure",
        "内容完整性补充": "content_completeness",
        "反模式纠正": "anti_pattern_correction",
        "AI 采纳率优化": "ai_adoption_optimization",
        "AI 使用优化": "ai_usage_optimization",
    }
    for d in devs:
        sug = safe_get(d, "improvement_suggestions", default={}) or {}
        for label, key in keys_map.items():
            items = sug.get(key) or []
            if isinstance(items, list):
                for it in items:
                    if it and str(it).strip():
                        buckets[label].append(str(it).strip())
            elif items:
                buckets[label].append(str(items))

    for label, items in buckets.items():
        if not items:
            continue
        counter = Counter(items)
        top = counter.most_common(8)
        add_paragraph(doc, f"### {label}", bold=True, size=12)
        rows = [[s, str(c)] for s, c in top]
        add_table(doc, ["建议", "出现次数"], rows)


def chapter_gaps(doc, overview: dict):
    add_heading(doc, "第五章 不足与改进建议", level=1)
    devs = overview["developers"]
    no_data = [safe_get(d, "name", default="未知") for d in devs if not safe_get(d, "overall_score")]
    no_doc = [safe_get(d, "name", default="未知") for d in devs if safe_get(d, "ai_adoption_rate", "data_combination_type") == "code_only"]
    no_code = [safe_get(d, "name", default="未知") for d in devs if safe_get(d, "ai_adoption_rate", "data_combination_type") == "doc_only"]
    anti = [
        safe_get(d, "name", default="未知")
        for d in devs
        if safe_get(d, "anti_patterns", "has_issues") is True
    ]

    add_paragraph(doc, "### 当前不足", bold=True, size=12)
    rows = [
        ["数据缺失（无评分）", f"{len(no_data)} 人", ", ".join(no_data[:10]) + ("..." if len(no_data) > 10 else "")],
        ["缺文档（仅有代码）", f"{len(no_doc)} 人", ", ".join(no_doc[:10]) or "—"],
        ["缺代码（仅有文档）", f"{len(no_code)} 人", ", ".join(no_code[:10]) or "—"],
        ["反模式命中", f"{len(anti)} 人", ", ".join(anti[:10]) or "—"],
    ]
    add_table(doc, ["问题类型", "人数", "涉及人员（部分）"], rows)

    add_paragraph(doc, "### 改进建议", bold=True, size=12)
    add_paragraph(doc, "1. 提交时确保文档与代码同步，覆盖需求/设计/实现/问题/总结五要素。")
    add_paragraph(doc, "2. 避免单一函数反复提交；每次提交应有实质性改进。")
    add_paragraph(doc, "3. 充分利用 AI 辅助，但需人工审核、整合 AI 输出。")
    add_paragraph(doc, "4. 文档应真实反映开发过程，杜绝事后补写。")
    add_paragraph(doc, "5. 提高文档代码一致性，文档描述与代码实现保持一致。")


def chapter_missing(doc, missing: list[str], total_members: int, reviewed_count: int):
    add_heading(doc, "第六章 本周未提交者", level=1)
    add_paragraph(
        doc,
        f"应到 {total_members} 人，已评审 {reviewed_count} 人，未提交 {len(missing)} 人。",
    )
    if missing:
        rows = [[i + 1, name] for i, name in enumerate(missing)]
        add_table(doc, ["序号", "姓名"], rows)
    else:
        add_paragraph(doc, "本周无漏检，全员提交。")


def chapter_full_compare(doc, trend_md: Path | None):
    add_heading(doc, "第七章 全量比对所有历史周", level=1)
    add_paragraph(
        doc,
        "本章将本周数据与所有历史周数据进行全量对比，展示整体趋势与个体变化。",
    )
    if not trend_md or not trend_md.exists():
        add_paragraph(doc, "无趋势分析文件，跳过表格渲染。")
        return
    text = trend_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("## "):
            heading_text = ln.lstrip("# ").strip()
            level = 2
            if heading_text.startswith("1.") or heading_text.startswith("2."):
                level = 2
            add_heading(doc, heading_text, level=level)
            i += 1
            continue
        if ln.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|") and set(lines[i + 1].replace("|", "").strip()) <= {"-", " "}:
            header = [c.strip() for c in ln.strip("|").split("|")]
            i += 2
            data_rows = []
            while i < len(lines) and lines[i].startswith("|"):
                row = [c.strip() for c in lines[i].strip("|").split("|")]
                data_rows.append(row)
                i += 1
            if data_rows:
                add_table(doc, header, data_rows)
            continue
        if ln.startswith(">"):
            add_paragraph(doc, ln.lstrip("> ").strip())
        elif ln.strip().startswith("- "):
            add_paragraph(doc, "• " + ln.strip()[2:])
        elif ln.strip():
            add_paragraph(doc, ln.strip())
        i += 1


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 AI 辅助编程周报 DOCX")
    parser.add_argument("--json", required=True, help="review_results_*.json 路径")
    parser.add_argument("--excel", required=True, help="文档审查结果_*.xlsx 路径")
    parser.add_argument("--trend-md", default=None, help="趋势分析_*.md 路径")
    parser.add_argument("--missing-json", default=None, help="漏检结果 JSON 路径")
    parser.add_argument("--output", required=True, help="输出 docx 路径")
    parser.add_argument("--week", required=True, help="周次标签，如 0525-0531")
    args = parser.parse_args()

    json_path = Path(args.json)
    excel_path = Path(args.excel)
    trend_md = Path(args.trend_md) if args.trend_md else None
    missing_json = Path(args.missing_json) if args.missing_json else None
    output_path = Path(args.output)
    week = args.week

    overview = collect_overview(json_path, week)
    excel_headers, excel_rows = load_excel_rows(excel_path)

    missing = []
    total_members = 0
    reviewed_count = overview["count"]
    if missing_json and missing_json.exists():
        m = load_json(missing_json)
        missing = m.get("missing", [])
        total_members = m.get("total_members", 0)
        reviewed_count = m.get("reviewed_count", reviewed_count)

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Arial"
    style.font.size = Pt(11)
    style.font.color.rgb = BLACK
    rPr = style.element.get_or_add_rPr()
    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:eastAsia"), "微软雅黑")
    rFonts.set(qn("w:ascii"), "Arial")
    rFonts.set(qn("w:hAnsi"), "Arial")
    rPr.append(rFonts)

    title = doc.add_heading("", level=0)
    tr = title.add_run(f"AI 辅助编程评审报告（{week}）")
    tr.font.color.rgb = BLACK
    tr.font.name = "Arial"
    tr.font.size = Pt(22)
    tr.bold = True
    add_paragraph(doc, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", size=10)

    chapter_summary(doc, overview, json_path)
    chapter_stats(doc, overview)
    chapter_top_bottom(doc, overview, excel_headers, excel_rows)
    chapter_improvements(doc, overview)
    chapter_gaps(doc, overview)
    chapter_missing(doc, missing, total_members, reviewed_count)
    chapter_full_compare(doc, trend_md)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    print(f"报告已生成: {output_path}")


if __name__ == "__main__":
    main()
