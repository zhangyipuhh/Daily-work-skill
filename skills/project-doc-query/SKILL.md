---
name: project-doc-query
description: Use when the user asks questions about a software-engineering project's documents, milestones, deliverables, review schedule, or wants PMO-level advisory — applies three-layer framework overlay (PMP framework layer + PRINCE2落地层 + 系统分析师实务层) and forces intent-clarification (fact vs decision) before answering
---

# Project Doc Query（查询 / 咨询）

> **阶段定位**：本 skill 当前为 **V1 基础能力版**，未来会扩展到项目集/敏捷/量化管理。

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

1. **意图澄清优先**：先问"您问的是事实/数据，还是辅助决策？"，不要直接给"应该/建议"。
2. **强制框架标签**：每条回答首行输出 `【框架：{PMP|PRINCE2|系统分析师} · {框架层|落地层|实务层}】`。
3. **证据可追溯**：所有事实类回答必须附"项目证据"——策划表子标签名 + 文档路径 + 行/单元格。
4. **三层框架叠加**（互不冲突）：
   - **PMP 框架层**：5 过程组 / 10 知识领域（给"管理体系全景"）
   - **PRINCE2 落地层**：7 原则 / 7 主题 / 7 流程（给"具体怎么做"）
   - **系统分析师 实务层**：5 大模块（系统规划/需求分析/系统设计/测试与维护/信息化）（给"软件工程实际"）
5. **严禁虚构**：回答中所有数字、日期、人名必须来自项目资料；缺资料时**主动询问**用户。

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
Step 1  澄清用户意图（事实/数据 vs 决策）
   ↓
Step 2  按目录规则加载项目资料（DocumentLoader）
   ↓
Step 3  若事实/数据：直接给数据 + 证据
        若决策：选框架 → 引用框架速查表 → 给建议（带项目证据）
   ↓
Step 4  标注框架标签 + 数据来源
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

- 意图澄清提问模板：`references/澄清问题_模板.md`
- 框架速查表：`references/framework_pmp_速查.md`、`references/framework_prince2_速查.md`、`references/framework_系统分析师_速查.md`
- 框架选用决策树：`references/框架选用决策树.md`
- 策划表字段速查：`references/策划表_字段速查.md`
- 文档类型目录速查：`references/文档类型_目录速查.md`
- 评审计划提取方法：`references/评审计划_提取方法.md`

---

## 未来扩展（预留）

- 项目集/项目组合（PgMP/MSP）
- 敏捷双轨（Scrum/SAFe）
- 量化管理（QPM/CMMI）
- AI 辅助决策（基于历史项目数据库）
