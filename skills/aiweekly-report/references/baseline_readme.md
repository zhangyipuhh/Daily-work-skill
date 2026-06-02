# Baseline 基准库说明

> 路径：`D:\项目文档\AIAssistive\baseline\`  
> 最后更新：2026-06-02

---

## 1. 用途

Baseline 库用于：
1. 记录每期（周）每位开发者的评审总分
2. 报告"第七章 全量比对"按人列出最近 4 次总分
3. 跨周趋势分析、个体变化追踪
4. 防止评审数据丢失（永久存档）

---

## 2. 存储格式：SQLite

| 文件 | 说明 |
|------|------|
| `baseline.db` | 主数据库（SQLite 3） |

为什么用 SQLite：
- Python 内置 `sqlite3`，零外部依赖
- 支持 SQL 查询、索引、约束
- 单文件、易备份、易恢复
- 高效读取历史数据生成对比表

---

## 3. 表结构

```sql
CREATE TABLE review_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  week TEXT NOT NULL,                    -- 周次，如 '0525-0531'
  name TEXT NOT NULL,                    -- 开发者姓名
  overall_score REAL,                    -- 综合评分 (0-10)
  doc_quality REAL,                      -- 文档质量 (0-10)
  doc_completeness REAL,                 -- 文档完整性 (0-10)
  doc_clarity REAL,                      -- 文档清晰度 (0-10)
  doc_technical REAL,                    -- 技术准确性 (0-10)
  ai_adoption REAL,                      -- AI 采纳率 (0-1)
  doc_code_consistency REAL,             -- 文档代码一致性 (0-1)
  doc_task_consistency REAL,             -- 文档任务一致性 (0-1)
  has_anti_patterns INTEGER DEFAULT 0,  -- 是否反模式 (0/1)
  priority TEXT,                         -- 'high' / 'medium' / 'low'
  timestamp TEXT NOT NULL,               -- 写入时间 ISO 格式
  UNIQUE(week, name)                     -- 同一周同人只 1 条
);

CREATE INDEX idx_name ON review_history(name);
CREATE INDEX idx_week ON review_history(week);
```

---

## 4. 数据来源

每次 `update_baseline.py` 运行时：
- 读取 `output/review_results_<week>.json`
- 解析 `data.overall_score`、`data.name` 等字段
- 使用 `INSERT OR REPLACE` 写入（支持同周重跑覆盖）

---

## 5. 维护脚本

### 5.1 写入/更新

```bash
python scripts/update_baseline.py \
  --input "D:\项目文档\AIAssistive\output\review_results_0525-0531.json" \
  --db "D:\项目文档\AIAssistive\baseline\baseline.db"
```

行为：
- 同一 (week, name) 已存在则覆盖（用最新数据）
- 打印：新增 N 条、覆盖 M 条、跳过 K 条
- 返回码：0=成功，2=文件不存在

### 5.2 查询示例

```sql
-- 查询某开发者最近 4 次评分
SELECT week, overall_score, ai_adoption
FROM review_history
WHERE name = '张三'
ORDER BY week DESC
LIMIT 4;

-- 查询本周所有人评分
SELECT name, overall_score
FROM review_history
WHERE week = '0525-0531'
ORDER BY overall_score DESC;

-- 查询某周统计
SELECT COUNT(*) AS total,
       AVG(overall_score) AS avg_score,
       MAX(overall_score) AS max_score,
       MIN(overall_score) AS min_score
FROM review_history
WHERE week = '0525-0531';
```

---

## 6. 备份策略

- 每次写入自动更新（无需手动备份）
- 建议每周拷贝 `baseline.db` 到外部备份盘
- 删除文件前先用 `cp baseline.db baseline.db.bak` 备份

---

## 7. 与报告生成的关系

```
update_baseline.py (Step 7.5)
        ↓
   baseline.db
        ↓
generate_report.py (Step 8, --db 参数)
        ↓
  第七章"全量比对（最近 4 次）"表格
```

报告第七章的"最近 4 次"通过 SQL 查询 baseline.db 生成。

---

## 8. 容量预估

| 周次 | 人数 | 行数 |
|------|------|------|
| 1 周 | 40 | 40 |
| 10 周 | 40 | 400 |
| 52 周 | 40 | 2080 |

SQLite 处理 10 万行级数据无压力，可稳定运行多年。

---

> 任何对 baseline.db 的修改请记录在本文档"变更日志"中。

### 变更日志

| 日期 | 变更 | 操作人 |
|------|------|--------|
| 2026-06-02 | 初始创建 baseline.db 表结构 | AI Agent |
