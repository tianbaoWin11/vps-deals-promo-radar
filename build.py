# ::ILANG [TYPE:code][ROLE:从已核验数据生成静态站][BOUNDARY:不补造缺失价格或期限]
# ::RULE{品牌、厂商、域名均读取:.ilang/site.ilang}
import html
import hashlib
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from string import Template
from urllib.parse import urlsplit

from config import ROOT, load_config


def esc(value):
    return html.escape(str(value), quote=True)


def read_template(name):
    return Template((ROOT / "templates" / name).read_text(encoding="utf-8"))


def url_for(domain, path=""):
    return domain.rstrip("/") + "/" + path.lstrip("/")


def jsonld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace("<", "\\u003c") + "</script>"


def card(offer, provider):
    href = f"/deals/{esc(offer['id'])}/"
    return (f'<article class="card"><div class="eyebrow">{esc(provider["name"])} · Source checked</div>'
            f'<h3><a href="{href}">{esc(offer["title"])}</a></h3>'
            f'<p>{esc(offer["eligibility"])}</p>'
            f'<div class="card-footer"><a class="text-link" href="{href}">See source & terms →</a>'
            f'<span>{esc(offer["fetched_at"][:10])}</span></div></article>')


def layout(site, path, title, description, body, structured, updated):
    canonical = url_for(site["domain"], path)
    analytics_id = site.get("analytics_measurement_id", "")
    analytics_tag = (f'<script defer src="/analytics.js" data-measurement-id="{esc(analytics_id)}"></script>'
                     if analytics_id else "")
    analytics_settings = ('<button type="button" id="analytics-settings" class="footer-button">Cookie choices</button>'
                          if analytics_id else "")
    analytics_notice = (
        '<section id="analytics-consent" class="analytics-consent" aria-label="Analytics choice" hidden>'
        '<p>Allow Google Analytics to measure visits to this site? We load it only if you choose Allow. '
        'You can change this choice later in the footer. <a href="/privacy/">Privacy Policy</a></p>'
        '<div class="analytics-actions"><button type="button" data-analytics-choice="decline">Decline</button>'
        '<button type="button" data-analytics-choice="allow">Allow analytics</button></div></section>'
        if analytics_id else "")
    return read_template("base.html").substitute(
        lang=esc(site["locale"]), title=esc(title), description=esc(description),
        canonical=esc(canonical), brand=esc(site["brand"]), niche=esc(site["niche"]),
        og_image=esc(url_for(site["domain"], "og.svg")), updated=esc(updated[:10]),
        style_version=esc(site["style_version"]),
        body=body, structured="\n".join(jsonld(x) for x in structured),
        analytics_tag=analytics_tag, analytics_settings=analytics_settings,
        analytics_notice=analytics_notice,
        affiliate_note="Some provider links are approved affiliate links. We may earn a commission at no extra cost to you." if site.get("affiliate_active") else "No affiliate links are active.",
    )


def breadcrumb(domain, parts):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": label, "item": url_for(domain, path)}
        for i, (label, path) in enumerate(parts, 1)
    ]}


def itemlist(domain, offers):
    return {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i, "url": url_for(domain, f"deals/{offer['id']}/")}
        for i, offer in enumerate(offers, 1)
    ]}


def write_page(out, path, contents):
    target = out / path / "index.html" if path else out / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(contents, encoding="utf-8")


