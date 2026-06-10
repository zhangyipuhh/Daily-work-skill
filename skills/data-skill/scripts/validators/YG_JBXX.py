#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YG_JBXX 表的格式校验脚本。
构建期由 build_artifacts.py 自动生成，请勿手工修改。
运行时由 SKILL.md 通过 `python YG_JBXX.py --record '<json>'` 调用。
"""
import argparse
import json
import re
import sys
from datetime import datetime


TABLE_CODE = 'YG_JBXX'
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
  'comment': '参考国标要素代码取值"8004010100"'},
 {'seq': '4',
  'name': '证书编号',
  'code': 'ZSBH',
  'type': 'Char',
  'length': 32,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '5',
  'name': '项目名称',
  'code': 'XMMC',
  'type': 'Char',
  'length': 32,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '6',
  'name': '用地位置',
  'code': 'YDWZ',
  'type': 'Char',
  'length': 100,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '7',
  'name': '建设单位',
  'code': 'JSDW',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '8',
  'name': '建设单位地址',
  'code': 'JSDWDZ',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '9',
  'name': '投资批准机关',
  'code': 'TZPZJG',
  'type': 'Char',
  'length': 64,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '10',
  'name': '投资批准机关文号',
  'code': 'TZPZJGWH',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '11',
  'name': '预审选址意见书证号',
  'code': 'YSXZZSBH',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '12',
  'name': '出让合同编号',
  'code': 'HTH',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '13',
  'name': '总投资',
  'code': 'ZTZE',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '万元'},
 {'seq': '14',
  'name': '建设规模',
  'code': 'JSGM',
  'type': 'Char',
  'length': 100,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '15',
  'name': '土地取得方式',
  'code': 'TDQDFS',
  'type': 'Char',
  'length': 100,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '16',
  'name': '规划条件编号',
  'code': 'GHTJBH',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '17',
  'name': '用地性质',
  'code': 'YDXZ',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '18',
  'name': '总用地面积',
  'code': 'ZYDMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '19',
  'name': '净用地面积',
  'code': 'JYDMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '20',
  'name': '公共管理与公共服务用地',
  'code': 'GGGLYFW',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '21',
  'name': '交通运输用地',
  'code': 'JTYS',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '22',
  'name': '绿地与开敞空间用地',
  'code': 'LDYKCKJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '23',
  'name': '公用设施用地',
  'code': 'GGSSYD',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '24',
  'name': '特殊用地',
  'code': 'TSYD',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '25',
  'name': '其他土地',
  'code': 'QTTD',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': '平方米'},
 {'seq': '26',
  'name': '容积率',
  'code': 'RJL',
  'type': 'Char',
  'length': 100,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '27',
  'name': '建筑密度',
  'code': 'JSMD',
  'type': 'Char',
  'length': 100,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '28',
  'name': '绿地率',
  'code': 'LDL',
  'type': 'Char',
  'length': 100,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '29',
  'name': '商业比例',
  'code': 'SYBL',
  'type': 'Char',
  'length': 100,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '30',
  'name': '建筑限高',
  'code': 'JZXG',
  'type': 'Char',
  'length': 100,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '31',
  'name': '建筑间距',
  'code': 'JZJJ',
  'type': 'Char',
  'length': 100,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '32',
  'name': '停车位',
  'code': 'TCW',
  'type': 'Char',
  'length': 1000,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '33',
  'name': '主要出入口方位',
  'code': 'ZYCRKFW',
  'type': 'Char',
  'length': 100,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '34',
  'name': '建筑退线（界）要求',
  'code': 'JZTX',
  'type': 'Char',
  'length': 100,
  'decimal': None,
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
