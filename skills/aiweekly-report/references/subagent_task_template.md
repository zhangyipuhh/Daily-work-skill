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
4. **关键步骤 — 写入文件**：
   - 输出路径（必填）：{{output_path}}
   - 格式：JSON 数组 `[{...}, {...}, ...]`
   - 编码：UTF-8
   - 缩进：2 空格
   - ensure_ascii=False（保留中文）
5. 写盘完成后**必须回显**：`SAVED: {{output_path}}`

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

## 验证步骤

subagent 完成后，主 Agent 验证：
1. 检查文件 `{{output_path}}` 是否存在
2. 读取并解析为 JSON 数组
3. 数组长度应等于 `{{names}}` 列表长度
4. （可选）调用 `validate_review_results.py --input <batch_file>` 做格式验证
5. 验证通过后进入下一批或进入 Step 4.8 合并

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
