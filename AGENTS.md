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
