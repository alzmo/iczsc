"""Independent Tonglu output. Never joins the legacy /chapters/ collection."""
import html
import re
from datetime import datetime
from build_static import ROOT, metadata, paragraphs, render


def build_tonglu(out, now):
    chapters = []
    for source in (ROOT/'content/tonglu/chapters').glob('*.md'):
        if source.name.startswith('_'):
            continue
        meta, body = metadata(source)
        date = datetime.fromisoformat(meta['date'])
        due = datetime.fromisoformat(meta.get('publishDate', meta['date']))
        assert date.tzinfo and due.tzinfo
        if meta.get('draft', 'false').lower() == 'true' or due > now:
            continue
        slug = meta.get('slug', source.stem)
        assert re.fullmatch(r'[a-zA-Z0-9-]+', slug)
        chapters.append(dict(title=meta['title'], date=date, weight=int(meta['weight']),
                             url='/tonglu/chapters/'+slug+'/', body=body))
    chapters.sort(key=lambda c: c['weight'])
    assert len({c['weight'] for c in chapters}) == len(chapters)
    assert len({c['url'] for c in chapters}) == len(chapters)

    def write(url, title, body):
        target = out/url.strip('/')/'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(title, url, body, template_path='layouts/tonglu/baseof.html'), encoding='utf-8')

    listing = '<ol class="chapter-list">'+''.join(
        '<li><a href="'+c['url']+'"><span>'+html.escape(c['title'])+'</span><time datetime="'+c['date'].strftime('%Y-%m-%d')+'">'+c['date'].strftime('%Y.%m.%d')+'</time></a></li>'
        for c in chapters)+('' if chapters else '<li class="waiting">暂无已发布章节。</li>')+'</ol>'
    for url, title in [('/tonglu/', '同路'), ('/tonglu/chapters/', '章节目录')]:
        body = '<section class="book-intro"><p class="eyebrow">ICZSC · 独立连载</p><h1>'+title+'</h1><p class="book-note">《同路》专区 · 目录与阅读导航独立。</p>'
        body += ('<div class="book-actions"><a class="button" href="'+chapters[0]['url']+'">从第一章开始</a><a class="text-link" href="'+chapters[-1]['url']+'">阅读最新章 <span aria-hidden="true">→</span></a></div><p class="published">已更新 '+str(len(chapters))+' 章</p>') if chapters else '<p class="waiting">故事即将开始。</p>'
        body += '</section><section class="contents" aria-labelledby="contents-title"><div class="section-heading"><h2 id="contents-title">同路 · 章节目录</h2><a class="text-link" href="/tonglu/">作品首页</a></div>'+listing+'</section>'
        write(url, title, body)
    for i, c in enumerate(chapters):
        minutes = max(1, (len(re.findall(r'[\u3400-\u9fff]|[A-Za-z0-9]+', c['body']))+499)//500)
        body = '<article class="chapter"><header class="chapter-header"><a class="eyebrow" href="/tonglu/chapters/">同路 · 章节目录</a><h1>'+html.escape(c['title'])+'</h1><p class="chapter-meta"><time datetime="'+c['date'].isoformat()+'">'+c['date'].strftime('%Y年%m月%d日')+'</time><span>约 '+str(minutes)+' 分钟</span></p></header><div class="prose">'+paragraphs(c['body'])+'</div><nav class="chapter-nav" aria-label="章节翻页">'
        body += '<a href="'+chapters[i-1]['url']+'" rel="prev">← 上一章</a>' if i else '<span>已是第一章</span>'
        body += '<a href="/tonglu/chapters/">目录</a>'
        body += '<a href="'+chapters[i+1]['url']+'" rel="next">下一章 →</a>' if i+1 < len(chapters) else '<span>待续</span>'
        body += '</nav><a class="back-top" href="#main">回到页首 ↑</a></article>'
        write(c['url'], c['title'], body)
    print(f'Tonglu: {len(chapters)} independently released chapters')
    return ['/tonglu/', '/tonglu/chapters/']+[c['url'] for c in chapters]
