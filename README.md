# starforge ★ · GitHub Star 榜单浏览器

> 单文件 HTML · 零外部依赖 · 离线可用 · 作者 **晨星（CJX0712）**

一个装了 **235 个真实高星开源仓库**（合计 **13,893,502 ★**）的本地榜单浏览器。数据是从 GitHub Search API 实拉的快照，内嵌进 HTML，打开即用，不联网也能跑。

不是刷星工具。它做的是：**把散落在 GitHub 各处的顶级项目，按赛道整理成一份可筛选、可收藏、可导出的本地清单。**

---

## 功能

| 能力 | 说明 |
|---|---|
| 十大赛道筛选 | 机器学习基础 / 深度学习框架 / 大模型 LLM / AI Agent / RAG / 推理部署 / 计算机视觉 / 数据工程 / 开发者工具 / 前端生态 |
| 多维过滤 | 关键词模糊搜索（仓库名、组织、描述）+ 语言下拉 + 赛道 chips |
| 四种排序 | Star · Fork · 更新时间 · 名称 |
| 双视图 | 卡片视图（带简介、语言色点、License、更新时间）/ 紧凑表格视图 |
| 收藏清单 | ☆ 一键收藏，localStorage 持久化，刷新不丢 |
| 导出 | 收藏清单导出 **Markdown**（按赛道分组表格）或 **JSON**，自动复制到剪贴板 |
| 实时拉取 | 填 GitHub Token 拉自己的 Starred，或输入任意用户名读公开 starred 列表 |
| 赛道分布图 | 侧边横向条形图，10 个赛道的收录分布一眼看清 |

---

## 数据来源与时效

- 来源：GitHub REST / Search API，通过 `gh search repos` 按 topic + star 阈值实拉
- 规模：10 个赛道各取 Top 30 → 去重后 **235 个**独立仓库
- 快照日期：**2026-09-29**
- 字段：`fullName` / `stargazersCount` / `forksCount` / `language` / `description` / `updatedAt` / `license`
- ⚠️ 榜单是**静态快照**。要最新数据请用页面右上角的「实时拉取」，或直接重跑 [`refresh.py`](refresh.py)

---

## 快速开始

```bash
# 直接双击打开
index.html

# 或起个本地服务
python -m http.server 8080
```

**刷新数据**（需要安装并登录 [GitHub CLI](https://cli.github.com/)）：

```bash
python refresh.py     # 重新拉取 + 重建 index.html + 跑自检
```

---

## 榜单 TOP 10（快照）

| # | 仓库 | Stars | 赛道 |
|---|---|---|---|
| 1 | freeCodeCamp/freeCodeCamp | 456,456 | 数据工程 |
| 2 | affaan-m/ECC | 268,781 | AI Agent |
| 3 | react/react | 250,806 | 前端生态 |
| 4 | NousResearch/hermes-agent | 249,722 | AI Agent |
| 5 | tensorflow/tensorflow | 200,589 | 机器学习基础 |
| 6 | Significant-Gravitas/AutoGPT | 187,598 | AI Agent |
| 7 | firecrawl/firecrawl | 185,860 | 检索增强 RAG |
| 8 | ollama/ollama | 181,858 | 大模型 / LLM |
| 9 | f/prompts.chat | 171,477 | 大模型 / LLM |
| 10 | huggingface/transformers | 166,759 | 深度学习框架 |

---

## 目录结构

```
starforge/
├── index.html      单文件成品（112 KB，含全部数据）
├── template.html   页面模板（含 __SEED_DATA__ 占位符）
├── refresh.py      数据拉取 + 注入构建 + 自检
├── stars_seed.json 清洗后的数据种子
└── README.md
```

## 关于 Token

页面里的 Token **只在浏览器内存中**使用，直连 `api.github.com`，不上传任何服务器、不写入 localStorage、不落盘。不填 Token 也能用全部离线功能。

---

## License

MIT © 2026 晨星（CJX0712）
