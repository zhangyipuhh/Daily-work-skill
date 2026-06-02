#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
validate_review_results.py - review_results.json 格式验证脚本

按 references/review_prompt.md 中定义的 JSON 结构规范进行校验。
在所有"生成 review_results"的地方（Step 4.3 批次输出、Step 4.5 合并写盘前）调用。

Usage:
    python validate_review_results.py --input <path> [--strict] [--json]

Output:
    - 控制台：可读格式的校验报告
    - --json 时：stdout 输出 {"valid": bool, "errors": [...], "warnings": [...], "stats": {...}}
    - 返回码：0 = 全部通过，1 = 有错误，2 = 文件不存在
"""
import argparse
import json
import sys
from pathlib import Path
from collections import Counter


REQUIRED_DATA_FIELDS = [
    "name",
    "overall_score",
    "document_quality",
    "ai_adoption_rate",
    "anti_patterns",
    "improvement_suggestions",
]

REQUIRED_DOC_QUALITY_FIELDS = [
    "overall_score",
    "completeness",
    "clarity",
    "technical_accuracy",
    "ai_assistance_traces",
]

REQUIRED_AI_ADOPTION_FIELDS = [
    "adoption_rate",
    "data_combination_type",
    "doc_code_consistency",
    "ai_assistance_quality",
    "workflow_compliance",
]

REQUIRED_ANTI_PATTERNS_FIELDS = [
    "has_issues",
]

REQUIRED_IMPROVEMENT_FIELDS = [
    "document_structure",
    "content_completeness",
    "anti_pattern_correction",
    "ai_adoption_optimization",
    "ai_usage_optimization",
    "priority",
]


def err(errors: list, idx: int | str, msg: str) -> None:
    errors.append({"index": idx, "message": msg})


def warn(warnings: list, idx: int | str, msg: str) -> None:
    warnings.append({"index": idx, "message": msg})


def is_dict(v) -> bool:
    return isinstance(v, dict)


def is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def is_str(v) -> bool:
    return isinstance(v, str) and bool(v.strip())


def is_list(v) -> bool:
    return isinstance(v, list)


def is_bool(v) -> bool:
    return isinstance(v, bool)


def validate_item(item: object, idx: int, errors: list, warnings: list, strict: bool) -> dict:
    stats = {"has_name": False, "has_score": False, "warnings": 0}

    if not is_dict(item):
        err(errors, idx, f"元素不是对象 (type: {type(item).__name__})")
        return stats

    if "data" not in item:
        err(errors, idx, "缺少 'data' 字段")
        if strict:
            return stats
        data = {}
    else:
        data = item["data"]
        if not is_dict(data):
            err(errors, idx, f"'data' 不是对象 (type: {type(data).__name__})")
            return stats

    if "name" not in data:
        err(errors, idx, "data.name 缺失")
    elif not is_str(data["name"]):
        err(errors, idx, f"data.name 不是非空字符串 (value: {data['name']!r})")
    else:
        stats["has_name"] = True

    if "overall_score" in data:
        if is_number(data["overall_score"]):
            stats["has_score"] = True
        else:
            err(errors, idx, f"overall_score 不是数字 (type: {type(data['overall_score']).__name__})")
    else:
        if strict:
            err(errors, idx, "overall_score 缺失")
        else:
            warn(warnings, idx, "overall_score 缺失（视为数据不足，但不阻塞）")

    if "document_quality" in data:
        dq = data["document_quality"]
        if not is_dict(dq):
            err(errors, idx, f"document_quality 不是对象 (type: {type(dq).__name__})")
        else:
            for f in REQUIRED_DOC_QUALITY_FIELDS:
                if f not in dq:
                    warn(warnings, idx, f"document_quality.{f} 缺失")
    else:
        err(errors, idx, "document_quality 缺失")

    if "ai_adoption_rate" in data:
        ar = data["ai_adoption_rate"]
        if not is_dict(ar):
            err(errors, idx, f"ai_adoption_rate 不是对象 (type: {type(ar).__name__})")
        else:
            for f in REQUIRED_AI_ADOPTION_FIELDS:
                if f not in ar:
                    warn(warnings, idx, f"ai_adoption_rate.{f} 缺失")
    else:
        err(errors, idx, "ai_adoption_rate 缺失")

    if "anti_patterns" in data:
        ap = data["anti_patterns"]
        if not is_dict(ap):
            err(errors, idx, f"anti_patterns 不是对象 (type: {type(ap).__name__})")
        else:
            if "has_issues" in ap and not is_bool(ap["has_issues"]):
                err(errors, idx, f"anti_patterns.has_issues 不是布尔 (type: {type(ap['has_issues']).__name__})")
    else:
        err(errors, idx, "anti_patterns 缺失")

    if "improvement_suggestions" in data:
        sug = data["improvement_suggestions"]
        if not is_dict(sug):
            err(errors, idx, f"improvement_suggestions 不是对象 (type: {type(sug).__name__})")
        else:
            for f in REQUIRED_IMPROVEMENT_FIELDS:
                if f not in sug:
                    warn(warnings, idx, f"improvement_suggestions.{f} 缺失")
                elif f != "priority" and not is_list(sug[f]):
                    warn(warnings, idx, f"improvement_suggestions.{f} 不是数组")
    else:
        err(errors, idx, "improvement_suggestions 缺失")

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="review_results.json 格式验证")
    parser.add_argument("--input", required=True, help="review_results.json 路径")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="严格模式：缺失字段视为错误（而非警告）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="以 JSON 格式输出结果",
    )
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"[ERROR] 文件不存在: {path}", file=sys.stderr)
        sys.exit(2)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 解析失败: {e}", file=sys.stderr)
        sys.exit(2)

    errors: list = []
    warnings: list = []
    stats_counter = Counter()
    total_with_name = 0
    total_with_score = 0

    if not is_list(data):
        err(errors, "TOP", f"顶层不是数组 (type: {type(data).__name__})")
    else:
        stats_counter["total"] = len(data)
        for idx, item in enumerate(data):
            item_stats = validate_item(item, idx, errors, warnings, args.strict)
            if item_stats["has_name"]:
                total_with_name += 1
            if item_stats["has_score"]:
                total_with_score += 1

    stats_counter["with_name"] = total_with_name
    stats_counter["with_score"] = total_with_score
    stats_counter["missing_name"] = stats_counter["total"] - total_with_name
    stats_counter["missing_score"] = stats_counter["total"] - total_with_score

    valid = len(errors) == 0
    result = {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "stats": dict(stats_counter),
    }

    if args.output_json:
        print("---JSON-BEGIN---")
        print(json.dumps(result, ensure_ascii=False))
        print("---JSON-END---")
    else:
        print(f"文件: {path}")
        print(f"总数: {stats_counter['total']} 条")
        print(f"有 name: {total_with_name} 条")
        print(f"有 overall_score: {total_with_score} 条")
        print(f"错误: {len(errors)} 条")
        print(f"警告: {len(warnings)} 条")
        if errors:
            print("\n[错误详情]")
            for e in errors:
                idx = e["index"]
                msg = e["message"]
                print(f"  - 第 {idx} 条: {msg}")
        if warnings:
            print("\n[警告详情]")
            for w in warnings[:20]:
                idx = w["index"]
                msg = w["message"]
                print(f"  - 第 {idx} 条: {msg}")
            if len(warnings) > 20:
                print(f"  ... 还有 {len(warnings) - 20} 条警告")
        if valid:
            print("\n[PASS] JSON 格式验证通过")
        else:
            print(f"\n[FAIL] JSON 格式验证失败（{len(errors)} 个错误）")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
