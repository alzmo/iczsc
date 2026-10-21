"""Regression checks for separate books; all fixtures are removed before exit."""
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from build_static import ROOT, metadata, paragraphs
from build_tonglu import build_tonglu

old = sorted((ROOT/'content/chapters').glob('[0-9]*.md'))
new = sorted((ROOT/'content/tonglu/chapters').glob('[0-9]*.md'))
assert old and new
for folder, sources, title in [('chapters', old, '晚班地图师'), ('tonglu/chapters', new, '同路')]:
    for src in sources:
        meta, body = metadata(src)
        output = (ROOT/'docs'/folder/meta.get('slug',src.stem)/'index.html').read_text()
        assert '<div class="prose">'+paragraphs(body)+'</div>' in output
        assert f'{title} · 章节目录' in output
        nav = re.search(r'<nav class="chapter-nav".*?</nav>', output).group()
        assert all(h.startswith('/'+folder+'/') for h in re.findall(r'href="([^"]+)"',nav))
        assert '2026年' in output
    index=(ROOT/'docs'/folder/'index.html').read_text()
    assert len(re.findall('<li>',index)) == len(sources)
assert '已更新 '+str(len(old))+' 章' in (ROOT/'docs/index.html').read_text()
assert '已更新 '+str(len(new))+' 章' in (ROOT/'docs/tonglu/index.html').read_text()
assert 'href="/tonglu/"' in (ROOT/'docs/index.html').read_text()
# An added Tonglu chapter must not leak into the old collection; a future/draft
# chapter must not appear in Tonglu output either. Fixtures never reach Git.
fixture=ROOT/'content/tonglu/chapters/isolation-fixture.md'
assert not fixture.exists()
try:
    for flags in ['publishDate: 2999-01-01T00:00:00+08:00\ndraft: false', 'publishDate: 2000-01-01T00:00:00+08:00\ndraft: true']:
        fixture.write_text('---\ntitle: "ISOLATION_FIXTURE"\ndate: 2000-01-01T00:00:00+08:00\nweight: 999\nslug: isolation-fixture\n'+flags+'\n---\nThis is a test fixture.\n')
        with tempfile.TemporaryDirectory() as d:
            urls=build_tonglu(Path(d),datetime.now(timezone.utc))
            assert not any('fixture' in u for u in urls)
            assert len(urls)==len(new)+2
        gate=subprocess.run(['python','release_check.py'],cwd=ROOT,capture_output=True)
        assert gate.returncode != 0, 'Public source release gate accepted a future/draft chapter'
finally:
    fixture.unlink(missing_ok=True)
print('PASS: exact prose, separate counts/index/navigation, and future/draft public-source gates')
