"""Check generated pages, canonical URLs, sitemap entries, and local links."""

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, unquote
from xml.etree import ElementTree

from config import ROOT, load_config


def main():
    site, _ = load_config()
    output = ROOT / "site"
    domain = site["domain"].rstrip("/")
    analytics_id = site.get("analytics_measurement_id", "")
    site_host = urlsplit(site["domain"]).hostname
    html_pages = sorted(output.rglob("index.html"))
    if not html_pages:
        raise AssertionError("no generated HTML pages")

    expected_urls = set()
    for page in html_pages:
        relative = page.relative_to(output).parent.as_posix()
        path = "" if relative == "." else relative + "/"
        canonical = f"{domain}/{path}"
        content = page.read_text(encoding="utf-8")
        if f'<link rel="canonical" href="{canonical}">' not in content:
            raise AssertionError(f"canonical mismatch: {page}")
        if "lorem ipsum" in content.lower() or "coming soon" in content.lower():
            raise AssertionError(f"placeholder copy: {page}")
        if analytics_id:
            tag = (f'<script defer src="/analytics.js" data-measurement-id="{analytics_id}" '
                   f'data-site-host="{site_host}"></script>')
            if content.count(tag) != 1:
                raise AssertionError(f"analytics consent script missing or duplicated: {page}")
            if "googletagmanager.com/gtag/js" in content:
                raise AssertionError(f"Google tag loaded before consent: {page}")
        for href in re.findall(r'href="([^"]+)"', content):
            if not href.startswith("/") or href.startswith("//"):
                continue
            target_path = unquote(urlsplit(href).path).lstrip("/")
            target = output / target_path
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                raise AssertionError(f"broken local link {href} in {page}")
        expected_urls.add(canonical)

    tree = ElementTree.parse(output / "sitemap.xml")
    actual_urls = {
        item.text for item in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    }
    if expected_urls != actual_urls:
        missing = expected_urls - actual_urls
        extra = actual_urls - expected_urls
        raise AssertionError(f"sitemap mismatch; missing={missing}; extra={extra}")

    robots = (output / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {domain}/sitemap.xml" not in robots:
        raise AssertionError("robots.txt sitemap URL mismatch")
    if analytics_id:
        if not (output / "analytics.js").exists():
            raise AssertionError("analytics.js missing")
        privacy = (output / "privacy" / "index.html").read_text(encoding="utf-8")
        if "Google Analytics 4" not in privacy or "Cookie choices" not in privacy:
            raise AssertionError("privacy page does not explain analytics choice")
    print(f"Verified {len(html_pages)} HTML pages, canonical URLs, local links, and sitemap entries")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ElementTree.ParseError) as exc:
        print(f"Site verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
