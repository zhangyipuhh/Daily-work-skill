# Subagent 任务模板

> **用途**：主 Agent 在派发评审 subagent 时，按本模板填充变量后下发。
> **目的**：保证 subagent 严格按协议写盘到指定文件，不出现"只返回 JSON 字符串而不写盘"的情况。

---

## 变量清单

| 变量 | 含义 | 示例 |
|------|------|------|
| `{{idx}}` | 批次索引（从 1 开始） | `3` |
| `{{week}}` | 周次标签 | `0525-0531` |
| `{{names}}` | 本批次开发者姓名列表（多行） | `付玉\n任佳鑫\n余伟鸿\n冯健\n刘芬` |
| `{{input_path}}` | 周目录绝对路径 | `D:\项目文档\AIAssistive\aiweek\2026\05\0525-0531` |
| `{{output_path}}` | 必填输出文件路径 | `D:\项目文档\AIAssistive\tmp\batch_0525-0531_3.json` |
| `{{tmp_dir}}` | 临时目录路径 | `D:\项目文档\AIAssistive\tmp` |
| `{{scripts_dir}}` | 验证脚本目录 | `D:\项目文档\AIAssistive\ai\skills\aiweekly-report\scripts` |

---

## 任务模板

主 Agent 把以下内容作为 subagent 的 prompt 完整下发（变量已替换）：

````
你是 subagent #{{idx}}，负责评审本周 ({{week}}) 的以下开发者：

{{names}}

## 输入
- 周目录（每个开发者一个子目录）：{{input_path}}
- 评审模板（必读）：{skill_dir}/references/review_prompt.md

## 评审流程
1. 读取评审模板 references/review_prompt.md 加载评审维度
2. 遍历本批次的每个开发者：
   - 读取 {{input_path}}/<开发者姓名>/*.md 文档内容
   - 按评审模板输出结构化 JSON
3. 收集本批次所有 JSON，组成一个 JSON 数组
4. **写入文件**：
   - 输出路径（必填）：{{output_path}}
   - 格式：JSON 数组 `[{...}, {...}, ...]`
   - 编码：UTF-8
   - 缩进：2 空格
   - ensure_ascii=False（保留中文）
5. **写盘后自验证**：
   - 调用 `python {{scripts_dir}}/validate_review_results.py --input {{output_path}}`
   - 验证失败则修正后重写，直到通过
6. **验证通过后必须回显**：`PASSED: {{output_path}}`

## 输出约束（刚性）
- 必须把结果写入磁盘文件 {{output_path}}
- 不允许只返回 JSON 字符串而不写盘（这会导致后续合并步骤失败）
- 文件不存在 = 任务失败
- 回显 "SAVED: ..." = 任务成功

## 失败处理
如果某开发者文档为空 / 不存在：
- 在 JSON 中标记 "insufficient_data" 字段
- 不跳过，继续处理其他开发者
- 最后仍要写盘

如果写入失败（权限、磁盘满等）：
- 回显错误信息
- 任务失败，让主 Agent 决定如何处理
````

---

## 主 Agent 调用示例

```python
# 主 Agent 伪代码
batch_size = 5
actually_attended = [...]  # 40 个姓名
for idx, batch_start in enumerate(range(0, len(actually_attended), batch_size), 1):
    names = actually_attended[batch_start:batch_start + batch_size]
    names_str = "\n".join(names)
    output_path = f"D:\\项目文档\\AIAssistive\\tmp\\batch_{week}_{idx}.json"
    prompt = template.render(idx=idx, week=week, names=names_str, ..., output_path=output_path)
    dispatch_subagent(prompt)  # Task 工具
```

---

## 写盘后自验证（刚性步骤）

subagent 写盘后**必须**执行以下验证流程：

1. **立即调用验证脚本**：
   ```
   python {{scripts_dir}}/validate_review_results.py --input {{output_path}}
   ```
2. **验证失败时**（返回码 ≠ 0）：
   - 检查 JSON 解析是否成功
   - 修正格式问题（字段缺失、类型错误）
   - 重新写入文件
   - 重新验证，直到通过
3. **验证通过后必须回显**：`PASSED: {{output_path}}`
4. **验证通过后才算任务成功**，方可返回结果

> 注意：`{{scripts_dir}}` = `D:\项目文档\AIAssistive\ai\skills\aiweekly-report\scripts`

---

## 验证失败重试示例

```
写盘 → 验证失败 → 修正格式 → 重写 → 验证通过 → 返回 PASSED
```

如果某批次反复验证失败超过 3 次，回显错误并退出，让主 Agent 决定处理方式。

---

## 验证通过标准

- JSON 可解析为数组
- 每个元素包含 `name` 字段
- 关键字段存在：`overall_score`、`document_quality`、`ai_adoption_rate`、`anti_patterns`、`improvement_suggestions`
- `overall_score` 为数字（或 `insufficient_data=true`）

---

## 临时文件命名规则

固定格式：`batch_<week>_<idx>.json`

- `<week>`：周次标签（如 `0525-0531`）
- `<idx>`：批次索引，从 1 开始

示例：
- `batch_0525-0531_1.json` — 第 1 批
- `batch_0525-0531_2.json` — 第 2 批
- `...
- `batch_0525-0531_8.json` — 第 8 批

这种命名支持：
- 同一天多次运行（week 标签区分）
- 流程结束后按 `batch_<week>_*.json` 模式批量清理
