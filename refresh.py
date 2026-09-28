#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
starforge 数据刷新器  ·  作者: 晨星 (CJX0712)

一键完成：GitHub 实拉 → 去重清洗 → 注入模板 → 生成 index.html → 跑自检

前置：本机安装并登录 GitHub CLI（https://cli.github.com/）
      gh auth login

用法：
    python refresh.py              # 全量刷新 + 构建 + 自检
    python refresh.py --skip-fetch # 跳过拉取，用现有 stars_tmp 重建
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import collections
import datetime
import pathlib
import shutil

ROOT = pathlib.Path(__file__).parent.resolve()
TMP = ROOT / "stars_tmp"

# 赛道 -> GitHub 搜索语句（topic + star 阈值）
QUERIES = [
    ("foundation",   "topic:machine-learning stars:>60000"),
    ("deeplearning", "topic:deep-learning stars:>40000"),
    ("llm",          "topic:llm stars:>25000"),
    ("agent",        "topic:agents stars:>15000"),
    ("rag",          "topic:rag stars:>8000"),
    ("inference",    "topic:inference stars:>10000"),
    ("vision",       "topic:computer-vision stars:>30000"),
    ("data",         "topic:data-engineering stars:>15000"),
    ("infra",        "topic:developer-tools stars:>40000"),
    ("frontend",     "topic:react stars:>50000"),
]

CATMAP = {
    "foundation": "机器学习基础", "deeplearning": "深度学习框架", "llm": "大模型 / LLM",
    "agent": "AI Agent", "rag": "检索增强 RAG", "inference": "推理与部署",
    "vision": "计算机视觉", "data": "数据工程", "infra": "开发者工具", "frontend": "前端生态",
}


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", **kw)


# ---------------------------------------------------------------- 1. 拉取
def fetch(limit=30):
    TMP.mkdir(exist_ok=True)
    ok = True
    for cat, query in QUERIES:
        out = TMP / f"{cat}.json"
        print(f"  ▸ 拉取 {CATMAP[cat]:<12} {query}")
        r = run(["gh", "search", "repos", query, "--limit", str(limit), "--json",
                 "fullName,stargazersCount,forksCount,language,description,updatedAt,url,license"])
        if r.returncode != 0 or not r.stdout.strip():
            print(f"    ✗ 失败：{r.stderr.strip()[:120]}")
            ok = False
            continue
        try:
            rows = json.loads(r.stdout)
        except json.JSONDecodeError as e:
            print(f"    ✗ 返回非 JSON：{e}")
            ok = False
            continue
        out.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
        print(f"    ✓ {len(rows)} 条")
    return ok


