# 人名配置清单说明

## 标准清单

**唯一权威来源**：`D:\项目文档\AIAssistive\project_284_members.txt`

格式：每行一个姓名，UTF-8 编码，纯文本。**人数随清单动态变化，不写死**。

## 用法

漏检检测脚本 `check_missing.py` 默认从该文件读取应到名单。

如需在 Skill 调用时临时更换清单，可通过 `--members` 参数指定其他文件。

## 维护规则

- 新增成员：在文件末尾追加一行
- 删除成员：删除对应行
- 不要修改现有行的顺序或格式

## 与 config.yaml 中 user_mapping 的关系

`D:\项目文档\AIAssistive\script\checkCode\config\config.yaml` 里的 `user_mapping` 段
记录的是"中文名 → GitLab username"映射，用于代码提交查询。
本 Skill **不**使用该映射（因为评审不需要 GitLab username，仅需中文名匹配）。
