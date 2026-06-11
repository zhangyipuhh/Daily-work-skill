# project-doc-write · CLI 脚本使用速查

> 本 skill 共有 1 个私有 CLI + 1 套库。读任意项目文件用本 skill 自带的 read_doc.py；抽 docx 章节用 extract_docx_outline.py。

## 0. 脚本清单

| 脚本 | 类型 | 用途 |
|---|---|---|
| `scripts/check_env.py` | CLI | 环境自检 |
| `scripts/extract_docx_outline.py` | CLI | **抽 docx 章节作格式范本**（write 私有副本） |
| `scripts/read_doc.py` | CLI | 读其他项目文件（Excel/PDF/CSV/邮件 等） |
| `scripts/DocumentLoader.py` | 库 | 通用文件加载 |
| `scripts/loader/*.py` | 库 | 8 种格式 Loader |

> extract_docx_outline.py 在 write 和 outline 两个 skill 下**各有 1 份独立副本**。

---

## 1. extract_docx_outline.py（write 私有副本）

| 参数 | 类型 | 默认 | 必填 | 说明 |
|---|---|---|---|---|
| `--docx` | PATH | — | 是 | docx 文件绝对路径 |
| `--output` | PATH | — | 是 | 输出 markdown 路径 |
| `--max-depth` | INT (1-4) | 4 | 否 | Heading 截断深度 |

### 退出码：0 成功 / 1 文件不存在 / 3 抽取失败

### 用例

```bash
# 抽实施方案作格式范本
python scripts/extract_docx_outline.py \
    --docx "D:\项目文档\202410-C0008-...\03_技术文档及评审\01_实施方案\实施方案V1.0.docx" \
    --output "D:\...\AIAssistive\output\202410-C0008\格式范本.md"

# 仅一二级
python scripts/extract_docx_outline.py --docx plan.docx --output out.md --max-depth 2
```

---

## 2. read_doc.py（write 自带副本）

参数与 query skill 完全一致：

| 参数 | 说明 |
|---|---|
| `--file` | 必填 |
| `--output` | text / json / table |
| `--max-rows` | 默认 50 |
| `--keyword` | substring 过滤 |
| `--output-file` | 写到文件 |
| `--sheet` / `--row-range` / `--include-hidden` | Excel 专用 |
| `--jq-schema` / `--text-content` | JSON 专用 |
| `--encoding` / `--prefer-encoding` | 文本/邮件 |

### write 场景常见用法

#### 2.1 读策划表抽评审计划

```bash
python scripts/read_doc.py --file "D:\...\策划表V1.0.xlsm" --sheet 评审计划 --output table
```

#### 2.2 读需求 docx 取证据

```bash
python scripts/read_doc.py --file "D:\...\需求说明书V1.0.docx" --max-rows 100 --output text
```

#### 2.3 读 PDF（注意扫描件）

```bash
python scripts/read_doc.py --file "D:\...\需求.pdf" --output json
# metadata 中 is_scanned=true 表示扫描件，需提示用户提供可读版
```

#### 2.4 读邮件

```bash
python scripts/read_doc.py --file "D:\...\客户反馈.eml" --output text
```

---

## 3. 反模式 → 正确写法 对照表

| 反模式 | 正确写法 |
|---|---|
| `python -c "from docx import Document; for p in doc.paragraphs: ..."` 抽章节 | `python scripts/extract_docx_outline.py --docx ... --output ...` |
| `python -c "from DocumentLoader import DocumentLoader; docs = loader.load()"` | `python scripts/read_doc.py --file ...` |
| 引用 outline skill 的 extract_docx_outline.py | 用 write 本地副本（高内聚） |
| 引用 query 的 read_doc.py | write 已自带 |
| 在 Python 里 `open(file, encoding='utf-8').read()` | `python scripts/read_doc.py --file ...` |

---

## 4. 常见问题 FAQ

**Q: write 流程什么时候用 read_doc.py？**
A: Step 2 加载项目资料时（策划表 / 需求 / 设计 / 合同 / 邮件），用 read_doc.py 替代 Python import。

**Q: write 的 extract_docx_outline.py 和 outline 的有何区别？**
A: 当前**功能完全一致**（两个独立副本）。write 抽出来用作 Step 3 的"格式范本"，outline 抽出来用作 Step 3 的"项目内同类文档风格参考"。

**Q: PDFLoader 提取文本 < 100 字符时怎么办？**
A: 视为扫描件，提示用户提供可读版（docx/md/txt）。**禁止**用 OCR/PDF 图像识别等越界手段。
