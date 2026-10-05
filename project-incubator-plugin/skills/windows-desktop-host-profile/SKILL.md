---
name: windows-desktop-host-profile
description: Use when：Router 已为 desktop-product 明确选择 windows-desktop，需要把通用桌面孵化规则收紧为 Windows 环境、交付与真实环境 Evidence；不得单独触发或改写 P0–P6。
---

# Windows Desktop Host Profile

## 作用边界

本 Profile 只在 `desktop-product + windows-desktop` 路由已确认后与 Desktop Child Skill 配合使用。它增加 Windows 约束和 Evidence 要求，不定义业务能力、不拥有浏览器扩展，也不得重命名、跳过或增加 P0–P6 阶段。

## 必填环境上下文

在影响设计、构建或验证前，记录 Windows 版本与构建号、CPU/OS 架构及目标二进制架构、安装范围（当前用户/所有用户/便携模式）、权限模式（标准用户/按需提权/管理员运行）和分发格式。

未知值必须显式标为未知，不得自动采用当前开发机作为默认支持范围。

## Windows 收紧规则

### 文件系统、进程与系统集成

明确程序文件、用户数据、缓存、日志和临时文件位置；验证路径规范化、链接/重解析点、占用文件和意外覆盖。记录前台进程、后台进程、托盘、服务与子进程生命周期。注册表、文件关联、协议处理器、开机启动、防火墙规则和系统范围写入仅在 Product Boundary 明确包含且 Maker 授权时使用。

### 权限与安全软件

默认以标准用户和最小权限设计。需要提权时说明具体操作、范围、时机、取消与失败行为。把 Defender、SmartScreen、企业策略和第三方安全软件视为环境约束；被放行不等于行为安全，被拦截也不能在无证据时归因于单一原因。

### 打包与签名

验证产物清单、架构、依赖、版本信息和可复现来源。代码签名、证书信誉、时间戳与分发渠道按实际发布范围评估；未签名构建必须明确限制结论，不能宣称已具备生产信誉。

### 安装、升级、卸载与恢复

为适用的安装范围记录前置状态、写入位置、权限提示、进程占用、失败清理和完成状态。升级必须处理版本关系、配置/数据迁移、正在运行的旧进程和失败回滚。卸载必须区分程序文件、用户数据和共享资源。恢复路径至少提供安全停止、回到 Known-Good Baseline 或清楚的人工恢复步骤之一。

## TARGET_HOST_VALIDATION

真实环境 Evidence 至少绑定：Artifact 标识与哈希、Windows 版本/构建号、架构、安装范围、权限模式、分发格式、测试步骤、观察结果、失败/副作用和 Evidence 引用。

自动化测试可以证明纯逻辑与可重复操作；Desktop Automation 只能证明被测会话；`TARGET_HOST_VALIDATION` 只能支持已绑定环境。未测试的 Windows 版本、架构、权限模式、安全软件或企业策略不得纳入兼容声明。

涉及提权、系统范围写入、后台服务、开机启动、安全策略、自动更新或真实用户数据时，执行前需要 Maker Authorization 或既有明确授权范围。Host Profile 只能收紧 Shared Kernel 权限，不能放宽它。
