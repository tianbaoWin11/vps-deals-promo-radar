# 文章发布记录

此表只记录从线上地址读回并确认可访问的文章。每日任务先从 `content/keyword-batch.json` 按 `order` 选词，核对已有文章与 sitemap，发布并验证后再追加一行；未上线的草稿不记为已发布。

| 日期（北京时间） | 批次行 | 标题 | 线上地址 | 证据 |
| --- | --- | --- | --- | --- |
| 2026-10-09 | 1 | Hostinger coupon code: official page check | https://vpsdealbeacon.com/guides/hostinger-coupon-code/ | 公网 HTTP 200；canonical 指向该页；`sitemap.xml` 收录该 URL（本机当日实测）。 |
| 2026-10-10 | 2 | Hostinger domain coupon code: check the product first | https://vpsdealbeacon.com/guides/hostinger-domain-coupon-code/ | Cloudflare Pages 对提交 `c71c917` 显示 `deploy / success`；公网文章 HTTP 200，canonical 指向自身，sitemap 含该 URL；两张 SVG 图片均 HTTP 200（本机当日实测）。 |
