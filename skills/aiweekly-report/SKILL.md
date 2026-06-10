---
name: aiweekly-report
description: 当用户要求生成 AI 辅助编程周报、运行周审查、生成 review_results、输出文档审查 Excel、生成辅助编程报告 docx 时使用此 skill
---

# AI 辅助编程周报生成 Skill

## 概述

本 Skill 驱动大模型（Agent 自身即评审者）端到端完成"AI 辅助编程周报"全流程。
**核心原则：确定的事由脚本完成，需要判断的事由大模型完成。**

## 刚性约束（违反即视为执行失败）

1. **评审者名单唯一来源 = `D:\项目文档\AIAssistive\project_284_members.txt`**
   - 即使目录中存在其他评审者配置（如 `script\checkCode\config\config.yaml` 的 `user_mapping`、其他名单文件、目录扫描到的人名子目录等），**一律以本清单为准**
   - 不得用其他名单覆盖、补充或缩减排评审者范围
   - 周目录里出现的非清单内开发者 → 视为"额外材料"，**不计入评审**
   - 缺材料的清单内开发者 → 走漏检 → 补 0 分
   - **人数随清单动态变化，不写死任何具体数字**

2. **必须使用 subagent 并行评审（subagent-driven-development）**
   - 主 Agent **不得**串行评审任何开发者文档
   - 必须按 `batch_size = 5` 切批后，**对每个批次派发一个独立 subagent（Task 工具）并行执行**
   - 批次总数 = ⌈len(actually_attended) / 5⌉，**不写死**
   - 每个 subagent 必须按 `references/subagent_task_template.md` 填充后下发，**并将结果写入磁盘**（`tmp\batch_<week>_<idx>.json`）
   - 即使某批次只有 1 人，也必须派发 subagent
   - **禁止以任何理由绕过 subagent**，包括但不限于：
     - "效率更高 / 更准确 / 更可控"
     - "team plan 验证要求所有 dependent task 都有 verifier"
     - "verifier 缺失 / 补 verifier 太麻烦"
     - "节省时间 / 节省 token"
     - "主 Agent 直接评审更稳"
   - **如遇 team plan / verifier 等外部约束限制 subagent 派发**，**必须修改 plan 配置补充 verifier**，**而非**让主 Agent 串行评审或主 Agent 直接评审
   - 任何"我直接开搞，自己跑评审"之类的输出**视为违反本约束**

## 触发条件

当用户输入包含以下意图时，主 Agent 应加载本 Skill：
- "生成 XX 周周报"
- "运行周审查 / 评审某周提交"
- "生成 review_results"
- "生成文档审查 Excel"
- "生成辅助编程报告"
- 路径形如 `D:\项目文档\AIAssistive\aiweek\YYYY\MM\MMDD-MMDD` 的目录被作为输入

## 输入

用户提供一个周目录绝对路径，例如：

```
D:\项目文档\AIAssistive\aiweek\2026\05\0525-0531
```

目录结构：`<week>/<开发者姓名>/*.md`（每个开发者一个子目录）

## 输出（三个产物，统一在 `D:\项目文档\AIAssistive\output\`）

1. `review_results_<week>.json` — 模型评审原始结果
2. `文档审查结果_<week>.xlsx` — 结构化评审表
3. `AI辅助编程报告_<week>.docx` — 完整周报

## 9 步工作流

### Step 1 — 加载人名清单
**刚性约束**：必须从 `D:\项目文档\AIAssistive\project_284_members.txt` 读取 `set_should_attend`（**人数随清单动态变化，不写死**）。**忽略所有其他人名来源**（如 `config.yaml` 的 `user_mapping`、其他名单文件、目录扫描的人名子目录等），以本清单为唯一真相。读取后建议打印 `set_should_attend` 前 5 人做 sanity check。

### Step 2 — 扫描周目录
列出 `<input_path>/*/` 下所有子目录名，得到 `set_actually_attended`。

### Step 3 — 漏检检测（脚本，V2.2 拆分两类）
```bash
python scripts/check_missing.py \
  --members "D:\项目文档\AIAssistive\project_284_members.txt" \
  --attended "<week_dir>" \
  --reviewed "D:\项目文档\AIAssistive\output\review_results_<week>.json" \
  --output-json "D:\项目文档\AIAssistive\output\missing_<week>.json"
```

