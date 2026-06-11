---
name: project-doc-write
description: Use when the user has an approved outline and wants the document body filled in based strictly on existing project artifacts (策划表/需求/合同/方案/周报 etc.) — generates 决策与意见 from real project data deltas, never invents content, asks user when info is missing
---

# Project Doc Write（填充内容 + 决策建议）

## ⚠️ 强约束: 不瞎编 (NO FABRICATION)

**本 skill 严禁**在执行过程中**任何**环节编造：
- 人名 / 日期 / 数字 / 工具名 / 角色签名表 / 文档状态 / 框架标签

**遇到证据缺失**：
1. 立即调 `../intent-clarification/` 走对应维度
2. 用户回答"待定" → 重新问"停止 / 提供详细信息"
3. 用户没指定 → **不写**，**不擅自填默认值**

**严禁**"写占位后续补"：
- ❌ `| XX | — |` / `| XX | TBD |` / `| XX | 待定 |` 单独使用
- ✅ `| XX | **待补**：<字段名> |` 必带说明

详见 `../intent-clarification/references/no_fabrication.md`。

> **阶段定位**：V1 基础能力版。

## 概述

在 `project-doc-outline` 输出的章节大纲上，**严格基于项目已有资料**填充正文，并基于策划表/合同/周报的实际值与基线值之差生成"决策与意见"。

> **核心原则：确定的事由脚本完成，需要判断的事由大模型完成。**
> 读取策划表子标签、抽取 docx 章节等"机械工作"走 `scripts/`，正文撰写与决策建议由模型完成。

---

## 触发条件

- 用户已有大纲（hub 生成或 outline 提供）
- 用户要求"按已有项目资料写完整文档"
- 用户要求"补全/更新某文档"

---

## 刚性约束

1. **严禁虚构**：所有正文内容必须有项目证据。证据缺失 → **主动询问**用户。
2. **格式范本**：默认从 `<项目根>/03_技术文档及评审/01_实施方案/*.docx` 抽取章节作为格式范本。
3. **决策与意见来源**：`references/决策建议生成规则.md` + `references/严禁虚构_红线清单.md`。
4. **多框架叠加**：每条决策与意见必须标注 `【框架：{PMP|PRINCE2|系统分析师} · {层次}】`。
5. **变更记录强制**：每次写完文档，**必须**在 `<项目根>/06_变更及暂停/变更记录.md` 追加一条记录（按策划表子标签规整格式）。
6. **读文件走 DocumentLoader**：禁止在 `tmp/` 或 `D:\` 根目录写一次性脚本读文件。
   走本 skill **自带的** `scripts/DocumentLoader.py`（**所有 .py 都在 `scripts/` 下**），不依赖外部包。
   8 个 Loader（Word/PDF/Text/Markdown/CSV/JSON/Eml/Excel）全部在 `scripts/loader/` 子包内。
7. **扫描件检测**：PDFLoader 提取文本 < 100 字符 → 视为扫描件 → 提示用户提供可读版。
8. **目录强制**：每个生成的 .md 文档**必须**含 `## 目录` 段，列 1-3 级标题链接（markdown 静态层）。
9. **内容净化**：写正文时遵守 `references/文档内容_净化规则.md`——不写"评审稿"、不写"编制/审核/批准"（策划表未指明时）、不写"—"占位、不写空话引用、不写项目资料未提及的工具。
10. **无数据章节**：用 `**待补**：[具体说明]` 模式，不写"—"占位；写前用 `references/数据完整性_询问模板.md` 主动询问用户。
11. **word 落盘**：.md 写完后**必须**通过"操作 word 的 skill"（如 docx-skill）转成 .docx 后落盘到项目目录。write **不**自己实现 markdown → docx，**不**硬编码调用第三方 skill 路径。详见 `references/word_落盘_流程.md`。

---

## 启动时环境自检（刚性约束）

执行任何读文件动作前，**必须**先运行本 skill 的 `scripts/check_env.py`：

```bash
python scripts/check_env.py
```

- 退出码 `0` → 环境就绪，继续后续动作
- 退出码 `1` → 缺 Python，按错误信息中的安装链接处理
- 退出码 `2` → 缺库且自动安装失败，按提示手动 `pip install -r scripts/requirements.txt`
- 退出码 `3` → 缺 `scripts/requirements.txt`，视为 skill 损坏

**严禁跳过自检**。Work agent 在执行任何读文件动作前必须先调用本脚本。

依赖清单（4 个必需库）：`openpyxl` / `python-docx` / `pypdf` / `chardet`。
可选依赖：`langchain_core`（缺失时 DocumentLoader 退化为轻量 Document 替身）。

---

## 核心流程

