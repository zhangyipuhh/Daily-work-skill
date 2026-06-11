---
name: project-doc-outline
description: Use when the user wants a chapter outline (no body content) for any of the 10 supported software-engineering deliverable types (售前方案/需求说明书/概要设计/详细设计/实施方案/测试方案/测试报告/验收报告/实施部署方案/培训方案) — picks the corresponding reference template and applies software-engineering standard chapter structure
---

# Project Doc Outline（文档大纲）

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

按目标文档类型挑选对应 reference 模板，输出**章节级大纲**（不含正文内容）。

大纲必须符合软件工程规范（GB/T 8564、ISO/IEC/IEEE 42010、ISO 21500），并**不包含任何虚构正文**。

---

## 触发条件

- 用户说"写个测试方案大纲"
- 用户说"实施方案应该有哪些章节"
- 用户提供目标文档类型 + 需要"先看大纲"

## 不适用

- 用户要求"完整文档"（切到 `project-doc-write`）
- 用户只问"项目有什么文档"（切到 `project-doc-query`）

---

## 刚性约束

1. **大纲 ≠ 正文**：只输出章节标题（一级/二级），不写正文
2. **章节编号规范**：一级 1、2、3；二级 1.1、1.2；三级 1.1.1（如必要）
3. **每章必须说明**：用途（这一章解决什么问题）+ 必备小节（如有规范）
4. **参考范本来源**：默认从 `<项目根>/03_技术文档及评审/01_实施方案/*.docx` 抽取章节；为空则回退到 02 需求 → 03 概要
5. **抽取脚本**：用 `scripts/extract_docx_outline.py` 走 DocumentLoader
6. **环境/技术/合规澄清必走**：写大纲前**必须**调 `intent-clarification`（C.environment 维度，10 个技术点 reference：tech_hardware.md / tech_software.md / tech_database.md / tech_network.md / tech_deployment.md / tech_third_party_ops.md / tech_security_level.md / tech_localization.md / tech_architecture.md / tech_localization_list.md）
   - 即使用户已上传资料，**也要询问**并完整引用原文 + 标注来源文件 + 行号，让用户确认"是否根据已有信息写"
   - 用户回答"待定" → 再次询问"是否停止大纲生成 / 提供详细信息"
   - 询问结果记录到 `.project/<项目号>/clarification_log.md`
   - 跳过此步直接写大纲视为反模式

---

## 支持的 10 种文档类型

| # | 类型 | reference 模板 |
|---|---|---|
| 1 | 售前方案 | `references/outline_售前方案.md` |
| 2 | 需求说明书 | `references/outline_需求说明书.md` |
| 3 | 概要设计说明书 | `references/outline_概要设计说明书.md` |
| 4 | 详细设计说明书 | `references/outline_详细设计说明书.md` |
| 5 | 实施方案 | `references/outline_实施方案.md` |
| 6 | 测试方案 | `references/outline_测试方案.md` |
| 7 | 测试报告 | `references/outline_测试报告.md` |
| 8 | 验收报告 | `references/outline_验收报告.md` |
| 9 | 实施部署方案 | `references/outline_实施部署方案.md` |
| 10 | 培训方案 | `references/outline_培训方案.md` |
| — | 其他过程文档 | `references/outline_其他过程文档.md` |

---

## 核心流程

```
Step 0  【必走】调 intent-clarification（环境/技术/合规 10 个技术点）
   ↓
Step 1  接收目标文档类型
   ↓
Step 2  加载对应 reference 模板
   ↓
Step 3  （可选）从项目已有同类 docx 抽取格式范本（extract_docx_outline.py）
   ↓
Step 4  输出"章节级"大纲（不写正文）
   ↓
Step 5  在每章末标注"用途"和"必备小节"提示
   ↓
Step 6  调 manage_project_log.py append-operation 写主日志
```

---

## 资源引用

- 10 个 outline reference：`references/outline_*.md`
- 10 个技术点 reference（由 intent-clarification 调度）：`references/tech_*.md`
- CLI 脚本使用速查（参数表 + 典型用例 + 排错）：`references/cli_脚本使用速查.md`
- 范本抽取脚本：`scripts/extract_docx_outline.py`（outline skill 自带，调用本 skill 的 DocumentLoader + loader.ExcelLoader）
- 元说明（套件内各 skill 介绍）：`../project-doc-overview/SKILL.md`
- 统一澄清协议：`../intent-clarification/SKILL.md`

---

## 反模式红线（刚性约束 · 2026-06-11 强化 · 写代码前先看）

**禁止**在 `python -c "..."` 或任何 Python 代码中使用：

- ❌ `from DocumentLoader import DocumentLoader, ExcelLoader, ...`
- ❌ `from loader.ExcelLoader import ExcelLoader` / `from loader.WordLoader import WordLoader` 等
- ❌ `import openpyxl` / `from openpyxl import load_workbook` 直接读 xlsm/xlsx
- ❌ `from docx import Document` 直接读 docx（用于抽章节时）
- ❌ `import csv` / `import json` 直接读 csv/json

**必须**改为调用本 skill `scripts/` 下的 CLI 脚本：

| 场景 | CLI |
|---|---|
| 抽项目内 docx 章节作格式范本 | `python scripts/extract_docx_outline.py --docx <path> --output <md>` |
| 读其他项目文件 | `python scripts/read_doc.py --file <path> [--sheet ...] [--keyword ...]` |

### 快捷入口（避免你写临时脚本）

| 痛点 | 解决方案 |
|---|---|
| PowerShell 引号转义麻烦、路径太长 | 调 query skill 的 `dump_paths.py` 生成 `$VAR="..."` |
| PowerShell 5.1 GBK 编码乱码 | `read_doc.py --output-file PATH` 写到文件 |
| 想用 `\| Select-Object -First N` 截断 | `read_doc.py --max-rows N`（内置） |

**违反此约束的代码视为反模式**，应重写为调用 CLI 脚本。

---

## 未来扩展

- 不同行业（政务/金融/医疗）的行业版大纲
- 自动从策划表 WBS 反推项目阶段文档结构
