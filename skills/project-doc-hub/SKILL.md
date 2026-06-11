---
name: project-doc-hub
description: Use when the user wants to create, query, or update software-engineering project deliverables (实施方案/需求说明书/概要设计/详细设计/测试方案/测试报告/验收报告/实施部署/培训方案等) under a project root such as D:\项目文档\202410-C0008-... — acts as the entry point that dispatches to project-doc-query/outline/write/workflow
---
# Project Doc Hub（项目管理 Skill V1 · 总入口）

> **阶段定位**：本套件当前为 **V1 基础能力版**，未来会持续扩展（PMP/PRINCE2/系统分析师 多框架叠加，详见各子 skill 的"未来扩展"）。

## 概述

受理用户关于"软件工程项目文档"的需求，作为总入口调度：

1. `project-doc-query` —— 回答"项目里有什么/什么时候交/评审节点"等问题
2. `project-doc-outline` —— 按目标文档类型生成符合软件工程规范的章节大纲
3. `project-doc-write` —— 严格基于项目资料填充大纲 + 生成决策意见
4. `project-doc-workflow` —— 编排 4 步流水线检查清单

> 提示：本 skill 是**调度层**，不直接写文档；写文档在 `project-doc-write` 内完成。

---

## 触发条件（When to use）

- 用户提及"项目"+"文档"+"生成/查询/更新"等意图（如"写一份测试方案""实施方案大纲""什么时候评审"）
- 用户提供了项目根目录路径（如 `D:\项目文档\202410-C0008-...`）
- 用户使用本套件术语（"项目过程文档""策划表""实施方案""概要设计"等）

---

## 核心流程（调度）

```
Step 1  受理需求
   ↓
Step 2  澄清：项目根目录 + 目标文档类型 + 意图（查询/生成/更新）
   ↓ （如未指定项目，列出根目录下所有项目让用户选）
Step 3  加载并激活相应子 skill
   ├─ 仅查询/咨询 → project-doc-query
   ├─ 仅大纲     → project-doc-outline
   ├─ 生成文档   → project-doc-workflow（自动串联 query→outline→write）
   └─ 更新文档   → project-doc-write（增量模式）
   ↓
Step 4  收集输出位置确认（项目目录 vs 中间稿）
   ↓
Step 5  汇报产物路径
```

---

## 关键文件加载方式（刚性约束）

- **所有读文件动作必须走** 各 skill **自带的** `scripts/DocumentLoader.py`：
  - 项目咨询类走 `project-doc-query/scripts/DocumentLoader.py`
  - 文档生成类走 `project-doc-write/scripts/DocumentLoader.py`
- 禁止在 `tmp/` 或 `D:\` 根目录写一次性脚本读文件
- 禁止以"按扩展名直接 `open()`"绕开 DocumentLoader

---

## 强制澄清项（与用户对话前必走 intent-clarification）

**禁止**在 hub SKILL.md 内联问。**必须**调 `intent-clarification` skill（详见 `../intent-clarification/SKILL.md` + `../project-doc-query/references/intent.md`）。

### Step 0: 场景分流（必走 · 第一步）

**用户问题进来第一件事**：识别场景类型。

| 场景 | 用户话术特征 | 必走的询问维度 |
|---|---|---|
| `A0.technical_doc` | "写 XX 方案/设计/测试/部署/培训" | A.intent (doc_type) + C.environment (10 个技术点) |
| `A0.administrative` | "变更记录/周报/纪要" | A.intent (doc_type) + D.document_attr |
| `A0.factual_query` | "什么时候/谁/多少/在哪" | A.intent (fact/decision) |
| `A0.advisory` | "建议/应该/哪种/怎么选" | A.intent (decision) + 三层框架 |

**关键**：技术文档场景必须问技术细节（10 个 C.environment 技术点），不能跳过。

### Step 1: 5 个 intent 维度子项

澄清项共 5 个子项（intent 维度）：
1. 事实/决策（intent_fact_or_decision）
2. 范围（scope_project_or_industry）
3. 项目根目录（project_root）
4. 目标文档类型（doc_type）
5. 意图（action_intent：查询 / 生成 / 更新 / 删除）

---

## 输出位置规范

| 输出         | 位置                                                         |
| ------------ | ------------------------------------------------------------ |
| 最终正式文档 | `<项目根>/03_技术文档及评审/<对应子目录>/<文档名>.md`      |
| 变更记录     | `<项目根>/06_变更及暂停/变更记录.md`（追加）               |
| 中间稿/草稿  | `D:\项目文档\AIAssistive\output\<项目号>\<文档名>_草稿.md` |

---

## 未来扩展（预留，不实现）

- 项目集/项目组合管理（PgMP/MSP）
- 敏捷双轨（Scrum/SAFe）
- 量化项目管理（QPM/CMMI）
- AI 辅助决策（基于历史项目数据库）

---

## 资源引用

- 项目根目录与子目录对应表：`references/project_root_index.md`
- 策划表子标签说明模板：`references/策划表子标签说明模板.md`
- 决策意见模板：`references/decision_advisory_template.md`
- 文档加载器（每个使用 skill 自带，无 shared 共享包，**所有 .py 都在 `scripts/` 下**）：
  - 查/咨询类走 `../project-doc-query/scripts/DocumentLoader.py`
  - 写/生成类走 `../project-doc-write/scripts/DocumentLoader.py`
  - 大纲类走 `../project-doc-outline/scripts/DocumentLoader.py`
- 8 个 Loader 子包（与 DocumentLoader 同 skill 配套，全部在 `scripts/loader/` 下）：
  - `../project-doc-query/scripts/loader/` 包含 `WordLoader / PDFLoader / TextLoader / MarkdownLoader / CSVLoader / JSONLoader / EmlLoader / ExcelLoader`
  - `../project-doc-write/scripts/loader/` 同上
  - `../project-doc-outline/scripts/loader/` 同上
- 子 skill 脚本使用速查（参数表 + 典型用例 + 排错 + 反模式对照）：
  - 查询类：`../project-doc-query/references/cli_脚本使用速查.md`
  - 写文档类：`../project-doc-write/references/cli_脚本使用速查.md`
  - 大纲类：`../project-doc-outline/references/cli_脚本使用速查.md`
  - 端到端工作流：`../project-doc-workflow/references/cli_脚本使用速查.md`
- write skill 内容规则：
  - word 格式范本（封面/字体/行间距/页眉页脚/目录 写死版）：`../project-doc-write/references/word_格式范本_规则.md`
  - word 落盘流程（含 docx-skill 自检）：`../project-doc-write/references/word_落盘_流程.md`
  - 文档内容净化规则（去"评审稿/—占位/编制审核"等废话）：`../project-doc-write/references/文档内容_净化规则.md`
  - 数据完整性 reference（无数据章节主动询问）：`../project-doc-write/references/data_missing_section.md` + `numeric_field_missing.md`
- **元说明 skill（套件内各 skill 介绍）**：`../project-doc-overview/SKILL.md`
- **统一澄清协议**：`../intent-clarification/SKILL.md`
  - intent 5 子项：`../project-doc-query/references/intent.md`
  - environment 10 个技术点：`../project-doc-outline/references/tech_*.md`
- .project 日志管理脚本：`../project-doc-query/scripts/manage_project_log.py`（init / append-clarification / append-operation / read）