⚠️ **此步骤在 Step 4 完成后执行**（因为需要 review_results.json）。

**V2.2 拆分两类漏检**：
- **真未提交 (A)**：人名清单有，但周目录无子目录 → 应补 **0 分**
- **漏评审 (B)**：周目录有子目录，但 review_results.json 缺该名字 → 应**补件**（重派 subagent 评审）

输出 JSON：
```json
{
  "total_members": 40,
  "actually_attended": 35,
  "reviewed_count": 33,
  "not_submitted": ["张三", "李四", ...],   // 情况 A
  "not_submitted_count": 5,
  "not_reviewed": ["周八", "吴九"],          // 情况 B
  "not_reviewed_count": 2,
  "missing": [...],                          // 兼容字段
  "missing_count": 7
}
```

**不阻断流程**。漏检名单将传至 Step 8 嵌入报告第五章 5.x。

### Step 4 — 分批并行评审（核心）
1. 把 `set_actually_attended` 按 `batch_size = 5` 切分（**批次总数 = ⌈len(actually_attended) / 5⌉，不写死**）
2. **刚性约束**：必须使用 subagent（Task 工具）派发，**禁止主 Agent 串行评审**（串行评审违反 subagent-driven-development 规范且丢失并发优势）。即使某批次只有 1 人，也必须派发 subagent。**禁止以任何理由绕过 subagent**（包括效率、team plan 验证约束、verifier 缺失等）
3. **每个 subagent 任务必须按 `references/subagent_task_template.md` 填充后下发**：
   - 必填输入变量：`{{idx}}`、`{{week}}`、`{{names}}`、`{{input_path}}`、`{{output_path}}`
   - **刚性约束**：
     - 必须把结果写入磁盘文件 `{{output_path}}`（即 `D:\项目文档\AIAssistive\tmp\batch_<week>_<idx>.json`）
     - 不允许只返回 JSON 字符串而不写盘（这会导致后续合并步骤失败）
     - 写盘后必须回显 `SAVED: <完整路径>`
     - 文件命名固定：`batch_<week>_<idx>.json`
4. 主 Agent 等待所有 subagent 返回
5. **批次级格式验证**（脚本）：对每个批次输出调用 `validate_review_results.py`：
   ```bash
   python scripts/validate_review_results.py --input "D:\项目文档\AIAssistive\tmp\batch_<week>_<idx>.json"
   ```
   验证失败的批次要求 subagent 重新评审。
6. 数量/完整性校验：
   - 文件存在性：`D:\项目文档\AIAssistive\tmp\batch_<week>_<idx>.json` 必须存在
   - 数量：`sum(len(batch_results)) == len(actually_attended)`？
   - 完整性：所有人名都在结果中？
   - 字段：关键字段（`overall_score`、`summary`）非空？
7. 补执行：对缺失/失败的开发者重新派发 subagent（写入 `batch_<week>_<idx>_re<N>.json`）
8. **合并批次 JSON**（脚本）：调用 `merge_review_results.py`：
   ```bash
    python scripts/merge_review_results.py \
      --input "D:\项目文档\AIAssistive\tmp\batch_<week>_1.json" \
      --input "D:\项目文档\AIAssistive\tmp\batch_<week>_2.json" \
      ... \
      --input "D:\项目文档\AIAssistive\tmp\batch_<week>_<N>.json" \
      --output "D:\项目文档\AIAssistive\output\review_results_<week>.json" \
      --on-duplicate last
   ```
   - 脚本按 `data.name` 合并所有批次（重名保留最后一个）
   - 内嵌格式验证，验证失败则返回码非 0
   - 验证失败时主 Agent 应阻断后续步骤，提示检查评审质量
   - 可选参数：`--on-duplicate {last|first|fail}`、`--no-validate`
   - **合并成功后保留 `tmp\batch_<week>_*.json` 不删**（Step 9 统一清理）
9. 验证通过的合并 JSON 即为最终产物，位于 `D:\项目文档\AIAssistive\output\review_results_<week>.json`

### Step 4.10 — 自动补件（仅当 not_reviewed > 0，V2.2 新增）

**触发条件**：Step 3 漏检检测发现 `not_reviewed_count > 0`（漏评审）

