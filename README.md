# VPS Deals

An English-language VPS and cloud hosting offer ledger built from public, official provider pages. The site shows the original source and check time for every published claim. It does not use affiliate links until an approved program and its terms are confirmed.

Production URL: https://vpsdealbeacon.com/

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

`.github/workflows/update.yml` checks every six hours, runs the scraper and static builder, then commits the latest verified snapshot. Cloudflare Pages uses build command `exit 0` and output directory `site`; GitHub Actions commits the built files. A GitHub Actions schedule may be delayed by GitHub, and source sites may refuse a request. A failed request archives an offer page instead of presenting an unverified old offer as current.

Source-checked guides live in `content/articles/*.json`; `build.py` generates their HTML pages, the `/guides/` index, homepage cards, and sitemap entries. `content/keyword-batch.json` records the owner's fixed keyword order and coach-supplied search-volume estimates for planning only. A scheduled editor must check official public sources at publication time, avoid duplicate search intent, run `python build.py` and `python verify_site.py`, then deploy. The offer-refresh workflow also runs `verify_site.py` after each rebuild.

The owned domain is connected to Pages. `functions/_middleware.js` redirects the temporary Pages host to the owned domain with a 301 while preserving paths and query strings. The domain in `.ilang/site.ilang` drives canonical URLs and the sitemap.

The GA4 measurement ID in `.ilang/site.ilang` is a public site identifier. `build.py` adds a local consent script to each page; that script loads Google's tag only after a visitor selects "Allow analytics." The privacy page explains this choice, and the footer lets visitors change it. Optional Analytics data sharing and enhanced measurement were left off during setup. Do not infer traffic from a successful tag deployment; read actual GA4 reports.

Credit amounts are not VPS plan prices. No price, expiry, coupon, or commission is inferred. Structured price data is emitted only when the original source provides a verified price and currency.

For monetization after approval, enter the approved HTTPS tracking URL and its platform (`CJ`, `ShareASale`, or `Impact`) for that provider in `.ilang/site.ilang`, and set `affiliate_approved:true` only after checking that program's terms for this site and offer. The detail page then labels the paid link, sets `rel="sponsored"`, and retains the direct official source link. Empty fields keep the original official link. No commission amount is asserted.

Site rules are described in I-Lang in `.ilang/site.ilang`; protocol information: https://ilang.ai.
