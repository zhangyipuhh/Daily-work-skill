# data-skill

把本地业务文件（PDF/DOCX/图片/Excel）通过 MinerU OCR 解析后, LLM 选表+抽字段, 脚本校验, SQLite 入库。

## 架构原则

- **确定的事脚本做**: 解析、类型/必填/长度校验、INSERT OR IGNORE、配置改写、清单核验。
- **语义的事 LLM 做**: 选表、字段抽取、错误重试决策、配置语义提取。

## 资产分层

| 层级 | 位置 | 性质 |
|---|---|---|
| Skill 包 | `D:\项目文档\AIAssistive\ai\skills\data-skill\` | 可复用, 版本管理 |
| 运行时产物 | `C:\Users\<user>\.data-skill\` | 用户级, 首跑生成 |
| 过程产物 | `<输入文件夹>\.data-skill\` | 任务级, 每次运行 |

## 快速开始

### 1. 安装依赖
```bash
pip install openpyxl pyyaml requests aiofiles
```

### 2. 重建静态资产（开发期, 改了 xlsx 后）
```bash
python scripts/_build_artifacts.py
```
会从 `D:\项目文档\AIAssistive\data_skill_tmp\数据库规范.xlsx` 重新生成:
- `tables/*.md` (20)
- `scripts/validators/*.py` (20)

### 3. 在 OpenCode 中调用
```bash
/data-skill <file|dir|--config "...">
```
首跑会触发 AskUserQuestion 人机回路配置 OCR 地址和 DB 路径。

## 入参形态

| 入参 | 行为 |
|---|---|
| `D:\docs\xxx.pdf` | 单文件处理 |
| `D:\docs\batch\` | 批处理 + 自愈核验 |
| `--config "把 OCR 地址改成 xxx"` | 配置变更 |

## 数据库

- SQLite, 路径在 `~/.data-skill/data.db`
- 入库策略: `INSERT OR IGNORE`（主键冲突跳过）
- 20 张表, schema 来自 `tables/*.md`, 运行时建表由 `init_db.py` 跑

## 支持的文件类型

`.pdf`, `.docx`, `.doc`, `.txt`, `.md`, `.csv`, `.xlsx`, `.xls`, `.png`, `.jpg`, `.jpeg`

## 20 张表清单

| 表 code | 业务名 |
|---|---|
| ZZ_PFXX | 农用地转用和土地征收-批复信息表 |
| ZZ_JBXX | 农用地转用和土地征收-基本信息表 |
| ZZHX | 农用地转用和土地征收-报批红线表 |
| XS_XKZ | 建设项目用地预审与规划选址-许可证表 |
| XS_JBXXB | 建设项目用地预审与规划选址-项目基本信息表 |
| XSHX | 建设项目用地预审与规划选址-预审红线表 |
| HTXX | 供地-合同信息表 |
| JBXX | 供地-基本信息表 |
| GDHX | 供地-供地红线表 |
| YG_XKXX | 用地规划-许可证表 |
| YG_JBXX | 用地规划-项目基本信息表 |
| DZ_YDHX | 用地红线表 |
| DZ_GG_XKXX | 房屋建筑工程规划许可-许可证表 |
| DZ_GG_JBXX | 房屋建筑工程规划许可-项目基本信息表 |
| DZ_GG_JZDTGK | 建筑用地单体 |
| DZ_GG_JYDFW | 建筑用地范围 |
| DZ_GG_LZFW | 建筑绿化范围 |
| DZ_HY_XKXX | 合同规划核实-合同信息表 |
| DZ_HY_MX | 合同规划核实-合同详细表 |
| DZ_HSJZ | 房屋建筑 |

## 自愈核验

批处理结束自动 verify:
- `missing` (pending/processing) → 自动重跑
- `needs_retry` (skipped/no_match) → 疑似幻觉, 重跑
- 最多 2 轮, 仍有则报用户决定
