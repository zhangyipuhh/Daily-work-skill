---
name: project-doc-query
description: Use when the user asks questions about a software-engineering project's documents, milestones, deliverables, review schedule, or wants PMO-level advisory — applies three-layer framework overlay (PMP framework layer + PRINCE2落地层 + 系统分析师实务层) and forces intent-clarification (fact vs decision) before answering
---

# Project Doc Query（查询 / 咨询）

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

> **阶段定位**：本 skill 当前为 **V1 基础能力版**，未来会扩展到项目集/敏捷/量化管理。

---

## ⚠️ 反模式红线（写代码前先看 · 2026-06-11 强化）

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
| 找最新版策划表 | `python scripts/find_planning_sheet.py --project-root <path>` |
| 扫项目目录 | `python scripts/scan_project_root.py --project-root <path> [--subdir ...] [--ext ...]` |
| 输出项目根常用路径 | `python scripts/dump_paths.py --project-root <path> --format ps1` |

`read_doc.py` 自动按扩展名分发到对应 Loader，支持全部 8 种格式：xlsx/xlsm/docx/doc/pdf/txt/md/csv/json/eml。

### 快捷入口（避免你写临时脚本）

| 痛点 | 解决方案 |
|---|---|
| PowerShell 引号转义麻烦、路径太长 | 用 `dump_paths.py` 生成 `$VAR="..."`，`. (ps1)` 加载后用变量 |
| PowerShell 5.1 GBK 编码乱码 | `read_doc.py --output-file PATH` 写到文件，绕开控制台 |
| 想用 `\| Select-Object -First N` 截断 | `read_doc.py --max-rows N`（内置） |
| 想用 `\| Where-Object` 过滤 | `read_doc.py --keyword xxx`（page_content 维度过滤） |
| 想在 Python 里继续处理读出的内容 | `read_doc.py --output json --output-file PATH` 后用 LLM 读 JSON |

**违反此约束的代码视为反模式**，应重写为调用 CLI 脚本。

---

## 概述

对软件工程项目的**事实/数据**与**决策建议**两类问题，按 **PMP + PRINCE2 + 系统分析师 三层框架叠加**给出答案。

回答前**必须**先做"意图澄清"（事实 vs 决策）；回答中**必须**显式标注所用框架。

---

## 触发条件

- 用户问"项目里有什么 / 什么时候交 / 谁负责 / 评审怎么安排"
- 用户问"这个文档应该包含什么 / 测试覆盖率怎么定 / 风险如何应对"
- 用户希望获取 PMO 层面的咨询意见

---

## 刚性约束

1. **澄清必走 intent-clarification**：本 skill 启动时**必须**调 `intent-clarification` skill（详见 references/intent.md）。**禁止**在 SKILL.md 内联问"事实/决策"或"项目根"。
2. **强制框架标签**：每条回答首行输出 `【框架：{PMP|PRINCE2|系统分析师} · {框架层|落地层|实务层}】`。
3. **证据可追溯**：所有事实类回答必须附"项目证据"——策划表子标签名 + 文档路径 + 行/单元格。
4. **三层框架叠加**（互不冲突）：
   - **PMP 框架层**：5 过程组 / 10 知识领域（给"管理体系全景"）
   - **PRINCE2 落地层**：7 原则 / 7 主题 / 7 流程（给"具体怎么做"）
   - **系统分析师 实务层**：5 大模块（系统规划/需求分析/系统设计/测试与维护/信息化）（给"软件工程实际"）
5. **严禁虚构**：回答中所有数字、日期、人名必须来自项目资料；缺资料时调 `intent-clarification` 走 data 维度。

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
Step 1  调 intent-clarification skill（澄清意图 + 项目根 + 范围）
   ├─ 5 个子项见 references/intent.md
   └─ 必要时流程中再问（澄清可重入）
   ↓
Step 2  按目录规则加载项目资料（DocumentLoader）
   ↓
Step 3  若事实/数据：直接给数据 + 证据
         若决策：选框架 → 引用框架速查表 → 给建议（带项目证据）
   ↓
