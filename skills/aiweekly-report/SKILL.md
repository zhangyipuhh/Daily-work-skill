---
name: aiweekly-report
description: 当用户要求生成 AI 辅助编程周报、运行周审查、生成 review_results、输出文档审查 Excel、生成辅助编程报告 docx 时使用此 skill
---

# AI 辅助编程周报生成 Skill

## 概述

本 Skill 驱动大模型（Agent 自身即评审者）端到端完成"AI 辅助编程周报"全流程。
**核心原则：确定的事由脚本完成，需要判断的事由大模型完成。**

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
读取 `D:\项目文档\AIAssistive\project_284_members.txt`，得到 `set_should_attend`（40 人）。

### Step 2 — 扫描周目录
列出 `<input_path>/*/` 下所有子目录名，得到 `set_actually_attended`。

### Step 3 — 漏检检测（脚本）
调用：
```bash
python scripts/check_missing.py \
  --members "D:\项目文档\AIAssistive\project_284_members.txt" \
  --reviewed <待 Step 4 完成后填入> \
  --output-json "D:\项目文档\AIAssistive\output\missing_<week>.json"
```

⚠️ **此步骤在 Step 4 完成后执行**（因为需要 review_results.json）。
脚本会输出漏检名单到控制台，并将结果 JSON 写入指定路径。
**不阻断流程**。漏检名单将传至 Step 7 嵌入报告第六章。

### Step 4 — 分批并行评审（核心）
1. 把 `set_actually_attended` 按 `batch_size = 5` 切分（40 人 → 8 批）
2. 对每个批次派发一个 subagent（Task 工具）**并行**执行
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
     --input "D:\项目文档\AIAssistive\tmp\batch_<week>_8.json" \
     --output "D:\项目文档\AIAssistive\output\review_results_<week>.json" \
     --on-duplicate last
   ```
   - 脚本按 `data.name` 合并所有批次（重名保留最后一个）
   - 内嵌格式验证，验证失败则返回码非 0
   - 验证失败时主 Agent 应阻断后续步骤，提示检查评审质量
   - 可选参数：`--on-duplicate {last|first|fail}`、`--no-validate`
   - **合并成功后保留 `tmp\batch_<week>_*.json` 不删**（Step 9 统一清理）
9. 验证通过的合并 JSON 即为最终产物，位于 `D:\项目文档\AIAssistive\output\review_results_<week>.json`

### Step 5 — 回跑漏检检测
使用 Step 4 生成的 `review_results_<week>.json` 回跑 Step 3 的脚本，
将漏检名单 JSON 写入指定路径。

### Step 6 — 生成 Excel（脚本，参数化）
```bash
python scripts/generate_excel.py \
  --input "D:\项目文档\AIAssistive\output\review_results_<week>.json" \
  --output "D:\项目文档\AIAssistive\output\文档审查结果_<week>.xlsx"
```

> generate_excel.py 已参数化，支持 `--input` 和 `--output` 参数。
> 不传参数时使用默认路径（`script\checkCode\output\review_results.json`）保持向后兼容。

输出：`D:\项目文档\AIAssistive\output\文档审查结果_<week>.xlsx`

### Step 7 — 全量历史对比（脚本）
```bash
python scripts/compare_history.py \
  --current "D:\项目文档\AIAssistive\output\review_results_<week>.json" \
  --history-dir "D:\项目文档\AIAssistive\output" \
  --output "D:\项目文档\AIAssistive\output\趋势分析_<week>.md"
```

输出：`趋势分析_<week>.md`，包含：
- 整体指标趋势表（所有历史周 vs 本周）
- 开发者个体变化（与最近一次有数据的周对比）
- 进步/退步/持平/新增汇总
- 关键洞察

### Step 7.5 — 更新 Baseline 基准库（脚本）[V2.1 新增]
```bash
python scripts/update_baseline.py \
  --input "D:\项目文档\AIAssistive\output\review_results_<week>.json" \
  --db "D:\项目文档\AIAssistive\baseline\baseline.db"
```

行为：
- 将本周评审结果写入 SQLite（`baseline.db`）
- 同一 (week, name) 已存在则**覆盖**最新值
- 打印：新增 N 条、覆盖 M 条、跳过 K 条
- **必须**在 Step 8 DOCX 生成前跑完
- 数据库不存在时自动初始化（含 review_history 表 + 索引）

数据库结构详见 `references/baseline_readme.md`。

### Step 8 — 生成最终 DOCX 报告（脚本）
```bash
python scripts/generate_report.py \
  --json "D:\项目文档\AIAssistive\output\review_results_<week>.json" \
  --excel "D:\项目文档\AIAssistive\output\文档审查结果_<week>.xlsx" \
  --trend-md "D:\项目文档\AIAssistive\output\趋势分析_<week>.md" \
  --missing-json "D:\项目文档\AIAssistive\output\missing_<week>.json" \
  --db "D:\项目文档\AIAssistive\baseline\baseline.db" \
  --output "D:\项目文档\AIAssistive\output\AI辅助编程报告_<week>.docx" \
  --week "<week>"
```

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
- **Python 脚本**：`scripts/`（6 个脚本）
  - `check_missing.py` — 漏检检测
  - `validate_review_results.py` — 格式验证（独立工具）
  - `merge_review_results.py` — 多批次合并（Step 4.8）
  - `generate_excel.py` — JSON → Excel
  - `compare_history.py` — 全量历史对比
  - `update_baseline.py` — Baseline 维护（Step 7.5，SQLite 写入）
  - `generate_report.py` — 生成最终 DOCX

## 错误处理

| 错误 | 处理 |
|------|------|
| 周目录不存在 | 报错并退出 |
| 人名清单不存在 | 报错并退出 |
| 开发者文档为空 | 标记 `"insufficient_data"`，不阻断 |
| Excel 生成失败 | 报错并保留 JSON |
| 历史 Excel 为空 | 报告"无历史可比对"，跳过趋势章 |
| 漏检人数 > 0 | **不阻断**，写入报告第五章 5.x |
| review_results 格式验证失败 | 阻断后续步骤，提示检查评审质量 |
| baseline.db 不存在 | `update_baseline.py` 自动初始化；DOCX 报告"无历史可比对" |
| baseline.db 字段缺失 | `update_baseline.py` 跳过该条记录并打印跳过数 |

## 设计原则

- ✅ **确定的事由脚本完成**：漏检检测、格式验证、Excel 生成、对比、DOCX 排版
- ✅ **判断的事由模型完成**：文档质量评审、AI 痕迹识别、洞察生成
- ✅ **并行提速**：评审步骤按 5 人/批派发 8 个 subagent 并行
- ✅ **可复现**：所有机械步骤封装为可独立运行的 Python 脚本
- ✅ **可观测**：每个产物落盘到 `output/`，控制台打印关键路径
- ✅ **可验证**：每批评审输出和最终合并 JSON 都要经过格式验证脚本
