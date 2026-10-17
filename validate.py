"""Validate the static public output, without network access."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import argparse
import re

ROOT = Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--output',default='docs')
parser.add_argument('--expected-chapters',type=int)
parser.add_argument('--check-mirror',action='store_true')
args=parser.parse_args()
OUT=(ROOT/args.output).resolve()
PROMO='https://down.dginv.click/#/register?code=7R92Q79A'
class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.ids=set();self.promo=0;self.h1=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        assert tag not in ('iframe','form','input','textarea'),tag
        for k,v in attrs:
            assert not k.startswith('on'),('Inline event',k)
            if k in ('href','src'):
                assert not v.startswith(('javascript:','data:')),v
                self.links.append(v)
        if a.get('target')=='_blank':assert {'noopener','noreferrer'} <= set(a.get('rel','').split())
        if a.get('href')==PROMO:
            self.promo+=1
            assert a.get('target')=='_blank'
            assert a.get('rel')=='sponsored nofollow noopener noreferrer'
        if tag=='script':assert a.get('src')=='/reading.js'

pages=list(OUT.rglob('*.html'));assert pages
for page in pages:
    body=page.read_text()
    assert 'localhost' not in body and 'livereload' not in body,page
    assert not re.search(r'[CD]:[\\/]|301123|奕东电子|api[_-]?key|access_token|/workspace/|continuity-private',body),page
    assert all(s in body for s in ['晚班地图师','站外推广','公开只读','跳至正文','lang="zh-CN"']),page
    assert not any(s in body for s in ['上证收盘研究','复盘归档','market.css','/reports/']),page
    p=Links();p.feed(body);assert p.promo==1 and p.h1==1,(page,p.promo,p.h1)
    for link in p.links:
        parts=urlsplit(link)
        assert parts.scheme in ('','https'),(page,link)
        if parts.netloc not in ('','iczsc.com'):continue
        target=OUT/unquote(parts.path.lstrip('/')) if parts.path.startswith('/') else page.parent/unquote(parts.path)
        if not parts.path:target=page
        if target.is_dir():target=target/'index.html'
        assert target.is_file(),(page,link)
        if parts.fragment:
            target_parser=Links();target_parser.feed(target.read_text())
            assert parts.fragment in target_parser.ids,(page,link)
    if args.check_mirror:assert page.read_bytes()==(ROOT/page.relative_to(OUT)).read_bytes(),('mirror',page)
assert (OUT/'CNAME').read_text().strip()=='iczsc.com'
assert (OUT/'.nojekyll').exists()
assert not (OUT/'reports').exists()
chapters=list((OUT/'chapters').glob('*/index.html'))
if args.expected_chapters is not None:assert len(chapters)==args.expected_chapters,len(chapters)
if chapters:
    assert '已是第一章' in chapters[0].read_text()
    assert '从第一章开始' in (OUT/'index.html').read_text()
for path in OUT.rglob('*'):
    if path.is_file() and args.check_mirror:assert path.read_bytes()==(ROOT/path.relative_to(OUT)).read_bytes()
js=(OUT/'reading.js').read_text()
assert not re.search(r'fetch\(|XMLHttpRequest|sendBeacon|document.cookie',js)
assert not any(p.suffix in ('.md','.py','.toml','.zip','.gz','.bundle') for p in OUT.rglob('*'))
print(f'Validated {len(pages)} pages, {len(chapters)} chapters: links, accessibility landmarks, privacy, domain, promotion, future-content boundary'+(', root mirror' if args.check_mirror else ''))
