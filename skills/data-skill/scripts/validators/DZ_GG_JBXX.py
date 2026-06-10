#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DZ_GG_JBXX 表的格式校验脚本。
构建期由 build_artifacts.py 自动生成，请勿手工修改。
运行时由 SKILL.md 通过 `python DZ_GG_JBXX.py --record '<json>'` 调用。
"""
import argparse
import json
import re
import sys
from datetime import datetime


TABLE_CODE = 'DZ_GG_JBXX'
PRIMARY_KEY = 'InstanceID'
FIELDS = [{'seq': '1',
  'name': '主建ID',
  'code': 'InstanceID',
  'type': 'Char',
  'length': 14,
  'decimal': None,
  'constraint': 'M',
  'comment': '主键'},
 {'seq': '2',
  'name': '用地许可主键',
  'code': 'YDZKID',
  'type': 'Char',
  'length': 32,
  'decimal': None,
  'constraint': 'M',
  'comment': 'DZ_YG_XKXX主键'},
 {'seq': '3',
  'name': '要素代码',
  'code': 'YSDM',
  'type': 'Char',
  'length': 32,
  'decimal': None,
  'constraint': 'M',
  'comment': '参考国标要素代码取值"8005010100"'},
 {'seq': '4',
  'name': '电子监管号',
  'code': 'DZJGH',
  'type': 'Char',
  'length': 32,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '5',
  'name': '行政区代码',
  'code': 'XZQDM',
  'type': 'Char',
  'length': 20,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '6',
  'name': '行政区名称',
  'code': 'XZQMC',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '7',
  'name': '项目名称',
  'code': 'XMMC',
  'type': 'Char',
  'length': 200,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '8',
  'name': '建设单位',
  'code': 'JSDW',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '9',
  'name': '建设位置',
  'code': 'JSWZ',
  'type': 'Char',
  'length': 1000,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '10',
  'name': '设计单位',
  'code': 'SJDW',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '11',
  'name': '设计资质',
  'code': 'SJZZ',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '12',
  'name': '总投资',
  'code': 'ZTZ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '13',
  'name': '证书编号',
  'code': 'ZSBH',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '14',
  'name': '预审选址证号',
  'code': 'YSXZZH',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '15',
  'name': '用地许可证号',
  'code': 'YDXKZH',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '16',
  'name': '投资批准机关',
  'code': 'TZPZJG',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '17',
  'name': '投资批准文号',
  'code': 'TZPZWH',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '18',
  'name': '土地证批准机关',
  'code': 'TDZPZJG',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '19',
  'name': '土地证号',
  'code': 'TDZH',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '20',
  'name': '项目性质',
  'code': 'XMXZ',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '21',
  'name': '建设规模',
  'code': 'JSGM',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '22',
  'name': '土地用途',
  'code': 'TDYT',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '23',
  'name': '土地取得方式',
  'code': 'TDQDFS',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '22',
  'name': '总用地面积',
  'code': 'ZYDMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '23',
  'name': '净用地面积',
  'code': 'JYDMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '24',
  'name': '计容用地面积',
  'code': 'JRYDMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '25',
  'name': '总建筑面积',
  'code': 'ZJZMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'M',
  'comment': '平方米'},
 {'seq': '26',
  'name': '地上总建筑面积',
  'code': 'DSZJZMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '27',
  'name': '地下总建筑面积',
  'code': 'DXZJZMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '28',
  'name': '计容建筑面积',
  'code': 'JRJZMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '29',
  'name': '容积率',
  'code': 'RJL',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '30',
  'name': '建筑密度',
  'code': 'JZMD',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '31',
  'name': '绿地率',
  'code': 'LDL',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '32',
  'name': '建筑限高',
  'code': 'JZXG',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '米'},
 {'seq': '33',
  'name': '机动车停车位',
  'code': 'JDCTCW',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '34',
  'name': '地上机动车停车位',
  'code': 'DSJDCTCW',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '35',
  'name': '地下机动车停车位',
  'code': 'DXJDCTCW',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '36',
  'name': '非机动车停车位',
  'code': 'FJDCTCW',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '37',
  'name': '地上非机动车停车位',
  'code': 'DSFJDCTCW',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '38',
  'name': '地下非机动车停车位',
  'code': 'DXFJDCTCW',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '39',
  'name': '拆迁安置面积',
  'code': 'CQAZMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '40',
  'name': '廉租房面积',
  'code': 'LZFMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
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
