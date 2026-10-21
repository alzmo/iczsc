"""Limited offline renderer for this site's plain-paragraph chapter format.

Hugo remains the preferred build. This fallback has no third-party dependencies,
rejects unsupported chapter markup, and never includes future/draft chapters.
It does not evaluate arbitrary Hugo templates; keep layouts and this renderer in sync.
"""
import argparse
import html
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def metadata(path):
    raw = path.read_text(encoding='utf-8')
    assert raw.startswith('---\n'), f'YAML front matter required: {path}'
    head, body = raw[4:].split('\n---\n', 1)
    fields = {}
    for line in head.splitlines():
        if not line.strip() or line.lstrip().startswith('#'): continue
        key, value = line.split(':', 1)
        fields[key.strip()] = value.strip().strip('"\'')
    return fields, body

def paragraphs(text):
    blocks = []
    for block in re.split(r'\n\s*\n', text.strip()):
        block = block.strip()
        if not block: continue
        if block == '---': blocks.append('<hr>'); continue
        if block.startswith('## '): blocks.append('<h2>'+html.escape(block[3:])+'</h2>'); continue
        assert not re.search(r'(^[>#*`|]|!\[|\]\(|<[^>]+>)', block, re.M), 'Unsupported Markdown; use Hugo for this chapter'
        blocks.append('<p>'+html.escape(block.replace('\n', '\n'))+'</p>')
    return '\n'.join(blocks)

def render(title, url, body, home=False, template_path="layouts/_default/baseof.html"):
    template = (ROOT/template_path).read_text()
    template = template.replace('{{ if not .IsHome }}{{ .Title }} · {{ end }}', '' if home else html.escape(title)+' · ')
    template = template.replace('{{ .Permalink }}', 'https://iczsc.com'+url)
    template = template.replace('{{ block "main" . }}{{ end }}', body)
    assert '{{' not in template
    return template

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--now', help='Explicit ISO build time, for isolated tests only')
    parser.add_argument('--destination', default='docs')
    args = parser.parse_args()
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
    assert now.tzinfo, 'Build time must include timezone'
    out = (ROOT/args.destination).resolve()
    assert out != ROOT and (out == ROOT/'docs' or ROOT in out.parents), 'Unsafe destination'
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    for source in (ROOT/'static').iterdir():
        if source.is_file(): shutil.copy2(source, out/source.name)
    chapters=[]
    for source in (ROOT/'content/chapters').glob('*.md'):
        if source.name.startswith('_'): continue
        meta,body=metadata(source)
        date=datetime.fromisoformat(meta['date'])
        publish=datetime.fromisoformat(meta.get('publishDate',meta['date']))
        assert date.tzinfo and publish.tzinfo
        if meta.get('draft','false').lower() == 'true' or publish > now: continue
        slug=meta.get('slug', source.stem)
        assert re.fullmatch(r'[a-zA-Z0-9-]+',slug)
        chapters.append(dict(title=meta['title'], date=date, weight=int(meta['weight']), url='/chapters/'+slug+'/',body=body))
    chapters.sort(key=lambda c:c['weight'])
    assert len({c['weight'] for c in chapters})==len(chapters)
    def write(path,content):
        target=out/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content)
    listing='<ol class="chapter-list">'+''.join('<li><a href="'+c['url']+'"><span>'+html.escape(c['title'])+'</span><time datetime="'+c['date'].strftime('%Y-%m-%d')+'">'+c['date'].strftime('%Y.%m.%d')+'</time></a></li>' for c in chapters)+('' if chapters else '<li class="waiting">暂无已发布章节。</li>')+'</ol>'
    intro='<section class="book-intro"><p class="eyebrow">ICZSC · 长篇连载</p><h1>晚班地图师</h1><p class="book-note">留一盏灯，读一章故事。</p><p class="schedule">每晚更新 · 北京时间</p>'
    intro+=('<div class="book-actions"><a class="button" href="'+chapters[0]['url']+'">从第一章开始</a><a class="text-link" href="'+chapters[-1]['url']+'">阅读最新章 <span aria-hidden="true">→</span></a></div><p class="published">已更新 '+str(len(chapters))+' 章</p>') if chapters else '<p class="waiting">故事即将开始。</p>'
    intro+='</section><section class="contents" aria-labelledby="contents-title"><div class="section-heading"><h2 id="contents-title">章节目录</h2><span>按连载顺序</span></div>'+listing+'</section>'
    intro+='<section class="contents" aria-labelledby="other-books"><div class="section-heading"><h2 id="other-books">本站其他作品</h2></div><p><a class="text-link" href="/tonglu/">《同路》 · 进入独立专区 →</a></p></section>'
    write('index.html', render('', '/', intro,True))
    write('chapters/index.html', render('章节目录','/chapters/','<section class="contents full-contents"><p class="eyebrow">晚班地图师</p><h1>章节目录</h1><p class="book-note">每晚一章，慢慢读。</p>'+listing+'</section>'))
    for i,c in enumerate(chapters):
        # Match Hugo's hasCJKLanguage reading-time convention for Chinese prose.
        minutes=max(1,(len(re.findall(r'[\u3400-\u9fff]|[A-Za-z0-9]+',c['body']))+499)//500)
        body='<article class="chapter"><header class="chapter-header"><a class="eyebrow" href="/chapters/">晚班地图师 · 章节目录</a><h1>'+html.escape(c['title'])+'</h1><p class="chapter-meta"><time datetime="'+c['date'].isoformat()+'">'+c['date'].strftime('%Y年%m月%d日')+'</time><span>约 '+str(minutes)+' 分钟</span></p></header><div class="prose">'+paragraphs(c['body'])+'</div><nav class="chapter-nav" aria-label="章节翻页">'
        body+=('<a href="'+chapters[i-1]['url']+'" rel="prev">← 上一章</a>') if i else '<span>已是第一章</span>'
        body+='<a href="/chapters/">目录</a>'
        body+=('<a href="'+chapters[i+1]['url']+'" rel="next">下一章 →</a>') if i+1<len(chapters) else '<span>待续</span>'
        body+='</nav><a class="back-top" href="#main">回到页首 ↑</a></article>'
        write(c['url'].strip('/')+'/index.html',render(c['title'],c['url'],body))
    write('404.html',render('这一页不在这里','/404.html','<section class="not-found"><p class="eyebrow">404</p><h1>这一页不在这里</h1><p>旧页面已收起，故事从首页开始。</p><a class="button" href="/">返回首页</a></section>'))
    from build_tonglu import build_tonglu
    tonglu_urls=build_tonglu(out,now)
    urls=['/','/chapters/']+[c['url'] for c in chapters]+tonglu_urls
    write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://iczsc.com'+u+'</loc></url>' for u in urls)+'</urlset>\n')
    print(f'Limited Python render: {len(chapters)} released chapters; output {out.name}; cutoff {now.isoformat()}')

if __name__=='__main__':main()
