# VPS Deals

An English-language VPS and cloud hosting offer ledger built from public, official provider pages. The site shows the original source and check time for every published claim. It does not use affiliate links until an approved program and its terms are confirmed.

Production URL: https://vps-deals-promo-radar-7iu.pages.dev/ (verify after deployment)

## Run locally

Python 3.12 or newer; no third-party Python packages or API keys.

```bash
python scraper.py
python build.py
```

Open `site/index.html` or serve `site/` with `python -m http.server 8000 -d site`.

## Change a provider

Edit `.ilang/site.ilang`. Each provider has an official home page, public source page, and an optional regex. A blank pattern keeps the provider in the watch list without creating an offer. `scraper.py` checks `robots.txt` and reads that file. `build.py` reads it again for the brand, provider pages, canonical URLs, and sitemap.

## Automatic checks and deployment

`.github/workflows/update.yml` checks every six hours, runs the scraper and static builder, then commits the latest verified snapshot. Cloudflare Pages should connect to the public GitHub repository with build command `python build.py` and output directory `site`. A GitHub Actions schedule may be delayed by GitHub, and source sites may refuse a request. A failed request never keeps an unverified old offer active.

The initial Pages host is temporary. Once an owned domain is chosen, set `domain` in `.ilang/site.ilang`, rebuild, and connect that domain to Pages so canonical URLs and the sitemap use the owned domain.

Credit amounts are not VPS plan prices. No price, expiry, coupon, or commission is inferred. Structured price data is emitted only when the original source provides a verified price and currency.

For monetization after approval, enter the approved HTTPS tracking URL and its platform (`CJ`, `ShareASale`, or `Impact`) for that provider in `.ilang/site.ilang`, and set `affiliate_approved:true` only after checking that program's terms for this site and offer. The detail page then labels the paid link, sets `rel="sponsored"`, and retains the direct official source link. Empty fields keep the original official link. No commission amount is asserted.

Site rules are described in I-Lang in `.ilang/site.ilang`; protocol information: https://ilang.ai.
