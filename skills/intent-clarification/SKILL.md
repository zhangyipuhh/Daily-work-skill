---
name: intent-clarification
description: Use whenever any project-doc skill (query/outline/write/workflow/data-skill) needs to confirm something with the user — unified protocol: scan project artifacts first, show prior answers, cite source+line, handle "待定" by re-asking. Re-entrant: can be invoked from any step, not just the start.
---

# Intent Clarification（项目级澄清协议 · 给模型读）

> 目标对象：**模型**（不是用户）。模型加载本 skill 后应能自动：
> - 知道任何"问用户"必须先调本 skill
> - 知道澄清记录存放位置（`.project/<项目号>/`，**不在 skill 内**）
> - 知道 4 大询问场景（intent/data/environment/document_attr）
> - 知道可重入（流程中任何时机可调）

<HARD-GATE>
Do NOT write any outline / document / answer without first invoking this skill and completing clarification. Each clarification produces a row in `<用户工作根>/.project/<project_id>/clarification_log.md` (NOT inside the skill).
</HARD-GATE>

<HARD-GATE: NO FABRICATION>
Do NOT fabricate ANY content under ANY circumstance. When a fact is missing from project materials:
1. Mark as "**待补**：<具体字段名>" (NEVER "—" / "TBD" / "待定" 单独使用)
2. Cite source field: "无项目资料支撑"
3. Append to clarification_log.md via manage_project_log.py
4. NEVER write a guess, even a plausible one

This applies to:
- People names (策划表里没"张三"就别写"张三")
- Dates (策划表里没"2025-12-31"就别写)
- Numbers (用例数/工期/成本等无证据→"**待补**")
- Tool names (项目没提"禅道"/"Git"/"钉钉"就别写)
- Role signoff (无具体姓名→保持沉默，不写)
- Doc status (用户没说→保持沉默，不写"评审稿")
- Framework tags (PMP/PRINCE2/系统分析师 标注要准确)

When in doubt: ASK, don't WRITE.
</HARD-GATE: NO FABRICATION>

---

## Step 0: 场景分流（必走 · 第一步）

**用户问题进来第一件事**：识别场景类型。

| 场景 | 用户话术特征 | 必走的询问维度 |
|---|---|---|
| `A0.technical_doc` | "写 XX 方案/设计/测试/部署/培训" | A.intent (doc_type) + C.environment (10 个技术点) |
| `A0.administrative` | "变更记录/周报/纪要" | A.intent (doc_type) + D.document_attr |
| `A0.factual_query` | "什么时候/谁/多少/在哪" | A.intent (fact/decision) |
| `A0.advisory` | "建议/应该/哪种/怎么选" | A.intent (decision) + 三层框架 |

**如果识别不出**：主动问用户"您要做的是写文档 / 查事实 / 要建议？"

**关键**：技术文档场景必须问技术细节（10 个 C.environment 技术点），不能跳过。

## Where to Log（关键：所有过程文件都在 skill 外部）

**Runtime records MUST go to**（不放在 skill 内）：

```
<用户工作根>/.project/<project_id>/          ← 与项目目录平级
├── project_log.md         ← 主操作日志（每个 skill 流程结束追加 1 条）
├── clarification_log.md   ← 澄清记录（每次 Q/A 追加 1 条）
├── drafts/                ← 中间稿（write 流程的草稿）
└── session_<YYYY-MM-DD>.md ← 会话日志（可选）
```

**Do NOT** create or modify files inside the skill itself for runtime records.

## When to Invoke

- **At the start of any skill flow** that needs user input (project root, doc type, intent)
- **At any step** when a new question emerges (missing data, ambiguous requirement, environmental constraint)
- **When prior answer in log** is ambiguous or outdated
- **NOT for trivial one-word confirmations** that the user has already implicitly given

## Checklist

1. **Identify dimension** — see `references/澄清维度_清单.md` (4 scenarios: intent / data / environment / document_attr)
2. **Read existing log** at `<用户工作根>/.project/<project_id>/clarification_log.md`
   - Prior answer exists → show it + ask "confirm or update"
3. **Scan project artifacts** for evidence (策划表/合同/需求) using `read_doc.py`
   - If found → cite file + line + show excerpt
4. **Ask user** using the dimension-specific template
5. **Handle "待定"** — re-ask: "stop or provide details"
6. **Append row to log** via `scripts/manage_project_log.py append-clarification`
7. **Return value** to calling skill
8. **After skill flow ends** — append to `project_log.md` via `manage_project_log.py append-operation`

## 4 Dimensions

| 场景 | 子项 | Reference template |
|---|---|---|
| A. 流程澄清 (intent) | 5 子项（见文件） | `../project-doc-query/references/intent.md` |
| B. 数据完整性 (data) | 章节无数据 / 数值字段缺失 | `../project-doc-write/references/data_missing_section.md`<br>`../project-doc-write/references/numeric_field_missing.md` |
| C. 环境/技术/合规 (environment) | 10 个技术点 | `../project-doc-outline/references/tech_*.md`（10 个文件） |
| D. 文档属性 (document_attr) | 角色签名表 / 文档状态 | `../project-doc-write/references/role_signoff.md`<br>`../project-doc-write/references/doc_status.md` |

## Key Principles

1. **One dimension per call** - Don't bundle intent + data + env
2. **Multiple choice preferred** - 4 options max
3. **Show prior first** - Avoid re-asking
4. **Cite source+line** - When from artifacts
5. **待定 is not an answer** - Re-ask: stop or provide
6. **Persist to log** - All Q/A in `<用户工作根>/.project/<project_id>/clarification_log.md`
7. **Re-entrant** - Can be called from any step
8. **All files outside skill** - 过程文件全在 `.project/<项目号>/`，**不在 skill 内**

## Anti-Patterns

| 反模式 | 后果 |
|---|---|
| 在 SKILL.md 内联问而不调本 skill | 5 处澄清不一致 |
| 跳澄清直接给"应该/建议" | 违反 HARD-GATE |
| "待定"也算答案继续 | 不完整大纲后续返工 |
| 澄清结果不记 | 跨 skill 重复问 |
| 多个维度一锅问 | 答案互相干扰 |
| 把过程文件写在 skill/references/ 下 | 违反"过程文件不放在 skill 中"原则 |

## After Clarification

调用方 skill 收到返回值后：
- 用返回值继续
- 不再次询问相同维度（除非用户明确表示"重新问"）
- 把 clarification_log.md 路径告知后续 skill
- 流程结束后调 `manage_project_log.py append-operation` 写主日志
