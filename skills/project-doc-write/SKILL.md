---
name: project-doc-write
description: Use when the user has an approved outline and wants the document body filled in based strictly on existing project artifacts (策划表/需求/合同/方案/周报 etc.) — generates 决策与意见 from real project data deltas, never invents content, asks user when info is missing
---

# Project Doc Write（填充内容 + 决策建议）

> **阶段定位**：V1 基础能力版。

## 概述

在 `project-doc-outline` 输出的章节大纲上，**严格基于项目已有资料**填充正文，并基于策划表/合同/周报的实际值与基线值之差生成"决策与意见"。

> **核心原则：确定的事由脚本完成，需要判断的事由大模型完成。**
> 读取策划表子标签、抽取 docx 章节等"机械工作"走 `scripts/`，正文撰写与决策建议由模型完成。

---

## 触发条件

- 用户已有大纲（hub 生成或 outline 提供）
- 用户要求"按已有项目资料写完整文档"
- 用户要求"补全/更新某文档"

---

## 刚性约束

1. **严禁虚构**：所有正文内容必须有项目证据。证据缺失 → **主动询问**用户。
2. **格式范本**：默认从 `<项目根>/03_技术文档及评审/01_实施方案/*.docx` 抽取章节作为格式范本。
3. **决策与意见来源**：`references/决策建议生成规则.md` + `references/严禁虚构_红线清单.md`。
4. **多框架叠加**：每条决策与意见必须标注 `【框架：{PMP|PRINCE2|系统分析师} · {层次}】`。
5. **变更记录强制**：每次写完文档，**必须**在 `<项目根>/06_变更及暂停/变更记录.md` 追加一条记录（按策划表子标签规整格式）。
6. **读文件走 DocumentLoader**：禁止在 `tmp/` 或 `D:\` 根目录写一次性脚本读文件。
   走本 skill **自带的** `scripts/DocumentLoader.py`（**所有 .py 都在 `scripts/` 下**），不依赖外部包。
   8 个 Loader（Word/PDF/Text/Markdown/CSV/JSON/Eml/Excel）全部在 `scripts/loader/` 子包内。
7. **扫描件检测**：PDFLoader 提取文本 < 100 字符 → 视为扫描件 → 提示用户提供可读版。

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
Step 1  接收大纲（来自 outline）
   ↓
Step 2  加载项目资料（DocumentLoader）
   ├─ 策划表 xlsm
   ├─ 需求/设计/合同 docx/pdf
   └─ 格式范本 docx（从 01_实施方案 取）
   ↓
Step 3  按章节顺序逐章填充
   ├─ 内容有证据 → 直接写
   ├─ 内容无证据 → 询问用户（用 references/澄清问题_模板.md 的提问脚本）
   └─ 内容超规范 → 提示超范围，询问是否保留
   ↓
Step 4  生成"决策与意见"章节（references/decision_advisory_template.md）
   ↓
Step 5  扫描件检测（references/扫描件_处理规则.md）
   ↓
Step 6  追加变更记录（references/变更记录_追加格式.md）
   ↓
Step 7  输出（项目目录最终落盘 + AIAssistive\output\ 中间稿）
```

---

## 资源引用

- 格式范本提取方法：`references/实施方案_格式范本_提取说明.md`
- 软件工程文档章节填写规范：`references/软件工程文档_章节填写规范.md`
- 决策建议生成规则：`references/决策建议生成规则.md`
- 严禁虚构红线清单：`references/严禁虚构_红线清单.md`
- 范本抽取脚本：`scripts/extract_docx_outline.py`（已配置为同 skill 内 import DocumentLoader + ExcelLoader）

---

## 未来扩展

- 自动从历史同类文档反推模板
- AI 决策建议打分（与项目集/PMO 库联动）
- 多语言版本生成
