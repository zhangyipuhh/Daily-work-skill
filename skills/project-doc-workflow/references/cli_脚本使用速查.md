# project-doc-workflow · CLI 脚本使用速查

> 本 skill 共有 1 个私有 CLI 脚本。所有动作走 CLI。

## 0. 脚本清单

| 脚本 | 类型 | 用途 |
|---|---|---|
| `scripts/append_change_log.py` | CLI | **向项目变更记录追加一行** |

> workflow 不带 DocumentLoader 库与 read_doc.py（自身不读项目文件）。
> 流程中**读项目文件**的动作委托给 query / write skill 的 CLI（见 §3 跨 skill 引用）。

---

## 1. append_change_log.py 完整说明

### 1.1 用途

向 `<项目根>/06_变更及暂停/变更记录.md` 追加一行变更记录（Markdown 表格行）。

### 1.2 参数

| 参数 | 类型 | 默认 | 必填 | 说明 |
|---|---|---|---|---|
| `--project-root` | PATH | — | 是 | 项目根目录绝对路径 |
| `--doc-type` | TEXT | — | 是 | 文档类型（如 "测试方案"） |
| `--change-type` | TEXT | 新增 | 否 | 变更类型：新增/更新/删除 |
| `--summary` | TEXT | (auto) | 否 | 变更摘要（缺省自动拼 "由 project-doc-skill V1 自动新增"） |
| `--operator` | TEXT | project-doc-skill | 否 | 操作人/系统 |

### 1.3 自动行为

- 文件不存在 → 自动创建并写入表头
- 项目编号从项目根目录名自动提取（如 `202410-C0008-...` → `202410-C0008`）
- 日期自动填今天（YYYY-MM-DD）

### 1.4 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 项目根目录不存在 |

### 1.5 用例

#### 1.5.1 新增文档后追加记录

```bash
python scripts/append_change_log.py \
    --project-root "D:\项目文档\202410-C0008-..." \
    --doc-type "测试方案" \
    --change-type "新增" \
    --summary "自动生成 V1.0 大纲与正文" \
    --operator "project-doc-skill"
```

#### 1.5.2 更新文档

```bash
python scripts/append_change_log.py \
    --project-root "D:\项目文档\202410-C0008-..." \
    --doc-type "需求说明书" \
    --change-type "更新" \
    --summary "按客户反馈补充非功能需求章节"
```

#### 1.5.3 仅指定必填项（其他用默认）

```bash
python scripts/append_change_log.py \
    --project-root "D:\项目文档\202410-C0008-..." \
    --doc-type "验收报告"
```

---

## 2. workflow 流程与 CLI 的对应

workflow 的 4 步流水线中，每步"机械动作"对应的 CLI：

| 步骤 | CLI |
|---|---|
| Step 1 hub 调度 | （无 CLI，调度由 hub 负责） |
| Step 2 query 资料抽取 | 委托给 query skill（用 query 的 read_doc.py / find_planning_sheet.py） |
| Step 3 outline 生成大纲 | 委托给 outline skill（用 outline 的 extract_docx_outline.py） |
| Step 4 write 填充 + 决策 + 落盘 | 委托给 write skill（用 write 的 read_doc.py / extract_docx_outline.py） |
| **Step 4 末尾追加变更记录** | **本 skill 的 append_change_log.py** |

---

## 3. 跨 skill 引用（read 项目文件时）

workflow 自身不带 read_doc.py，**读项目文件的动作需跨 skill 调用**：

```bash
# 读策划表评审计划
python ../project-doc-query/scripts/read_doc.py --file "D:\...\策划表V1.0.xlsm" --sheet 评审计划 --output table

# 找最新版策划表
python ../project-doc-query/scripts/find_planning_sheet.py --project-root "D:\项目文档\202410-C0008-..." --output path
```

完整参数表见 `../project-doc-query/references/cli_脚本使用速查.md`。

---

## 4. 反模式 → 正确写法 对照表

| 反模式 | 正确写法 |
|---|---|
| 手动 `open("变更记录.md", "a").write(...)` | `python scripts/append_change_log.py --project-root ... --doc-type ...` |
| `python -c "from openpyxl import load_workbook; ..."` | 委托给 query skill 的 read_doc.py |
| 跳过追加变更记录 | 强制调用 append_change_log.py（Step 4.6 刚性约束） |

---

## 5. 常见问题 FAQ

**Q: append_change_log.py 重复跑会怎样？**
A: 每次追加一行新的表格行，**不去重**。如果担心重复，可在调用前先 Read 变更记录文件看是否已存在相同条目。

**Q: 变更记录文件在哪里？**
A: `<项目根>/06_变更及暂停/变更记录.md`（固定路径，写在脚本常量中）。

**Q: workflow 的 4 步是否可以全部用本 skill CLI 闭环？**
A: 当前不能。Step 2/3/4 的"读项目文件"动作必须跨 skill 调用 query/write/outline 的 CLI（高内聚低耦合的代价）。如需"一步到位"，可在 workflow 下加聚合脚本（未来扩展）。
