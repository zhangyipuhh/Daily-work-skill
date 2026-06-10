#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GDHX 表的格式校验脚本。
构建期由 build_artifacts.py 自动生成，请勿手工修改。
运行时由 SKILL.md 通过 `python GDHX.py --record '<json>'` 调用。
"""
import argparse
import json
import re
import sys
from datetime import datetime


TABLE_CODE = 'GDHX'
PRIMARY_KEY = 'OBJECTID'
FIELDS = [{'seq': '1',
  'name': '主键',
  'code': 'OBJECTID',
  'type': 'INT',
  'length': None,
  'decimal': None,
  'constraint': 'M',
  'comment': '主键'},
 {'seq': '2',
  'name': '土地供应主键',
  'code': 'TDGYID',
  'type': 'Char',
  'length': 254,
  'decimal': None,
  'constraint': 'M',
  'comment': 'DZ_GD_HTXX主键'},
 {'seq': '3',
  'name': '项目空间码',
  'code': 'XMKJM',
  'type': 'Char',
  'length': 254,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '4',
  'name': '行政区名称',
  'code': 'XZQMC',
  'type': 'Char',
  'length': 254,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '5',
  'name': '电子监管号',
  'code': 'DZJGH',
  'type': 'Char',
  'length': 254,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '6',
  'name': '批复文号',
  'code': 'PZWH',
  'type': 'Char',
  'length': 254,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '7',
  'name': '合同编号',
  'code': 'HTBH',
  'type': 'Char',
  'length': 254,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '8',
  'name': '出让面积',
  'code': 'CRMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'M',
  'comment': '平方米'},
 {'seq': '9',
  'name': '面积',
  'code': 'MJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'M',
  'comment': '平方米'},
 {'seq': '10',
  'name': '出让价款',
  'code': 'CRJK',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'M',
  'comment': '万元'},
 {'seq': '11',
  'name': '受让人',
  'code': 'SRR',
  'type': 'Char',
  'length': 254,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '12',
  'name': '签订日期',
  'code': 'QDRQ',
  'type': 'Date',
  'length': None,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '13',
  'name': '项目名称',
  'code': 'XMMC',
  'type': 'Char',
  'length': 254,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '14',
  'name': '供应方式',
  'code': 'GYFS',
  'type': 'Char',
  'length': 254,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '15',
  'name': '土地坐落',
  'code': 'TDZL',
  'type': 'Char',
  'length': 254,
  'decimal': None,
  'constraint': 'M',
  'comment': ''}]


def _is_blank(v) -> bool:
    return v is None or (isinstance(v, str) and v.strip() == "")


def _check_char(value, length, field_code, errors):
    if not isinstance(value, str):
        errors.append(f"{field_code}: 类型错误, 期望 str, 实际 {type(value).__name__}")
        return
    if length is not None and len(value) > length:
        errors.append(f"{field_code}: 长度超限, 最大 {length}, 实际 {len(value)}")


def _check_int(value, field_code, errors):
    if isinstance(value, bool):
        errors.append(f"{field_code}: 类型错误, 期望 int, 实际 bool")
        return
    if not isinstance(value, int):
        errors.append(f"{field_code}: 类型错误, 期望 int, 实际 {type(value).__name__}")


def _check_float(value, decimal, field_code, errors):
    if isinstance(value, bool):
        errors.append(f"{field_code}: 类型错误, 期望 float, 实际 bool")
        return
    if not isinstance(value, (int, float)):
        errors.append(f"{field_code}: 类型错误, 期望 float, 实际 {type(value).__name__}")
        return
    if decimal is not None:
        s = str(value)
        if "." in s:
            frac = s.split(".", 1)[1]
            if len(frac) > decimal:
                errors.append(f"{field_code}: 小数位超限, 最大 {decimal}, 实际 {len(frac)}")


def _check_date(value, field_code, errors):
    if not isinstance(value, str):
        errors.append(f"{field_code}: 类型错误, 期望 str(ISO 8601), 实际 {type(value).__name__}")
        return
    if not re.match(r"^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}:\d{2})?$", value):
        errors.append(f"{field_code}: 日期格式错误, 期望 YYYY-MM-DD 或 ISO 8601, 实际 {value!r}")
        return
    try:
        datetime.fromisoformat(value.replace(" ", "T"))
    except ValueError:
        errors.append(f"{field_code}: 日期值非法, {value!r}")


def validate(record: dict) -> tuple[bool, list[str]]:
    """格式校验

    Args:
        record: LLM 抽出的字段 dict

    Returns:
        (ok, errors) 元组
    """
    errors: list[str] = []
    if not isinstance(record, dict):
        return False, ["record 必须是 dict"]

    for f in FIELDS:
        code = f["code"]
        ftype = f["type"]
        flen = f["length"]
        fdec = f["decimal"]
        constraint = f["constraint"]
        value = record.get(code)

        if _is_blank(value):
            if constraint == "M":
                errors.append(f"{code}: 必填字段为空")
            continue

        if ftype == "Char":
            _check_char(value, flen, code, errors)
        elif ftype == "INT":
            _check_int(value, code, errors)
        elif ftype == "Float":
            _check_float(value, fdec, code, errors)
        elif ftype == "Date":
            _check_date(value, code, errors)

    return (len(errors) == 0, errors)


def main():
    parser = argparse.ArgumentParser(description=f"{TABLE_CODE} 表格式校验")
    parser.add_argument("--record", required=True, help="JSON 字符串或 @file 路径")
    args = parser.parse_args()

    if args.record.startswith("@"):
        with open(args.record[1:], "r", encoding="utf-8") as f:
            record = json.load(f)
    else:
        record = json.loads(args.record)

    ok, errors = validate(record)
    print(json.dumps({"ok": ok, "errors": errors}, ensure_ascii=False))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
