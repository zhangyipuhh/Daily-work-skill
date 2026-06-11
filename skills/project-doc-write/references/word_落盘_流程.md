# write Step 4.7 落盘流程（word 文档生成）

> write 流程产物的 .md 文件**必须**通过"操作 word 的 skill"转成 .docx 后落盘。本文档说明完整流程。

## 0. 前置条件

- 已按 Step 4.1~4.6 完成 .md 内容生成
- .md 已含"封面信息 + 目录 + 正文 + 表格 + 列表"等完整结构（见 `word_格式范本_规则.md §8`）
- 内容已通过 `references/文档内容_净化规则.md` 净化（去掉评审稿/—/废话）

## 1. 落盘流程

```
Step 4.7 落盘
   │
   ├─ 4.7.1 落 .md 到项目目录
   │        <项目根>/03_技术文档及评审/<对应子目录>/<文档名>.md
   │
   ├─ 4.7.2 【关键】检查"操作 word 的 skill"是否在当前 skill 库
   │        │
   │        ├─ 模型自检：当前可用 skill 中是否有以下任一：
   │        │     - docx-skill
   │        │     - word-skill
   │        │     - docx-generator
   │        │     - markdown-to-word
   │        │     - md2docx
   │        │     - pandoc-skill
   │        │     - 或其他可处理 .md → .docx 转换的 skill
   │        │
   │        ├─ 存在 → 4.7.3
   │        │
   │        └─ 不存在 → 【提示用户】
   │              停止落 .docx 流程
   │              输出提示："⚠️ 项目级 .docx 文档生成需要操作 word 的 skill，
   │                      当前环境未找到。本文档将只落 .md 中间稿。
   │                      请确认：
   │                      1) 安装 docx-skill（或同类 skill）后重跑 Step 4.7
   │                      2) 或手动用 Word/Pandoc 打开 .md 转换"
   │              跳到 4.7.4
   │
   ├─ 4.7.3 【调 word skill 转 .docx】
   │        │
   │        └─ 模型动作：
   │              - 调"操作 word 的 skill"将 <output.md> 转成 <output.docx>
   │              - 套用 `references/word_格式范本_规则.md` 的样式：
   │                * 封面（项目名/编号/文档名/版本/日期）
   │                * 目录（1-3 级标题）
   │                * 字体/字号/行间距/段落间距
   │                * 页眉页脚（项目编号/文档名/页码）
   │              - 输出 <项目根>/03_技术文档及评审/<对应子目录>/<文档名>.docx
   │
   ├─ 4.7.4 落中间稿到 AIAssistive\output\
   │        <项目根>/AIAssistive/output/<项目号>/<文档名>_草稿.md
   │
   └─ 4.7.5 追加变更记录
            python ../project-doc-workflow/scripts/append_change_log.py
            --project-root <项目根> --doc-type <文档类型>
            --change-type 新增 --summary "自动生成 V1.0 + 调 word skill 转 .docx"
```

## 2. 关键约束

### 2.1 write 不创建 docx-skill

write **不**自行创建或安装 docx-skill。这是用户安装的第三方 skill。

### 2.2 write 不硬编码调用方式

write **不**在 SKILL.md / reference 中硬编码：
- ❌ `python ../docx-skill/scripts/md_to_docx.py ...`
- ❌ `from docx import Document` 自己写转换逻辑

write **只告诉模型**"去调操作 word 的 skill"，由模型根据当前 skill 库选择。

### 2.3 write 不替模型做决定

若模型判断当前无 word skill，**提示用户**即可，**不**自动跳过、**不**自动用 pandoc 命令行兜底。

### 2.4 落盘必须同时落 .md 和 .docx

- .md 是**正式产物**（项目目录必须有，可被评审引用）
- .docx 是**正式产物**（项目目录必须有，可走项目评审流程）
- 中间稿（AIAssistive\output\）只保留 .md 即可

## 3. 反模式（严禁）

| 反模式 | 后果 |
|---|---|
| write 自己用 python-docx 现场生成 .docx | 违反单一职责 + 违反反模式红线（python 代码中 import） |
| write 硬编码 `python ../docx-skill/scripts/...` | 违反高内聚低耦合 |
| 跳过 docx-skill 检查直接落盘 | 用户拿不到 .docx，违反流程 |
| 用 pandoc 命令行兜底 | 跨平台不一致 + 违反"调 skill 而非命令" |
| 只落 .md 不落 .docx | 用户需手动转换，违反 V1.0 流程目标 |

## 4. 状态标签与角色表

| 字段 | 规则 | 来源 |
|---|---|---|
| 文档状态 | 默认不写；用户在策划表/需求中明确指定时按其要求写 | `word_格式范本_规则.md §11` |
| 角色签名表 | 默认不写；策划表中有具体姓名时按策划表填写 | `word_格式范本_规则.md §12` |
| 编制/审核/批准 | 角色名取自策划表的具体字段 | 同上 |

## 5. 错误处理

| 场景 | 处理 |
|---|---|
| docx-skill 调用失败 | 提示用户，但 .md 已落盘的项目目录保留 |
| docx-skill 输出 .docx 缺封面/目录 | 提示用户检查 docx-skill 配置，不重试 |
| 文档内容无数据（如测试报告） | Step 4.2.5 主动询问；用户确认"无数据"后章节保留但带"**待补**"标记，不写占位 |

## 6. 与 project-doc-workflow 的协作

workflow skill 的 Step 4.6 调 `append_change_log.py` 追加变更记录，**不**直接调 word skill。word skill 落盘由 write 在 Step 4.7 完成。
