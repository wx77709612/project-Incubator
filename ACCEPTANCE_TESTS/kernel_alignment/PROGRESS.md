# 执行记录 — KERNEL_ALIGNMENT_IMPLEMENTATION_PLAN.md

2026-10-19：Maker 确认正式规格、逐项 Invariant 与 Task 1–4。

Pre-flight：Task 1 产出失败检查供 Task 2 使用；Task 2 的自包含指导供 Task 3 候选验证；Task 4 汇总实际安装与回归，接口无冲突。

Ruling：在既有 ACCEPTANCE_TESTS/kernel_alignment 维护持久执行记录，避免额外权威文档；不使用依赖 Bash 的技能脚本，按仓库 Task 格式直接记录验证。

Task 1: RED captured — 9 checks, 8 failed, 1 negative-control passed; drift-red.log.
Ruling：保留被替换的旧指导为 references/legacy 的非活动参考，RC 显式构建读取该参考；旧文案测试改为验证此兼容参考，运行逻辑测试保留。新增作用域说明覆盖旧活动规格。
Task 2: implementation written; validation pending.

Legacy integration RED：32 tests，2 errors + 2 failures；RC renderer 把新 Legacy 注释误判为 YAML 起点。移除渲染输入前置注释后保留原 RC frontmatter；未改校验器或 Runtime。

Task 2: Plugin suite 312/312; Legacy unit 132/132 and e2e 3/3; integration fix verification pending.
Task 3: Candidate drift RED reproduced: old verifier returned 0 for injected obsolete guidance and Mod fallback. Added shared candidate/source checker; GREEN verification pending.

独立审查：Critical 0 / Important 3 / Minor 0。三项均经 review-red.log 和 review-rc-red.log 复现：同行否定豁免、相对/Windows 规格路径、RC 根 AGENTS/README 混用。
Ruling：漂移检测按分句处理否定，并保守拒绝任何大小写或分隔符形式的 SPECS 路径；显式 RC 对根 AGENTS/README 也使用 Legacy 参考，现行 Plugin 保持不分发 Legacy。
Final review declined事项处置：安装/宿主加载仍必须执行；真实项目和scriverse明确排除；不把自然语言lint当完备语义证明；无merge/push/release。既有领域/Profile/_V未改，pyc已恢复。

Final: fixed all 3 Important findings — review-green.log 11/11, RC builder 7/7, complete Plugin suite 342/342; Legacy final133/32/3; all11Acceptance stages79/79. No deferred minors.
Task 3: official codex plugin add installed 0.3.0+codex.20261019210340; source/candidate 41 files identical; candidate and installed aggregate SHA256 identical; global old Skill fully backed up outside active skills, minimal shim installed.
Host first run: read-only CLI default never policy rejected MCP calls before execution; subsequent model capacity failure. A replay with standard --approve-for-me is in progress; no bypass.

本地实现提交63f1565，分支codex/runtime-skill-alignment；无合并/推送/发布。新日志加入index后发现Node失败输出自带行尾空格，已只规范化.log行尾空白，不改测试内容或结果。
Host新会话inspect_project已成功：revision0，Receipt verified；三路由误用project_type/host_profile被真实Schema拒绝，已提供精确JSON重放；Kernel未更改。

Task 1: complete — initial RED8/9; final source/candidate checks green.
Task 2: complete — guidance/governance and RC compatibility, protected code/Profile unchanged.
Task 3: complete — official install0.3.0+codex.20261019210340, hash/source paths match, newhost inspect and three routes PASS.
Task 4: complete — Plugin342; Legacy133/32/3; Acceptance79; allA01–A11closed; no deferred minors or release claims.
