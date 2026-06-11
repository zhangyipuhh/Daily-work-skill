# project-doc-query · CLI 脚本使用速查

> 本 skill 共有 3 个 CLI 脚本 + 1 个环境自检脚本。所有读项目文件的动作必须走 CLI，禁止 Python import。

## 0. 脚本清单

| 脚本 | 类型 | 用途 |
|---|---|---|
| `scripts/check_env.py` | CLI | 环境自检（依赖库是否齐备） |
| `scripts/read_doc.py` | CLI | **万能文件读取**（按扩展名自动分发到 8 种 Loader） |
| `scripts/find_planning_sheet.py` | CLI | 定位项目根下最新版策划表 xlsm |
| `scripts/scan_project_root.py` | CLI | 扫描项目根目录，列文件清单 |
| `scripts/DocumentLoader.py` | 库 | 通用文件加载（被 CLI 内部使用） |
| `scripts/loader/*.py` | 库 | 8 种格式 Loader（被 CLI 内部使用） |

> **重要**：DocumentLoader 与 8 个 Loader 是**库**，**禁止**在 Python 代码中 import 它们。读文件必须走 `read_doc.py`。

---

## 1. read_doc.py 完整说明

### 1.1 用途

按扩展名自动分发到 DocumentLoader 下的 8 个 Loader，支持：

- `.xlsx` / `.xlsm` → ExcelLoader
- `.docx` / `.doc` → WordLoader
- `.pdf` → PDFLoader
- `.txt` → TextLoader
- `.md` / `.markdown` → MarkdownLoader
- `.csv` → CSVLoader
- `.json` → JSONLoader
- `.eml` → EmlLoader

### 1.2 通用参数（所有格式适用）

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `--file` | PATH | 必填 | 文件绝对路径 |
| `--output` | text/json/table | text | 输出格式 |
| `--output-file` | PATH | None | 写入文件（绕开 Windows 控制台 GBK 编码） |
| `--max-rows` | INT | 50 | 最大输出片段数（0=不限） |
| `--keyword` | TEXT | None | page_content substring 过滤（不区分大小写） |

### 1.3 按扩展名分发的透传参数

| 扩展名 | 参数 | 透传到 |
|---|---|---|
| `.xlsx` `.xlsm` | `--sheet` (sheet 名，模糊匹配) | `ExcelLoader(sheet_name=)` |
| `.xlsx` `.xlsm` | `--row-range` (如 `5-20`) | `ExcelLoader(row_range=)` |
| `.xlsx` `.xlsm` | `--include-hidden` (flag) | `ExcelLoader(include_hidden=True)` |
| `.json` | `--jq-schema` (如 `.data.items`) | `JSONLoader(jq_schema=)` |
| `.json` | `--text-content` (flag) | `JSONLoader(text_content=True)` |
| `.txt` `.csv` | `--encoding` | `TextLoader/CSVLoader(encoding=)` |
| `.eml` | `--prefer-encoding` | `EmlLoader(prefer_encoding=)` |

### 1.4 输出格式

| `--output` | 说明 |
|---|---|
| `text` | 默认，逐片段输出 `--- 片段 N --- [metadata] + page_content` |
| `json` | 结构化 JSON，含 index / page_content / metadata |
| `table` | markdown 表格（仅 Excel/CSV 风格数据友好，文本行以 `\t` 分隔时自动解析为表格） |

### 1.5 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 文件不存在 |
| 2 | 不支持的扩展名 |
| 3 | 加载异常（文件被锁/损坏） |
| 4 | 无匹配结果（按 sheet/keyword 过滤后为空） |

---

## 2. find_planning_sheet.py 完整说明

### 2.1 用途

在 `<项目根>/01_项目策划/` 下按 glob 模式找策划表 xlsm，**按版本号降序排序**。

### 2.2 参数

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `--project-root` | PATH | 必填 | 项目根目录绝对路径 |
| `--pattern` | GLOB | `*策划表V*.xlsm` | 匹配模式 |
| `--output` | path/info/json | path | path=输出绝对路径（便于管道）；info=人类可读；json=结构化 |

### 2.3 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 项目根目录不存在 |
| 4 | 未找到匹配项 |

---

## 3. scan_project_root.py 完整说明

### 3.1 用途

扫描项目根目录（或指定子目录），按扩展名过滤列文件清单。

### 3.2 参数

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `--project-root` | PATH | 必填 | 项目根目录 |
| `--subdir` | NAME | None | 子目录名（支持多级，如 `03_技术文档及评审/01_实施方案`） |
| `--ext` | LIST | None | 扩展名过滤，逗号分隔（如 `.docx,.pdf`） |
| `--output` | list/json/table | list | 输出格式 |
| `--output-file` | PATH | None | 写入文件 |

> 自动跳过 `~$` 开头的 Excel 临时锁文件。

---

## 4. 典型用例

### 4.1 评审计划提取（最常见）

```bash
# 一步：定位 + 读
python scripts/find_planning_sheet.py --project-root "D:\项目文档\202410-C0008-..." --output path
# → D:\...\策划表V1.0.xlsm

python scripts/read_doc.py --file "D:\...\策划表V1.0.xlsm" --sheet 评审计划 --output table
```

### 4.2 Excel 行级关键字过滤

```bash
# 找"张三"参与的所有行
python scripts/read_doc.py --file "D:\...\策划表V1.0.xlsm" --sheet 评审计划 --keyword 张三 --output table
```

### 4.3 Excel 行号范围

```bash
# 只看第 5-20 行
python scripts/read_doc.py --file "D:\...\策划表V1.0.xlsm" --sheet 评审计划 --row-range 5-20
```

### 4.4 PDF 抽文本（扫描件检测）

