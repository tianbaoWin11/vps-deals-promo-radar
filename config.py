# ::ILANG [TYPE:code][ROLE:解析站点配置][BOUNDARY:不从代码补造厂商或优惠]
# ::RULE{站点配置唯一来源:.ilang/site.ilang}
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / ".ilang" / "site.ilang"


def _fields(line):
    body = line[line.index("{") + 1 : line.rindex("}")]
    fields = {}
    for part in body.split("|"):
        if ":" in part:
            key, value = part.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def load_config(path=CONFIG):
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("::ILANG [TYPE:config]"):
        raise ValueError("site.ilang must begin with an I-Lang config header")
    site = None
    providers = []
    for line in text.splitlines():
        if line.startswith("::STATE{@SITE|"):
            site = _fields(line)
        elif line.startswith("::PROVIDER{"):
            provider = _fields(line)
            required = {"id", "name", "home", "source", "pattern", "offer_type", "eligibility"}
            if not required.issubset(provider):
                raise ValueError("provider missing fields: " + line)
            providers.append(provider)
    if not site or not providers:
        raise ValueError("site and providers are required in site.ilang")
    if len({p["id"] for p in providers}) != len(providers):
        raise ValueError("provider ids must be unique")
    return site, providers
