# DZ_GG_JYDFW - 建设工程规划许可-净用地范围

- **表代码**: `DZ_GG_JYDFW`
- **业务名称**: 建设工程规划许可-净用地范围
- **字段总数**: 45
- **主键**: `OBJECTID`（序号 1，约束 M）

## 字段说明

| 序号 | 字段名称 | 字段代码 | 类型 | 长度 | 小数 | 约束 | 备注 |
|------|---------|---------|------|------|------|------|------|
| 1 | 主键 | `OBJECTID` | INT |  |  | M | 主键 |
| 2 | 工规许可主键 | `GGXKID` | Char | 254 |  | M | DZ_YG_XKXX主键 |
| 3 | 要素代码 | `YSDM` | Char | 254 |  | M | 参考国标要素代码取值"8005010300" |
| 4 | 电子监管号 | `DZJGH` | Char | 254 |  | M |  |
| 5 | 项目代码 | `XMDM` | Char | 254 |  | O |  |
| 6 | 用地许可证号 | `YGDZJGH` | Char | 254 |  | O |  |
| 7 | 建设单位 | `JSDW` | Char | 254 |  | M |  |
| 8 | 建设项目名称 | `XMMC` | Char | 254 |  | M |  |
| 9 | 证书编号 | `ZSBH` | Char | 254 |  | M |  |
| 10 | 发证日期 | `FZRQ` | Date |  |  | M |  |
| 11 | 发证机关 | `FZJG` | Char | 254 |  | M |  |
| 12 | 建设拟选位置 | `JSWZ` | Char | 254 |  | M |  |
| 13 | 拟建设规模 | `JSGM` | Char | 254 |  | O |  |
| 14 | 拟用地面积 | `YDMJ` | Char | 254 |  | O |  |
| 15 | 总用地面积 | `ZYDMJ` | Float |  | 4 | O |  |
| 16 | 净用地面积 | `JYDMJ` | Float |  | 4 | O |  |
| 17 | 计容用地面积 | `JRYDMJ` | Float |  | 4 | O | 平方米 |
| 18 | 总建筑面积 | `ZJZMJ` | Float |  | 4 | M | 平方米 |
| 19 | 地上总建筑面积 | `DSZJZMJ` | Float |  | 4 | O | 平方米 |
| 20 | 地下总建筑面积 | `DXZJZMJ` | Float |  | 4 | O | 平方米 |
| 21 | 计容建筑面积 | `JRJZMJ` | Float |  | 4 | O | 平方米 |
| 22 | 住宅建筑面积 | `ZZJZMJ` | Char |  |  | O |  |
| 23 | 商业建筑面积 | `SYJZMJ` | Char |  |  | O |  |
| 24 | 容积率 | `RJL` | Float |  | 4 | O |  |
| 25 | 建筑密度 | `JZMD` | Float |  | 4 | O |  |
| 26 | 绿地率 | `LDL` | Float |  | 4 | O |  |
| 27 | 建筑限高 | `JZXG` | Float |  | 4 | O | 米 |
| 28 | 机动车停车位 | `JDCTCW` | Float |  | 4 | O |  |
| 29 | 地上机动车停车位 | `DSJDCTCW` | Float |  | 4 | O |  |
| 30 | 地下机动车停车位 | `DXJDCTCW` | Float |  | 4 | O |  |
| 31 | 非机动车停车位 | `FJDCTCW` | Float |  | 4 | O |  |
| 32 | 地上非机动车停车位 | `DSFJDCTCW` | Float |  | 4 | O |  |
| 33 | 地下非机动车停车位 | `DXFJDCTCW` | Float |  | 4 | O |  |
| 34 | 社区服务站（含党群服务用房） | `SQFWZ` | Float |  | 4 | O | 平方米 |
| 35 | 养老服务设施 | `YLFWSS` | Float |  | 4 | O | 平方米 |
| 36 | 菜市场 | `CSC` | Float |  | 4 | O | 平方米 |
| 37 | 物业用房及社区快递驿站 | `WYYF` | Float |  | 4 | O | 平方米 |
| 38 | 体育设施 | `TYSS` | Float |  | 4 | O | 平方米 |
| 39 | 便利店 | `BLD` | Float |  | 4 | O | 平方米 |
| 40 | 文化活动室 | `WHHDS` | Float |  | 4 | O | 平方米 |
| 41 | 卫生医疗 | `WSYL` | Float |  | 4 | O | 平方米 |
| 43 | 拆迁安置面积 | `CQAZMJ` | Float |  | 4 | O | 平方米 |
| 44 | 廉租房面积 | `LZFMJ` | Float |  | 4 | O | 平方米 |
| 45 | 户数 | `HS` | Float |  | 4 | O |  |
| 46 | 人口 | `RKS` | Float |  | 4 | O |  |