def load_articles():
    directory = ROOT / "content" / "articles"
    articles = []
    slugs = set()
    for source in sorted(directory.glob("*.json")):
        article = json.loads(source.read_text(encoding="utf-8"))
        required = {"slug", "title", "description", "primary_keyword", "answer",
                    "checked_at", "published_at", "sections", "sources"}
        if not required.issubset(article):
            raise ValueError(f"article missing required fields: {source}")
        slug = article["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in slugs:
            raise ValueError(f"invalid or duplicate article slug: {slug}")
        if not article["sources"] or not article["sections"]:
            raise ValueError(f"article needs sections and sources: {source}")
        for item in article["sources"]:
            if urlsplit(item["url"]).scheme != "https":
                raise ValueError(f"article source must be HTTPS: {source}")
        datetime.fromisoformat(article["checked_at"].replace("Z", "+00:00"))
        datetime.fromisoformat(article["published_at"])
        slugs.add(slug)
        articles.append(article)
    return sorted(articles, key=lambda item: (item["published_at"], item["slug"]), reverse=True)


def render_article_body(article):
    facts = "".join(
        f'<tr><th scope="row">{esc(fact["label"])}</th><td>{esc(fact["value"])}</td>'
        f'<td><a href="{esc(fact["source_url"])}" rel="noopener noreferrer">Official source ↗</a></td></tr>'
        for fact in article.get("facts", []))
    fact_table = (f'<div class="table-wrap"><table><thead><tr><th>Check</th><th>Observed result</th>'
                  f'<th>Source</th></tr></thead><tbody>{facts}</tbody></table></div>') if facts else ""
    sections = ""
    for section in article["sections"]:
        paragraphs = "".join(f"<p>{esc(p)}</p>" for p in section.get("paragraphs", []))
        bullets = ("<ul>" + "".join(f"<li>{esc(p)}</li>" for p in section["bullets"]) + "</ul>") if section.get("bullets") else ""
        sections += f'<section><h2>{esc(section["heading"])}</h2>{paragraphs}{bullets}</section>'
    sources = "".join(
        f'<li><a href="{esc(item["url"])}" rel="noopener noreferrer">{esc(item["label"])}</a></li>'
        for item in article["sources"])
    return read_template("article.html").substitute(
        title=esc(article["title"]), answer=esc(article["answer"]),
        checked=esc(article["checked_at"][:10]), published=esc(article["published_at"]),
        keyword=esc(article["primary_keyword"]), fact_table=fact_table,
        sections=sections, sources=sources,
        method=esc(article.get("method", "Facts were checked against the linked official pages.")))


def main():
    site, providers = load_config()
    site["style_version"] = hashlib.sha256((ROOT / "templates" / "style.css").read_bytes()).hexdigest()[:12]
    data_path = ROOT / "data" / "offers.json"
    data = json.loads(data_path.read_text(encoding="utf-8")) if data_path.exists() else {"offers": [], "generated_at": ""}
    offers = data.get("offers", [])
    provider_by_id = {p["id"]: p for p in providers}
    articles = load_articles()
    today = datetime.now(timezone(timedelta(hours=8))).date().isoformat()
    # The dataset is a historical input; never silently treat an old fetch as live.
    current = []
    for offer in offers:
        if offer.get("provider_id") not in provider_by_id:
            continue
        fetched = offer.get("fetched_at", "")
        try:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(fetched)).total_seconds()
        except ValueError:
            continue
        if age < 0 or age > 48 * 3600:
            continue
        if offer.get("valid_until") and offer["valid_until"] < today:
            continue
        current.append(offer)
    site["affiliate_active"] = any(o.get("affiliate_url") for o in current)
    updated = data.get("generated_at") or datetime.now(timezone.utc).isoformat(timespec="seconds")
    out = ROOT / "site"
    if out.resolve().parent != ROOT.resolve():
        raise RuntimeError("site output must remain inside the repository")
    # Keep published deal URLs available when a later source check no longer
    # verifies an offer. The archived page must not present it as current.
    previous_deal_paths = {
        page.relative_to(out).parent.as_posix() + "/"
        for page in out.glob("deals/*/index.html")
    } if out.exists() else set()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(exist_ok=True)
    month = datetime.now(timezone.utc).strftime("%B %Y")
    provider_links = "".join(f'<a class="provider-pill" href="/providers/{esc(p["id"])}/">{esc(p["name"])} <span>↗</span></a>' for p in providers)
    cards = "".join(card(o, provider_by_id[o["provider_id"]]) for o in current)
    if not cards:
        cards = '<div class="empty">No current offer passed source verification. Browse the official provider pages below.</div>'
    article_cards = "".join(
        f'<article class="card guide-card"><div class="eyebrow">GUIDE · {esc(a["published_at"])}</div>'
        f'<h3><a href="/guides/{esc(a["slug"])}/">{esc(a["title"])}</a></h3>'
        f'<p>{esc(a["description"])}</p><div class="card-footer"><a class="text-link" '
        f'href="/guides/{esc(a["slug"])}/">Read guide →</a></div></article>'
        for a in articles[:3])
    body = read_template("index.html").substitute(niche=esc(site["niche"]), cards=cards,
        providers=provider_links, count=len(current), updated=esc(updated[:10]),
        article_cards=article_cards)
    write_page(out, "", layout(site, "", f"Verified VPS offers · {month} | {site['brand']}",
        f"Official-source VPS and cloud hosting offers checked on {updated[:10]}. Eligibility and source links included.",
        body, [itemlist(site["domain"], current)], updated))

    for provider in providers:
        own = [o for o in current if o["provider_id"] == provider["id"]]
        own_cards = "".join(card(o, provider) for o in own) or '<div class="empty">No current offer passed verification for this provider. Check the official source directly.</div>'
        verification_note = (
            f"No current {provider['name']} offer passed this site's source check. "
            "Use the official source and provider website above to check the latest terms directly."
            if not own else
            f"The {provider['name']} offer cards below link to verified claims, their check dates, and direct official sources."
        )
        body = read_template("provider.html").substitute(name=esc(provider["name"]), source=esc(provider["source"]),
            home=esc(provider["home"]), cards=own_cards, count=len(own), verification_note=esc(verification_note))
        path = f"providers/{provider['id']}/"
        structured = [breadcrumb(site["domain"], [("Home", ""), (provider["name"], path)])]
        if own and all("price" in o and "currency" in o for o in own):
            structured.append({"@context": "https://schema.org", "@type": "Service", "name": provider["name"] + " VPS hosting", "offers": [
                {"@type": "Offer", "price": o["price"], "priceCurrency": o["currency"], "url": o["offer_url"]} for o in own]})
        write_page(out, path, layout(site, path, f"{provider['name']} VPS offers · {month} | {site['brand']}",
            f"Verified {provider['name']} offers and direct official sources. Checked {updated[:10]}.", body, structured, updated))

    for offer in current:
        provider = provider_by_id[offer["provider_id"]]
        path = f"deals/{offer['id']}/"
        credit = f'<div class="fact"><span>Credit</span><strong>{esc(offer["credit"])}</strong></div>' if offer.get("credit") else ""
        duration = f'<div class="fact"><span>Duration</span><strong>{esc(offer["duration"])}</strong></div>' if offer.get("duration") else ""
        body = read_template("deal.html").substitute(title=esc(offer["title"]), provider=esc(provider["name"]),
            provider_path=esc(f"/providers/{provider['id']}/"), source=esc(offer["source_url"]),
            excerpt=esc(offer["source_excerpt"]), checked=esc(offer["fetched_at"]),
            eligibility=esc(offer["eligibility"]), credit=credit, duration=duration,
            offer_url=esc(offer.get("affiliate_url", offer["offer_url"])),
            link_rel="sponsored noopener noreferrer" if offer.get("affiliate_url") else "noopener noreferrer",
            affiliate_disclosure='<p class="fineprint">Approved affiliate link via ' + esc(offer["affiliate_platform"]) + '. We may earn a commission at no extra cost to you.</p>' if offer.get("affiliate_url") else "")
        structured = [breadcrumb(site["domain"], [("Home", ""), (provider["name"], f"providers/{provider['id']}/"), (offer["title"], path)])]
        if "price" in offer and "currency" in offer:
            schema_offer = {"@context": "https://schema.org", "@type": "Offer", "name": offer["title"],
                "price": offer["price"], "priceCurrency": offer["currency"], "url": offer["offer_url"],
                "availability": "https://schema.org/InStock"}
            if offer.get("valid_until"):
                schema_offer["priceValidUntil"] = offer["valid_until"]
            structured.append(schema_offer)
        write_page(out, path, layout(site, path, f"{offer['title']} · {month} | {site['brand']}",
            f"{offer['title']}. {offer['eligibility']}. Official source checked {offer['fetched_at'][:10]}.",
            body, structured, offer["fetched_at"]))

    rows = "".join(f'<tr><th scope="row"><a href="/providers/{esc(p["id"])}/">{esc(p["name"])}</a></th>'
        f'<td>{len([o for o in current if o["provider_id"] == p["id"]])}</td>'
        f'<td><a href="{esc(p["source"])}" rel="noopener noreferrer">Official source ↗</a></td></tr>' for p in providers)
    body = read_template("compare.html").substitute(rows=rows, updated=esc(updated[:10]))
    write_page(out, "compare/", layout(site, "compare/", f"Compare verified VPS offers · {month} | {site['brand']}",
        f"Compare which VPS providers have verified published offers as of {updated[:10]}.",
        body, [itemlist(site["domain"], current)], updated))

    editorial_pages = (
        ("about/", "About VPS Deals", "How VPS Deals checks public VPS and cloud hosting offers."),
        ("contact/", "Contact VPS Deals", "Contact the VPS Deals site editor about corrections or questions."),
        ("privacy/", "Privacy Policy", "How VPS Deals handles site visits and email correspondence."),
    )
    for path, title, description in editorial_pages:
        body = read_template(path.rstrip("/") + ".html").substitute(
            contact_email=esc(site["contact_email"]))
        write_page(out, path, layout(site, path, f"{title} | {site['brand']}",
            description, body, [], updated))

    if articles:
        guide_cards = "".join(
            f'<article class="card guide-card"><div class="eyebrow">{esc(a["published_at"])}</div>'
            f'<h3><a href="/guides/{esc(a["slug"])}/">{esc(a["title"])}</a></h3>'
            f'<p>{esc(a["description"])}</p><div class="card-footer"><a class="text-link" '
            f'href="/guides/{esc(a["slug"])}/">Read guide →</a></div></article>'
            for a in articles)
        guide_body = (f'<section class="page-hero wrap"><div class="eyebrow">RESEARCH NOTES</div>'
                      f'<h1>VPS guides</h1><p>Practical checks with dated primary sources.</p></section>'
                      f'<section class="band"><div class="wrap"><div class="cards">{guide_cards}</div></div></section>')
        write_page(out, "guides/", layout(site, "guides/", f"VPS guides | {site['brand']}",
            "Source-checked VPS coupon and hosting guides.", guide_body, [], articles[0]["checked_at"]))
        for article in articles:
            path = f'guides/{article["slug"]}/'
            structured = [breadcrumb(site["domain"], [("Home", ""), ("Guides", "guides/"),
                (article["title"], path)])]
            write_page(out, path, layout(site, path, f'{article["title"]} | {site["brand"]}',
                article["description"], render_article_body(article), structured,
                article["checked_at"]))

    current_deal_paths = {f"deals/{o['id']}/" for o in current}
    archived_paths = sorted(previous_deal_paths - current_deal_paths)
    for path in archived_paths:
        provider = next((p for p in providers if path.startswith(f"deals/{p['id']}-")), None)
        source = (f'<p><a href="{esc(provider["source"])}" rel="noopener noreferrer">'
                  'Check the official source for current terms →</a></p>') if provider else ""
        body = ('<section class="page-hero wrap"><h1>Offer not currently verified</h1>'
                '<p>This previously published offer is not currently verified. '
                'Check the provider’s official source before signing up.</p>'
                + source + '</section>')
        write_page(out, path, layout(site, path, f"Offer not currently verified | {site['brand']}",
            "This previously published offer is not currently verified.", body, [], updated))

    paths = (["", "compare/"] + (["guides/"] if articles else [])
             + [f'guides/{article["slug"]}/' for article in articles]
             + [path for path, _, _ in editorial_pages]
             + [f"providers/{p['id']}/" for p in providers]
             + sorted(current_deal_paths) + archived_paths)
    # lastmod records material offer changes, not each routine check.
    offer_times = {f"deals/{o['id']}/": o.get("content_updated_at", o["fetched_at"])[:10] for o in current}
    if current:
        latest_material = max(o.get("content_updated_at", o["fetched_at"])[:10] for o in current)
    else:
        latest_material = updated[:10]
    for provider in providers:
        own = [o for o in current if o["provider_id"] == provider["id"]]
        offer_times[f"providers/{provider['id']}/"] = max(
            (o.get("content_updated_at", o["fetched_at"])[:10] for o in own), default=latest_material)
    offer_times[""] = max(latest_material, *(a["published_at"] for a in articles)) if articles else latest_material
    offer_times["compare/"] = latest_material
    for path, _, _ in editorial_pages:
        offer_times[path] = today
    if articles:
        offer_times["guides/"] = max(a["checked_at"][:10] for a in articles)
        for article in articles:
            offer_times[f'guides/{article["slug"]}/'] = article["checked_at"][:10]
    for path in archived_paths:
        offer_times[path] = today
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f'<url><loc>{esc(url_for(site["domain"], path))}</loc><lastmod>{esc(offer_times[path])}</lastmod></url>\n' for path in paths)
    (out / "sitemap.xml").write_text(sitemap + "</urlset>\n", encoding="utf-8")
    (out / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + url_for(site["domain"], "sitemap.xml") + "\n", encoding="utf-8")
    (out / "style.css").write_text((ROOT / "templates" / "style.css").read_text(encoding="utf-8"), encoding="utf-8")
    if site.get("analytics_measurement_id"):
        (out / "analytics.js").write_text((ROOT / "templates" / "analytics.js").read_text(encoding="utf-8"), encoding="utf-8")
    (out / "og.svg").write_text((ROOT / "templates" / "og.svg").read_text(encoding="utf-8").replace("{{BRAND}}", esc(site["brand"])), encoding="utf-8")
    print(f"Built {len(paths)} HTML pages into {out}")


if __name__ == "__main__":
    main()
