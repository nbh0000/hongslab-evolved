# -*- coding: utf-8 -*-
"""랜딩 원페이지(_landing_backup.html)를 메뉴별 개별 페이지로 분리하는 빌드 스크립트."""
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = open("_landing_backup.html", encoding="utf-8").read()
css = src[src.find("<style>") + 7:src.find("</style>")]
js = src[src.rfind("<script>") + 8:src.rfind("</script>")]
land = re.search(r"const LAND_B64='([^']+)'", js).group(1)

def block(start, end, s=src):
    i = s.find(start); j = s.find(end, i) + len(end)
    assert i >= 0 and j > i, start
    return s[i:j]

hero = block('<section class="hero"', '</section>')
secs = {k: block(f'<section class="section" id="{k}"', '</section>') for k in
        ['portfolio', 'effect', 'pricing', 'maintenance', 'estimate', 'process', 'faq', 'contact']}
marquee = block('<div class="marquee"', '</div></div>')
header = block('<header id="header">', '</aside>')
footer = block('<footer>', '</footer>')
mbar = block('<div class="mobile-bar">', '</div>')
modal = block('<div class="preview-modal"', 'alt="포트폴리오 확대 이미지"></div></div>')

PAGES = [('index', '홈', 'index.html'), ('portfolio', '제작 사례', 'portfolio.html'), ('pricing', '제작 요금', 'pricing.html'),
         ('estimate', '간단 견적', 'estimate.html'), ('process', '제작 과정', 'process.html'), ('faq', '자주 묻는 질문', 'faq.html'),
         ('contact', '상담하기', 'contact.html')]
hmap = {'#top': 'index.html', '#portfolio': 'portfolio.html', '#pricing': 'pricing.html', '#estimate': 'estimate.html',
        '#process': 'process.html', '#faq': 'faq.html', '#contact': 'contact.html'}

def links(s):
    for k, v in hmap.items():
        s = s.replace(f'href="{k}"', f'href="{v}"')
    return s

for k in secs:
    secs[k] = links(secs[k])
secs['pricing'] = re.sub(r'data-plan="(\w+)" href="estimate.html"', r'data-plan="\1" href="estimate.html?plan=\1"', secs['pricing'])
hero, header, footer, mbar = links(hero), links(header), links(footer), links(mbar)
for key, label, fn in PAGES[1:]:
    header = header.replace(f'<a href="{fn}">{label}</a>', f'<a href="{fn}" data-page="{key}">{label}</a>')

css = css.replace('.section+.section{padding-top:40px}',
                  '.section+.section{padding-top:40px}\nmain>.section:first-child{padding-top:170px}')
open("site.css", "w", encoding="utf-8", newline="\n").write(css.strip() + "\n")

site_js = open("site.src.js", encoding="utf-8").read().replace('__LAND__', land)
open("site.js", "w", encoding="utf-8", newline="\n").write(site_js)

HEAD = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="홍스랩 | 소상공인 홈페이지 제작 159,000원부터. 제작 사례, 간단 견적, 카카오톡 상담.">
<title>{title}</title>
<link href="fonts.css" rel="stylesheet">
<link href="site.css" rel="stylesheet">
</head>
<body data-theme="{theme}" data-page="{key}">
<div class="grid-bg"></div>
<div class="cursor" id="cursor"></div>
'''

def page(key, title, theme, content):
    return (HEAD.format(title=title, theme=theme, key=key) + header + '\n\n<main id="top">\n' + content +
            '\n</main>\n\n' + footer + '\n\n' + mbar + '\n' + modal + '\n<script src="site.js"></script>\n</body>\n</html>\n')

T = '홍스랩 | 소상공인 홈페이지 제작 159,000원부터'
out = {
    'index.html': page('index', T, 'dark', hero + '\n\n' + secs['effect'] + '\n\n' + marquee),
    'portfolio.html': page('portfolio', '제작 사례 | 홍스랩', 'dark', secs['portfolio']),
    'pricing.html': page('pricing', '제작 요금 | 홍스랩', 'light', secs['pricing'] + '\n\n' + secs['maintenance']),
    'estimate.html': page('estimate', '간단 견적 | 홍스랩', 'dark', secs['estimate']),
    'process.html': page('process', '제작 과정 | 홍스랩', 'dark', secs['process']),
    'faq.html': page('faq', '자주 묻는 질문 | 홍스랩', 'dark', secs['faq']),
    'contact.html': page('contact', '상담하기 | 홍스랩', 'dark', secs['contact']),
}
for fn, html in out.items():
    open(fn, "w", encoding="utf-8", newline="\n").write(html)
print(sorted(out), "| leftover # links:", [fn for fn, h in out.items() if re.search(r'href="#', h)])
