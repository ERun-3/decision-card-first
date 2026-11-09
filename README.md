# decision-card-first

> 防止 AI 重复造轮子：动手之前，先查一遍世界上有没有现成的。

给 Agent 一句「帮我做个 XX 工具」，它通常立刻开始写代码——哪怕轮子早就有人造好了。这个 Skill 让 Agent 先调研现成软件与开源实现、核对许可证和维护状态，输出一张决策卡（候选表 / 硬门 / 五选一 / 盲区），**然后停下等你确认**——不写代码、不装依赖、不提 PR。

结论五选一：**直接用 / 抄思路 / 给上游贡献 / 长期分叉 / 自己写**。微小任务和「不要调研」走分流，不会每个任务都硬查一轮。

同类里有 5 个（[github-build-or-reuse](https://github.com/ghspain/github-build-or-reuse)、[reuse-before-build](https://github.com/Ai-Eastern/reuse-before-build) 等），都没做这两件事：**出报告后真的停下来等确认**、**安装时把默认触发注册进全局规则**。这是本项目的全部差异。

## 实测

在 WorkBuddy / DSH / ZCode 三个平台实测：安装自举 3/3 通过（MD5 复核落盘，不采信自述）；两个平台独立调研收敛到同一候选；「不要调研」对照组实测写出 940 行自研渲染，调研后的薄层方案约 150 行。完整方案见 [`docs/TEST-PLAN.md`](docs/TEST-PLAN.md)，逐 case 记录见 [`docs/results.csv`](docs/results.csv)。

闸门是文档级软约束；要 100% 保证需配 UserPromptSubmit hook。

## 安装

把 [`decision-card-first.zip`](https://github.com/ERun-3/decision-card-first/releases/download/v3.1.0/decision-card-first.zip) 解压到本平台的**用户级** skills 目录，包内 `INSTALL.md` 是给安装 Agent 的约定——**装了不等于默认生效**，注册那一步不能省。

## 探测脚本

```bash
python scripts/probe_reuse.py "motion photo converter" --per-query 8
python scripts/probe_reuse.py --repo owner/name
```

零依赖，只读 GitHub API（支持 `GITHUB_TOKEN`），输出 stars / 许可证分级 / 活跃度。

## 许可

MIT，见 [LICENSE](LICENSE)。
