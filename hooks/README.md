# 硬保证（可选）：UserPromptSubmit hook

SKILL.md 的闸门是文档级软约束。这是官方提供的 hook 脚本，把它配置进支持
hooks 的 Agent 宿主（如 Claude Code），每次你提交 prompt 时会自动检查：
从零构建类请求会被注入一行工作流提醒，从机制上兜底。

脚本零第三方依赖，只读取 stdin 的 JSON、只输出文字，不联网、不写文件。

## 配置（Claude Code 兼容宿主）

在宿主的 hooks 配置中加入：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python /path/to/decision-card-first/hooks/user_prompt_submit.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

把 `/path/to/decision-card-first/` 换成你实际的安装目录。

## 行为

- 命中「做一个 / 写一个 / 开发 / build me …」等从零构建特征 → 注入一行默认工作流提醒
- 用户说了「不要调研 / 直接写」→ 不提醒（分流规则优先）
- 微小任务（「改一下 / 10 行」）→ 不提醒
- hook 解析失败 → 静默放行，绝不阻塞你的 prompt

## 闸门分级（SKILL.md 第 6 步配套）

- 结论为「直接用」→ 用户简短确认即可
- 结论为「自己写 / 长期分叉」（≥ 几百行）→ 用户需明确选定方案
- 用户搁置卡片超过 24 小时后继续 → 先重跑 probe 确认候选未过期，再进实现
