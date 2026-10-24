"""Independent Dudong output. Never joins the legacy /chapters/ collection."""
import html
import re
from datetime import datetime
from build_static import ROOT, metadata, paragraphs, render


def build_dudong(out, now):
    completed = metadata(ROOT/"content/dudong/_index.md")[0].get("completed", "false").lower() == "true"
    chapters = []
    for source in (ROOT/'content/dudong/chapters').glob('*.md'):
        if source.name.startswith('_'):
            continue
        meta, body = metadata(source)
        date = datetime.fromisoformat(meta['date'])
        due = datetime.fromisoformat(meta.get('publishDate', meta['date']))
        assert date.tzinfo and due.tzinfo
        if meta.get('draft', 'false').lower() == 'true' or due > now:
            continue
        assert int(meta['weight']) <= 40 or ('volume' in meta and 'volumeTitle' in meta), 'Explicit volume metadata required after volume one'
        slug = meta.get('slug', source.stem)
        assert re.fullmatch(r'[a-zA-Z0-9-]+', slug)
        chapters.append(dict(title=meta['title'], date=date, weight=int(meta['weight']),
                             url='/dudong/chapters/'+slug+'/', body=body,
                             volume=int(meta.get('volume', '1')), volume_title=meta.get('volumeTitle', '第一卷 · 云州雪夜')))
    chapters.sort(key=lambda c: c['weight'])
    assert len({c['weight'] for c in chapters}) == len(chapters)
    assert len({c['url'] for c in chapters}) == len(chapters)

    if completed:
        assert [c["weight"] for c in chapters] == list(range(1,401)), "Completed Dudong requires all 400 published chapters"

    def write(url, title, body):
        target = out/url.strip('/')/'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(title, url, body, template_path='layouts/dudong/baseof.html'), encoding='utf-8')

    def chapter_listing(group):
        return '<ol class="chapter-list">'+''.join(
        '<li><a href="'+c['url']+'"><span>'+html.escape(c['title'])+'</span><time datetime="'+c['date'].strftime('%Y-%m-%d')+'">'+c['date'].strftime('%Y.%m.%d')+'</time></a></li>'
        for c in group)+'</ol>'
    groups = []
    for c in chapters:
        if not groups or groups[-1][0] != c['volume']:
            assert all(g[0] < c['volume'] for g in groups), 'Volumes must be consecutive blocks in chapter order'
            groups.append((c['volume'], c['volume_title'], []))
        assert groups[-1][1] == c['volume_title'], 'Inconsistent volume title'
        groups[-1][2].append(c)
    listing = ''.join('<h3 class="volume-heading" id="volume-'+str(n)+'">'+html.escape(title)+'</h3>'+chapter_listing(group) for n,title,group in groups)
    if not chapters: listing = '<p class="waiting">暂无已发布章节。</p>'
    for url, title in [('/dudong/', '渡冬'), ('/dudong/chapters/', '章节目录')]:
        body = '<section class="book-intro"><p class="eyebrow">ICZSC · 独立连载</p><h1>'+title+'</h1><p class="book-note">按卷分组 · 按章节顺序阅读</p>'
        body += ('<div class="book-actions"><a class="button" href="'+chapters[0]['url']+'">从第一章开始</a><a class="text-link" href="'+chapters[-1]['url']+'">阅读最新章 <span aria-hidden="true">→</span></a></div><p class="published">已更新 '+str(len(chapters))+' 章</p>') if chapters else '<p class="waiting">故事即将开始。</p>'
        if completed:
            body = body.replace('已更新 '+str(len(chapters))+' 章', '全书完结 · 共 '+str(len(chapters))+' 章')
        body += '</section><section class="contents" aria-labelledby="contents-title"><div class="section-heading"><h2 id="contents-title">渡冬 · 章节目录</h2><a class="text-link" href="/dudong/">作品首页</a></div>'+listing+'</section>'
        write(url, title, body)
    for i, c in enumerate(chapters):
        minutes = max(1, (len(re.findall(r'[\u3400-\u9fff]|[A-Za-z0-9]+', c['body']))+499)//500)
        body = '<article class="chapter"><header class="chapter-header"><a class="eyebrow" href="/dudong/chapters/">渡冬 · 章节目录</a><p class="eyebrow">'+html.escape(c['volume_title'])+'</p><h1>'+html.escape(c['title'])+'</h1><p class="chapter-meta"><time datetime="'+c['date'].isoformat()+'">'+c['date'].strftime('%Y年%m月%d日')+'</time><span>约 '+str(minutes)+' 分钟</span></p></header><div class="prose">'+paragraphs(c['body'])+'</div><nav class="chapter-nav" aria-label="章节翻页">'
        body += '<a href="'+chapters[i-1]['url']+'" rel="prev">← 上一章</a>' if i else '<span>已是第一章</span>'
        body += '<a href="/dudong/chapters/">目录</a>'
        body += '<a href="'+chapters[i+1]['url']+'" rel="next">下一章 →</a>' if i+1 < len(chapters) else ('<span>全书完结</span>' if completed else '<span>待续</span>')
        body += '</nav><a class="back-top" href="#main">回到页首 ↑</a></article>'
        write(c['url'], c['title'], body)
    print(f'Dudong: {len(chapters)} independently released chapters')
    return ['/dudong/', '/dudong/chapters/']+[c['url'] for c in chapters]
