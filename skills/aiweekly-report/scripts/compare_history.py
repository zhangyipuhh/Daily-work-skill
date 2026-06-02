#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
compare_history.py - 全量历史对比脚本

将当前周的 review_results.json 与所有历史周的 JSON 进行对比，
输出 Markdown 格式的趋势分析报告。

对比维度（按"开发者"为连接键）：
- 综合评分变化
- 文档质量评分变化
- AI 采纳率变化
- 文档代码一致性变化
- 反模式检测变化

Usage:
    python compare_history.py --current <path> --history-dir <dir> --output <path>
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def safe_get(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def load_week_data(path: Path) -> dict[str, dict]:
    if not path.exists():
        print(f"[ERROR] 文件不存在: {path}", file=sys.stderr)
        sys.exit(2)
    data = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for item in data:
        if not isinstance(item, dict):
            continue
        d = item.get("data", {})
        if not isinstance(d, dict):
            continue
        name = d.get("name")
        if name:
            out[name] = d
    return out


def extract_metrics(d: dict) -> dict:
    return {
        "overall_score": safe_get(d, "overall_score"),
        "doc_quality": safe_get(d, "document_quality", "overall_score"),
        "doc_completeness": safe_get(d, "document_quality", "completeness", "score"),
        "doc_clarity": safe_get(d, "document_quality", "clarity", "score"),
        "doc_technical": safe_get(d, "document_quality", "technical_accuracy", "score"),
        "ai_adoption": safe_get(d, "ai_adoption_rate", "adoption_rate"),
        "doc_code_consistency": safe_get(
            d, "ai_adoption_rate", "doc_code_consistency", "consistency_score"
        ),
        "doc_task_consistency": safe_get(d, "doc_task_consistency", "score"),
        "has_anti_patterns": safe_get(d, "anti_patterns", "has_issues"),
    }


def fmt(v):
    if v is None or v == "":
        return "—"
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


def diff_value(prev, cur):
    if prev is None or cur is None:
        return ""
    try:
        delta = float(cur) - float(prev)
        sign = "+" if delta > 0 else ""
        return f"({sign}{delta:.2f})"
    except (TypeError, ValueError):
        return ""


def trend_label(prev, cur):
    if prev is None or cur is None:
        return "—"
    try:
        delta = float(cur) - float(prev)
        if delta > 0.3:
            return "📈 进步"
        if delta < -0.3:
            return "📉 退步"
        return "➡️ 持平"
    except (TypeError, ValueError):
        return "—"


def collect_history_files(history_dir: Path, current: Path) -> list[Path]:
    if not history_dir.exists():
        return []
    files = []
    for p in history_dir.glob("review_results_*.json"):
        if p.resolve() != current.resolve():
            files.append(p)
    return sorted(files)


def build_per_developer_trend(current: dict, history_weeks: list[tuple[str, dict]]) -> dict:
    rows = []
    for name, cur_data in current.items():
        cur_metrics = extract_metrics(cur_data)
        prev_weeks = []
        for week_label, week_data in history_weeks:
            if name in week_data:
                prev_weeks.append((week_label, extract_metrics(week_data[name])))
        if not prev_weeks:
            continue
        latest_week, latest_metrics = prev_weeks[-1]
        rows.append(
            {
                "name": name,
                "current": cur_metrics,
                "latest_prev_week": latest_week,
                "latest_prev": latest_metrics,
                "all_history": prev_weeks,
            }
        )
    return {"rows": rows, "total_in_current": len(current), "matched_with_history": len(rows)}


def build_overall_stats(current: dict, history_weeks: list[tuple[str, dict]]) -> dict:
    def avg(vals):
        vs = [v for v in vals if isinstance(v, (int, float))]
        return sum(vs) / len(vs) if vs else None

    cur_scores = [
        extract_metrics(d).get("overall_score")
        for d in current.values()
        if extract_metrics(d).get("overall_score") is not None
    ]
    cur_ai = [
        extract_metrics(d).get("ai_adoption")
        for d in current.values()
        if extract_metrics(d).get("ai_adoption") is not None
    ]
    cur_doc = [
        extract_metrics(d).get("doc_quality")
        for d in current.values()
        if extract_metrics(d).get("doc_quality") is not None
    ]

    stats = {
        "current": {
            "developers": len(current),
            "avg_overall": avg(cur_scores),
            "avg_ai_adoption": avg(cur_ai),
            "avg_doc_quality": avg(cur_doc),
        },
        "history_weeks": [],
    }
    for week_label, week_data in history_weeks:
        scores = [
            extract_metrics(d).get("overall_score")
            for d in week_data.values()
            if extract_metrics(d).get("overall_score") is not None
        ]
        ais = [
            extract_metrics(d).get("ai_adoption")
            for d in week_data.values()
            if extract_metrics(d).get("ai_adoption") is not None
        ]
        docs = [
            extract_metrics(d).get("doc_quality")
            for d in week_data.values()
            if extract_metrics(d).get("doc_quality") is not None
        ]
        stats["history_weeks"].append(
            {
                "week": week_label,
                "developers": len(week_data),
                "avg_overall": avg(scores),
                "avg_ai_adoption": avg(ais),
                "avg_doc_quality": avg(docs),
            }
        )
    return stats


def render_markdown(
    current_path: Path,
    current: dict,
    trend: dict,
    stats: dict,
    history_files: list[Path],
) -> str:
    lines = []
    lines.append("# AI 辅助编程周报 — 趋势分析（当前周 vs 全量历史）\n")
    lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"> 当前周文件: `{current_path.name}`  ")
    lines.append(f"> 历史周数: {len(history_files)}\n")

    lines.append("## 1. 整体指标趋势\n")
    lines.append("| 周次 | 评审人数 | 平均综合评分 | 平均 AI 采纳率 | 平均文档质量 |")
    lines.append("|------|----------|--------------|----------------|--------------|")
    for w in stats["history_weeks"]:
        lines.append(
            f"| {w['week']} | {w['developers']} | {fmt(w['avg_overall'])} | "
            f"{fmt(w['avg_ai_adoption'])} | {fmt(w['avg_doc_quality'])} |"
        )
    lines.append(
        f"| **{current_path.stem.replace('review_results_', '**📍 ')}** | "
        f"**{stats['current']['developers']}** | "
        f"**{fmt(stats['current']['avg_overall'])}** | "
        f"**{fmt(stats['current']['avg_ai_adoption'])}** | "
        f"**{fmt(stats['current']['avg_doc_quality'])}** |"
    )
    lines.append("")

    lines.append("## 2. 开发者个体变化趋势（与最近一次有数据的周对比）\n")
    if not trend["rows"]:
        lines.append("> 当前周的所有开发者都未在历史数据中找到匹配项。\n")
    else:
        lines.append(
            "| 开发者 | 维度 | 上次 | 本次 | 变化 | 趋势 |\n"
            "|--------|------|------|------|------|------|"
        )
        for row in trend["rows"]:
            name = row["name"]
            cur = row["current"]
            prev = row["latest_prev"]
            week = row["latest_prev_week"]
            for dim, label in [
                ("overall_score", "综合评分"),
                ("doc_quality", "文档质量"),
                ("ai_adoption", "AI 采纳率"),
                ("doc_code_consistency", "文档代码一致性"),
            ]:
                p, c = prev.get(dim), cur.get(dim)
                lines.append(
                    f"| {name} | {label} | {fmt(p)} ({week}) | {fmt(c)} | "
                    f"{diff_value(p, c)} | {trend_label(p, c)} |"
                )
        lines.append("")

    lines.append("## 3. 进步 / 退步 汇总\n")
    improved, declined, stable, new_devs = [], [], [], []
    for row in trend["rows"]:
        prev_overall = row["latest_prev"].get("overall_score")
        cur_overall = row["current"].get("overall_score")
        label = trend_label(prev_overall, cur_overall)
        if "进步" in label:
            improved.append(row["name"])
        elif "退步" in label:
            declined.append(row["name"])
        else:
            stable.append(row["name"])
    in_history = {row["name"] for row in trend["rows"]}
    for name in current.keys():
        if name not in in_history:
            new_devs.append(name)

    lines.append(f"- 📈 进步: **{len(improved)}** 人 — {', '.join(improved) if improved else '无'}")
    lines.append(f"- 📉 退步: **{len(declined)}** 人 — {', '.join(declined) if declined else '无'}")
    lines.append(f"- ➡️ 持平: **{len(stable)}** 人 — {', '.join(stable) if stable else '无'}")
    lines.append(f"- 🆕 本周新增（无历史对照）: **{len(new_devs)}** 人 — {', '.join(new_devs) if new_devs else '无'}\n")

    lines.append("## 4. 关键洞察\n")
    if stats["history_weeks"]:
        first = stats["history_weeks"][0]
        cur_avg = stats["current"]["avg_overall"]
        if cur_avg is not None and first["avg_overall"] is not None:
            delta = cur_avg - first["avg_overall"]
            sign = "+" if delta > 0 else ""
            lines.append(
                f"- 综合评分从历史最早一周（{first['week']}）的 {fmt(first['avg_overall'])} "
                f"变化到本周的 {fmt(cur_avg)}，整体{sign}{delta:.2f}。"
            )
    if improved and declined:
        lines.append(
            f"- 本周 {len(improved)} 人进步、{len(declined)} 人退步，整体呈"
            f"{'上升' if len(improved) > len(declined) else '下降'}趋势。"
        )
    if new_devs:
        lines.append(f"- 出现 {len(new_devs)} 名新成员或无历史对照人员，需建立基线。")
    if not history_files:
        lines.append("- 当前为首次运行，无历史数据可比对。")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="全量历史对比")
    parser.add_argument("--current", required=True, help="当前周 review_results_*.json 路径")
    parser.add_argument(
        "--history-dir",
        required=True,
        help="历史 review_results_*.json 所在目录",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="输出的 Markdown 文件路径",
    )
    args = parser.parse_args()

    current_path = Path(args.current)
    history_dir = Path(args.history_dir)
    output_path = Path(args.output)

    current = load_week_data(current_path)
    history_files = collect_history_files(history_dir, current_path)

    history_weeks: list[tuple[str, dict]] = []
    for f in history_files:
        label = f.stem.replace("review_results_", "")
        try:
            week_data = load_week_data(f)
            history_weeks.append((label, week_data))
        except Exception as e:
            print(f"[WARN] 跳过历史文件 {f}: {e}", file=sys.stderr)

    trend = build_per_developer_trend(current, history_weeks)
    stats = build_overall_stats(current, history_weeks)

    md = render_markdown(current_path, current, trend, stats, history_files)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding="utf-8")
    print(f"趋势分析已生成: {output_path}")
    print(
        f"统计: 当前 {stats['current']['developers']} 人, "
        f"历史 {len(history_files)} 周, "
        f"匹配 {trend['matched_with_history']} 人"
    )


if __name__ == "__main__":
    main()
