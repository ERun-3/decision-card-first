# decision-card-first

> 让 Agent 在写第一行代码之前，先交一张纸。
> Make your agent hand you a one-page decision before it writes a single line of code.

**不承诺省首轮 token，承诺少返工一次。**

一个「造轮子前先调研」的 Skill：从零构建任务开始时，先检索现成软件与开源实现，核对许可证和维护状态，输出一张「直接用 / 抄思路 / 给上游贡献 / 长期分叉 / 自己写」的决策卡，**然后停下等确认**，不直接开干。

真实会话对照：

- [16:30 · 闸门失效](https://workbuddy.link/p/J0OxbXrJczkWowuJDfA7II?shareId=11f4f8c3-c84c-4bad-9fc9-06bab1f724f7&ext2=copy_link) — 边调研边装 PyInstaller，用户手动叫停
- [16:48 · v2 通过](https://workbuddy.link/p/vmZ2nmMvwFHJzSaG9IwP11?shareId=46981c69-12f2-4bba-a39f-54456ee0b9dd&ext2=copy_link) — 21 次只读调用、0 行代码，出完决策卡停下

## 它解决什么

给 Agent 一句「帮我做个 XX 工具」，它通常立刻开始装依赖、建目录、写代码。等方案选错了，依赖已经装好、代码已经铺开，返工成本全在你这边。

这个 Skill 把「调研」变成一个有交付物、有边界的阶段：

1. **分流** — 微小任务、改既有代码、明确说「不要调研」时跳过，不污染所有任务。
2. **检索** — GitHub REST API + 网页搜索 + PyPI/npm 等生态；先窄后宽，逐条剔除噪声。
3. **许可证红线** — `NO-LICENSE` / `NOASSERTION` 法律上默认保留所有权利，只能读思路不可抄代码；MIT/Apache/BSD、LGPL/MPL、GPL/AGPL 分级处理。
4. **决策卡** — 候选表（覆盖度 / 许可证 / 活跃度）、五选一结论、理由、可借鉴的坑、差异化空间、召回边界、红线与盲区。
5. **硬闸门** — 决策卡是本轮唯一交付物。输出后不写代码、不建目录、不装依赖、不做「顺手预检」；只有用户明确说「继续」才进入实现。

## 前后对照（同一句需求，同一个模型）

| | v1 · 16:30 | v2 · 16:48 |
| --- | --- | --- |
| 规则是否被读到 | ✅ 首句引用默认工作流 | ✅ 逐字复述规则并主动加载 Skill |
| 调研动作 | ✅ 查了 GitHub / PyPI / 许可证 | ✅ 两轮 6 个 query + 11 次来源核实 |
| 是否先交报告 | ❌ 并行装 PyInstaller | ✅ 决策卡完整输出后才结束 |
| 写操作 | ❌ 装依赖（用户中途停止） | ✅ 21 次工具调用**全部只读**，0 行代码 |
| 结束状态 | 被手动叫停 | 「回我『按 A 做』或『按 B 做』」 |

v2 那次还从源码里挖出几个会致命的坑：`md2img` 的 `fonts.go` 没有 Windows 字体路径，中文会退化成 7×13 位图字体；`arran4/md2png` 的 issue #96 证明批量转换是常见缺口；puppeteer/playwright 类方案与「离线单 exe 分发」根本冲突；中文字体必须用 OFL 许可才能随包分发。

## 跨平台实测（2026-11-09，3 个平台）

安装（L0）与行为（L1）按 `docs/TEST-PLAN.md` 的固定提示词在三个 Agent 平台上实测，逐项独立复核落盘（MD5 比对、全局规则文件 grep、产物文件），不采信 Agent 自述：

| 平台 | L0 安装+注册 | L1a 先出决策卡再停 | L1b 「不要调研」分流 | L1c 微任务分流 |
| --- | --- | --- | --- | --- |
| WorkBuddy (Hy4) | 6/6 | **Y/Y**（v1 边查边装依赖 → v2 修复后通过） | 未跑 | 未跑 |
| DSH | **6/6**（识别出 `~/.dsh/skills` 与 `~/.dsh/AGENTS.md`，未硬套路径） | 截断（规则可见，被手动中断） | **Y** | **Y** |
| ZCode (deepseek-flash) | **6/6** | 截断（规则可见，被手动中断） | 未跑 | 未跑 |

**安装时自举在 3 个平台全部通过**：每个安装者都正确找到本平台的用户级目录与全局规则文件并逐字写入触发规则。两个平台独立调研同一需求，收敛到同一个最优候选（`jmaciasluque/md2img`），并各自从 `fonts.go` 源码独立复现了「Windows 无字体路径、中文必退化为位图字体」这一结论。

## 这个赛道有 5 个玩家，缺的是什么

「先调研再动手」这个想法已经不新了——发布前我们用这个 Skill 查了自己，找到 5 个同类。检索还漏了 3 个（star 排序埋没 0★ 新项目 + 词族覆盖不全，复盘后已修进第 1/3 步），这条教训本身写进了技能里。把他们摆在一起看，缺口很清楚：

| | [github-build-or-reuse](https://github.com/ghspain/github-build-or-reuse) | [reuse-before-build](https://github.com/Ai-Eastern/reuse-before-build) | [search-before-building](https://github.com/yeaight7/agent-powerups) | 本项目 |
| --- | --- | --- | --- | --- |
| 决策输出 | USE / CONTRIBUTE / FORK / BUILD | Take / Borrow / Build | 四步检查 + 决策表 | 一页**决策卡**（候选表 / 硬门 / 五选一 / 召回边界 / 盲区） |
| 输出后停下等确认 | ❌ 给「最小可逆下一步」，继续走 | ❌ 仅在用户要求时实现 | ❌ 无停止机制 | ✅ **硬闸门**：不写代码、不建目录、不装依赖、不提 PR，等用户确认 |
| 安装时自举默认触发 | ❌ | ❌ | ❌ | ✅ 安装者把默认规则注册进本平台全局规则文件 |
| 跨平台行为实测 | 证据 demo（可 replay） | 17 runs 对照（自评小样本） | 目录站安全扫描 | ✅ 3 平台 L0/L1 实测，逐 case 锁包哈希 |
| 反提示注入 | ✅ 候选内容不可信 | — | — | ✅（v3.1 从同类借鉴） |
| 检索范围 | GitHub / 开源 | 优先查你的代码库 | 代码库 → 包注册表 → MCP | 外部现成软件与开源项目 + 生态目录站 |

前面几行是各家都做到位的——「先调研再动手」已经被充分验证，不需要第五个人再讲一遍。**没有人做的是中间两行：让 Agent 出了报告真的停下来，以及装了就默认生效。**本项目只讲这两件事。

## 已知弱点

- **闸门是文档级软约束**。v1 实测中模型曾边调研边装依赖；v2 修复后单样本通过，但要 100% 保证需配 UserPromptSubmit hook。
- **只查外部，不查你的代码库**。repo-first 类技能与本项目互补而非替代。
- **验证仍薄**。3 个平台的 L0 全部通过、L1a 通过 1 例、分流通过 2 例；L1 的完整矩阵与成本对照仍在按 `docs/TEST-PLAN.md` 扩充。每行记录都锁了包哈希，可复跑。
- **踩过的坑留痕**：测试材料与被测包同目录导致评分表泄漏（等于开卷考）；用户中途停止的截断样本不能当最终结果；v1 包被覆盖未归档，无法复跑旧版本。
- **多副本同步是真实风险**：本地优化后各平台安装副本会落后于源目录，跨副本同步曾险些丢失 GITHUB_TOKEN 支持（靠 MD5 比对发现）。v3 起以单一源目录 + 一键打包为准。

## 成本账（把账摊开，不编百分比）

调研这一轮的**实测**用量，取自会话 `usage`：

| 项 | 实测值 |
| --- | --- |
| outputTokens | 5,025 |
| inputTokens | 81,944（单次上下文快照，非会话累计） |
| 分类 | systemPrompt 9,734 / conversation 39,509 / tools 29,135 / mcp 328 / **skills 3,238（3.9%）** |

端到端的对照（调研轮为实测；其余为估算，非实测）：

| 路径 | 量级 |
| --- | --- |
| 调研这一轮 | ≈ 1.0M input（21 轮 × 平均 ~50k，估算） |
| 一次返工（发现→改→重打包→复验） | 0.3–1.0M input + 代码重写 |
| 不调研直接自研渲染引擎 | **实测 940 行**（DSH 在「不要调研」指令下从零写了 940 行纯 Pillow 渲染：CJK 断行、表格列宽、代码块硬断行）——正是决策卡警告的「自研排版深坑」的实测尺寸；调研后的薄层方案约 100–200 行 + 复用 MIT 库 |
| 调研后直接用现成成品 | 实现成本 ≈ 0 |

所以**不宣称省首轮 token**：调研本身是净增加成本。省的是两处——避免返工、以及当结论为「直接用/复用现成库」时省掉整个实现阶段。也正因为调研有成本，第 0 步分流不是装饰：对 10 行脚本硬做调研，账上是亏的。

## 安装

对已支持 Skill 机制的 Agent，把仓库根目录或 [`decision-card-first.zip`](https://github.com/ERun-3/decision-card-first/releases/download/v3.1.0/decision-card-first.zip) 解压到本平台的**用户级** skills 目录（WorkBuddy 为 `~/.workbuddy/skills/decision-card-first/`）。包内 `INSTALL.md` 写明了安装约定，包括把默认规则注册到用户级长期记忆／全局规则文件——**装了不等于默认生效**，这一步不能省。

装完开一个全新会话，发一句普通的从零构建需求即可。规则是软约束；要 100% 强制需配 UserPromptSubmit hook。

## 复现

```bash
python scripts/probe_reuse.py "motion photo converter" "video to live photo" --per-query 8
python scripts/probe_reuse.py --json "motion photo converter"
python scripts/probe_reuse.py --repo owner/name
```

脚本零第三方依赖，只向 `api.github.com` 发只读 GET（支持 `GITHUB_TOKEN` 提升限速），输出 stars / SPDX 许可证 / 最后提交 / 归档状态 / 陈旧标记 / 许可证分级，支持表格与 JSON；JSON 模式下 description 自动截断至 300 字符并清理转义换行。按 stars 排序会埋没 0★ 新项目，脚本会提示另查目录站或按更新时间补搜。

- `docs/TEST-PLAN.md` — 完整的跨 Agent 实测方案：L0 冒烟、L1 延迟验收、L2 的 2×2 归因、E 阴性对照、事先写死的判定阈值
- `docs/results.csv` — 逐 case 的实测记录（含包哈希，锁住输入版本）
- `references/license-and-sources.md` — 许可证判定表、生态检索入口、实测校准案例

这套实测方案本身也踩过坑并留了记录：评分表与被测包同目录导致「开卷考」、用户中途停止的截断样本不能当最终结果、改包前必须归档否则无法复跑旧版本。

## 目录

```
SKILL.md                          工作流、闸门、决策卡模板
INSTALL.md                        安装约定（跨平台）
scripts/probe_reuse.py            零依赖 GitHub 探测
references/license-and-sources.md 许可证与检索入口
docs/TEST-PLAN.md                 实测方案
docs/results.csv                  实测记录
prepare_release.py                一键同步 + 校验 + 打包
```

## 许可

MIT，见 [LICENSE](LICENSE)。字体、依赖与候选项目各有独立许可，决策卡会单独标注。

