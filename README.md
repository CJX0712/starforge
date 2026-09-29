# starforge ★ · GitHub Star 榜单浏览器

零依赖 · 单文件 HTML 的 GitHub 高星开源仓库榜单浏览器。**247 个真实高星仓库 · 12,251,211 颗星 · 10 大赛道**，数据快照取自 GitHub Search API。

## 运行

双击 `starforge.html` 即可，无需服务器、无需构建、无任何外部依赖。

## 功能

- **10 大赛道筛选**：LLM 与智能体 / RAG 与检索 / 深度学习框架 / NLP 与多模态 / 计算机视觉 / 语音 / AutoML 与表格 / 强化学习 / 工程与部署 / 数据与可视化
- **搜索**：按仓库名 / 描述 / 语言即时过滤
- **排序**：⭐ 星数 / ⑂ forks / 名称
- **收藏**：☆ 一键收藏，`localStorage` 持久化，支持导出 JSON / CSV 收藏清单
- **星级条**：相对当前榜单最高星的占比可视化

## 数据

数据快照于 2026-09，每条记录含 `full_name · stars · forks · language · 官方 topics · 跳转链接`。
收录门槛：单仓 ≥ 8,000 星，按 10 个赛道关键词检索后去重合并。

## 可验证的不变量（浏览器控制台输出 `selfTest`）

| 不变量 | 验证方式 |
| --- | --- |
| 无重复仓库 | `full_name` 集合大小 == 数组长度 |
| 恰好 10 赛道 | 赛道集合大小 == 10 |
| 收录门槛 | 每仓 `stars >= 8000` |
| 链接合法 | 每仓 `url` 以 `https://github.com/` 开头 |

## 无头自检

```bash
node -e "const h=require('fs').readFileSync('starforge.html','utf8');const d=JSON.parse(h.match(/const DATA = (\[[\s\S]*?\]);/)[1]);console.log(d.length, new Set(d.map(x=>x.track)).size==10, new Set(d.map(x=>x.full)).size==d.length)"
# 247 true true
```

---
作者 晨星 (Chen Xing) · [CJX0712](https://github.com/CJX0712) · MIT License