```
Step 1  接收大纲（来自 outline）
   ↓
Step 2  加载项目资料（DocumentLoader）
   ├─ 策划表 xlsm
   ├─ 需求/设计/合同 docx/pdf
   └─ 格式范本 docx（从 01_实施方案 取）
   ↓
Step 3  按章节顺序逐章填充
   ├─ 内容有证据 → 直接写
   ├─ 内容无证据 → 调 intent-clarification（B.data 维度，references/data_missing_section.md / numeric_field_missing.md）
   ├─ 数据驱动章节无数据 → 同上走 B.data
   ├─ 角色签名表/文档状态 → 调 intent-clarification（D.document_attr 维度，references/role_signoff.md / doc_status.md）
   └─ 内容超规范 → 提示超范围，询问是否保留
   ↓
Step 4  生成"决策与意见"章节（references/decision_advisory_template.md）
   ↓
Step 5  扫描件检测（references/扫描件_处理规则.md）
   ↓
Step 6  内容净化自检（references/文档内容_净化规则.md）
   ├─ 删"评审稿/草稿"等状态标签
   ├─ 删"编制/审核/批准"角色表（策划表未指定时）
   ├─ 删"—"占位 → 改"**待补**"段
   ├─ 删空话引用
   └─ 删项目资料未提及的工具/术语
   ↓
Step 7  输出（项目目录最终落盘 + AIAssistive\output\ 中间稿）
   ├─ 7.1 落 .md 到项目目录
   ├─ 7.2 【关键】检查"操作 word 的 skill"是否在当前 skill 库
   │       ├─ 存在 → 7.3
   │       └─ 不存在 → 提示用户安装 docx-skill，跳过 7.3
   ├─ 7.3 调 word skill 转 .docx（套用 references/word_格式范本_规则.md 的样式）
   ├─ 7.4 落中间稿到 AIAssistive\output\
   └─ 7.5 追加变更记录（references/变更记录_追加格式.md）
```

---

## 资源引用

- 格式范本提取方法：`references/实施方案_格式范本_提取说明.md`
- 软件工程文档章节填写规范：`references/软件工程文档_章节填写规范.md`
- 决策建议生成规则：`references/决策建议生成规则.md`
- 严禁虚构红线清单：`references/严禁虚构_红线清单.md`
- CLI 脚本使用速查（参数表 + 典型用例 + 排错）：`references/cli_脚本使用速查.md`
- **word 格式范本规则**（写死版，封面/字体/行间距/页眉页脚/目录）：`references/word_格式范本_规则.md`
- **word 落盘流程**（Step 7 详细说明，含 docx-skill 自检）：`references/word_落盘_流程.md`
- **文档内容净化规则**（不写"评审稿/—占位/编制审核"等废话）：`references/文档内容_净化规则.md`
- **数据完整性 reference**（Step 4.2.5 主动询问，由 intent-clarification 调度）：
  - `references/data_missing_section.md`
  - `references/numeric_field_missing.md`
- **文档属性 reference**（角色签名表/文档状态）：
  - `references/role_signoff.md`
  - `references/doc_status.md`
- 范本抽取脚本：`scripts/extract_docx_outline.py`（已配置为同 skill 内 import DocumentLoader + ExcelLoader）
- word 样式抽取脚本：`scripts/extract_word_style.py`（一次性从实施方案抽样式基准，输出 JSON）
- 元说明（套件内各 skill 介绍）：`../project-doc-overview/SKILL.md`
- 统一澄清协议：`../intent-clarification/SKILL.md`

---

## 反模式红线（刚性约束 · 2026-06-11 强化 · 写代码前先看）

**禁止**在 `python -c "..."` 或任何 Python 代码中使用：

- ❌ `from DocumentLoader import DocumentLoader, ExcelLoader, ...`
- ❌ `from loader.ExcelLoader import ExcelLoader` / `from loader.WordLoader import WordLoader` 等
- ❌ `import openpyxl` / `from openpyxl import load_workbook` 直接读 xlsm/xlsx
- ❌ `from docx import Document` 直接读 docx
- ❌ `from pypdf import PdfReader` 直接读 pdf
- ❌ `import csv` / `import json` / `import email` 直接读 csv/json/eml

**必须**改为调用本 skill `scripts/` 下的 CLI 脚本：

| 场景 | CLI |
|---|---|
| 读任意文件 | `python scripts/read_doc.py --file <path> [--sheet ...] [--keyword ...]` |
| 抽 docx 章节作格式范本 | `python scripts/extract_docx_outline.py --docx <path> --output <md>` |
| 抽 word 样式基准 | `python scripts/extract_word_style.py --docx <path> --output <json>` |

`read_doc.py` 自动按扩展名分发到对应 Loader，支持全部 8 种格式：xlsx/xlsm/docx/doc/pdf/txt/md/csv/json/eml。

### 快捷入口（避免你写临时脚本）

| 痛点 | 解决方案 |
|---|---|
| PowerShell 引号转义麻烦、路径太长 | 调 query skill 的 `dump_paths.py` 生成 `$VAR="..."`，`. (ps1)` 加载后用变量 |
| PowerShell 5.1 GBK 编码乱码 | `read_doc.py --output-file PATH` 写到文件，绕开控制台 |
| 想用 `\| Select-Object -First N` 截断 | `read_doc.py --max-rows N`（内置） |
| 想在 Python 里继续处理读出的内容 | `read_doc.py --output json --output-file PATH` 后用 LLM 读 JSON |

**违反此约束的代码视为反模式**，应重写为调用 CLI 脚本。

---

## 未来扩展

- 自动从历史同类文档反推模板
- AI 决策建议打分（与项目集/PMO 库联动）
- 多语言版本生成
