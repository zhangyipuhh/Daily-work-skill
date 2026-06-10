# DZ_GG_JBXX - 建设工程规划许可-项目基本

- **表代码**: `DZ_GG_JBXX`
- **业务名称**: 建设工程规划许可-项目基本
- **字段总数**: 42
- **主键**: `InstanceID`（序号 1，约束 M）

## 字段说明

| 序号 | 字段名称 | 字段代码 | 类型 | 长度 | 小数 | 约束 | 备注 |
|------|---------|---------|------|------|------|------|------|
| 1 | 主建ID | `InstanceID` | Char | 14 |  | M | 主键 |
| 2 | 用地许可主键 | `YDZKID` | Char | 32 |  | M | DZ_YG_XKXX主键 |
| 3 | 要素代码 | `YSDM` | Char | 32 |  | M | 参考国标要素代码取值"8005010100" |
| 4 | 电子监管号 | `DZJGH` | Char | 32 |  | M |  |
| 5 | 行政区代码 | `XZQDM` | Char | 20 |  | O |  |
| 6 | 行政区名称 | `XZQMC` | Char | 50 |  | O |  |
| 7 | 项目名称 | `XMMC` | Char | 200 |  | M |  |
| 8 | 建设单位 | `JSDW` | Char | 64 |  | M |  |
| 9 | 建设位置 | `JSWZ` | Char | 1000 |  | M |  |
| 10 | 设计单位 | `SJDW` | Char | 64 |  | O |  |
| 11 | 设计资质 | `SJZZ` | Char | 64 |  | O |  |
| 12 | 总投资 | `ZTZ` | Float |  | 4 | O |  |
| 13 | 证书编号 | `ZSBH` | Char | 64 |  | M |  |
| 14 | 预审选址证号 | `YSXZZH` | Char | 64 |  | O |  |
| 15 | 用地许可证号 | `YDXKZH` | Char | 64 |  | O |  |
| 16 | 投资批准机关 | `TZPZJG` | Char | 64 |  | O |  |
| 17 | 投资批准文号 | `TZPZWH` | Char | 64 |  | O |  |
| 18 | 土地证批准机关 | `TDZPZJG` | Char | 64 |  | O |  |
| 19 | 土地证号 | `TDZH` | Char | 64 |  | O |  |
| 20 | 项目性质 | `XMXZ` | Char | 64 |  | O |  |
| 21 | 建设规模 | `JSGM` | Char | 64 |  | O |  |
| 22 | 土地用途 | `TDYT` | Char | 64 |  | O |  |
| 23 | 土地取得方式 | `TDQDFS` | Char | 64 |  | O |  |
| 22 | 总用地面积 | `ZYDMJ` | Float |  | 4 | O | 平方米 |
| 23 | 净用地面积 | `JYDMJ` | Float |  | 4 | O | 平方米 |
| 24 | 计容用地面积 | `JRYDMJ` | Float |  | 4 | O | 平方米 |
| 25 | 总建筑面积 | `ZJZMJ` | Float |  | 4 | M | 平方米 |
| 26 | 地上总建筑面积 | `DSZJZMJ` | Float |  | 4 | O | 平方米 |
| 27 | 地下总建筑面积 | `DXZJZMJ` | Float |  | 4 | O | 平方米 |
| 28 | 计容建筑面积 | `JRJZMJ` | Float |  | 4 | O | 平方米 |
| 29 | 容积率 | `RJL` | Float |  | 4 | O |  |
| 30 | 建筑密度 | `JZMD` | Float |  | 4 | O |  |
| 31 | 绿地率 | `LDL` | Float |  | 4 | O |  |
| 32 | 建筑限高 | `JZXG` | Float |  | 4 | O | 米 |
| 33 | 机动车停车位 | `JDCTCW` | Float |  | 4 | O |  |
| 34 | 地上机动车停车位 | `DSJDCTCW` | Float |  | 4 | O |  |
| 35 | 地下机动车停车位 | `DXJDCTCW` | Float |  | 4 | O |  |
| 36 | 非机动车停车位 | `FJDCTCW` | Float |  | 4 | O |  |
| 37 | 地上非机动车停车位 | `DSFJDCTCW` | Float |  | 4 | O |  |
| 38 | 地下非机动车停车位 | `DXFJDCTCW` | Float |  | 4 | O |  |
| 39 | 拆迁安置面积 | `CQAZMJ` | Float |  | 4 | O |  |
| 40 | 廉租房面积 | `LZFMJ` | Float |  | 4 | O |  |
