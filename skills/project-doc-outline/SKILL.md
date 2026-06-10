---
name: project-doc-outline
description: Use when the user wants a chapter outline (no body content) for any of the 10 supported software-engineering deliverable types (售前方案/需求说明书/概要设计/详细设计/实施方案/测试方案/测试报告/验收报告/实施部署方案/培训方案) — picks the corresponding reference template and applies software-engineering standard chapter structure
---

# Project Doc Outline（文档大纲）

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
Step 1  接收目标文档类型
   ↓
Step 2  加载对应 reference 模板
   ↓
Step 3  （可选）从项目已有同类 docx 抽取格式范本（extract_docx_outline.py）
   ↓
Step 4  输出"章节级"大纲（不写正文）
   ↓
Step 5  在每章末标注"用途"和"必备小节"提示
```

---

## 资源引用

- 10 个 outline reference：`references/outline_*.md`
- 范本抽取脚本：`scripts/extract_docx_outline.py`

---

## 未来扩展

- 不同行业（政务/金融/医疗）的行业版大纲
- 自动从策划表 WBS 反推项目阶段文档结构