Step 4  标注框架标签 + 数据来源
   ↓
Step 5  调 manage_project_log.py append-operation 写主日志
```

---

## 框架选用决策树

| 场景 | 优先框架 | 层次 |
|---|---|---|
| 评审/交付物安排 | PMP · 框架层（进度管理） | + PRINCE2 落地层（管理阶段边界） |
| 范围/变更控制 | PRINCE2 · 落地层（变更主题） | + PMP（范围/变更/综合） |
| 质量/测试 | 系统分析师 · 实务层（测试与维护） | + PMP（质量管理） + PRINCE2（质量主题） |
| 风险 | PMP · 框架层（风险管理） | + PRINCE2（风险主题） |
| 资源/成本 | PMP · 框架层（资源/成本） | + PRINCE2（商业论证主题） |
| 需求分析 | 系统分析师 · 实务层（需求分析） | + PMP（范围） |
| 架构/设计 | 系统分析师 · 实务层（系统设计） | + PMP（范围/进度） |
| 实施/部署 | 系统分析师 · 实务层（实施运维） | + PMP（执行） + PRINCE2（交付主题） |
| 收尾/验收 | PMP · 框架层（收尾过程组） | + PRINCE2（持续业务验证） |

---

## 关键文件加载方式

- 走本 skill **自带的** `scripts/DocumentLoader.py`（**所有 .py 都在 `scripts/` 下**）
- 8 个 Loader 全部在 `scripts/loader/` 子包内（Word/PDF/Text/Markdown/CSV/JSON/Eml/Excel）
- PDF / eml 提取文本 < 100 字符视为扫描件 → 提示用户提供可读版

---

## 资源引用

- 流程澄清（intent 5 子项，由 intent-clarification 调度）：`references/intent.md`
- 框架速查表：`references/framework_pmp_速查.md`、`references/framework_prince2_速查.md`、`references/framework_系统分析师_速查.md`
- 框架选用决策树：`references/框架选用决策树.md`
- 策划表字段速查：`references/策划表_字段速查.md`
- 文档类型目录速查：`references/文档类型_目录速查.md`
- 评审计划提取方法：`references/评审计划_提取方法.md`
- CLI 脚本使用速查（参数表 + 典型用例 + 排错）：`references/cli_脚本使用速查.md`
- 元说明（套件内各 skill 介绍）：`../project-doc-overview/SKILL.md`
- 统一澄清协议：`../intent-clarification/SKILL.md`

---

## ⚠️ 反模式红线（写代码前先看 · 2026-06-11 强化）

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
| 找最新版策划表 | `python scripts/find_planning_sheet.py --project-root <path>` |
| 扫项目目录 | `python scripts/scan_project_root.py --project-root <path> [--subdir ...] [--ext ...]` |
| 输出项目根常用路径 | `python scripts/dump_paths.py --project-root <path> --format ps1` |

`read_doc.py` 自动按扩展名分发到对应 Loader，支持全部 8 种格式：xlsx/xlsm/docx/doc/pdf/txt/md/csv/json/eml。

### 快捷入口（避免你写临时脚本）

| 痛点 | 解决方案 |
|---|---|
| PowerShell 引号转义麻烦、路径太长 | 用 `dump_paths.py` 生成 `$VAR="..."`，`. (ps1)` 加载后用变量 |
| PowerShell 5.1 GBK 编码乱码 | `read_doc.py --output-file PATH` 写到文件，绕开控制台 |
| 想用 `\| Select-Object -First N` 截断 | `read_doc.py --max-rows N`（内置） |
| 想用 `\| Where-Object` 过滤 | `read_doc.py --keyword xxx`（page_content 维度过滤） |
| 想在 Python 里继续处理读出的内容 | `read_doc.py --output json --output-file PATH` 后用 LLM 读 JSON |

**违反此约束的代码视为反模式**，应重写为调用 CLI 脚本。

---

## 未来扩展（预留）

- 项目集/项目组合（PgMP/MSP）
- 敏捷双轨（Scrum/SAFe）
- 量化管理（QPM/CMMI）
- AI 辅助决策（基于历史项目数据库）
