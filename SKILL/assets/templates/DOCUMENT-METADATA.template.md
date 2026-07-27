# Document Metadata Template

> 用于 Project Incubator Skill 在目标项目 `DOCS/` 下创建权威项目文档时生成文档状态元数据。实例化后删除本说明。

## 文档状态

| 字段 | 当前值 |
| --- | --- |
| 所属项目 | {{PROJECT_NAME}} |
| 所有者 Phase | {{OWNER_PHASE}} |
| 文档状态 | Draft |
| 权威范围 | {{AUTHORITY_SCOPE}} |
| 消费 Phase | {{CONSUMING_PHASES}} |
| 更新条件 | {{UPDATE_CONDITIONS}} |
| 依赖文档 | {{DEPENDENCY_DOCUMENTS}} |
| 最后更新 | {{DATE}} |

## 使用规则

- 仅用于目标项目 `DOCS/PROJECT_STATE.md` 或 `DOCS/<phase>/` 下的权威项目文档；
- 不用于目标项目根目录 `AGENTS.md`、Skill runtime reference、代码、配置、Prompt 正文或非文档资产；
- 实例化时必须用 Maker 已确认事实或已接入项目材料填充占位字段；
- 如果某字段无法确认，先保留为待确认内容，不得用 AI 自由补造事实；
- 具体正文结构由对应 Phase、文档类型模板或 Maker 明确授权决定。