# ---------------------------------------------------------------- 2. 合并清洗
def build_seed():
    rows = {}
    for cat, _ in QUERIES:
        p = TMP / f"{cat}.json"
        if not p.exists():
            continue
        for raw in json.loads(p.read_text(encoding="utf-8")):
            fn = raw.get("fullName")
            if not fn or "/" not in fn:
                continue
            owner, repo = fn.split("/", 1)
            lic = (raw.get("license") or {}).get("spdx_id") or "NOASSERTION"
            rec = dict(
                name=fn, owner=owner, repo=repo,
                stars=raw.get("stargazersCount", 0),
                forks=raw.get("forksCount", 0),
                lang=raw.get("language") or "Unknown",
                desc=(raw.get("description") or "").replace("\n", " ").strip(),
                url=raw.get("url") or f"https://github.com/{fn}",
                updated=(raw.get("updatedAt") or "")[:10],
                license="自定义" if lic == "NOASSERTION" else lic,
                cat=CATMAP[cat], cats=[CATMAP[cat]],
            )
            cur = rows.get(fn)
            if cur:                                   # 跨赛道去重，合并标签
                if CATMAP[cat] not in cur["cats"]:
                    cur["cats"].append(CATMAP[cat])
                cur["stars"] = max(cur["stars"], rec["stars"])
            else:
                rows[fn] = rec

    data = sorted(rows.values(), key=lambda x: -x["stars"])
    cats = [CATMAP[c] for c, _ in QUERIES]
    seed = dict(
        meta=dict(
            generated_at=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
            total=len(data),
            total_stars=sum(d["stars"] for d in data),
            cats=cats,
            cat_count={k: sum(1 for d in data if k in d["cats"]) for k in cats},
            lang_count=dict(collections.Counter(d["lang"] for d in data).most_common(12)),
        ),
        repos=data,
    )
    (ROOT / "stars_seed.json").write_text(
        json.dumps(seed, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"  ✓ 去重后 {seed['meta']['total']} 个仓库 / {seed['meta']['total_stars']:,} ★")
    return seed


# ---------------------------------------------------------------- 3. 注入
def inject(seed):
    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    if "__SEED_DATA__" not in tpl:
        sys.exit("✗ template.html 缺少 __SEED_DATA__ 占位符")
    raw = json.dumps(seed, ensure_ascii=False, separators=(",", ":")).replace("</", r"<\/")
    out = (ROOT / "index.html")
    out.write_text(tpl.replace("__SEED_DATA__", raw), encoding="utf-8")
    print(f"  ✓ index.html {out.stat().st_size / 1024:.1f} KB")
    return out


# ---------------------------------------------------------------- 4. 自检
def verify(html_path):
    html = html_path.read_text(encoding="utf-8")
    results = []

    m = re.search(r'<script type="application/json" id="seed">(.*?)</script>', html, re.S)
    if not m:
        return [("✗", "未找到 seed 数据块", "")]
    try:
        seed = json.loads(m.group(1).replace(r"<\/", "</"))
        results.append(("✓", "Seed JSON 可解析", f"{seed['meta']['total']} 仓库"))
    except json.JSONDecodeError as e:
        return [("✗", "Seed JSON 非法", str(e)[:60])]

    bodies = re.findall(r"<script>(.*?)</script>", html, re.S)
    tmp = pathlib.Path(tempfile.gettempdir()) / "_starforge_syntax.js"
    tmp.write_text(bodies[-1], encoding="utf-8")
    node = shutil.which("node") or shutil.which("node.exe")
    if not node:
        results.append(("~", "JS 语法检查", "未找到 node，跳过"))
    else:
        r = run([node, "--check", str(tmp)])
        results.append(("✓" if r.returncode == 0 else "✗", "JS 语法",
                        r.stderr.strip()[:80] if r.returncode else "通过"))

    rep = seed["repos"]
    need = ("name", "stars", "forks", "lang", "desc", "url", "updated", "license", "cat", "cats")
    bad = [x["name"] for x in rep if not all(k in x for k in need)]
    results.append(("✓" if not bad else "✗", "字段完整性", "全部齐备" if not bad else str(bad[:3])))

    dupe = len(rep) - len({x["name"] for x in rep})
    results.append(("✓" if dupe == 0 else "✗", "去重", f"重复 {dupe} 条"))

    ext = re.search(r'(?:src|href)\s*=\s*"https?://(?!api\.github\.com)', html)
    results.append(("✓" if not ext else "✗", "零外部依赖", "无第三方资源引用" if not ext else "发现外链"))

    return results


def main():
    skip = "--skip-fetch" in sys.argv
    print("\nstarforge · 数据刷新器  (作者 晨星)\n" + "─" * 46)

    print("[1/4] GitHub 实拉")
    if skip:
        print("  ~ 已跳过（--skip-fetch）")
    else:
        if run(["gh", "auth", "status"]).returncode != 0:
            sys.exit("  ✗ gh 未登录，请先执行：gh auth login")
        fetch()

    print("[2/4] 合并清洗")
    seed = build_seed()

    print("[3/4] 注入构建")
    html_path = inject(seed)

    print("[4/4] 自检")
    for s, k, v in verify(html_path):
        print(f"  {s} {k:<14} {v}")

    print("─" * 46)
    top = seed["repos"][:5]
    print("  TOP5: " + " | ".join(f"{x['name']} {x['stars']:,}" for x in top))
    print(f"  完成 → {html_path}\n")


if __name__ == "__main__":
    main()
