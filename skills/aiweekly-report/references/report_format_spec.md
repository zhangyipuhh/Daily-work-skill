# AI 辅助编程评审报告 格式说明

> 适用版本：aiweekly-report Skill V2.1+  
> 参考样例：`D:\项目文档\AIAssistive\output\AI辅助编程评审报告0511-0517.docx`  
> 最后更新：2026-06-02

本说明定义每周 DOCX 报告的统一样式，任何报告生成脚本（`scripts/generate_report.py`）必须严格遵守。

---

## 1. 全局样式

| 项 | 规范 |
|---|---|
| 字体（中英文混排） | Arial + 微软雅黑 |
| 字体颜色 | 黑色 `RGBColor(0, 0, 0)` |
| 正文字号 | 11 pt |
| 页面 | A4 默认页边距（2.54cm） |
| 段落默认对齐 | 左对齐 |
| 行距 | 单倍 |

---

## 2. 标题层级

| 级别 | 用途 | 字号 | 样式 | 对齐 |
|------|------|------|------|------|
| Title | 报告主标题"AI 辅助编程评审报告" | 22 pt | docx Title | 居中 |
| Heading 1 | 一级标题"第 X 章 XXX" | 18 pt | Heading 1 | 左对齐 |
| Heading 2 | 二级标题"X.X XXX" | 14 pt | Heading 2 | 左对齐 |
| Heading 3 | 三级标题"### XXX" | 12 pt | Normal + bold | 左对齐 |

字体规范：所有标题均使用 `Arial + 微软雅黑`，加粗。

---

## 3. 章节结构（7 + 1 模型）

报告必须按以下顺序生成 7 个章节 + 1 个总结。

| 顺序 | 章节 | 实现函数 | 必选 |
|------|------|----------|------|
| 0 | 标题 + 副标题 | `add_title()` | ✅ |
| 1 | 第一章 概述 | `chapter_summary()` | ✅ |
| 2 | 第二章 汇总统计 | `chapter_stats()` | ✅ |
| 3 | 第三章 评审结果汇总 | `chapter_top_bottom()` | ✅ |
| 4 | 第四章 改进建议汇总 | `chapter_improvements()` | ✅ |
| 5 | 第五章 不足与改进建议 | `chapter_gaps()` | ✅ |
| 5.x | 5.x 本周未提交者 | `chapter_missing_inline()` | ✅ |
| 6 | 第六章 整体趋势变化分析 | `chapter_full_compare()` | ✅ |
| 总结 | 总结 | `chapter_conclusion()` | ✅ |
| 7 | 第七章 全量比对（最近 4 次） | `chapter_baseline_compare()` | ✅ |

### 3.1 章节子编号规则

- 一级章节：第一章 ~ 第七章
- 二级章节：2.1、2.2、2.3、3.1、3.2、4.1~4.5、5.1~5.3、5.x（漏检）
- 三级标题：使用"### 标题"格式

### 3.2 漏检名单位置

漏检名单嵌入第五章，作为子章节 "5.x 本周未提交者"（参考样例无独立漏检章节）。

---

## 4. 表格样式

| 项 | 规范 |
|---|---|
| 表格样式 | `Light Grid Accent 1` |
| 表头填充色 | `#4472C4`（深蓝） |
| 表头文字 | 白色 + 加粗 + 10 pt |
| 隔行底纹 | 偶数行 `#F2F2F2`（浅灰） |
| 单元格字体 | Arial + 微软雅黑 + 10 pt |
| 单元格对齐 | 水平左对齐、垂直居中 |
| 缺失值 | 渲染为 `—`（em dash） |

### 4.1 通用表格结构

```python
def add_table(doc, headers, rows):
    table = doc.add_table(rows=1+len(rows), cols=len(headers))
    table.style = "Light Grid Accent 1"
    # 表头：白字 + 深蓝填充
    # 偶数行：浅灰底纹
    # 单元格：10pt 黑色 Arial
```

---

## 5. 段落样式

| 段落类型 | 样式名 | 对齐 | 用途 |
|----------|--------|------|------|
| 普通正文 | `Normal` | 左对齐 | 描述、说明 |
| 列表项 | `List Paragraph` | 左对齐缩进 | 建议、要点列表 |
| 强调段落 | `Normal` + bold | 左对齐 | 章节子标题（###） |

---

## 6. 关键章节细节

### 6.1 第二章 汇总统计

- 必须包含 1 张主表（指标 × 数值）
- 平均值保留 2 位小数
- 百分比保留 1 位小数 + `%` 后缀
- 反模式命中数（has_issues=True 的人数）

### 6.2 第三章 评审结果汇总

- 包含 3 张表：Top 10、Bottom 5（如有）、Excel 样本
- Top 10 表头：`排名 | 开发者 | 综合评分 | AI 采纳率 | 改进优先级`
- Bottom 5 表头：`排名 | 开发者 | 综合评分`

### 6.3 第四章 改进建议汇总

- 包含 5 张子表（4.1~4.5）：
  - 4.1 文档结构方面
  - 4.2 内容完整性方面
  - 4.3 反模式修正方面
  - 4.4 AI 采纳优化方面
  - 4.5 AI 使用优化方面
- 每张子表：`建议 | 出现次数`（Top 8 频次）

### 6.4 第五章 不足与改进建议

- 必含 2 张表：
  - 5.1 当前不足表：`问题类型 | 人数 | 涉及人员（部分）`
  - 5.x 本周未提交者表：`序号 | 姓名`

### 6.5 第七章 全量比对（最近 4 次）

- **新模型**：从 baseline.db 读取每位开发者最近 4 周评分
- 表头：`开发者 | 第1次 | 第2次 | 第3次 | 第4次 | 趋势 |
- 趋势列：`↑ 提升` / `↓ 下降` / `— 持平` 
- 按本周评分降序排列
- **仅含本周提交者**（不含历史周已离开人员）

---

## 7. 输出文件命名

```
AI辅助编程报告_<week>.docx
```

示例：`AI辅助编程报告_0525-0531.docx`

---

## 8. 字体实现细节

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_run_fonts(run, ascii_font="Arial", east_asia_font="微软雅黑"):
    """统一设置 run 字体：ASCII + 东亚双字体"""
    run.font.name = ascii_font
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:eastAsia"), east_asia_font)
    rFonts.set(qn("w:ascii"), ascii_font)
    rFonts.set(qn("w:hAnsi"), ascii_font)
```

所有 `add_paragraph`、`add_heading`、`set_cell_text` 必须调用此函数。

---

## 9. 验收检查清单

生成报告后必须逐项验证：

- [ ] 报告主标题居中、22pt
- [ ] 第一章~第七章 + 总结 顺序正确
- [ ] 漏检名单嵌入第五章 5.x
- [ ] 表格表头深蓝、隔行浅灰
- [ ] 缺失值渲染为 `—`
- [ ] 第七章从 baseline.db 读取，每人最多 4 行 + 趋势列
- [ ] 中文字体正确（无宋体回退、无乱码）
- [ ] 字体颜色全部黑色
- [ ] 页边距 2.54cm（A4 默认）

---

> 本说明是 aiweekly-report Skill 内部的"格式契约"，任何与本说明冲突的脚本代码视为 BUG。
