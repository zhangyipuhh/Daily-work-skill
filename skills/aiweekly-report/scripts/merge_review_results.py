#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
merge_review_results.py - 合并多个批次 review_results JSON 脚本

按 data.name 连接键合并 N 个批次 JSON 数组。
内嵌格式验证逻辑（与 validate_review_results.py 一致）。

Usage:
    python merge_review_results.py \
        --input batch_1.json --input batch_2.json ... \
        --output "D:\\项目文档\\AIAssistive\\output\\review_results_0525-0531.json" \
        [--on-duplicate last|first|fail] [--no-validate]

Output:
    - 控制台：合并统计、格式验证结果
    - 返回码：0=成功且验证通过，1=验证失败，2=文件/参数错误
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="合并多个批次 review_results JSON 数组"
    )
    parser.add_argument(
        "--input",
        action="append",
        required=True,
        help="输入 JSON 路径（可重复传多次）",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="合并后输出 JSON 路径",
    )
    parser.add_argument(
        "--on-duplicate",
        choices=["last", "first", "fail"],
        default="last",
        help="data.name 重复时如何处理（默认 last：保留最后一个）",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="跳过格式验证（默认会验证）",
    )
    return parser.parse_args()


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


def load_batch(path: Path) -> list[dict]:
    if not path.exists():
        print(f"[ERROR] 批次文件不存在: {path}", file=sys.stderr)
        sys.exit(2)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[ERROR] 批次 JSON 解析失败 {path}: {e}", file=sys.stderr)
        sys.exit(2)
    if not is_list(data):
        print(f"[ERROR] 批次不是数组 {path}", file=sys.stderr)
        sys.exit(2)
    return data


def get_name(item: dict) -> str | None:
    if not is_dict(item):
        return None
    data = item.get("data")
    if not is_dict(data):
        return None
    name = data.get("name")
    if is_str(name):
        return name
    return None


def merge_batches(
    batches: list[list[dict]],
    on_duplicate: str,
) -> tuple[list[dict], dict]:
    merged: list[dict] = []
    name_index: dict[str, int] = {}
    stats = {
        "batches_count": len(batches),
        "batches_sizes": [],
        "total_input": 0,
        "duplicates": [],
        "duplicates_action": on_duplicate,
        "merged_count": 0,
    }

    for batch_idx, batch in enumerate(batches):
        stats["batches_sizes"].append(len(batch))
        stats["total_input"] += len(batch)
        for item in batch:
            name = get_name(item)
            if name is None:
                merged.append(item)
                continue
            if name in name_index:
                stats["duplicates"].append({"name": name, "batch_index": batch_idx})
                if on_duplicate == "last":
                    merged[name_index[name]] = item
                elif on_duplicate == "first":
                    pass
                elif on_duplicate == "fail":
                    print(
                        f"[ERROR] data.name 重复: {name}（来自批次 {batch_idx}）",
                        file=sys.stderr,
                    )
                    sys.exit(2)
            else:
                name_index[name] = len(merged)
                merged.append(item)

    stats["merged_count"] = len(merged)
    stats["unique_names"] = len(name_index)
    return merged, stats


