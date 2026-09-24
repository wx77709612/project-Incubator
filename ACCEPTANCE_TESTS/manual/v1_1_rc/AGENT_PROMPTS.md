# 雾港提醒器：Agent Prompt 序列

## 使用规则

- Round 0 已由 Maker 完成，可直接从 Round 1 开始。
- 一次只发送一个 Prompt，等待 Agent 完成当前轮并提出必要问题。
- 不发送本文件的标题、轮次目的或任何 Maker 专用资料。
- Prompt 中的运行记录视为模拟目标环境的真实 Observation，不要求 Agent 重现实验。

## Round 0：RC 身份确认

```text
$project-incubator-v1-1-rc 请只报告实际加载的 Skill Identity、Package Version 和 Invocation Policy，不执行任何项目变更。
```

## Round 1：项目初始化与产品边界

```text
$project-incubator-v1-1-rc 我想孵化一个叫“雾港提醒器”的 Windows 11 桌面提醒工具。用户可以创建一次性或每日提醒，查看、编辑、停用提醒；提醒数据只保存在本机。核心体验是：应用窗口关闭甚至 Windows 重启后，到点仍应出现原生系统通知。

这是一个用于验证项目孵化流程的模拟项目。我最多能配合 4 次真实环境人工测试，不使用云服务，也暂不支持 Windows 以外的平台。请初始化项目，但本轮只澄清 Product Point、成功结果、不支持范围和需要我决定的事项，不要直接冻结技术架构或开始实现。
```

## Round 2：不透明性与证据等级

```text
我已经确认上一轮的产品边界。现在补充已知信息：公开资料只说明 Windows 存在原生通知接口和计划通知能力，但没有给出“任意未打包桌面程序在进程退出和系统重启后仍可靠触发”的稳定承诺。我们还没有做真实环境实验。

请评估各项 Capability 的不透明性，区分事实、Observation、Runtime Assumption、Hypothesis 和 Decision，并说明当前每项结论最多能达到哪个 Evidence 等级。不要因为 API 存在就宣称核心体验成立。
```

## Round 3：实施计划与垂直切片

```text
补充两类证据：

1. 本地确定性测试已经证明提醒数据的创建、编辑、停用和序列化规则可工作。
2. 一个隔离调用实验成功获得了计划通知注册 ID，但尚未观察到完整目标环境结果。

请据此制定进入实现阶段的最小计划。计划需要说明第一个代表性垂直切片、自动化验证与目标环境验证的边界、4 次人工测试预算如何使用、Known-Good Baseline 何时建立，以及什么情况下必须停止继续补丁。
```

## Round 4：P4 中假设失效

```text
请把以下内容作为 P4 实现阶段获得的真实运行记录：

- 人工测试 1：应用进程保持运行时，提醒按时出现。
- 人工测试 2：创建提醒后完全退出应用进程，提醒没有出现。
- 人工测试 3：创建提醒后重启 Windows，重启后提醒没有出现，而且原注册 ID 无法查询。
- 调用过程没有抛出异常，注册步骤仍返回成功。

这些结果与此前候选架构中的“计划通知由系统独立持久化”假设冲突。请处理当前项目状态并告诉我下一步，但不要把它当作功能已经完成后的普通 P6 迭代。
```

## Round 5：重复失败与模型审查

```text
补充失败记录：针对同一失效路径，先后尝试了增加等待时间、启动时重试注册、调整通知权限检查三种补丁。三次都得到相同结果：进程运行时成功，进程退出或重启后丢失；没有获得能区分新根因的证据。人工测试预算还剩 1 次。

请判断是否还应继续同方向修补，并更新当前 Assumption、Candidate Model、Confidence、Advisory 和下一步证据计划。
```

## Round 6：轻量纠偏与 Maker 决策

```text
现在获得新的平台证据：目标 Windows 版本中，这条持久通知路径要求应用具有打包身份，并通过清单注册后台激活入口；当前未打包的 Python 进程只能可靠覆盖进程存活期间的通知。

我的 Product Decision 不变：重启后仍能提醒是核心范围，不能通过缩小产品目标来关闭问题。我愿意接受“增加最小打包宿主”作为候选 Architecture Decision，但不批准重写本地提醒管理模块。

请在 P4 内执行必要的轻量设计与计划纠偏，明确哪些内容被重开、哪些保持冻结、哪些文档或实现受影响，以及恢复实现前还需要什么确认。
```

## Round 7：Baseline 与 Drift

```text
当前已知可工作状态如下：本地提醒 CRUD、序列化、停用逻辑和进程存活期间的通知路径均已通过；它们组成最近一次 Known-Good Baseline。

同时发现实现代码已经出现“打包宿主适配器”和“后台激活标识”两个概念，但 Active Design 里还没有这些概念。请在继续修改前检查 Baseline 回归影响和 Artifact/Implementation Drift，并给出最小处理方案。
```

## Round 8：Decision Supersession

```text
此前的活动 Architecture Decision 写着“由未打包 Python 主进程直接注册并承载全部通知生命周期”。新证据只推翻其中关于持久通知生命周期的部分；本地提醒管理仍由 Python 模块负责。

请更新 Decision 状态。不要通过无限追加全文来保留历史；使用活动视图、有界 Changelog 和必要归档，并说明 Supersedes、Effective Scope、New Evidence 与 Migration Impact。
```

## Round 9：最后一次人工证据与 Ring Closure

```text
人工测试 4 的结果如下：最小打包宿主安装成功；创建一条一次性提醒后重启 Windows，提醒在目标时间出现；本地 CRUD 回归测试仍通过。尚未验证每日提醒、权限被撤销、升级安装、多个 Windows 版本和长期重复运行。

人工测试预算已经用完。请判断当前 Ring 是否可以闭合，更新 Evidence Level、Capability Claim、Confidence 和 Known-Good Baseline，并明确哪些结论现在不能声明。不要要求我重复同类测试。
```