**逻辑**：
1. 主 Agent 检测到漏评审（情况 B）
2. 自动派发新 subagent，**仅评审 not_reviewed 名单**（避免重复工作）
3. 写 `tmp/batch_<week>_repair_<idx>.json`
4. subagent **内置自验证**（写盘后自动调用 validate_review_results.py，失败自动重试）
5. 调用 `merge_review_results.py` 合并到 review_results.json
6. **回跑 Step 3** 验证 not_reviewed → 0
7. **最多重试 2 轮**（避免无限循环），仍 > 0 则控制台报警

**为什么需要补件**：周目录有子目录说明开发者提交了材料，但模型评审时漏掉，强行 0 分不公正。必须重新评审。

**subagent 自验证**：补件 subagent 按 `subagent_task_template.md` 执行，写盘后自动验证格式，验证通过才返回。

### Step 4.11 — 补 0 分（insufficient_data 或 not_submitted，V2.2 新增）

**触发条件**：Step 4.10 完成后，再跑 Step 3 漏检，若 `not_submitted_count > 0`

```bash
python scripts/fill_zero_score.py \
  --reviewed "D:\项目文档\AIAssistive\output\review_results_<week>.json" \
  --missing "D:\项目文档\AIAssistive\output\missing_<week>.json"
```

**行为**：
- 从 missing.json 读 `not_submitted` 字段（不读 `missing`，避免污染）
- 给真未提交者补 0 分条目（含反模式命中、priority=high）
- 已存在的同名记录**跳过**（不覆盖）

**补充**：update_baseline.py 已修改为自动将 `insufficient_data` 条目填充为 0 分写入 baseline.db（无需额外处理）
- 输出 review_results.json 原地覆盖

**为什么是 0 分**：真未提交 = 完全没材料，应得 0 分。计入"有效评分人数"和平均分（拉低平均）。

### Step 5 — 回跑漏检检测
使用 Step 4.11 补 0 后的 `review_results_<week>.json` 回跑 Step 3 的脚本。

**期望结果**：
- `not_submitted: []`（已补 0）
- `not_reviewed: []`（已补件）
- 两者都为空 → 进入 Step 6
- 否则阻断（补 0/补件没成功）
### Step 6 — 生成 Excel（脚本，参数化）
```bash
python scripts/generate_excel.py \
  --input "D:\项目文档\AIAssistive\output\review_results_<week>.json" \
  --output "D:\项目文档\AIAssistive\output\文档审查结果_<week>.xlsx"
```

> generate_excel.py 已参数化，支持 `--input` 和 `--output` 参数。
> 不传参数时使用默认路径（`script\checkCode\output\review_results.json`）保持向后兼容。

输出：`D:\项目文档\AIAssistive\output\文档审查结果_<week>.xlsx`

### Step 7 — 更新 Baseline 基准库（脚本）
```bash
python scripts/update_baseline.py \
  --input "D:\项目文档\AIAssistive\output\review_results_<week>.json" \
  --db "D:\项目文档\AIAssistive\baseline\baseline.db"
```

行为：
- 将本周评审结果写入 SQLite（`baseline.db`）
- 同一 (week, name) 已存在则**覆盖**最新值
- 打印：新增 N 条、覆盖 M 条、跳过 K 条
- 数据库不存在时自动初始化（含 review_history 表 + 索引）

数据库结构详见 `references/baseline_readme.md`。

### Step 8 — 生成最终 DOCX 报告（脚本）
```bash
python scripts/generate_report.py \
  --json "D:\项目文档\AIAssistive\output\review_results_<week>.json" \
  --excel "D:\项目文档\AIAssistive\output\文档审查结果_<week>.xlsx" \
  --missing-json "D:\项目文档\AIAssistive\output\missing_<week>.json" \
  --db "D:\项目文档\AIAssistive\baseline\baseline.db" \
  --output "D:\项目文档\AIAssistive\output\AI辅助编程报告_<week>.docx" \
  --week "<week>"
```

> `--trend-md` 已废弃（第六章趋势分析现从 baseline.db 读取），传入 `/dev/null` 即可。

