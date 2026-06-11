# project-doc-outline · CLI 脚本使用速查

> 本 skill 共有 1 个私有 CLI 脚本 + 1 个环境自检 + 1 套库。所有读项目文件的动作必须走 CLI，禁止 Python import。

## 0. 脚本清单

| 脚本 | 类型 | 用途 |
|---|---|---|
| `scripts/check_env.py` | CLI | 环境自检 |
| `scripts/extract_docx_outline.py` | CLI | **从项目内 docx 抽章节作为大纲格式范本** |
| `scripts/read_doc.py` | CLI | 读其他项目文件（Excel/PDF/CSV 等） |
| `scripts/DocumentLoader.py` | 库 | 通用文件加载（被 CLI 内部使用） |
| `scripts/loader/*.py` | 库 | 8 种格式 Loader（被 CLI 内部使用） |

> **重要**：extract_docx_outline.py 是 outline skill 的**私有脚本**，与 write skill 的 extract_docx_outline.py **同名独立副本**，不跨 skill 引用。

---

## 1. extract_docx_outline.py 完整说明

### 1.1 用途

从项目内的 .docx 文件抽取 Heading 1/2/3/4 标题，渲染为 markdown 格式范本。

供 outline 输出章节级大纲时参考"项目已有同类文档"的章节风格。

### 1.2 参数

| 参数 | 类型 | 默认 | 必填 | 说明 |
|---|---|---|---|---|
| `--docx` | PATH | — | 是 | docx 文件绝对路径 |
| `--output` | PATH | — | 是 | 输出 markdown 路径 |
| `--max-depth` | INT (1-4) | 4 | 否 | Heading 截断深度 |

### 1.3 输出格式

```markdown
# 格式范本：<文件名>

# 一级标题
## 二级标题
### 三级标题
#### 四级标题
```

### 1.4 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 文件不存在 |
| 3 | 抽取失败（python-docx 解析异常） |

### 1.5 用例

#### 1.5.1 抽取实施方案作格式范本

```bash
python scripts/extract_docx_outline.py \
    --docx "D:\项目文档\202410-C0008-...\03_技术文档及评审\01_实施方案\实施方案V1.0.docx" \
    --output "D:\...\AIAssistive\output\202410-C0008\格式范本_实施方案.md"
```

#### 1.5.2 仅看一二级标题

```bash
python scripts/extract_docx_outline.py --docx plan.docx --output out.md --max-depth 2
```

#### 1.5.3 抽取需求说明书作范本（fallback）

```bash
python scripts/extract_docx_outline.py \
    --docx "D:\...\02_需求\需求说明书V1.0.docx" \
    --output "D:\...\AIAssistive\output\202410-C0008\格式范本_需求.md"
```

---

## 2. read_doc.py 完整说明

> 本 skill 自带 read_doc.py，与 query skill 同名独立副本。

| 参数 | 说明 |
|---|---|
| `--file` | 必填，文件绝对路径 |
| `--output` | text / json / table |
| `--max-rows` | 默认 50 |
| `--keyword` | substring 过滤 |
| `--output-file` | 写到文件（绕开控制台乱码） |
| `--sheet` | Excel sheet 名（模糊匹配） |
| `--row-range` | 如 `5-20` |
| `--jq-schema` | JSON 路径 |
| `--encoding` / `--prefer-encoding` | 文本/邮件编码 |

完整参数表见 query 速查的对应章节（**本 skill 不重复**，命令语法完全一致）。

---

## 3. 反模式 → 正确写法 对照表

| 反模式 | 正确写法 |
|---|---|
| `python -c "from docx import Document; ..."` 抽章节 | `python scripts/extract_docx_outline.py --docx ... --output ...` |
| `python -c "from DocumentLoader import DocumentLoader, ExcelLoader; ..."` | `python scripts/read_doc.py --file ...` |
| 引用 write skill 的 extract_docx_outline.py | 用 outline 本地副本（高内聚低耦合） |
| 直接复制整篇 docx 正文到大纲里 | 用本 CLI 抽章节标题，正文留 write 阶段处理 |
| 引用 query 的 read_doc.py | outline 已自带，无需跨 skill 引用 |

---

## 4. 常见问题 FAQ

**Q: outline 抽出来的格式范本和最终大纲是什么关系？**
A: 范本是参考"项目内同类文档的章节风格"，大纲仍按 `references/outline_*.md` 模板生成。

**Q: 为什么 outline 不直接调用 write 的脚本？**
A: 高内聚低耦合原则。每个 skill 拥有完整工具集，不依赖其他 skill。

**Q: --max-depth 选几合适？**
A: 通常 2-3。`1`=只大纲，`4`=细节全要。

**Q: 抽取后中文乱码？**
A: 本 CLI 写入 markdown 走 UTF-8，不会乱码；如用 Read 工具查看 raw bytes 看到乱码，是工具问题不是脚本问题。
