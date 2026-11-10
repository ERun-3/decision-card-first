# 贡献你的实测结果

`docs/results.csv` 是跨 Agent 平台的行为实测记录。欢迎用 PR 追加你所在平台的行。

## 规则

1. 每行必须含 `pkg_sha256`——锁住被测包版本，否则无法复跑，一律拒收。
2. L0（安装）六项按 `docs/TEST-PLAN.md` 的定义评分，**复核落盘后再填**：
   MD5 比对安装文件、grep 全局规则文件、检查产物，不采信 Agent 自述。
3. L1a 拆两列：`rule_visible`（规则被读到）与 `gate_respected`（先出卡并停下）。
   被用户中断的会话记「截断」、`valid_for_threshold=0`，不要猜终态。
4. 平台目录 / 全局规则文件路径各异：P1/P3 按 `TEST-PLAN.md` 的「平台换算」节判定，
   不支持 Skill 机制的记 N/A 而非 0 分。
5. 一行一 case，notes 写清时间、会话来源与复核方式。

## 当前缺口（欢迎认领）

- WorkBuddy / ZCode 平台的 L1b、L1c
- E 阴性对照（blank control）
- 任何新平台的完整 L0
