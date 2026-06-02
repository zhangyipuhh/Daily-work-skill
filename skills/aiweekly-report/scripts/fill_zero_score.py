#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fill_zero_score.py - 真未提交者补 0 分脚本（V2.2）

读取 missing_<week>.json 中的 not_submitted 名单，把这些人补成 overall_score=0
的条目，写入 review_results_<week>.json。

只处理"真未提交"（情况 A），不处理"漏评审"（情况 B，漏评审由主 Agent 重派 subagent 处理）。

输出条目结构（与 review_prompt.md 的 JSON schema 保持一致）：
{
  "data": {
    "name": "<未提交者>",
    "overall_score": 0,
    "document_quality": {"overall_score": 0, ...},
    "ai_adoption_rate": {"adoption_rate": 0, "data_combination_type": "no_submission", ...},
    "anti_patterns": {"has_issues": true, ...},
    "improvement_suggestions": {"priority": "high", ...},
    "summary": "本周未提交任何评审材料",
    "review_time": "<ISO>",
    "_zero_filled": true
  }
}

Usage:
    python fill_zero_score.py \
      --reviewed "output/review_results_0525-0531.json" \
      --missing "output/missing_0525-0531.json"
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def make_zero_entry(name: str, ts: str) -> dict:
    """构造一条 0 分条目，字段对齐 review_prompt.md 的 JSON schema"""
    return {
        "data": {
            "name": name,
            "review_time": ts,
            "document_quality": {
                "overall_score": 0,
                "completeness": {
                    "score": 0,
                    "has_requirement": False,
                    "has_design": False,
                    "has_implementation": False,
                    "has_problem_solution": False,
                    "has_summary": False,
                    "analysis": "未提交任何内容",
                },
                "clarity": {"score": 0, "analysis": "未提交任何内容"},
                "technical_accuracy": {"score": 0, "analysis": "未提交任何内容"},
                "ai_assistance_traces": {
                    "estimated_ai_ratio": 0,
                    "integration_quality": "—",
                    "analysis": "未提交任何内容",
                },
            },
            "ai_adoption_rate": {
                "adoption_rate": 0,
                "data_combination_type": "no_submission",
                "doc_code_consistency": {
                    "consistency_score": 0,
                    "has_document": False,
                    "has_code": False,
                    "function_match": "—",
                    "logic_match": "—",
                    "interface_match": "—",
                },
                "ai_assistance_quality": {
                    "doc_ai_ratio": 0,
                    "code_ai_ratio": 0,
                    "effectiveness": "未提交内容，无 AI 辅助评估",
                },
                "workflow_compliance": {
                    "doc_first": False,
                    "sync_development": False,
                    "authentic_reflection": "未提交内容",
                },
                "analysis": "本周未提交任何材料，AI 采纳率无法评估，按 0 处理。",
            },
            "doc_task_consistency": {
                "score": 0,
                "has_task_list": False,
                "goal_alignment": "—",
                "coverage_completeness": "—",
                "scope_control": "—",
                "analysis": "未提交任何内容",
            },
            "anti_patterns": {
                "has_issues": True,
                "single_function_repeated_commits": {
                    "detected": False,
                    "analysis": "未提交内容",
                },
                "unrelated_to_ai_coding": {
                    "detected": True,
                    "indicators": ["未提交任何评审材料"],
                    "analysis": "本周未提交任何内容，按 0 分处理。",
                },
                "other_patterns": [],
                "overall_assessment": "本周未提交任何评审材料，反模式命中。",
            },
            "improvement_suggestions": {
                "document_structure": ["请提交开发过程文档（需求/设计/实现/总结）"],
                "content_completeness": ["请覆盖需求描述、设计思路、实现过程、问题解决、总结反思五要素"],
                "anti_pattern_correction": ["请先完成文档编写和代码实现，再提交评审"],
                "ai_adoption_optimization": ["请提供文档和代码以评估 AI 编程采纳率"],
                "ai_usage_optimization": ["请提供文档内容以便分析 AI 辅助痕迹"],
                "priority": "high",
            },
            "overall_score": 0,
            "summary": "本周未提交任何评审材料，按 0 分处理。",
            "coach_notes": "建议下周按时提交文档和代码，便于团队给予改进建议。",
            "_zero_filled": True,
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="真未提交者补 0 分（基于 missing.json 的 not_submitted 字段）"
    )
    parser.add_argument("--reviewed", required=True, help="review_results_<week>.json 路径")
    parser.add_argument("--missing", required=True, help="missing_<week>.json 路径")
    parser.add_argument(
        "--output",
        default=None,
        help="输出路径（默认原地覆盖 --reviewed）",
    )
    args = parser.parse_args()

    reviewed_path = Path(args.reviewed)
    missing_path = Path(args.missing)
    output_path = Path(args.output) if args.output else reviewed_path

    if not reviewed_path.exists():
        print(f"[ERROR] review_results 不存在: {reviewed_path}", file=sys.stderr)
        return 2
    if not missing_path.exists():
        print(f"[ERROR] missing.json 不存在: {missing_path}", file=sys.stderr)
        return 2

    reviewed = load_json(reviewed_path)
    if not isinstance(reviewed, list):
        print(f"[ERROR] review_results 根节点必须是数组", file=sys.stderr)
        return 2

    missing_doc = load_json(missing_path)
    not_submitted = missing_doc.get("not_submitted", [])
    if not not_submitted:
        not_submitted = missing_doc.get("missing", [])

    if not not_submitted:
        print("[OK] 无真未提交者，无需补 0 分。")
        return 0

    existing_names = set()
    for item in reviewed:
        if isinstance(item, dict):
            d = item.get("data", {})
            if isinstance(d, dict) and d.get("name"):
                existing_names.add(d["name"])

    ts = datetime.now().isoformat(timespec="seconds")
    added = 0
    skipped = 0
    for name in not_submitted:
        if name in existing_names:
            skipped += 1
            continue
        reviewed.append(make_zero_entry(name, ts))
        added += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(reviewed, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"[OK] 0 分补全完成")
    print(f"     源文件:   {reviewed_path}")
    print(f"     漏检文件: {missing_path}")
    print(f"     输出文件: {output_path}")
    print(f"     新增:     {added} 条")
    print(f"     跳过:     {skipped} 条（review_results 已有同名记录，避免覆盖）")
    print(f"     合计:     {len(reviewed)} 条评审数据")
    return 0


if __name__ == "__main__":
    sys.exit(main())
