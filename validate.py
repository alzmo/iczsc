"""Validate the static public output, without network access."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src"):
                self.links.append(value)

pages = list(OUT.rglob("*.html"))
assert pages, "No pages generated"
for page in pages:
    body = page.read_text(encoding="utf-8")
    assert "localhost" not in body and "livereload" not in body, page
    assert not re.search(r"[CD]:[\\/]|301123|奕东电子|api[_-]?key|access_token", body), page
    assert "https://down.dginv.click/#/register?code=7R92Q79A" in body, page
    assert 'rel="sponsored nofollow noopener noreferrer"' in body, page
    parser = Links()
    parser.feed(body)
    for link in parser.links:
        path = urlsplit(link)
        if path.netloc not in ("", "iczsc.com") or not path.path:
            continue
        target = OUT / path.path.lstrip("/")
        if target.is_dir():
            target = target / "index.html"
        assert target.is_file(), (page, link)
home = (OUT / "index.html").read_text(encoding="utf-8")
assert "3951.507" in home or "收盘点位" in home
assert "数据与判断边界" in home
assert (OUT / "CNAME").read_text().strip() == "iczsc.com"
print(f"Validated {len(pages)} pages: internal links, privacy, promotion, production URLs")
