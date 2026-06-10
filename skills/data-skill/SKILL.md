---
name: "data-skill"
description: "把本地业务文件（PDF/DOCX/图片/Excel）通过 MinerU OCR 解析后, LLM 选表+抽字段, 脚本校验, SQLite 入库。自动批处理 + 自愈核验 (verify+补跑)。触发场景: 用户给一个文件/文件夹想入库, 或 `--config` 改 OCR/DB 配置。"
---

# data-skill

业务文件 → OCR → LLM 选表抽字段 → 脚本校验 → SQLite 入库。

## 核心原则

- **确定的事脚本做**: 解析、类型/必填/长度校验、INSERT OR IGNORE、配置改写、清单核验、补跑控制。
- **语义的事 LLM 做**: 选表、字段抽取、错误重试决策、配置语义提取、跳过/重试的人机交互。

## 路径约定

| 资产 | 位置 |
|---|---|
| Skill 包 | `D:\项目文档\AIAssistive\ai\skills\data-skill\` |
| 运行时配置 + DB | `C:\Users\<user>\.data-skill\config.yml` 和 `data.db` |
| 过程产物 | `<输入文件夹>\.data-skill\inventory.json` 等 |

`$SKILL_DIR` 指 skill 包根目录, `$DATA_DIR` 指 `~/.data-skill/`, `$INV_DIR` 指 `<输入文件夹>/.data-skill/`。

## 入参识别

`/data-skill <args>`, 解析如下:

- `<args>` 是 `--config "<自然语言>"` → 配置变更
- `<args>` 是文件路径且文件存在 → 单文件
- `<args>` 是目录路径且目录存在 → 批处理
- 其他 → 用 AskUserQuestion 让用户补全

---

## 流程 A：首跑（检测到 `$DATA_DIR/config.yml` 不存在）

无论走单文件还是批处理, 都先做首跑检测。

### 1. 读默认配置
读 `D:\项目文档\AIAssistive\data_skill_tmp\配置.md`, 提取默认值:
- `file_parser_server_url`
- `file_parser_api_url`

### 2. AskUserQuestion 人机回路
用 `question` 工具逐项询问, 展示默认值, 让用户确认或改写:
1. `file_parser_server_url` (默认 = 配置.md 中的值)
2. `file_parser_api_url` (默认 = 配置.md 中的值)
3. `db_path` (默认 = `~/.data-skill/data.db`)
4. `parser_output_format` (默认 = `json`, 选项 json/md/both)
5. `parser_lang_list` (默认 = `ch`)

### 3. 写 yml + 建库
```bash
python $SKILL_DIR/scripts/init_config.py --values '<人机回路收集的 JSON>'
python $SKILL_DIR/scripts/init_db.py
```

### 4. 进入流程 B 或 C

---

## 流程 B：单文件

```
入参 = <file>
   │
   ▼
创建 $INV_DIR/_parse/ 目录
   │
   ▼
调 parse_file.py
   python $SKILL_DIR/scripts/parse_file.py \
     --file <file> --output-dir $INV_DIR/_parse --format both
   │
   ▼
读 list_sheets.py 拿到所有表名 + 业务说明
   python $SKILL_DIR/scripts/list_sheets.py
   │
   ▼
