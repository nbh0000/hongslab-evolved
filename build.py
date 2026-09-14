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
_css = css.strip() + "\n"

site_js = open("site.src.js", encoding="utf-8").read().replace('__LAND__', land)
open("site.js", "w", encoding="utf-8", newline="\n").write(site_js)

STUDIO_CSS = """
/* ===== 히어로 배경 이미지 (index) ===== */
.hero:before{content:"";position:absolute;inset:0;z-index:0;background:url(studio-2560.jpg) 82% 45%/cover no-repeat;opacity:.42;transform:scale(1.04);animation:heroBg 2.4s var(--ease-out) forwards}
.hero:after{content:"";position:absolute;inset:0;z-index:0;background:radial-gradient(70% 60% at 50% 45%,rgba(23,23,23,.25),rgba(23,23,23,.9) 80%),linear-gradient(180deg,rgba(23,23,23,.65),transparent 28%,transparent 62%,#171717)}
.hero .wrap,.hero .hero-scroll{position:relative;z-index:1}
@keyframes heroBg{to{transform:none}}
@media(max-width:900px){.hero:before{background-image:url(studio-1600.jpg);background-position:62% 45%;opacity:.42}}
/* ===== 스튜디오 비주얼 (index) ===== */
.studio{padding-top:0}
.studio .frame{position:relative;margin-top:44px;border-radius:22px;overflow:hidden;border:1px solid var(--line-strong);background:#0f0f11;box-shadow:0 40px 120px rgba(168,20,90,.18),0 20px 60px rgba(0,0,0,.5)}
.studio .frame img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;transform:scale(1.02);transition:transform 1.6s var(--ease-out)}
.studio .frame.in img{transform:none}
.studio .frame:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(23,23,23,.28),transparent 40%,transparent 75%,rgba(23,23,23,.55));pointer-events:none}
.studio .tag{position:absolute;z-index:2;font-family:var(--font-mono);font-size:.62rem;letter-spacing:.28em;text-transform:uppercase;color:rgba(240,240,248,.82);display:inline-flex;align-items:center;gap:.7em;padding:8px 12px;border:1px solid rgba(255,255,255,.16);border-radius:999px;background:rgba(20,20,22,.55);backdrop-filter:blur(8px)}
.studio .tag b{width:6px;height:6px;border-radius:50%;background:var(--accent-2);box-shadow:0 0 12px var(--accent-2)}
.studio .tag.tl{top:22px;left:22px}
.studio .tag.br{right:22px;bottom:22px}
.studio .caption{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;margin-top:14px;font-family:var(--font-mono);font-size:.66rem;letter-spacing:.2em;text-transform:uppercase;color:var(--muted)}
@media(max-width:720px){.studio .frame{border-radius:14px}.studio .frame img{aspect-ratio:4/3}.studio .tag.br{display:none}.studio .caption{display:none}}
"""

STUDIO_HTML = """<section class="section studio" id="studio">
  <div class="wrap">
    <div class="reveal"><div class="eyebrow scramble">AI STUDIO · SEJONG</div><h2 class="title">아이디어 하나도<br>제대로 동작하는 제품으로<em>.</em></h2><p class="lead">Studio Genilo는 AI를 활용해 기획부터 화면 설계, 개발까지 한 번에 진행합니다. 정리된 구조와 또렷한 첫인상, 그 기준을 그대로 담았습니다.</p></div>
    <figure class="frame reveal">
      <span class="tag tl"><b></b>AI STUDIO GENILO · WEB APP</span>
      <img src="studio-1600.jpg" srcset="studio-1600.jpg 1600w, studio-2560.jpg 2560w" sizes="(max-width:1240px) 100vw, 1180px" width="2560" height="1429" alt="Studio Genilo 스튜디오 데스크. 모니터에 마젠타 파티클 지구본이 표시된 다크 모드 홈페이지 시안이 떠 있다." loading="lazy" decoding="async">
      <span class="tag br"><b></b>4K · 5504 × 3072</span>
    </figure>
    <div class="caption reveal"><span>AI-ASSISTED · PLAN TO DEPLOY</span><span>PC · MOBILE RESPONSIVE</span></div>
  </div>
</section>"""
open("site.css", "w", encoding="utf-8", newline="\n").write((_css + STUDIO_CSS).strip() + "\n")

HEAD = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Studio Genilo | AI로 만드는 웹 앱 제작 스튜디오. 랜딩 페이지부터 로그인·결제·관리자 기능이 있는 웹 앱까지 기획·디자인·개발을 한 번에.">
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

T = 'Studio Genilo | AI 웹 앱 제작 스튜디오'
out = {
    'index.html': page('index', T, 'dark', hero + '\n\n' + marquee),
    'portfolio.html': page('portfolio', '제작 사례 | Studio Genilo', 'dark', secs['portfolio']),
    'pricing.html': page('pricing', '제작 요금 | Studio Genilo', 'light', secs['pricing'] + '\n\n' + secs['maintenance']),
    'estimate.html': page('estimate', '간단 견적 | Studio Genilo', 'dark', secs['estimate']),
    'process.html': page('process', '제작 과정 | Studio Genilo', 'dark', secs['process']),
    'faq.html': page('faq', '자주 묻는 질문 | Studio Genilo', 'dark', secs['faq']),
    'contact.html': page('contact', '상담하기 | Studio Genilo', 'dark', secs['contact']),
}
for fn, html in out.items():
    open(fn, "w", encoding="utf-8", newline="\n").write(html)
print(sorted(out), "| leftover # links:", [fn for fn, h in out.items() if re.search(r'href="#', h)])
