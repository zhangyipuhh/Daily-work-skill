# JBXX - 供地基本信息

- **表代码**: `JBXX`
- **业务名称**: 供地基本信息
- **字段总数**: 55
- **主键**: `InstanceID`（序号 1，约束 M）

## 字段说明

| 序号 | 字段名称 | 字段代码 | 类型 | 长度 | 小数 | 约束 | 备注 |
|------|---------|---------|------|------|------|------|------|
| 1 | 主建ID | `InstanceID` | Char | 14 |  | M | 主键 |
| 2 | 土地供应主键 | `TDGYID` | Char | 254 |  | M | DZ_GD_HTXX主键 |
| 10 | 电子监管号 | `DZJGH` | Char | 20 |  | O |  |
| 5 | 合同编号 | `HTBH` | Char | 254 |  | M |  |
| 3 | 批复文号 | `PFWH` | Char | 25 |  | O |  |
| 4 | 宗地编号 | `ZDBH` | Char | 25 |  | M | 主键 |
| 5 | 土地位置 | `TDWZ` | Char | 200 |  | O |  |
| 6 | 土地面积 | `TDMJ` | Float |  | 4 | O |  |
| 7 | 项目名称 | `XMMC` | Char | 100 |  | O |  |
| 8 | 受让单位 | `SRDW` | Char | 50 |  | O |  |
| 9 | 土地用途 | `ZSLX` | Char | 30 |  | O |  |
| 11 | 容积率 | `RJL` | Char | 30 |  | O |  |
| 12 | 地上总建筑面积 | `DSZJZ` | Float | 20 | 4 | O |  |
| 13 | 出让年限 | `CRNX` | Char | 50 |  | O |  |
| 14 | 受让人 | `SRR` | Char | 20 |  | O |  |
| 15 | 成交价款 | `CJJK` | Char | 100 |  | O |  |
| 16 | 成交日期 | `CJRQ` | Date |  |  | O |  |
| 17 | 保障性住房配建 | `BZSZFPJ` | Char | 2 |  | O |  |
| 18 | 回迁情况 | `HQQK` | Char | 255 |  | O |  |
| 19 | 供地方式 | `GDFS` | Char | 20 |  | O |  |
| 20 | 自持面积 | `ZCMJ` | Float | 20 | 4 | O |  |
| 21 | 联系人 | `LXR` | Char | 20 |  | O |  |
| 22 | 公示期 | `GSQ` | Char | 50 |  | O |  |
| 23 | 备注 | `BZ` | Char | 200 |  | O |  |
| 24 | 数据来源 | `SJLY` | Char | 20 |  | O |  |
| 25 | 报建年份 | `BJNF` | Char | 20 |  | O |  |
| 26 | 经办人 | `JBR` | Char | 20 |  | O |  |
| 27 | 竞买保证金 | `JMBZJ` | Char | 50 |  | O |  |
| 28 | 土地抵押年限 | `TDDYNX` | Char | 50 |  | O |  |
| 29 | 行业分类 | `HYFL` | Char | 50 |  | O |  |
| 30 | 合同签订日期 | `HTQDRQ` | Date |  |  | O |  |
| 31 | 约定开工日期 | `YDKGRQ` | Date |  |  | O |  |
| 32 | 招拍挂截止时间 | `ZPGJZSJ` | Date |  |  | O |  |
| 33 | 招拍挂起始时间 | `ZPGQSSJ` | Date |  |  | O |  |
| 34 | 成交公示截止日期 | `CJGSJZ` | Char | 50 |  | O |  |
| 35 | 成交公示起始日期 | `CJGSKS` | Char | 50 |  | O |  |
| 36 | 报名截止日期 | `BMJZRQ` | Date |  |  | O |  |
| 37 | 报名起始日期 | `BMQSRQ` | Date |  |  | O |  |
| 38 | 约定交地时间 | `YDJDSJ` | Date |  |  | O |  |
| 39 | 约定竣工时间 | `YDJGSJ` | Date |  |  | O |  |
| 40 | 加价幅度 | `JJFD` | Char | 50 |  | O |  |
| 41 | 建筑面积 | `JZMJ` | Float |  | 4 | O |  |
| 42 | 建筑密度上限 | `JZMDMAX` | Char | 10 |  | O |  |
| 43 | 建筑密度下限 | `JZMDMIN` | Char | 10 |  | O |  |
| 44 | 建筑限高上限 | `JZXGMAX` | Char | 10 |  | O |  |
| 45 | 绿化率上限 | `LHVMAX` | Char | 10 |  | O |  |
| 46 | 绿化率下限 | `LHVMIN` | Char | 10 |  | O |  |
| 47 | 容积率上限 | `RJLMAX` | Char | 10 |  | O |  |
| 48 | 容积率下限 | `RJLMIN` | Char | 10 |  | O |  |
| 49 | 起始价 | `QSJ` | Char | 50 |  | O |  |
| 50 | 土地级别 | `TDJB` | Char | 50 |  | O |  |
| 51 | 土地使用权人 | `TDSYR` | Char | 50 |  | O |  |
| 52 | 行政区代码 | `XZQDM` | Char | 50 |  | O |  |
| 53 | 行政区 | `XZQ` | Char | 50 |  | O |  |
| 54 | 估价报告备案号 | `GJBGBAH` | Char | 50 |  | O |  |
