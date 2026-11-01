"""Three-book publication regression checks. Private fixtures are always removed."""
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from build_static import ROOT, metadata, paragraphs
from build_dudong import build_dudong

# Hidden-site regression: retain all sources, but never publish or index any of them.
if metadata(ROOT/'content/dudong/_index.md')[0].get('draft', 'false').lower() == 'true':
    import sys
    sources = sorted((ROOT/'content/dudong/chapters').glob('[0-9]*.md'))
    assert len(sources) == 400
    assert [int(metadata(p)[0]['weight']) for p in sources] == list(range(1,401))
    for base in [ROOT/'docs', ROOT]:
        assert not (base/'dudong').exists(), 'Hidden book output survived'
        for src in sources:
            slug = metadata(src)[0].get('slug', src.stem)
            assert not (base/'dudong/chapters'/slug/'index.html').exists()
    for output in (ROOT/'docs').rglob('*'):
        if output.is_file() and output.suffix in ['.html', '.xml', '.json', '.js']:
            text = output.read_text()
            assert '/dudong/' not in text and '渡冬' not in text, output
    section = (ROOT/'content/dudong/_index.md').read_text()
    assert 'cascade:' in section and '  build:' in section and '    render: never' in section
    # Even a direct component build must remove stale output, rather than leave it readable.
    with tempfile.TemporaryDirectory() as d:
        out = Path(d)
        stale = out/'dudong/chapters/001/index.html'
        stale.parent.mkdir(parents=True)
        stale.write_text('stale prose')
        assert build_dudong(out, datetime.now(timezone.utc)) == []
        assert not (out/'dudong').exists()
    subprocess.run([sys.executable, 'test_isolation.py'], cwd=ROOT, check=True)
    print('PASS: 400 recoverable sources; all 400 old chapter outputs and catalogs absent in both trees; no public entry/index; direct build cleans stale prose')
    sys.exit(0)

books = [('chapters', '晚班地图师'), ('tonglu/chapters', '同路'), ('dudong/chapters', '渡冬')]
for folder, title in books:
    sources = sorted((ROOT/'content'/folder).glob('[0-9]*.md'))
    assert sources, f'No final chapters: {title}'
    assert [int(metadata(p)[0]['weight']) for p in sources] == list(range(1,len(sources)+1))
    urls = ['/'+folder+'/'+metadata(p)[0].get('slug',p.stem)+'/' for p in sources]
    index=(ROOT/'docs'/folder/'index.html').read_text()
    assert len(re.findall('<li>',index)) == len(sources)
    for i,src in enumerate(sources):
        meta,body=metadata(src)
        output=(ROOT/'docs'/folder/meta.get('slug',src.stem)/'index.html').read_text()
        assert '<div class="prose">'+paragraphs(body)+'</div>' in output, src
        assert f'{title} · 章节目录' in output
        nav=re.search(r'<nav class="chapter-nav".*?</nav>',output).group()
        expected=([urls[i-1]] if i else [])+['/'+folder+'/']+([urls[i+1]] if i+1<len(urls) else [])
        assert re.findall(r'href="([^"]+)"',nav)==expected,(src,nav)
        assert ('rel="prev"' in nav)==(i>0)
        assert ('rel="next"' in nav)==(i+1<len(urls))
    home=(ROOT/'docs'/('index.html' if folder=='chapters' else folder.split('/')[0]+'/index.html')).read_text()
    completed = folder == 'dudong/chapters' and metadata(ROOT/'content/dudong/_index.md')[0].get('completed','false').lower() == 'true'
    assert (f'全书完结 · 共 {len(sources)} 章' if completed else f'已更新 {len(sources)} 章') in home
    if completed:
        assert len(sources) == 400
        assert '<span>全书完结</span>' in nav and '待续' not in nav
home=(ROOT/'docs/index.html').read_text()
assert all(x in home for x in ['晚班地图师','href="/tonglu/"','《同路》','href="/dudong/"','《渡冬》'])
count=len(list((ROOT/'content/dudong/chapters').glob('[0-9]*.md')))
fixture=ROOT/'content/dudong/chapters/isolation-fixture.md'
assert not fixture.exists()
try:
    for flags in ['publishDate: 2999-01-01T00:00:00+08:00\ndraft: false','publishDate: 2000-01-01T00:00:00+08:00\ndraft: true']:
        fixture.write_text('---\ntitle: "ISOLATION_FIXTURE"\ndate: 2000-01-01T00:00:00+08:00\nweight: 999\nslug: isolation-fixture\n'+flags+'\n---\nThis is a test fixture.\n')
        with tempfile.TemporaryDirectory() as d:
            urls=build_dudong(Path(d),datetime.now(timezone.utc))
            assert not any('fixture' in u for u in urls)
            assert len(urls)==count+2
        gate=subprocess.run(['python','release_check.py'],cwd=ROOT,capture_output=True)
        assert gate.returncode != 0
finally:
    fixture.unlink(missing_ok=True)
print('PASS: three-book prose, contiguous numbering, exact adjacent navigation, counts, isolation and release gate')

# Only published volume labels appear, with each chapter in its stated volume.
expected_groups=[]
for src in sorted((ROOT/'content/dudong/chapters').glob('[0-9]*.md')):
    meta,_=metadata(src)
    volume=int(meta.get('volume','1'))
    title=meta.get('volumeTitle','第一卷 · 云州雪夜')
    if not expected_groups or expected_groups[-1] != (volume,title):
        expected_groups.append((volume,title))
    output=(ROOT/'docs/dudong/chapters'/meta.get('slug',src.stem)/'index.html').read_text()
    assert '<p class="eyebrow">'+title+'</p>' in output
for rel in ['dudong/index.html','dudong/chapters/index.html']:
    output=(ROOT/'docs'/rel).read_text()
    actual=re.findall(r'<h3 class="volume-heading" id="volume-(\d+)">(.*?)</h3>',output)
    assert [(int(n),title) for n,title in actual]==expected_groups
print('PASS: published-volume grouping and chapter volume labels')
