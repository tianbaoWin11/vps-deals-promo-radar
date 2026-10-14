# 2026-10-14 并行工作断点

本周期继续锁定 `vps deals` 及 `lowendbox.com`、`liquidweb.com`、`forbes.com`。今天按 `content/keyword-batch.json` 顺序发布第 6 行 `vultr promo code`；四个同族词合并在同一页。教练给的搜索量未独立核实，不作为站点事实。

| 线 | 当日产物与证据 | 限制 |
| --- | --- | --- |
| T1 视觉 | 系统 Chrome 以 390px 宽度查看新文章首屏，标题、答案和导航可读；`document.documentElement.clientWidth` 与 `scrollWidth` 均为 390，未见整页横向溢出。临时移动端模拟已恢复。`python verify_site.py` 验证 17 个 HTML 页面、canonical、站内链接和 sitemap。 | 这是浏览器模拟宽度，不等同于所有实体手机和网络的实测；今日未改站点样式。 |
| T2 对标 | 沿用 `research/benchmark-2026-10-09.md` 的 LowEndBox 与 Forbes 已读样本。新文章按“优惠类型→官方限制→账单实际结果”组织，并提供本站自写的四字段核对记录；没有引用或改写对标正文。 | Liquid Web 正文仍被验证墙挡住，不能称三站共同缺口或断言排名原因。 |
| T3 素材 | 系统 Chrome 当场读取 Google US 可见问题、Vultr 官方优惠页及 Vultr Docs。来源、时间和限制记录在 `research/editorial-ammo-2026-10-14.md`。 | Vultr 的单项促销详情页显示安全验证，Reddit 讨论显示网络封锁；两者正文都未读取，不用作优惠事实。Google 提示不等于搜索量。 |
| T4 问答 | `content/articles/vultr-promo-code.json` 第一屏直接区分首次充值匹配与公开列出的赠额代码；正文回答是否给免费额度、能否叠加及最大标称额度是否一定划算，并提供本站独立的核对步骤。文章已按 `content/publish-log.md` 从公网核验。 | 没有创建账户、输入代码、充值或测试结账；不声称这些代码对任何具体读者已生效。 |
| T5 图和视频 | 原创路径图 `content/media/vultr-code-paths.svg` 从生成源发布到文章，系统 Chrome 看到图像，线上 SVG HTTP 200。 | 本日没有上传视频；既有 YouTube 频道状态未重新核对。 |

部署证据：提交 `7f6a0f9` 推送 GitHub `main` 后，系统 Chrome 在 `https://vpsdealbeacon.com/guides/vultr-promo-code/` 读到新正文及正确 canonical；浏览器网络响应 HTTP 200。`https://vpsdealbeacon.com/sitemap.xml` 返回 HTTP 200，含新页 URL。下一词批行是 `coupon contabo`；今日已验证发布，不再取下一行。