【LLM 语义】读 $INV_DIR/_parse/<原文件名>.json + .md
   │
   ├─ 标题/内容明显命中某张表 → 选该表
   ├─ 跨多表 → 选多张, 逐个走
   └─ 无明显命中 → 尝试扫 tables/*.md 找最相关
   │
   ▼
【LLM 语义】读 tables/<表 code>.md, 抽字段 → record dict
   │
   ▼
【脚本】调 validators/<表 code>.py
   python $SKILL_DIR/scripts/validators/<表 code>.py --record '<JSON>'
   │
   ├─ ok=true  → 调 insert_record.py
   │              python $SKILL_DIR/scripts/insert_record.py \
   │                --table <表 code> --record '<JSON>'
   │              → 完成, 输出 inserted/skipped
   │
   └─ ok=false → 把 errors 喂回 LLM 重抽
                  最多 3 次
                  仍失败 → 输出失败原因, 不入库
   │
   ▼
反馈用户: 文件 / 表 / 字段数 / 主键值 / inserted?skipped?failed?
```

---

## 流程 C：批处理 + 自愈

### 1. 建清单
```bash
python $SKILL_DIR/scripts/build_inventory.py --dir <dir>
```
输出 `$INV_DIR/inventory.json` (含 status: pending/processing/done/failed/skipped)。

### 2. 逐个处理 (status=pending)
走流程 B 的"解析 → 选表 → 抽字段 → 校验 → 入库", 处理完更新 inventory.json:
- done: 写 primary_key
- skipped: 写 errors=["no_match: ..."]
- failed: 写 errors=[...]

### 3. 核验
```bash
python $SKILL_DIR/scripts/verify_inventory.py --dir <dir>
```
输出 `$INV_DIR/verify_report.json`:
- `missing`: pending + processing
- `needs_retry`: skipped 且 errors 含 no_match（疑似 LLM 幻觉漏判）
- `failed_items`: failed 且 errors 非空

### 4. 自愈循环（最多 2 轮）
```
need_action = (missing 非空 或 needs_retry 非空)
  │
  ├─ 否 → 完成
  └─ 是 → 重新跑这些项 (走流程 B)
           跑完再 verify
           仍 need_action → 报用户: 列出 missing/needs_retry
                              选项: 重试 / 跳过 / 标记
```

### 5. 报告
- 处理总数 / done / skipped / failed
- 仍在 pending/processing 的（如有）
- DB 中新插入的 record 数

---

## 流程 D：配置变更

```
入参 = --config "<自然语言>"
   │
   ▼
【LLM 语义】从自然语言抽 (key, value), key 必须在以下集合:
  {file_parser_server_url, file_parser_api_url, db_path,
   parser_output_format, parser_lang_list}
   │
   ▼
【LLM】调 update_config.py
   python $SKILL_DIR/scripts/update_config.py --key <key> --value <value>
   │
   ▼
读回 yml, 反馈新值
```

LLM 抽取规则:
- "OCR 地址改成 xxx" → key=file_parser_server_url
- "DB 改到 xxx" → key=db_path
- "输出改成 md" → key=parser_output_format
- 无法识别 → 用 AskUserQuestion 让用户明确

---

## 错误处理

| 阶段 | 失败 | 行为 |
|---|---|---|
| 解析 | 网络/超时 | status=failed, reason=parse_error |
| 选表 | 无匹配 | status=skipped, reason=no_match（自愈循环会重试） |
| 抽字段 | 校验失败 | LLM 重抽 ≤ 3 次, 仍失败 status=failed |
| 入库 | DB 错误 | status=failed, reason=db_error（带 sqlite 错误码） |

---

## 幂等

- 主键 INSERT OR IGNORE: 主键存在则跳过, 不抛错
- inventory.json 持久化, 重跑只处理 pending/skipped/failed
- 解析产物落盘 $INV_DIR/_parse/, 可清理

---

## 文件结构

```
D:\项目文档\AIAssistive\ai\skills\data-skill\
├── SKILL.md                       # 本文件
├── tables\<表 code>.md × 20       # 静态 (构建期生成)
├── scripts\
│   ├── init_config.py             # 写 yml
│   ├── init_db.py                 # 建表
│   ├── update_config.py           # 改 yml
│   ├── parse_file.py              # OCR
│   ├── insert_record.py           # 入库
│   ├── list_sheets.py             # 列表
│   ├── build_inventory.py         # 建清单
│   ├── verify_inventory.py        # 核验
│   ├── _build_artifacts.py        # 构建期 (开发用, 发布可删)
│   └── validators\<表 code>.py × 20  # 静态 (构建期生成)
└── README.md
```

---

## 调用示例

```bash
# 首跑 (会触发 AskUserQuestion)
/data-skill D:\docs\农用地转用批复.pdf

# 批处理
/data-skill D:\docs\batch202606\

# 改配置
/data-skill --config "把 OCR 地址改成 http://10.0.0.5:30000"
```
