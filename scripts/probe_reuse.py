#!/usr/bin/env python3
"""Probe GitHub for existing implementations before building from scratch.

Zero third-party dependencies. Uses the anonymous GitHub REST API.
Anonymous search is rate limited to ~10 requests/minute; keep query count small.

Usage:
  python probe_reuse.py "video to live photo" "live photo converter mp4"
  python probe_reuse.py --json "motion photo converter"
  python probe_reuse.py --repo owner/name
  python probe_reuse.py --min-stars 20 "live photo converter"
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime

API = "https://api.github.com"
UA = "decision-card-first-probe/1.0"
TIMEOUT = 15

# None / NOASSERTION means "all rights reserved" by default: read, do not copy.
ALLOW = {
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD",
    "Unlicense", "CC0-1.0", "Zlib", "BSL-1.0",
}
WEAK_COPYLEFT = {"MPL-2.0", "LGPL-2.1", "LGPL-3.0", "EPL-2.0", "EPL-1.0"}
STRONG_COPYLEFT = {
    "GPL-2.0", "GPL-3.0", "AGPL-3.0", "AGPL-1.0", "SSPL-1.0",
    "CC-BY-SA-4.0", "EUPL-1.2",
}

VERDICT = {
    "allow": "可直接复用代码（保留版权声明）",
    "weak": "需确认授权边界（弱 copyleft）",
    "strong": "有传染风险，除非项目可接受同协议开源",
    "blocked": "无明确授权，仅可参考思路，不可抄代码",
    "unknown": "未识别协议，需人工查看 LICENSE 文件",
}


def classify_license(spdx):
    if not spdx or spdx in ("NOASSERTION", "NONE"):
        return "blocked"
    if spdx in ALLOW:
        return "allow"
    if spdx in WEAK_COPYLEFT:
        return "weak"
    if spdx in STRONG_COPYLEFT:
        return "strong"
    return "unknown"


def api_get(path):
    url = path if path.startswith("http") else API + path
    headers = {
        "User-Agent": UA,
        "Accept": "application/vnd.github+json",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        # Raises the limit from ~10 search req/min (anonymous) to 30/min.
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.load(resp), None
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            return None, "GitHub API 速率受限（匿名搜索约 10 次/分钟），稍后重试或设置 GITHUB_TOKEN"
        return None, "HTTP %s: %s" % (e.code, e.reason)
    except Exception as e:  # noqa: BLE001 - surface any network failure, never silently skip
        return None, "网络失败: %s" % e


DESC_LIMIT = 300


def clean_description(text):
    """Flatten escaped whitespace and cap length so JSON stays agent-friendly."""
    text = text or ""
    for old, new in (("\\r\\n", " "), ("\\n", " "), ("\\r", " "), ("\\t", " "),
                     ("\r\n", " "), ("\r", " "), ("\n", " "), ("\t", " ")):
        text = text.replace(old, new)
    text = " ".join(text.split())
    if len(text) > DESC_LIMIT:
        text = text[:DESC_LIMIT - 1].rstrip() + "…"
    return text


def days_since(iso):
    try:
        return (date.today() - datetime.strptime(iso[:10], "%Y-%m-%d").date()).days
    except Exception:
        return None


def normalize(item):
    lic = (item.get("license") or {}).get("spdx_id")
    tier = classify_license(lic)
    pushed = item.get("pushed_at") or ""
    age = days_since(pushed)
    return {
        "full_name": item.get("full_name"),
        "url": item.get("html_url"),
        "stars": item.get("stargazers_count", 0),
        "forks": item.get("forks_count", 0),
        "language": item.get("language") or "-",
        "license": lic or "NO-LICENSE",
        "tier": tier,
        "verdict": VERDICT[tier],
        "pushed_at": pushed[:10] or "-",
        "days_since_push": age,
        "stale": (age is not None and age > 730),
        "archived": bool(item.get("archived")),
        "open_issues": item.get("open_issues_count", 0),
        "description": clean_description(item.get("description")),
        "matched_queries": [],
    }


def search(queries, per_query, min_stars):
    totals = {}
    found = {}
    errors = []
    for i, q in enumerate(queries):
        if i:
            time.sleep(6.5)  # stay under the anonymous 10 req/min search limit
        path = ("/search/repositories?q=" + urllib.parse.quote(q)
                + "&sort=stars&order=desc&per_page=" + str(min(per_query, 100)))
        data, err = api_get(path)
        if err:
            errors.append({"query": q, "error": err})
            continue
        totals[q] = data.get("total_count", 0)
        for item in data.get("items", []):
            rec = normalize(item)
            if rec["stars"] < min_stars:
                continue
            key = rec["full_name"]
            if key not in found:
                rec["matched_queries"] = [q]
                found[key] = rec
            elif q not in found[key]["matched_queries"]:
                found[key]["matched_queries"].append(q)
    rows = sorted(found.values(), key=lambda r: -r["stars"])
    return {"totals": totals, "candidates": rows, "errors": errors}


def single_repo(full_name):
    data, err = api_get("/repos/" + full_name.strip("/"))
    if err:
        return {"candidates": [], "errors": [{"query": full_name, "error": err}], "totals": {}}
    return {"totals": {}, "candidates": [normalize(data)], "errors": []}


def render(result, min_stars):
    lines = []
    if result["totals"]:
        lines.append("检索命中总数：")
        for q, n in result["totals"].items():
            lines.append("  %-40s %s" % (q, n))
        lines.append("")
    lines.append("候选（stars >= %d，按 stars 降序，共 %d 个去重仓库）：" % (min_stars, len(result["candidates"])))
    lines.append("")
    header = "%-7s %-44s %-14s %-8s %-12s %-10s %s"
    lines.append(header % ("STARS", "REPO", "LICENSE", "TIER", "LAST PUSH", "STALE", "DESCRIPTION"))
    lines.append("-" * 150)
    for r in result["candidates"]:
        flags = []
        if r["stale"]:
            flags.append("STALE")
        if r["archived"]:
            flags.append("ARCHIVED")
        lines.append(header % (
            r["stars"], (r["full_name"] or "")[:44], r["license"][:14], r["tier"],
            r["pushed_at"], ("/".join(flags) or "-"), r["description"][:70],
        ))
    lines.append("")
    lines.append("许可证判定：")
    for r in result["candidates"]:
        lines.append("  %-44s %s" % (r["full_name"], r["verdict"]))
    if result["errors"]:
        lines.append("")
        lines.append("错误（该查询未纳入结果，勿当作「无同类项目」）：")
        for e in result["errors"]:
            lines.append("  [%s] %s" % (e["query"], e["error"]))
    lines.append("")
    lines.append("注意：按 stars 排序会混入无关高星仓库。必须逐条核对 description 与 README 后再下结论。")
    return "\n".join(lines)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    p = argparse.ArgumentParser(description="Probe GitHub for reusable implementations.")
    p.add_argument("queries", nargs="*", help="one or more search query strings")
    p.add_argument("--repo", action="append", default=[], help="exact owner/name to inspect")
    p.add_argument("--per-query", type=int, default=8, help="results per query (default 8)")
    p.add_argument("--min-stars", type=int, default=0, help="drop repos below this star count")
    p.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = p.parse_args()

    if not args.queries and not args.repo:
        p.error("provide at least one query string or --repo owner/name")

    result = {"totals": {}, "candidates": [], "errors": []}
    if args.queries:
        part = search(args.queries, args.per_query, args.min_stars)
        result["totals"].update(part["totals"])
        result["errors"].extend(part["errors"])
        by_name = {r["full_name"]: r for r in part["candidates"]}
    else:
        by_name = {}
    for full in args.repo:
        part = single_repo(full)
        result["errors"].extend(part["errors"])
        for r in part["candidates"]:
            by_name[r["full_name"]] = r
    result["candidates"] = sorted(by_name.values(), key=lambda r: -r["stars"])

    result["caveats"] = [
        "GitHub API 结果按 stars 排序，不等于需求契合度；无关高星仓库需人工剔除。",
        "NO-LICENSE / NOASSERTION 在法律上默认保留所有权利，只能阅读思路，不可复制代码。",
        "星数与维护状态只说明活跃度，不说明可用性；须打开 README、issue 与最近提交核实功能边界。",
        "本脚本只覆盖 GitHub；npm / PyPI / 浏览器插件商店 / 商业 SaaS 需另行检索。",
    ]

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result, args.min_stars))
        print("")
        for c in result["caveats"]:
            print("- " + c)
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