```bash
python scripts/read_doc.py --file "D:\...\需求.pdf" --output json
# 输出 metadata 中 is_scanned=true 表示扫描件
```

### 4.5 DOCX 段落抽取

```bash
python scripts/read_doc.py --file "D:\...\实施方案.docx" --max-rows 30
```

### 4.6 CSV 转 markdown 表格

```bash
python scripts/read_doc.py --file "D:\...\成本.csv" --output table
```

### 4.7 JSON 按 jq schema 取字段

```bash
python scripts/read_doc.py --file "D:\...\接口.json" --jq-schema ".data.items" --output json
```

### 4.8 EML 读邮件头

```bash
python scripts/read_doc.py --file "D:\...\会议通知.eml" --output text
# 主题/发件人/收件人/日期/正文 5 段
```

### 4.9 扫描项目根目录的实施方案

```bash
python scripts/scan_project_root.py --project-root "D:\项目文档\202410-C0008-..." --subdir 03_技术文档及评审/01_实施方案 --ext .docx --output table
```

### 4.10 输出到文件绕开控制台乱码

```bash
python scripts/read_doc.py --file "D:\...\策划表V1.0.xlsm" --sheet 评审计划 --output table --output-file D:\review_plan.md
```

### 4.11 链式管道（find → read）

```powershell
$plan = python scripts/find_planning_sheet.py --project-root "D:\项目文档\202410-C0008-..." --output path
python scripts/read_doc.py --file $plan.Trim() --sheet 评审计划 --output table
```

### 4.12 完整工作流（推荐路径）

```powershell
# 1. 生成项目路径变量
python scripts/dump_paths.py --project-root "D:\项目文档\202410-C0008-..." --format ps1 --output-file D:\paths.ps1

# 2. 加载到 PowerShell
. D:\paths.ps1

# 3. 用变量直接调 read_doc.py
python scripts/read_doc.py --file $PLANNING_SHEET_LATEST --sheet 评审计划 --output json --output-file D:\review.json
```

---

## 5. dump_paths.py 完整说明

### 5.1 用途

一键输出项目根的常用路径（策划表/项目目录/邮件/输出/变更记录等），
输出格式为 PowerShell 变量赋值，可直接 `. (path.ps1)` 加载到当前 shell。

**解决的痛点**：PowerShell 长路径/中文路径/空格路径 → 引号转义麻烦。

### 5.2 参数

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `--project-root` | PATH | 必填 | 项目根目录 |
| `--format` | ps1 | ps1 | 输出格式（当前仅 ps1） |
| `--output-file` | PATH | None | 写到文件（推荐，避免控制台乱码） |

### 5.3 用例

```bash
# 加载到 PowerShell 后用变量
. (python scripts/dump_paths.py --project-root "D:\项目文档\202410-C0008-..." --format ps1)
python scripts/read_doc.py --file $PLANNING_SHEET_LATEST --output json

# 或者直接写到文件再 . 加载
python scripts/dump_paths.py --project-root "D:\项目文档\..." --format ps1 --output-file D:\paths.ps1
. D:\paths.ps1
python scripts/read_doc.py --file $PLANNING_SHEET_LATEST --output json
```

### 5.4 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 成功（含策划表） |
| 1 | 项目根不存在 |
| 2 | 找不到策划表（其他变量仍输出，警告到 stderr） |

### 5.5 输出的变量

| 变量 | 说明 |
|---|---|
| `$PROJECT_ROOT` | 项目根目录 |
| `$PROJECT_ID` | 项目编号（如 202410-C0008） |
| `$PLANNING_DIR` | 01_项目策划 目录 |
| `$PLANNING_SHEET_LATEST` | 最新版策划表 xlsm 绝对路径 |
| `$PLANNING_SHEET_OLD` | 次新版策划表 xlsm 绝对路径（多个时） |
| `$REVIEW_DIR` | 03_技术文档及评审 目录 |
| `$EMAIL_DIR` | 邮件存放目录（通常 = PLANNING_DIR） |
| `$OUTPUT_DIR` | AIAssistive\output\<项目号>\ 中间稿目录 |
| `$CHANGE_LOG` | 06_变更及暂停\变更记录.md 路径 |

---

## 6. 反模式 → 正确写法 对照表

| 反模式 | 正确写法 |
|---|---|
| `python -c "from DocumentLoader import DocumentLoader, ExcelLoader; ..."` | `python scripts/read_doc.py --file ...` |
| `python -c "from openpyxl import load_workbook; ..."` | `python scripts/read_doc.py --file ... --sheet ...` |
| `python -c "from docx import Document; ..."` | `python scripts/read_doc.py --file ...` |
| `python -c "from pypdf import PdfReader; ..."` | `python scripts/read_doc.py --file ...` |
| 在 `tmp/` 或 `D:\` 根目录写一次性脚本读文件 | 用本 skill 的 `scripts/` CLI |

---

## 7. 常见问题 FAQ

**Q: Windows PowerShell 输出乱码？**
A: 用 `--output-file PATH` 写到文件，绕过控制台编码；或升级到 PowerShell 7。

**Q: `--sheet 评审计划` 找不到？**
A: read_doc.py 自动模糊匹配，关键词含「评审」/「Review」/「Plan」即可。匹配不到时退出码 4 并打印所有可用 sheet 名。

**Q: 想批量读多个 sheet？**
A: read_doc.py 单次只支持单 sheet。多次调用即可（每次换 `--sheet`）。

**Q: ExcelLoader 的 3 个新参数（sheet_name/keyword/row_range）能否直接用库？**
A: 能，但属于"内部使用"，CLI 优先。库 API 仅供 CLI 内部 import。
