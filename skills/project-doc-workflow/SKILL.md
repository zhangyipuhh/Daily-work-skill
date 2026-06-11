---
name: project-doc-workflow
description: Use when generating a software-engineering project deliverable end-to-end (from initial user request to final document on disk) — orchestrates the 4-step pipeline (hub → query → outline → write) and provides the work-skill checklist
---

# Project Doc Workflow（端到端工作流）

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

把 `project-doc-hub` 受理的需求，按 4 步流水线（query → outline → write → 落盘 + 变更记录）编排成可执行的检查清单，**指导 work skill（执行 agent）按顺序执行**。

> **核心原则：确定的事由脚本完成，需要判断的事由大模型完成。**

---

## 触发条件

- 用户要"从 0 生成一份完整的项目文档"
- 用户要"按项目已有资料写完整文档"
- 不适用：仅查询/仅大纲/仅更新（这些走单个子 skill）

---

## 4 步流水线

```
┌────────────────────────────────────────┐
│  Step 1  project-doc-hub（受理 + 澄清）   │
│  - 调 intent-clarification 走 intent 维度 │
│  - 取项目根目录 + 文档类型 + 意图        │
│  - 多项目时让用户选择                    │
└────────────────────────────────────────┘
                  ↓
┌────────────────────────────────────────┐
│  Step 2  project-doc-query（资料抽取）    │
│  - 加载策划表 xlsm → 提取里程碑/评审计划  │
│  - 加载项目根目录 → 列出已有同类 docx   │
│  - 抽取 docx 章节作为格式范本            │
└────────────────────────────────────────┘
                  ↓
┌────────────────────────────────────────┐
│  Step 3  project-doc-outline（生成大纲）  │
│  - 调 intent-clarification 走 environment 维度 │
│  - 按文档类型选 reference 模板           │
│  - 输出"章节级"大纲（不含正文）          │
└────────────────────────────────────────┘
                  ↓
┌────────────────────────────────────────┐
│  Step 4  project-doc-write（填充 + 决策）  │
│  - 调 intent-clarification 走 data/document_attr 维度 │
│  - 严格基于项目已有资料填充正文          │
│  - 缺资料时主动询问用户                  │
│  - 生成"决策与意见"（带【框架】标签）     │
│  - 追加变更记录                          │
│  - 调 manage_project_log.py append-operation 写主日志 │
│  - 输出到项目目录 + 中间稿               │
└────────────────────────────────────────┘
```

---

## Work Skill 执行检查清单

执行 agent 必须按顺序完成每一项，每项完成后在 `□` 改为 `☑`：

```
□ Step 1 hub
   □ 1.1 列出根目录下所有项目
   □ 1.2 用户选择项目（或已提供）
   □ 1.3 用户选择目标文档类型
   □ 1.4 用户说明意图（生成/更新/查询）
   □ 1.5 用户确认输出位置

□ Step 2 query
   □ 2.1 加载策划表 xlsm（走 DocumentLoader + ExcelLoader）
   □ 2.2 提取里程碑/评审计划/损益分析/风险登记册
   □ 2.3 列出项目已有同类 docx（如有）
   □ 2.4 抽取 docx 章节作为格式范本（如有）
   □ 2.5 扫描件检测（PDF）

□ Step 3 outline
   □ 3.1 加载 outline_*.md reference 模板
   □ 3.2 输出章节级大纲
   □ 3.3 用户确认大纲

□ Step 4 write
   □ 4.1 按章节顺序逐章填充
   □ 4.2 每章标注数据源
   □ 4.3 缺资料时主动询问用户（不擅自编造）
   □ 4.4 生成"决策与意见"章节（带【框架】+【强度】+【数据源】）
   □ 4.5 自检严禁虚构红线清单
   □ 4.6 内容净化自检（去"评审稿/—占位/编制审核"等废话，详见 write/references/文档内容_净化规则.md）
   □ 4.7 追加变更记录到 <项目根>/06_变更及暂停/变更记录.md
   □ 4.8 输出最终文档到项目目录（.md + .docx）
        ├─ 4.8.1 落 .md 到项目目录
        ├─ 4.8.2 【调 word skill 转 .docx】—— 模型自检当前 skill 库是否有"操作 word 的 skill"（docx-skill / word-skill / docx-generator 等）
        │        ├─ 存在 → 调该 skill 转 .docx
        │        └─ 不存在 → 提示用户安装 docx-skill，仅落 .md
        ├─ 4.8.3 落中间稿到 AIAssistive\output\
   □ 4.9 汇报产物路径
```

---

## 关键执行约束

1. **必须按 Step 顺序**：不可跳过 Step 1 澄清
2. **每个 Step 必完成才能进下一步**：尤其是 Step 2 的资料抽取
3. **Step 4.3 是核心约束**：缺资料时必须询问，不可擅作主张
4. **Step 4.6 是强制输出**：变更记录必写
5. **Step 4.7 + 4.8 双输出**：项目目录（正式）+ AIAssistive\output\（中间稿）

---

## 资源引用

- 端到端工作流详细说明：`references/端到端_工作流.md`
- 输出文件命名规范：`references/输出文件_命名规范.md`

---

## 未来扩展

- 多文档并发生成（用 subagent 并行）
- 与 PMO 数据库联动（自动填历史项目数据）
- 评审邮件自动生成
