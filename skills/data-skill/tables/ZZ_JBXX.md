# ZZ_JBXX - 农用地转用和土地征收-基本信息表

- **表代码**: `ZZ_JBXX`
- **业务名称**: 农用地转用和土地征收-基本信息表
- **字段总数**: 16
- **主键**: `InstanceID`（序号 1，约束 M）

## 字段说明

| 序号 | 字段名称 | 字段代码 | 类型 | 长度 | 小数 | 约束 | 备注 |
|------|---------|---------|------|------|------|------|------|
| 1 | 主建ID | `InstanceID` | Char | 14 |  | M | 主键 |
| 2 | 用地报批ID | `YDBPID` | Char |  |  | O | DZ_ZZ_PFXX主键（DZ_ZZ_PFXX-InstanceID） |
| 3 | 要素代码 | `YSDM` | Char | 10 |  | M | 业务流水号 |
| 4 | 电子监管号 | `DZJGH` | Char | 19 |  | M | 批复文号 |
| 5 | 行政区代码 | `XZQDM` | Char | 6 |  | M |  |
| 6 | 行政区名称 | `XZQMC` | Char | 30 |  | M |  |
| 7 | 建设项目名称 | `JSXMMC` | Char | 300 |  | M |  |
| 8 | 项目位置 | `XMWZ` | Char | 300 |  | M |  |
| 9 | 用地总面积 | `YDZMJ` | Float |  | 8 | M |  |
| 10 | 新增建设用地面积 | `XZJSYDMJ` | Float |  | 8 | O |  |
| 11 | 占耕地面积 | `GDMJ` | Float |  | 8 | O |  |
| 12 | 占水田面积 | `STMJ` | Float |  | 8 | O |  |
| 13 | 占永久基本农田面积 | `YJJBNTMJ` | Float |  | 8 | O |  |
| 14 | 其中集体 | `JTTDMJ` | Float |  | 8 | O |  |
| 15 | 其中国有 | `GYTDMJ` | Float |  | 8 | O |  |
| 16 | 批次类型 | `PCLX` | Char | 30 |  | M |  |
