#!/usr/bin/env python3
"""Sync the installed skill into a clean, pushable repo and build the release zip.

Idempotent: run it again after tonight's test/tuning pass and everything is
regenerated from the single source of truth (the installed skill directory).

Hand-written files (README.md, LICENSE, .gitignore) are never touched.

Usage:
    python prepare_release.py
"""

import csv
import hashlib
import sys
import zipfile
from pathlib import Path

RELEASE = Path(__file__).resolve().parent
WORKSPACE = RELEASE.parent
SKILL_SRC = Path(r"C:\Users\41Run\.workbuddy\skills\decision-card-first")
DOCS_SRC = WORKSPACE / "dist"

SKILL_FILES = [
    "SKILL.md",
    "INSTALL.md",
    "scripts/probe_reuse.py",
    "references/license-and-sources.md",
]
DOC_FILES = [
    ("TEST-PLAN.md", "docs/TEST-PLAN.md"),
    ("results.csv", "docs/results.csv"),
]
HAND_WRITTEN = ["README.md", "LICENSE", ".gitignore"]


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def sync():
    print("=== 1. 从已安装目录同步 ===")
    for rel in SKILL_FILES:
        src = SKILL_SRC / rel
        if not src.exists():
            fail("缺少源文件: %s" % src)
        dst = RELEASE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        print("  %-45s %6d bytes" % (rel, src.stat().st_size))

    print("=== 2. 同步实测文档 ===")
    for src_name, rel in DOC_FILES:
        src = DOCS_SRC / src_name
        if not src.exists():
            fail("缺少实测文档: %s" % src)
        dst = RELEASE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        print("  %-45s %6d bytes" % (rel, src.stat().st_size))

    for name in HAND_WRITTEN:
        if not (RELEASE / name).exists():
            fail("手写文件缺失: %s" % name)
    print("  手写文件保留: " + ", ".join(HAND_WRITTEN))


def validate():
    print("=== 3. 校验 ===")
    skill = (RELEASE / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---"):
        fail("SKILL.md 缺少 YAML frontmatter")
    fm = skill.split("---", 2)[1]
    if "name:" not in fm or "description:" not in fm:
        fail("frontmatter 缺 name / description")
    if "停下等待用户确认" not in skill:
        fail("硬闸门措辞丢失——检查第 6 步是否被误删")
    print("  frontmatter OK / 硬闸门 OK")

    script = RELEASE / "scripts/probe_reuse.py"
    try:
        compile(script.read_text(encoding="utf-8"), str(script), "exec")
        print("  probe_reuse.py 语法 OK (compile, 不生成 pyc)")
    except SyntaxError as e:
        fail("脚本语法错误: %s" % e)

    with open(RELEASE / "docs/results.csv", encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.reader(f) if r]
    if not rows or any(len(r) != len(rows[0]) for r in rows):
        fail("results.csv 列数不一致")
    print("  results.csv OK (%d 列 / %d 行实测)" % (len(rows[0]), len(rows) - 1))

    junk = [str(p.relative_to(RELEASE)) for p in RELEASE.rglob("__pycache__")]
    if junk:
        fail("目录里有缓存目录: %s" % junk)
    print("  无 __pycache__ 残留")


def build_zip():
    print("=== 4. 生成发布 zip ===")
    out = RELEASE / "decision-card-first.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in SKILL_FILES:
            z.writestr("decision-card-first/" + rel, (RELEASE / rel).read_bytes())
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print("  %s" % out.name)
    print("  files=%d  sha256=%s" % (len(SKILL_FILES), digest))
    return digest


def preflight():
    readme = (RELEASE / "README.md").read_text(encoding="utf-8")
    print("=== 5. 发布前检查 ===")
    if "<!--" in readme:
        print("  [ ] README 底部仍有发布前待更新清单（HTML 注释），逐条确认后删掉")
    if "[`decision-card-first.zip`]" in readme:
        print("  [ ] README 里的 zip 链接仍是占位符，换成 Release 资产链接")
    print("  [ ] 确认 LICENSE 署名")
    print("  [ ] 今晚新增的实测数据已同步进 docs/results.csv 且列数一致")
    print("  [ ] git init / add / commit / push（本脚本不碰 git）")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if not SKILL_SRC.exists():
        fail("已安装 Skill 目录不存在: %s" % SKILL_SRC)
    sync()
    validate()
    build_zip()
    preflight()
    print("\n完成。今晚改完直接重跑本脚本即可，无需手工整理文件。")


if __name__ == "__main__":
    main()
