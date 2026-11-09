# 安装说明（decision-card-first）

本包是**全局默认工作流 Skill**，不是按需调用的工具。装错位置或漏掉第 3 步，等于没装。

## 给安装本包的 Agent：按序执行

1. **确认本平台约定** — 先确定本 Agent 的「用户级 skills 目录」和「用户级长期记忆／全局规则文件」各在哪。WorkBuddy 本机分别是 `~/.workbuddy/skills/` 与 `~/.workbuddy/*-personal/MEMORY.md`；其他 Agent 用各自的对应位置。无法确定时**询问用户**，不要硬套 WorkBuddy 路径，也不要因为路径不匹配就判定本包不适用。
2. **安装位置** — 装到上一步确认的**用户级**目录（WorkBuddy 为 `~/.workbuddy/skills/decision-card-first/`），不要放项目级目录（如 `{workspace}/.workbuddy/skills/`）：用户级对所有会话生效，项目级只对单个项目生效。
3. **安全审查** — 逐文件读完 `SKILL.md`、`scripts/probe_reuse.py`、`references/license-and-sources.md`。确认脚本只向 `api.github.com` 发只读 GET，不写用户文件、不执行外部命令、不上传数据。
4. **注册默认规则（关键）** — 把下面这行写进本平台的用户级长期记忆／全局规则文件，并告知用户写入的位置：

   > 开始任何从零构建类任务前（预计新建 ≥100 行代码、或需要架构选型、或引入新依赖），先加载 decision-card-first 做一次现成方案调研，输出造轮子决策卡后**停下等待用户确认**，得到明确同意再动手实现；用户明确说「直接写 / 不要调研」时跳过。

   无法写入时，必须如实说明「已安装，但默认触发未注册」，不要默认它已生效。

5. **验证** — `python scripts/probe_reuse.py --repo owner/name`，能输出表格或 JSON 即正常。

## 为什么第 3 步不能省

`SKILL.md` 正文只在技能被触发后才加载。只在包里声明「我是默认行为」，下次开工时正文未必在上下文里，规则会断。只有写进常驻位置（长期记忆／全局规则／hook）才真正默认。

两条常驻通道：

- `SKILL.md` 的 frontmatter `description` 会被平台常驻注入上下文 → 软全局规则（本包已写入兜底提示）。
- 用户级长期记忆 / 全局规则 / UserPromptSubmit hook → 更强，hook 是唯一硬强制。

因此安装约定必须是**动作指令（写文件）**，不能只是声明。

## 边界

- **跨平台**：上文出现的 `~/.workbuddy/...` 是 WorkBuddy 本机示例，不是硬性路径。其他 Agent 一律先确认本平台的用户级目录与全局规则文件，再按同一套动作执行；路径不同不影响第 4 步的必要性。
- 「用户给链接／zip，Agent 手动下载并逐文件审查」这条链路最可靠；走市场安装器按名称直接安装时，包内文档可能不被逐字读取，此时靠 `description` 兜底并主动补一次注册。
- 即便注册成功仍是软约束；要 100% 保证，需配置 hook。
- 阈值「≥100 行或引入新依赖才调研」是默认假设，按使用者偏好调整。

## 包内文件

| 文件 | 作用 |
| --- | --- |
| `SKILL.md` | 工作流、分流、许可证红线、决策卡模板、反模式 |
| `scripts/probe_reuse.py` | 零依赖 GitHub 探测，输出候选元数据与许可证分级（表格 / JSON） |
| `references/license-and-sources.md` | 许可证判定表、生态检索入口、实测校准案例 |
