#!/usr/bin/env python3
"""UserPromptSubmit hook for decision-card-first.

Reads the hook payload (JSON) from stdin and, when the user's prompt looks
like a from-scratch build request, prints a one-line reminder so the
decision-card-first workflow is enforced even if the model would otherwise
skip it. Zero third-party dependencies.

Install (Claude Code compatible hosts): see hooks/README.md
"""

import json
import sys

# Words that suggest "build something new from scratch"
BUILD_MARKERS = [
    "做一个", "写一个", "做个", "写个", "开发", "实现一个", "帮我实现",
    "搭建", "做个工具", "做个系统", "new tool", "build me", "implement a",
    "create a", "develop a",
]
# Words that mean the user already opted out
SKIP_MARKERS = ["不要调研", "直接写", "直接做", "别调研", "跳过调研",
                "no research", "skip research", "directly write"]
# Tiny tasks where research would be noise
TINY_MARKERS = ["改一下", "修一下", "改个", "加个", "few lines", "10 行", "十行"]


def should_remind(prompt: str) -> str | None:
    low = prompt.lower()
    if any(m in prompt for m in SKIP_MARKERS):
        return None
    if any(m in low for m in [m.lower() for m in SKIP_MARKERS]):
        return None
    if any(m in prompt for m in TINY_MARKERS):
        return None
    if any(m in prompt for m in BUILD_MARKERS):
        return "build"
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # malformed hook payload: never block the user
    prompt = str(payload.get("prompt", ""))
    if should_remind(prompt):
        print(
            "[decision-card-first] 这是一条从零构建类请求。按本项目的默认工作流，"
            "先加载 decision-card-first 技能做一次现成方案调研，输出造轮子决策卡后"
            "停下等待用户确认，再动手实现。用户明确说「不要调研」或任务是微小修改时跳过。"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
