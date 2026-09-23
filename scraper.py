# ::ILANG [TYPE:code][ROLE:核验厂商官方公开优惠][BOUNDARY:不绕过robots或登录]
# ::RULE{抓不到或条件不符⇒不发布优惠；数字必须来自匹配到的源页}
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from html.parser import HTMLParser

from config import ROOT, load_config

UA = "VPSDealLedger/1.0 (public-offer-monitor; no login)"


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def fetch(url, max_bytes=3_000_000):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,text/plain,*/*"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read(max_bytes + 1)[:max_bytes].decode("utf-8", errors="replace")


def robots_allow(url):
    bits = urllib.parse.urlsplit(url)
    robots_url = f"{bits.scheme}://{bits.netloc}/robots.txt"
    # The same User-Agent is used for robots.txt and the offer page.
    content = fetch(robots_url, max_bytes=250_000)
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(content.splitlines())
    return parser.can_fetch(UA, url)


def scrape_provider(provider, timestamp):
    if not provider["pattern"]:
        return None
    source = provider["source"]
    if not robots_allow(source):
        raise PermissionError("robots.txt disallows this source")
    parser = TextExtractor()
    parser.feed(fetch(source))
    visible_text = " ".join(" ".join(parser.parts).split())
    match = re.search(provider["pattern"], visible_text, flags=re.IGNORECASE)
    if not match:
        return None
    values = match.groupdict()
    if values.get("credit"):
        title = f"{provider['name']}: {values['credit']} free credit"
        if values.get("duration"):
            title += f" for the first {values['duration']}"
    else:
        title = f"{provider['name']}: free credits for up to {values['duration']}"
    offer = {
        "id": provider["id"] + "-signup-credit",
        "provider_id": provider["id"],
        "title": title,
        "offer_type": provider["offer_type"],
        "duration": values.get("duration"),
        "eligibility": provider["eligibility"],
        "offer_url": source,
        "source_url": source,
        "fetched_at": timestamp,
        "source_excerpt": match.group(0),
    }
    if values.get("credit"):
        offer["credit"] = values["credit"]
    return offer


def main():
    _, providers = load_config()
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    offers = []
    checks = []
    for provider in providers:
        if not provider["pattern"]:
            checks.append({"provider_id": provider["id"], "status": "monitor_only"})
            continue
        try:
            offer = scrape_provider(provider, timestamp)
            if offer:
                offers.append(offer)
            checks.append({"provider_id": provider["id"], "status": "verified" if offer else "no_match"})
        except (OSError, ValueError, PermissionError, re.error) as exc:
            checks.append({"provider_id": provider["id"], "status": "unavailable", "reason": type(exc).__name__})
            print(f"{provider['id']}: {type(exc).__name__}", file=sys.stderr)
    payload = {"generated_at": timestamp, "offers": offers, "checks": checks}
    output = ROOT / "data" / "offers.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Verified {len(offers)} live offer(s) from {len(providers)} configured provider(s)")


if __name__ == "__main__":
    main()
