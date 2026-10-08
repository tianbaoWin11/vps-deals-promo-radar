::ILANG [TYPE:agent-rules][PROJECT:vps-deals][LANG:zh]
::STATE{@PROJECT|goal:公开来源驱动的英文 VPS 优惠静态站|owner:仓库所有者}
::MODULE{SOURCES|title:数据来源}
  .ilang/site.ilang 是品牌、地区、厂商和抓取入口的唯一配置。
  scraper.py 遵守 robots.txt，读取厂商官方公开页面；data/offers.json 记录来源和抓取时间。
::MODULE{ACTIONS|title:允许的动作}
  可以修改 I-Lang 配置、抓取器、静态模板、构建器和 GitHub Actions。
  修改厂商后须运行 scraper.py 和 build.py，确认页面内容跟着变化。
::BOUNDARY{never:编造优惠 价格 佣金 期限；绕反爬；抓登录后内容；品牌词竞价；cookie注入；自买自推|scope:permanent}
::RULE{没有可核实的价格⇒页面和结构化数据均不写价格}
::RULE{抓取失败⇒不保留旧活动冒充现行活动}
::RULE{联盟链接只在平台批准且符合该计划条款后添加；原始来源链接可直接使用}

## 文章日更交接

- `content/keyword-batch.json` 是用户提供的第一批关键词和顺序；搜索量只是用户转述的教练数据，不得作为独立核验结果或站点事实发布。
- 每次从顺序中选择首个尚未有独立文章覆盖的词族。相同意图已写过则记下跳过原因，不换词、不杜撰下一批。
- 文章源文件为 `content/articles/*.json`，由 `build.py` 生成 `/guides/` 页面并加入 sitemap。不可只修改 `site/` 产物。
- 任何优惠码、价格、额度、期限和适用范围必须先在厂商公开官方页面当场核对；网页打不开或信息不明确时不猜、不发布该主张。文章第一屏直接回答问题，并附来源与核查日期。
- 不复制对标站正文。补充本站可复核的核查步骤或交叉比较，复核词族重复、页面 canonical 和 sitemap 后再部署。
- 三家指定对标站和当前阅读证据见 `research/benchmark-2026-10-09.md`；Liquid Web 的正文被验证墙阻挡，不能声称已读完或断言三家共同缺口。
