# 许可证判定表与检索入口

## 1. 许可证硬规则

| SPDX | 能否复制代码 | 必须履行的义务 / 主要风险 |
| --- | --- | --- |
| 缺失、`NOASSERTION`、自定义协议 | **否** | 默认「保留所有权利」。只能阅读实现思路后独立重写。GitHub 上大量个人项目属于此类。 |
| `MIT` | 是 | 保留版权声明与许可全文；最宽松。 |
| `Apache-2.0` | 是 | 保留声明、标注被修改的文件、附带 NOTICE；含专利授权与终止条款。 |
| `BSD-2-Clause` / `BSD-3-Clause` / `ISC` / `0BSD` | 是 | 保留声明；BSD-3 额外禁止用原作者名义背书。 |
| `Unlicense` / `CC0-1.0` | 是 | 公有领域奉献；部分司法辖区效力有争议。 |
| `MPL-2.0` | 有条件 | 文件级 copyleft：修改过的 MPL 文件须继续以 MPL 开源。与自有代码分文件隔离可控制风险。 |
| `LGPL-2.1` / `LGPL-3.0` / `EPL-2.0` | 有条件 | 库级／链接级 copyleft：动态链接通常可行，静态链接或修改库本身会触发开源义务。 |
| `GPL-2.0` / `GPL-3.0` | 谨慎 | 整个衍生作品须以同协议开源。作为独立进程通过命令行调用，通常不构成衍生，但边界需个案判断。 |
| `AGPL-3.0` / `SSPL-1.0` | 否（多数闭源场景） | AGPL 对通过网络提供服务同样触发开源义务；SSPL 更严，常被视为非 OSI 开源。 |
| `CC-BY-NC-*` / `CC-BY-SA-*` | 视用途 | NC 禁止商用；SA 要求相同方式共享。代码项目一般不采用 CC 系列，遇到需单独确认。 |

补充检查项：

- 主仓库的许可证不等于其依赖的许可证；`requirements.txt` / `package.json` / `Cargo.toml` 要一并看。
- 无 LICENSE 文件但 README 写了「随便用」，仍不足以构成明确授权。
- Fork 项目须回溯上游仓库的许可证。
- 星数、活跃度、作者身份都不改变许可证约束。

## 2. 抄代码前的工程检查清单

1. 功能覆盖度：全部 / 部分 / 仅思路。只覆盖部分需求时，评估「补完」与「重写」哪个更省。
2. 维护状态：最后提交时间、issue 是否有人回、是否 archived、依赖是否已失效。
3. 架构契合：语言、运行时、构建方式、是否强制引入重型框架。
4. 质量信号：有无测试、CI、文档、release；只有一次提交且无星的多为 demo 或 AI 一次性产物。
5. 可摘取粒度：能否只复制一个文件／一个函数，还是会牵出整棵依赖树。
6. 后续成本：抄进来的代码由谁维护、上游更新如何同步。
7. 差异化：候选没做而需求要的部分，是否正是项目价值所在。

## 3. 检索入口（脚本只覆盖 GitHub 仓库元数据）

| 目标 | 入口 |
| --- | --- |
| 通用开源代码 | GitHub REST `/search/repositories`、GitHub Topics、Sourcegraph |
| Python 包 | PyPI 搜索、libs.renzo.dev / awesome 列表 |
| Node 包 | npm search、npms.io |
| Java / Kotlin | Maven Central、mvnrepository |
| Rust / Go | crates.io、pkg.go.dev |
| 浏览器扩展 | Chrome Web Store、Edge Add-ons、Greasy Fork |
| 桌面 / 移动成品 | 应用商店、AlternativeTo、Product Hunt |
| 商业 SaaS | 网页搜索、垂直行业榜单 |
| 中文实现 | 网页搜索、公众号、掘金 / 知乎 / V2EX、Gitee |

## 4. 校准案例（2026-11-09 实测，需求：视频转 Live Photo）

用途：说明「搜得到」与「能直接用／能抄」之间的差距，避免把召回结果直接当结论。

中文网页搜索一次命中 3 个高度重合项目，其真实元数据：

| 仓库 | 星 | 语言 | 许可证 | 最后提交 | 判定 |
| --- | --- | --- | --- | --- | --- |
| `W4J1e/Video2LivePhoto` | 34 | JavaScript | 无 | 2026-06-07 | 纯前端方案，无授权 → 仅参考思路 |
| `969246694/video2livephoto` | 0 | Python | MIT | 2026-09-10 | Windows 桌面、无损元数据写入，创建当天即推送，0 星 → 可读代码但质量未验证 |
| `Flywith24/LivePhotoMaker` | 8 | Swift | 无 | 2026-09-09 | macOS 专用 → 仅参考思路 |

GitHub API 英文检索：

- `video to live photo` → total 306。Top 5 中 `bookworm52/EthicalHackingFromScratch`（120★）完全无关；`wszqkzqk/live-photo-conv`（236★，LGPL-2.1，2026-10 活跃）才是最强候选；`TouSC/Video2LivePhoto`（134★，无许可证，2024-06 停更）。
- `live photo converter mp4` → total 9，多数为 0–18★ 小项目。
- `motion photo converter` → total 13，但 `ZhiQiu-Kinsey/AppleLivePhotoConvert`（95★，MIT，2026-11-02）质量最高。

结论要点：

1. 匿名 GitHub API 可直接用（HTTP 200），一次检索几秒完成，「先调研」在技术上没有门槛。
2. 按 stars 排序必然混入噪声，必须逐条核对 description。
3. 3 个中文项目里 2 个无许可证 → 「直接抄代码」在多数情况下**不成立**；这是法律默认值，不是保守偏好。
4. 最贴合的候选反而是 0 星 MIT 项目与 236★ LGPL 项目，二者都不适合无脑复制：前者质量未验证，后者有 copyleft 边界。
5. 该需求若自用 PySide6 + 精简 ffmpeg + 硬件编解码探测链，工程深度明显高于上述候选 → 调研的正确产出是「知道边界与坑」，而不是「别做了」。
