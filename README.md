# decision-card-first

> 防止 AI 重复造轮子：动手之前，先查一遍世界上有没有现成的。

给 Agent 一句「帮我做个 XX 工具」，它通常立刻开始装依赖、写代码——哪怕这个轮子早就有人造好了。这个 Skill 让 Agent 在动手之前先调研：检索现成软件与开源实现，核对许可证和维护状态，输出一张决策卡（候选表 / 硬门 / 五选一结论 / 召回边界 / 盲区），**然后停下等你确认**——不写代码、不建目录、不装依赖、不提 PR。

五选一：**直接用 / 抄思路 / 给上游贡献 / 长期分叉 / 自己写**。微小任务和「不要调研」的指令会走分流，不会每个任务都硬查一轮。

## 这个赛道有 5 个玩家，缺的是什么

「先调研再动手」不新鲜——发布前用这个 Skill 查了自己，找到 5 个同类。缺口很清楚：

| | [github-build-or-reuse](https://github.com/ghspain/github-build-or-reuse) | [reuse-before-build](https://github.com/Ai-Eastern/reuse-before-build) | 本项目 |
| --- | --- | --- | --- |
| 决策输出 | USE / CONTRIBUTE / FORK / BUILD | Take / Borrow / Build | 一页决策卡（硬门 + 五选一 + 召回边界） |
| 输出后停下等确认 | ❌ 继续走 | ❌ 仅用户要求时实现 | ✅ **硬闸门** |
| 安装时自举默认触发 | ❌ | ❌ | ✅ 注册进本平台全局规则文件 |
| 跨平台行为实测 | 证据 demo | 17 runs 对照（自评小样本） | ✅ 3 平台实测，逐 case 锁包哈希 |

各家都把「调研」讲清楚了，不需要第五个人再讲一遍。**没人做的是中间两行：让 Agent 出了报告真的停下来，以及装了就默认生效。**

## 实测数据（2026-11-09）

- **安装自举 3 个平台全部通过**（WorkBuddy / DSH / ZCode）：每个安装者都正确找到本平台的用户级目录与全局规则文件，逐字写入触发规则。复核方式是 MD5 比对 + 规则文件 grep，不采信 Agent 自述。
- **两个平台独立调研同一需求，收敛到同一个最优候选**（`jmaciasluque/md2img`），并各自从 `fonts.go` 源码独立复现「Windows 无字体路径、中文必退化为位图字体」。
- **成本对照**：调研轮实测 output 5,025 tokens；「不要调研直接写」的对照组实测产出 **940 行**自研 Pillow 渲染——正是决策卡警告的「自研排版深坑」的尺寸；调研后的薄层方案约 100–200 行 + 复用 MIT 库。

完整方案见 [`docs/TEST-PLAN.md`](docs/TEST-PLAN.md)（L0 冒烟 / L1 延迟验收 / 2×2 归因 / 阴性对照），逐 case 记录见 [`docs/results.csv`](docs/results.csv)（每行锁包 sha256，可复跑）。

## 已知弱点

- 闸门是文档级软约束，要 100% 保证需配 UserPromptSubmit hook。
- 只查外部生态，不查你的代码库——repo-first 类技能（如 reuse-before-build）与本项目互补。
- 验证仍在扩充：L0 3 平台全过，L1 样本还少；踩过的坑（评分表泄漏、截断样本、包未归档）都留了记录。

## 安装

把 [`decision-card-first.zip`](https://github.com/ERun-3/decision-card-first/releases/download/v3.1.0/decision-card-first.zip) 解压到本平台的**用户级** skills 目录（WorkBuddy 为 `~/.workbuddy/skills/decision-card-first/`）。包内 `INSTALL.md` 是给安装 Agent 的约定——**装了不等于默认生效**，注册那一步不能省。

装完开一个全新会话，直接发一句普通的从零构建需求即可。

## 复现

```bash
python scripts/probe_reuse.py "motion photo converter" "video to live photo" --per-query 8
python scripts/probe_reuse.py --json "motion photo converter"
python scripts/probe_reuse.py --repo owner/name
```

零第三方依赖，只向 `api.github.com` 发只读 GET（支持 `GITHUB_TOKEN`），输出 stars / SPDX 许可证 / 活跃度 / 许可证分级。按 stars 排序会埋没 0★ 新项目，需另查 skills.sh、awesome 清单等目录站。

## 许可

MIT，见 [LICENSE](LICENSE)。候选项目各有独立许可，决策卡会单独标注。