报告章节（**7 + 1 模型**，严格匹配 `references/report_format_spec.md`）：
- 标题 + 副标题（居中）
1. 第一章 概述
2. 第二章 汇总统计
3. 第三章 评审结果汇总（Top 10 / Bottom 5，含 AI 采纳率 + 改进优先级列）
4. 第四章 改进建议汇总（4.1~4.5 五方面）
5. 第五章 不足与改进建议（含 5.x 本周未提交者）
6. 第六章 整体趋势变化分析
7. **总结**（独立章节，参考样例 `AI辅助编程评审报告0511-0517.docx`）
8. 第七章 全量比对（**最近 4 次**，从 baseline.db 读取，按人列趋势）

### Step 9 — 总结输出 + 临时文件清理
1. 控制台打印：
   - 三个产物路径
   - 漏检名单
   - 评审人数、本周 vs 历史对比的关键数字
2. **清理临时批次文件**：
   ```bash
   # 删除本周所有批次临时文件
   Remove-Item "D:\项目文档\AIAssistive\tmp\batch_<week>_*.json" -Force
   ```
3. **保留可复用文件**（不删）：
   - `D:\项目文档\AIAssistive\output\missing_<week>.json`（漏检结果，供后续周对比）
   - 所有 `output/` 下的最终产物

## 资源引用

- **评审模板**：`references/review_prompt.md`（基于 prompts.py 提炼）
- **人名清单说明**：`references/members_readme.md`
- **subagent 任务模板**：`references/subagent_task_template.md`（subagent 任务下发必读）
- **报告格式说明**：`references/report_format_spec.md`（DOCX 段落/字体/表格规范，7+1 章节模型）
- **Baseline 库说明**：`references/baseline_readme.md`（SQLite 表结构、查询示例、备份策略）
- **Python 脚本**：`scripts/`（8 个脚本）
  - `check_missing.py` — 漏检检测（V2.2 拆分 not_submitted/not_reviewed）
  - `validate_review_results.py` — 格式验证（独立工具）
  - `merge_review_results.py` — 多批次合并（Step 4.8）
  - `fill_zero_score.py` — 真未提交补 0 分（Step 4.11）
  - `generate_excel.py` — JSON → Excel
  - `update_baseline.py` — Baseline 维护（Step 7，SQLite 写入）
  - `generate_report.py` — 生成最终 DOCX

## 错误处理

| 错误 | 处理 |
|------|------|
| 周目录不存在 | 报错并退出 |
| 人名清单不存在 | 报错并退出 |
| 开发者文档为空 | 标记 `"insufficient_data"`，不阻断 |
| Excel 生成失败 | 报错并保留 JSON |
| 历史 Excel 为空 | 报告"无历史可比对"，跳过趋势章 |
| 漏检人数 > 0 | **不阻断**，分类处理：A 真未提交补 0 分；B 漏评审补件 |
| 漏评审 (B) 补件 2 轮后仍 > 0 | 控制台报警，标记异常，不阻断 |
| review_results 格式验证失败 | 阻断后续步骤，提示检查评审质量 |
| baseline.db 不存在 | `update_baseline.py` 自动初始化；DOCX 报告"无历史可比对" |
| baseline.db 字段缺失 | `update_baseline.py` 跳过该条记录并打印跳过数 |

## 设计原则

- ✅ **确定的事由脚本完成**：漏检检测、格式验证、Excel 生成、对比、DOCX 排版
- ✅ **判断的事由模型完成**：文档质量评审、AI 痕迹识别、洞察生成
- ✅ **并行提速**：评审步骤按 5 人/批切分后派发 ⌈N/5⌉ 个 subagent 并行执行
- ✅ **可复现**：所有机械步骤封装为可独立运行的 Python 脚本
- ✅ **可观测**：每个产物落盘到 `output/`，控制台打印关键路径
- ✅ **可验证**：每批评审输出和最终合并 JSON 都要经过格式验证脚本
- ✅ **评审者名单唯一**：始终以 `project_284_members.txt` 为准，目录内其他配置不参与名单决策（人数动态，不写死）
- ✅ **subagent 强制**：评审阶段必须派发 subagent 并行执行，主 Agent 仅负责调度/合并/验证
- ✅ **subagent 不可绕过**：禁止以效率/team plan 验证约束/verifier 缺失/节省时间等任何理由让主 Agent 串行评审或主 Agent 直接评审
