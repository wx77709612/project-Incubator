---
name: project-incubator
description: Use when：用户显式调用旧 project-incubator 名称，需要转交已安装的 Project Incubator Plugin Router；本兼容入口不执行项目孵化。
---

# Project Incubator 兼容入口

立即转交已安装插件的 `project-incubator-router` Skill，并遵守该 Router 的现行指引。项目类型、恢复和推进由 Plugin Router、已绑定 Child Skill 与 MCP Kernel 负责。

Plugin 或 Router 不可用时，报告缺失并停止；不得回退到旧运行资产，不得自行初始化、创建状态、推断路由或复制另一套 Runtime。

本文件仅保留旧名称的最小路由兼容性，不定义阶段、状态权威、授权流程或模板创建规则。