def validate_item(
    item: object, idx: int, errors: list, warnings: list
) -> dict:
    stats = {"has_name": False, "has_score": False}
    if not is_dict(item):
        err(errors, idx, f"元素不是对象 (type: {type(item).__name__})")
        return stats
    if "data" not in item:
        err(errors, idx, "缺少 'data' 字段")
        return stats
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
            err(
                errors,
                idx,
                f"overall_score 不是数字 (type: {type(data['overall_score']).__name__})",
            )
    else:
        warn(warnings, idx, "overall_score 缺失")

    if "document_quality" in data:
        dq = data["document_quality"]
        if not is_dict(dq):
            err(
                errors,
                idx,
                f"document_quality 不是对象 (type: {type(dq).__name__})",
            )
        else:
            for f in REQUIRED_DOC_QUALITY_FIELDS:
                if f not in dq:
                    warn(warnings, idx, f"document_quality.{f} 缺失")
    else:
        err(errors, idx, "document_quality 缺失")

    if "ai_adoption_rate" in data:
        ar = data["ai_adoption_rate"]
        if not is_dict(ar):
            err(
                errors,
                idx,
                f"ai_adoption_rate 不是对象 (type: {type(ar).__name__})",
            )
        else:
            for f in REQUIRED_AI_ADOPTION_FIELDS:
                if f not in ar:
                    warn(warnings, idx, f"ai_adoption_rate.{f} 缺失")
    else:
        err(errors, idx, "ai_adoption_rate 缺失")

    if "anti_patterns" in data:
        ap = data["anti_patterns"]
        if not is_dict(ap):
            err(
                errors,
                idx,
                f"anti_patterns 不是对象 (type: {type(ap).__name__})",
            )
        else:
            if "has_issues" in ap and not is_bool(ap["has_issues"]):
                err(
                    errors,
                    idx,
                    f"anti_patterns.has_issues 不是布尔 (type: {type(ap['has_issues']).__name__})",
                )
    else:
        err(errors, idx, "anti_patterns 缺失")

    if "improvement_suggestions" in data:
        sug = data["improvement_suggestions"]
        if not is_dict(sug):
            err(
                errors,
                idx,
                f"improvement_suggestions 不是对象 (type: {type(sug).__name__})",
            )
        else:
            for f in REQUIRED_IMPROVEMENT_FIELDS:
                if f not in sug:
                    warn(warnings, idx, f"improvement_suggestions.{f} 缺失")
                elif f != "priority" and not is_list(sug[f]):
                    warn(warnings, idx, f"improvement_suggestions.{f} 不是数组")
    else:
        err(errors, idx, "improvement_suggestions 缺失")

    return stats


def err(errors: list, idx, msg: str) -> None:
    errors.append({"index": idx, "message": msg})


def warn(warnings: list, idx, msg: str) -> None:
    warnings.append({"index": idx, "message": msg})


def validate_format(data: list[dict]) -> dict:
    errors: list = []
    warnings: list = []
    total_with_name = 0
    total_with_score = 0
    name_counter = Counter()

    for idx, item in enumerate(data):
        item_stats = validate_item(item, idx, errors, warnings)
        if item_stats["has_name"]:
            total_with_name += 1
        if item_stats["has_score"]:
            total_with_score += 1
        name = get_name(item)
        if name:
            name_counter[name] += 1

    duplicate_names = {n: c for n, c in name_counter.items() if c > 1}
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "total": len(data),
            "with_name": total_with_name,
            "with_score": total_with_score,
            "missing_name": len(data) - total_with_name,
            "missing_score": len(data) - total_with_score,
            "duplicate_names": duplicate_names,
        },
    }


def main() -> None:
    args = parse_args()

    batches: list[list[dict]] = []
    for path_str in args.input:
        path = Path(path_str)
        batch = load_batch(path)
        batches.append(batch)

    merged, merge_stats = merge_batches(batches, args.on_duplicate)

    print(f"合并 {merge_stats['batches_count']} 批：")
    for i, size in enumerate(merge_stats["batches_sizes"]):
        print(f"  批次 {i + 1}: {size} 条")
    print(f"输入总数: {merge_stats['total_input']} 条")
    print(
        f"data.name 重复: {len(merge_stats['duplicates'])} 个（策略: {merge_stats['duplicates_action']}）"
    )
    print(f"合并后: {merge_stats['merged_count']} 条（独立姓名: {merge_stats['unique_names']} 个）")

    if args.no_validate:
        print("[SKIP] 跳过格式验证（--no-validate）")
        validation = None
    else:
        print("\n开始格式验证...")
        validation = validate_format(merged)
        print(f"  错误: {len(validation['errors'])} 个")
        print(f"  警告: {len(validation['warnings'])} 个")
        if validation["valid"]:
            print("  [PASS] 格式验证通过")
        else:
            print(f"  [FAIL] 格式验证失败（前 5 个错误）")
            for e in validation["errors"][:5]:
                print(f"    - 第 {e['index']} 条: {e['message']}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n已写入: {output_path}")

    if validation and not validation["valid"]:
        print("[FAIL] 合并完成但格式验证未通过，请检查评审质量")
        sys.exit(1)

    print("[OK] 合并完成")
    sys.exit(0)


if __name__ == "__main__":
    main()
