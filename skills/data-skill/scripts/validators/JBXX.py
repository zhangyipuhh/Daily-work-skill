#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JBXX 表的格式校验脚本。
构建期由 build_artifacts.py 自动生成，请勿手工修改。
运行时由 SKILL.md 通过 `python JBXX.py --record '<json>'` 调用。
"""
import argparse
import json
import re
import sys
from datetime import datetime


TABLE_CODE = 'JBXX'
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
  'name': '土地供应主键',
  'code': 'TDGYID',
  'type': 'Char',
  'length': 254,
  'decimal': None,
  'constraint': 'M',
  'comment': 'DZ_GD_HTXX主键'},
 {'seq': '10',
  'name': '电子监管号',
  'code': 'DZJGH',
  'type': 'Char',
  'length': 20,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '5',
  'name': '合同编号',
  'code': 'HTBH',
  'type': 'Char',
  'length': 254,
  'decimal': None,
  'constraint': 'M',
  'comment': ''},
 {'seq': '3',
  'name': '批复文号',
  'code': 'PFWH',
  'type': 'Char',
  'length': 25,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '4',
  'name': '宗地编号',
  'code': 'ZDBH',
  'type': 'Char',
  'length': 25,
  'decimal': None,
  'constraint': 'M',
  'comment': '主键'},
 {'seq': '5',
  'name': '土地位置',
  'code': 'TDWZ',
  'type': 'Char',
  'length': 200,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '6',
  'name': '土地面积',
  'code': 'TDMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '7',
  'name': '项目名称',
  'code': 'XMMC',
  'type': 'Char',
  'length': 100,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '8',
  'name': '受让单位',
  'code': 'SRDW',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '9',
  'name': '土地用途',
  'code': 'ZSLX',
  'type': 'Char',
  'length': 30,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '11',
  'name': '容积率',
  'code': 'RJL',
  'type': 'Char',
  'length': 30,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '12',
  'name': '地上总建筑面积',
  'code': 'DSZJZ',
  'type': 'Float',
  'length': 20,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '13',
  'name': '出让年限',
  'code': 'CRNX',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '14',
  'name': '受让人',
  'code': 'SRR',
  'type': 'Char',
  'length': 20,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '15',
  'name': '成交价款',
  'code': 'CJJK',
  'type': 'Char',
  'length': 100,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '16',
  'name': '成交日期',
  'code': 'CJRQ',
  'type': 'Date',
  'length': None,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '17',
  'name': '保障性住房配建',
  'code': 'BZSZFPJ',
  'type': 'Char',
  'length': 2,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '18',
  'name': '回迁情况',
  'code': 'HQQK',
  'type': 'Char',
  'length': 255,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '19',
  'name': '供地方式',
  'code': 'GDFS',
  'type': 'Char',
  'length': 20,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '20',
  'name': '自持面积',
  'code': 'ZCMJ',
  'type': 'Float',
  'length': 20,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '21',
  'name': '联系人',
  'code': 'LXR',
  'type': 'Char',
  'length': 20,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '22',
  'name': '公示期',
  'code': 'GSQ',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '23',
  'name': '备注',
  'code': 'BZ',
  'type': 'Char',
  'length': 200,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '24',
  'name': '数据来源',
  'code': 'SJLY',
  'type': 'Char',
  'length': 20,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '25',
  'name': '报建年份',
  'code': 'BJNF',
  'type': 'Char',
  'length': 20,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '26',
  'name': '经办人',
  'code': 'JBR',
  'type': 'Char',
  'length': 20,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '27',
  'name': '竞买保证金',
  'code': 'JMBZJ',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '28',
  'name': '土地抵押年限',
  'code': 'TDDYNX',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '29',
  'name': '行业分类',
  'code': 'HYFL',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '30',
  'name': '合同签订日期',
  'code': 'HTQDRQ',
  'type': 'Date',
  'length': None,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '31',
  'name': '约定开工日期',
  'code': 'YDKGRQ',
  'type': 'Date',
  'length': None,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '32',
  'name': '招拍挂截止时间',
  'code': 'ZPGJZSJ',
  'type': 'Date',
  'length': None,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '33',
  'name': '招拍挂起始时间',
  'code': 'ZPGQSSJ',
  'type': 'Date',
  'length': None,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '34',
  'name': '成交公示截止日期',
  'code': 'CJGSJZ',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '35',
  'name': '成交公示起始日期',
  'code': 'CJGSKS',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '36',
  'name': '报名截止日期',
  'code': 'BMJZRQ',
  'type': 'Date',
  'length': None,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '37',
  'name': '报名起始日期',
  'code': 'BMQSRQ',
  'type': 'Date',
  'length': None,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '38',
  'name': '约定交地时间',
  'code': 'YDJDSJ',
  'type': 'Date',
  'length': None,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '39',
  'name': '约定竣工时间',
  'code': 'YDJGSJ',
  'type': 'Date',
  'length': None,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '40',
  'name': '加价幅度',
  'code': 'JJFD',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '41',
  'name': '建筑面积',
  'code': 'JZMJ',
  'type': 'Float',
  'length': None,
  'decimal': 4,
  'constraint': 'O',
  'comment': ''},
 {'seq': '42',
  'name': '建筑密度上限',
  'code': 'JZMDMAX',
  'type': 'Char',
  'length': 10,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '43',
  'name': '建筑密度下限',
  'code': 'JZMDMIN',
  'type': 'Char',
  'length': 10,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '44',
  'name': '建筑限高上限',
  'code': 'JZXGMAX',
  'type': 'Char',
  'length': 10,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '45',
  'name': '绿化率上限',
  'code': 'LHVMAX',
  'type': 'Char',
  'length': 10,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '46',
  'name': '绿化率下限',
  'code': 'LHVMIN',
  'type': 'Char',
  'length': 10,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '47',
  'name': '容积率上限',
  'code': 'RJLMAX',
  'type': 'Char',
  'length': 10,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '48',
  'name': '容积率下限',
  'code': 'RJLMIN',
  'type': 'Char',
  'length': 10,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '49',
  'name': '起始价',
  'code': 'QSJ',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '50',
  'name': '土地级别',
  'code': 'TDJB',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '51',
  'name': '土地使用权人',
  'code': 'TDSYR',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '52',
  'name': '行政区代码',
  'code': 'XZQDM',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '53',
  'name': '行政区',
  'code': 'XZQ',
  'type': 'Char',
  'length': 50,
  'decimal': None,
  'constraint': 'O',
  'comment': ''},
 {'seq': '54',
  'name': '估价报告备案号',
  'code': 'GJBGBAH',
  'type': 'Char',
  'length': 50,
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
