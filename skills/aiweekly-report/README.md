# aiweekly-report Skill

> AI 辅助编程周报生成 — 端到端自动化 Skill

## 这是什么

当你让 Agent "生成某周周报" 时，Agent 会加载本 Skill，按 9 步流程端到端产出三个文件：

| 产物 | 路径 | 用途 |
|------|------|------|
| JSON | `output/review_results_<week>.json` | 原始评审数据 |
| Excel | `output/文档审查结果_<week>.xlsx` | 结构化评审表 |
| DOCX | `output/AI辅助编程报告_<week>.docx` | 完整周报（含全量历史对比） |

## 核心设计

- **评审者是大模型本身**，不再调任何 LLM API
- **确定的事由脚本完成**（漏检检测、Excel 生成、历史对比、DOCX 排版）
- **判断的事由模型完成**（文档质量评分、AI 痕迹识别、洞察生成）
- **评审步骤按 5 人/批并行**：40 人 → 8 个 subagent 同时跑

## 9 步工作流

```
Step 1  加载人名清单
Step 2  扫描周目录
Step 3  漏检检测（脚本，不阻断）
Step 4  分批并行评审（5 人/批 × 8 批 + 批次验证 + 合并 + 补执行）
Step 5  回跑漏检检测（用真实评审结果）
Step 6  生成 Excel（脚本，参数化）
Step 7  全量历史对比（脚本）
Step 8  生成最终 DOCX（脚本）
Step 9  总结输出（控制台）
```

## 目录结构

```
aiweekly-report/
├── SKILL.md                       # 主入口（Agent 加载此文件执行）
├── README.md                      # 本文件
├── scripts/
│   ├── check_missing.py           # 漏检检测
│   ├── validate_review_results.py # 格式验证（独立工具）
│   ├── merge_review_results.py    # 多批次合并（Step 4.8）
│   ├── generate_excel.py          # JSON → Excel（参数化）
│   ├── compare_history.py         # 全量历史对比
│   └── generate_report.py         # 生成最终 DOCX
└── references/
    ├── review_prompt.md           # 评审模板（subagent 评审时必读）
    ├── subagent_task_template.md  # subagent 任务模板（主 Agent 派发任务时必读）
    └── members_readme.md          # 人名清单说明
```

## 单独运行脚本

每个脚本都可独立运行，便于调试和复用：

```bash
# 1. 漏检检测
python scripts/check_missing.py \
  --members "D:\项目文档\AIAssistive\project_284_members.txt" \
  --reviewed "D:\项目文档\AIAssistive\output\review_results_0525-0531.json" \
  --output-json "D:\项目文档\AIAssistive\output\missing_0525-0531.json"

# 2. 格式验证（独立工具，用于人工检查）
python scripts/validate_review_results.py \
  --input "D:\项目文档\AIAssistive\output\review_results_0525-0531.json"

# 3. 合并多个批次 JSON（Step 4.8）
python scripts/merge_review_results.py \
  --input "D:\项目文档\AIAssistive\tmp\batch_1.json" \
  --input "D:\项目文档\AIAssistive\tmp\batch_2.json" \
  --output "D:\项目文档\AIAssistive\output\review_results_0525-0531.json" \
  --on-duplicate last

# 4. JSON → Excel（参数化）
python scripts/generate_excel.py \
  --input "D:\项目文档\AIAssistive\output\review_results_0525-0531.json" \
  --output "D:\项目文档\AIAssistive\output\文档审查结果_0525-0531.xlsx"

# 5. 全量历史对比
python scripts/compare_history.py \
  --current "D:\项目文档\AIAssistive\output\review_results_0525-0531.json" \
  --history-dir "D:\项目文档\AIAssistive\output" \
  --output "D:\项目文档\AIAssistive\output\趋势分析_0525-0531.md"

# 6. 生成 DOCX
python scripts/generate_report.py \
  --json "D:\项目文档\AIAssistive\output\review_results_0525-0531.json" \
  --excel "D:\项目文档\AIAssistive\output\文档审查结果_0525-0531.xlsx" \
  --trend-md "D:\项目文档\AIAssistive\output\趋势分析_0525-0531.md" \
  --missing-json "D:\项目文档\AIAssistive\output\missing_0525-0531.json" \
  --output "D:\项目文档\AIAssistive\output\AI辅助编程报告_0525-0531.docx" \
  --week "0525-0531"
```

## 依赖

- Python 3.8+
- `openpyxl`
- `python-docx`

## 注意事项

- 评审提示词基于 `E:\laboratory\AI\Agents\agent-user-mangerment\app\features\AI_Coding_Check_agent\config\prompts.py` 提炼，**不要修改评审维度**
- 人名清单唯一来源：`D:\项目文档\AIAssistive\project_284_members.txt`
- 所有产物统一输出到 `D:\项目文档\AIAssistive\output\`
- **每批评审输出和最终 JSON 都要经过 `validate_review_results.py` 格式验证**
- `generate_excel.py` 已参数化（支持 `--input` / `--output`），向后兼容默认路径
- **subagent 必须把结果写入磁盘文件**（`tmp\batch_<week>_<idx>.json`），**不允许只返回 JSON 字符串**
- 临时批次文件由 Step 9 统一清理（`rm tmp\batch_<week>_*.json`）
