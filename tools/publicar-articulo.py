# -*- coding: utf-8 -*-
"""Turn one article, written as a JSON file, into the pages the site publishes.

WHY THIS EXISTS

The site is served exactly as it sits in this repository - there is no build
step. For an article to have its own address and be indexed by Google, its HTML
has to exist as a file. Writing that HTML by hand for every article would mean
re-deciding the canonical, the hreflang set, the Open Graph tags, the
breadcrumb, the structured data and the sitemap entry every single time, and
getting one of them wrong every so often.

So the article is written as content - a title, some sections, some questions -
and this script produces the pages. Everything the rest of the site already got
right is applied automatically and identically.

HOW IT WORKS

The skeleton is cloned from a page that already exists and is already correct,
rather than written from scratch, so the header, the footer, the menu, the
consent banner and every stylesheet stay in step with the rest of the site
forever. Only the parts that belong to this article are replaced.

USAGE

    python tools/publicar-articulo.py articulos/mi-articulo.json

Then check what it produced before publishing anything:

    python tools/publicar-articulo.py --comprobar
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BASE = 'https://marescolanofisioterapia.com'
SKELETON = 'tratamientos/puncion-seca.html'      # an article-shaped page, level 1
LANGS = ('es', 'va', 'en')
HTML_LANG = {'es': 'es', 'va': 'ca-ES-valencia', 'en': 'en'}
HREFLANG = {'es': 'es-ES', 'va': 'ca-ES', 'en': 'en'}
OG_LOCALE = {'es': 'es_ES', 'va': 'ca_ES', 'en': 'en_GB'}
PREFIX = {'es': '', 'va': '/va', 'en': '/en'}
BLOG = {'es': 'Blog', 'va': 'Blog', 'en': 'Blog'}
HOME = {'es': 'Inicio', 'va': 'Inici', 'en': 'Home'}
CRUMB_LABEL = {'es': 'Ruta de navegación', 'va': 'Ruta de navegació', 'en': 'Breadcrumb'}
SITE_NAME = 'Clínica de Fisioterapia Mar Escolano'
AUTHOR = 'Mar Escolano Morell'
CLINIC_ID = BASE + '/#clinica'

H2 = 'alt-font text-extra-dark-gray font-weight-600 mef-size-h6 margin-20px-bottom'
H3 = 'alt-font text-extra-dark-gray font-weight-600 mef-size-faq margin-10px-bottom'
COL = ('col-12 col-xl-8 col-lg-6 col-sm-8 margin-one-bottom '
       'md-margin-40px-bottom sm-margin-30px-bottom text-left')

READ = {'es': 'min de lectura', 'va': 'min de lectura', 'en': 'min read'}
BY = {'es': 'Por', 'va': 'Per', 'en': 'By'}
BACK = {'es': 'Ver todos los artículos', 'va': 'Veure tots els articles',
        'en': 'See all articles'}
CTA = {'es': 'Coger cita', 'va': 'Demanar cita', 'en': 'Book an appointment'}
# the small line above the title, inherited from the skeleton page otherwise
SUBTITLE = {'es': 'Desde la consulta', 'va': 'Des de la consulta',
            'en': 'From the treatment room'}
MONTH = {
    'es': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
           'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'],
    'va': ['gener', 'febrer', 'març', 'abril', 'maig', 'juny', 'juliol',
           'agost', 'setembre', 'octubre', 'novembre', 'desembre'],
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July',
           'August', 'September', 'October', 'November', 'December'],
}


def esc(t):
    """Escape for text content. The apostrophe is left alone on purpose: inside
    text it needs no escaping, and escaping it makes the visible words differ
    from the ones declared in the structured data."""
    return html.escape(t, quote=False)


def att(t):
    return html.escape(t, quote=True)


def path_of(slug, lang):
    return ('%s/blog/%s.html' % (PREFIX[lang], slug)).lstrip('/')


def url_of(slug, lang):
    return '%s%s/blog/%s' % (BASE, PREFIX[lang], slug)


def index_path(lang):
    return ('%s/blog.html' % PREFIX[lang]).lstrip('/')


def index_url(lang):
    return '%s%s/blog' % (BASE, PREFIX[lang])


def pretty_date(iso, lang):
    y, m, d = iso.split('-')
    return '%d de %s de %s' % (int(d), MONTH[lang][int(m) - 1], y) if lang != 'en' \
        else '%d %s %s' % (int(d), MONTH['en'][int(m) - 1], y)


def read_minutes(body):
    words = sum(len(' '.join(p).split()) for _, p in body)
    return max(1, round(words / 200))


# --------------------------------------------------------------- the skeleton
def skeleton(lang):
    """A correct page of the site, with everything article-specific stripped out.

    Cloned rather than written so that a future change to the header, the menu
    or the consent banner reaches new articles without anyone remembering to
    copy it here."""
    src = SKELETON if lang == 'es' else '%s/%s' % (lang, SKELETON)
    s = open(src, encoding='utf-8', errors='ignore').read()

    # every structured-data block belongs to the treatment, not to an article
    s = re.sub(r'[ \t]*<!--[^\n]*-->\n(?=[ \t]*<script type="application/ld\+json">)',
               '', s)
    s = re.sub(r'[ \t]*<script type="application/ld\+json">.*?</script>\n', '', s, flags=re.S)
    return s


def head_fields(s, *, lang, slug, title, desc, image):
    """Point every declaration in the head at this article."""
    alts = '\n'.join(
        '        <link rel="alternate" hreflang="%s" href="%s" />'
        % (HREFLANG[l], url_of(slug, l)) for l in LANGS)
    alts += ('\n        <link rel="alternate" hreflang="x-default" href="%s" />'
             % url_of(slug, 'es'))

    s = re.sub(r'<html class="no-js" lang="[^"]*">',
               '<html class="no-js" lang="%s">' % HTML_LANG[lang], s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">',
               '<link rel="canonical" href="%s">' % url_of(slug, lang), s, count=1)
    s = re.sub(r'([ \t]*<link rel="alternate" hreflang="[^"]*" href="[^"]*" />\n)+',
               alts + '\n', s, count=1)
    s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % att(title), s, flags=re.S, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*"',
               '<meta name="description" content="%s"' % att(desc), s, count=1)
    s = re.sub(r'<meta property="og:locale" content="[^"]*">',
               '<meta property="og:locale" content="%s">' % OG_LOCALE[lang], s, count=1)
    s = re.sub(r'<meta property="og:type" content="[^"]*">',
               '<meta property="og:type" content="article">', s, count=1)
    s = re.sub(r'<meta property="og:title" content="[^"]*">',
               '<meta property="og:title" content="%s">' % att(title), s, count=1)
    s = re.sub(r'<meta property="og:description" content="[^"]*">',
               '<meta property="og:description" content="%s">' % att(desc), s, count=1)
    s = re.sub(r'<meta property="og:url" content="[^"]*">',
               '<meta property="og:url" content="%s">' % url_of(slug, lang), s, count=1)
    s = re.sub(r'<meta property="og:image" content="[^"]*">',
               '<meta property="og:image" content="%s%s">' % (BASE, image), s, count=1)
    # the language switcher must point at this article, not at the skeleton's page
    for l in LANGS:
        s = re.sub(r'href="%s/%s"' % (PREFIX[l], re.escape(SKELETON)),
                   'href="%s"' % ('%s/blog/%s.html' % (PREFIX[l], slug)), s)
        s = s.replace('/%s/%s' % (l, SKELETON) if l != 'es' else '/' + SKELETON,
                      '%s/blog/%s.html' % (PREFIX[l], slug))
    return s


def jsonld(post, lang):
    """BlogPosting, tied to the clinic and signed by a named author. On health
    content an anonymous article is worth markedly less to a search engine, and
    to a reader."""
    d = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post[lang]['title'],
        "description": post[lang]['description'],
        "inLanguage": HTML_LANG[lang],
        "datePublished": post['date'],
        "dateModified": post.get('updated', post['date']),
        "mainEntityOfPage": {"@type": "WebPage", "@id": url_of(post['slug'], lang)},
        "url": url_of(post['slug'], lang),
        "image": BASE + post['image'],
        "author": {"@type": "Person", "name": AUTHOR,
                   "jobTitle": "Fisioterapeuta", "url": BASE + PREFIX[lang] + '/conocenos'},
        "publisher": {"@id": CLINIC_ID},
        "isPartOf": {"@type": "Blog", "@id": index_url(lang)},
    }
    return d


def faq_jsonld(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in pairs]}


def crumb_jsonld(post, lang):
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": HOME[lang],
             "item": BASE + PREFIX[lang] + '/'},
            {"@type": "ListItem", "position": 2, "name": BLOG[lang],
             "item": index_url(lang)},
            {"@type": "ListItem", "position": 3, "name": post[lang]['h1'],
             "item": url_of(post['slug'], lang)},
        ]}


def crumb_html(lang, name):
    sep = '<li style="display:inline;margin:0 7px;color:#fff" aria-hidden="true">&rsaquo;</li>'
    return (
        '\n                        <nav aria-label="%s" class="d-block alt-font margin-10px-top"'
        ' style="font-size:13px;line-height:20px">\n'
        '                            <ol style="list-style:none;margin:0;display:inline-block;'
        'padding:5px 14px;background:rgba(0,0,0,.4);border-radius:14px">\n'
        '                                <li style="display:inline"><a style="color:#fff" href="%s/">%s</a></li>\n'
        '                                %s\n'
        '                                <li style="display:inline"><a style="color:#fff" href="%s/blog">%s</a></li>\n'
        '                                %s\n'
        '                                <li style="display:inline;color:#fff" aria-current="page">%s</li>\n'
        '                            </ol>\n'
        '                        </nav>'
        % (CRUMB_LABEL[lang], PREFIX[lang] or '', HOME[lang], sep,
           PREFIX[lang], BLOG[lang], sep, esc(name)))


def body_html(post, lang):
    p = post[lang]
    out = []
    out.append('        <div class="row justify-content-center">')
    out.append('            <div class="%s">' % COL)
    out.append('                <p class="text-medium-gray" style="font-size:14px">%s %s &middot; %s &middot; %d %s</p>'
               % (BY[lang], esc(AUTHOR), pretty_date(post['date'], lang),
                  read_minutes(p['body']), READ[lang]))
    out.append('                <p align="justify"><strong>%s</strong></p>' % esc(p['lead']))
    out.append('            </div>')
    out.append('        </div>')

    out.append('        <div class="row justify-content-center">')
    out.append('            <div class="col-12 col-xl-10 col-lg-6 col-sm-8 margin-five-bottom '
               'md-margin-40px-bottom sm-margin-30px-bottom text-center">')
    out.append('                <p><img src="%s" alt="%s" width="%d" height="%d" '
               'loading="lazy" decoding="async"></p>'
               % (post['image'], att(post['image_alt'][lang]),
                  post['image_size'][0], post['image_size'][1]))
    out.append('            </div>')
    out.append('        </div>')

    for h, paras in p['body']:
        out.append('        <div class="row justify-content-center">')
        out.append('            <div class="%s">' % COL)
        out.append('                <h2 class="%s">%s</h2>' % (H2, esc(h)))
        for t in paras:
            out.append('                <p align="justify">%s</p>' % esc(t))
        out.append('            </div>')
        out.append('        </div>')

    if p.get('faq'):
        out.append('        <div class="row justify-content-center">')
        out.append('            <div class="%s">' % COL)
        out.append('                <h2 class="%s">%s</h2>'
                   % (H2, {'es': 'Preguntas frecuentes', 'va': 'Preguntes freqüents',
                           'en': 'Frequently asked questions'}[lang]))
        for q, a in p['faq']:
            out.append('                <h3 class="%s">%s</h3>' % (H3, esc(q)))
            out.append('                <p align="justify">%s</p>' % esc(a))
        out.append('            </div>')
        out.append('        </div>')

    out.append('        <div class="row justify-content-center">')
    out.append('            <div class="col-12 col-xl-10 col-lg-6 col-sm-8 margin-one-bottom '
               'md-margin-40px-bottom sm-margin-30px-bottom text-center">')
    out.append('                <p><a class="btn btn-large btn-dark-gray btn-rounded '
               'lg-margin-15px-bottom d-table d-lg-inline-block md-margin-lr-auto" '
               'href="%s/contacto">%s</a></p>' % (PREFIX[lang] or '', CTA[lang]))
    out.append('                <p><a class="btn btn-extra-large btn-transparent-dark-gray '
               'btn-rounded lg-margin-15px-bottom d-table d-lg-inline-block md-margin-lr-auto" '
               'href="%s/blog">%s</a></p>' % (PREFIX[lang] or '', BACK[lang]))
    out.append('            </div>')
    out.append('        </div>')
    return '\n'.join(out)


def build_article(post, lang):
    p = post[lang]
    s = skeleton(lang)
    s = head_fields(s, lang=lang, slug=post['slug'], title=p['title'],
                    desc=p['description'], image=post['image'])

    blocks = [jsonld(post, lang), crumb_jsonld(post, lang)]
    if p.get('faq'):
        blocks.append(faq_jsonld(p['faq']))
    ld = '\n'.join(
        '        <script type="application/ld+json">\n%s\n        </script>'
        % json.dumps(b, ensure_ascii=False, indent=8) for b in blocks)
    s = s.replace('    </head>', ld + '\n    </head>', 1)

    # the title block: h1 and breadcrumb
    # Replace the whole contents of the h1, not just a <strong> inside it: a
    # skeleton page may read "Mar Escolano <strong>fisioterapia</strong>", with
    # text before the tag, and a narrower pattern silently matches nothing and
    # leaves the borrowed page's own title in place.
    s = re.sub(r'(<h1[^>]*>).*?</h1>.*?(?=\n\s*<!-- end page title -->)',
               lambda m: m.group(1) + '<strong>' + esc(p['h1']) + '</strong></h1>'
               + crumb_html(lang, p['h1']), s, flags=re.S, count=1)
    s = re.sub(r'(<span[^>]*margin-5px-bottom">)[^<]*(</span>)',
               lambda m: m.group(1) + SUBTITLE[lang] + m.group(2), s, count=1)

    # the article itself replaces the treatment's content section
    start = s.find('<!-- start filter content -->')
    end = s.find('<!-- end filter content -->')
    if start < 0 or end < 0:
        raise SystemExit('no encuentro el bloque de contenido en el esqueleto')
    s = (s[:start] + '<!-- start article -->\n        <div class="container">\n'
         + body_html(post, lang)
         + '\n        </div>\n        <!-- end article -->\n        '
         + s[end + len('<!-- end filter content -->'):])
    return s


# ------------------------------------------------------------------ the index
def build_index(posts, lang):
    """The list of articles. Regenerated whole every time, so it can never fall
    out of step with what actually exists on disk."""
    src = 'conocenos.html' if lang == 'es' else '%s/conocenos.html' % lang
    s = open(src, encoding='utf-8', errors='ignore').read()
    s = re.sub(r'[ \t]*<!--[^\n]*-->\n(?=[ \t]*<script type="application/ld\+json">)', '', s)
    s = re.sub(r'[ \t]*<script type="application/ld\+json">.*?</script>\n', '', s, flags=re.S)

    title = {'es': 'Blog de fisioterapia | Clinica Mar Escolano en Gandia',
             'va': 'Blog de fisioterapia | Clinica Mar Escolano a Gandia',
             'en': 'Physiotherapy blog | Mar Escolano Clinic in Gandia'}[lang]
    desc = {'es': 'Articulos sobre dolor, lesiones y recuperacion escritos desde la consulta '
                  'de una clinica de fisioterapia en Gandia.',
            'va': "Articles sobre dolor, lesions i recuperacio escrits des de la consulta d'una "
                  'clinica de fisioterapia a Gandia.',
            'en': 'Articles on pain, injury and recovery written from the treatment room of a '
                  'physiotherapy clinic in Gandia.'}[lang]
    lead = {'es': 'Lo que preguntan los pacientes en consulta, explicado con calma.',
            'va': 'El que pregunten els pacients en consulta, explicat amb calma.',
            'en': 'What patients ask in the treatment room, explained without the rush.'}[lang]
    empty = {'es': 'Todavia no hay articulos publicados.',
             'va': 'Encara no hi ha articles publicats.',
             'en': 'No articles published yet.'}[lang]
    readmore = {'es': 'Leer el articulo', 'va': "Llegir l'article",
                'en': 'Read the article'}[lang]

    alts = '\n'.join('        <link rel="alternate" hreflang="%s" href="%s" />'
                     % (HREFLANG[l], index_url(l)) for l in LANGS)
    alts += '\n        <link rel="alternate" hreflang="x-default" href="%s" />' % index_url('es')

    s = re.sub(r'<html class="no-js" lang="[^"]*">',
               '<html class="no-js" lang="%s">' % HTML_LANG[lang], s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*">',
               '<link rel="canonical" href="%s">' % index_url(lang), s, count=1)
    s = re.sub(r'([ \t]*<link rel="alternate" hreflang="[^"]*" href="[^"]*" />\n)+',
               alts + '\n', s, count=1)
    s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % att(title), s, flags=re.S, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*"',
               '<meta name="description" content="%s"' % att(desc), s, count=1)
    for k, v in (('og:locale', OG_LOCALE[lang]), ('og:title', title),
                 ('og:description', desc), ('og:url', index_url(lang))):
        s = re.sub(r'<meta property="%s" content="[^"]*">' % k,
                   '<meta property="%s" content="%s">' % (k, att(v)), s, count=1)
    for l in LANGS:
        s = s.replace('%s/conocenos.html' % PREFIX[l], '%s/blog.html' % PREFIX[l])

    ld = {"@context": "https://schema.org", "@type": "Blog", "@id": index_url(lang),
          "name": title, "description": desc, "inLanguage": HTML_LANG[lang],
          "url": index_url(lang), "publisher": {"@id": CLINIC_ID},
          "blogPost": [{"@type": "BlogPosting", "headline": p[lang]['title'],
                        "url": url_of(p['slug'], lang), "datePublished": p['date']}
                       for p in posts]}
    s = s.replace('    </head>',
                  '        <script type="application/ld+json">\n%s\n        </script>\n    </head>'
                  % json.dumps(ld, ensure_ascii=False, indent=8), 1)

    s = re.sub(r'(<h1[^>]*>).*?</h1>',
               lambda m: m.group(1) + '<strong>Blog</strong></h1>', s, flags=re.S, count=1)
    s = re.sub(r'(<span[^>]*margin-5px-bottom">)[^<]*(</span>)',
               lambda m: m.group(1) + SUBTITLE[lang] + m.group(2), s, count=1)

    cards = []
    if not posts:
        cards.append('        <div class="row justify-content-center"><div class="%s">' % COL)
        cards.append('            <p align="justify">%s</p>' % esc(empty))
        cards.append('        </div></div>')
    for p in posts:
        a = p[lang]
        pre = PREFIX[lang] or ''
        cards.append('        <div class="row justify-content-center margin-40px-bottom">')
        cards.append('            <div class="col-12 col-xl-8 col-lg-6 col-sm-8 text-left">')
        cards.append('                <a href="%s/blog/%s.html" class="d-block margin-15px-bottom">'
                     % (pre, p['slug']))
        cards.append('                    <img src="%s" alt="%s" width="%d" height="%d" '
                     'loading="lazy" decoding="async" class="w-100 border-radius-6">'
                     % (p['image'], att(p['image_alt'][lang]),
                        p['image_size'][0], p['image_size'][1]))
        cards.append('                </a>')
        cards.append('                <p class="text-medium-gray mb-0" style="font-size:13px">%s</p>'
                     % pretty_date(p['date'], lang))
        cards.append('                <h2 class="%s"><a href="%s/blog/%s.html" '
                     'class="text-extra-dark-gray">%s</a></h2>'
                     % (H2, pre, p['slug'], esc(a['title'])))
        cards.append('                <p align="justify">%s</p>' % esc(a['description']))
        cards.append('                <p><a href="%s/blog/%s.html" class="alt-font '
                     'font-weight-600 text-extra-dark-gray">%s &rsaquo;</a></p>'
                     % (pre, p['slug'], readmore))
        cards.append('            </div>')
        cards.append('        </div>')

    intro = ('        <div class="row justify-content-center">\n'
             '            <div class="%s">\n'
             '                <p align="justify"><strong>%s</strong></p>\n'
             '            </div>\n        </div>' % (COL, esc(lead)))

    start = s.find('<section', s.find('</h1>'))
    end = s.find('<footer')
    s = (s[:start] + '<!-- start blog index -->\n    <section class="padding-70px-top '
         'padding-50px-bottom">\n        <div class="container">\n' + intro + '\n'
         + '\n'.join(cards) + '\n        </div>\n    </section>\n    '
         '<!-- end blog index -->\n    ' + s[end:])
    return s


def update_nav():
    """Put Blog in the menu of every page, once."""
    SKIP = {'.git', 'revolution', '__MACOSX', 'node_modules', 'images', 'css', 'js',
            'fonts', 'tools', 'articulos', '.atl'}
    n = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            if not f.endswith('.html'):
                continue
            p = os.path.join(root, f).replace(os.sep, '/').lstrip('./')
            lang = 'va' if p.startswith('va/') else ('en' if p.startswith('en/') else 'es')
            raw = open(p, encoding='utf-8', newline='').read()
            # NOT '>Blog</a>': an article's breadcrumb contains that too, which
            # would make every article skip its own menu entry.
            if re.search(r'<li><a href="[^"]*blog\.html">Blog</a></li>', raw):
                continue
            nl = '\r\n' if '\r\n' in raw else '\n'
            s = raw.replace('\r\n', '\n')
            depth = p.count('/') - (0 if lang == 'es' else 1)
            rel = '../' * depth
            m = re.search(r'(<li><a href="[^"]*instalaciones\.html">[^<]*</a></li>)', s)
            if not m:
                continue
            s = s.replace(m.group(1), m.group(1)
                          + '<li><a href="%sblog.html">Blog</a></li>' % rel, 1)
            open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', nl))
            n += 1
    print('[nav] paginas con Blog en el menu: %d' % n)


def load_posts():
    out = []
    if os.path.isdir('articulos'):
        for f in sorted(os.listdir('articulos')):
            if f.endswith('.json'):
                out.append(json.load(open('articulos/' + f, encoding='utf-8')))
    out.sort(key=lambda p: p['date'], reverse=True)
    return out


def comprobar():
    """Refuse to be trusted without evidence. Checks what is on disk, not what
    the script believes it wrote."""
    posts = load_posts()
    bad = []
    print('articulos en articulos/*.json : %d' % len(posts))
    for p in posts:
        for lang in LANGS:
            fp = path_of(p['slug'], lang)
            if not os.path.exists(fp):
                bad.append('falta %s' % fp)
                continue
            s = open(fp, encoding='utf-8', errors='ignore').read()
            if 'canonical" href="%s"' % url_of(p['slug'], lang) not in s:
                bad.append('%s: canonical incorrecta' % fp)
            for l in LANGS:
                if url_of(p['slug'], l) not in s:
                    bad.append('%s: sin hreflang a %s' % (fp, l))
            body = s[s.find('<h1'):s.find('<footer')]
            seq = [int(x.group(1)) for x in re.finditer(r'<h([1-6])[^>]*>', body)]
            if seq.count(1) != 1:
                bad.append('%s: %d elementos h1' % (fp, seq.count(1)))
            for i in range(1, len(seq)):
                if seq[i] > seq[i - 1] + 1:
                    bad.append('%s: salto h%d->h%d' % (fp, seq[i - 1], seq[i]))
            for im in re.finditer(r'<img\b[^>]*>', s):
                if not re.search(r'\balt="', im.group(0)):
                    bad.append('%s: imagen sin alt' % fp)
                src = re.search(r'src="(/images/[^"?]+)', im.group(0))
                if src and not os.path.exists(src.group(1).lstrip('/')):
                    bad.append('%s: la imagen %s no existe' % (fp, src.group(1)))
            for b in re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
                                 s, re.S):
                try:
                    json.loads(b.group(1))
                except Exception as e:
                    bad.append('%s: JSON-LD invalido (%s)' % (fp, e))
            if not re.search(r'<li><a href="[^"]*blog\.html">Blog</a></li>', s):
                bad.append('%s: sin Blog en el menu' % fp)
    for lang in LANGS:
        ip = index_path(lang)
        if not os.path.exists(ip):
            bad.append('falta el indice %s' % ip)
            continue
        s = open(ip, encoding='utf-8', errors='ignore').read()
        for p in posts:
            if '/blog/%s.html' % p['slug'] not in s:
                bad.append('%s: no enlaza el articulo %s' % (ip, p['slug']))
    print('problemas: %d' % len(bad))
    for b in bad[:20]:
        print('   %s' % b)
    return len(bad) == 0


def main():
    if '--comprobar' in sys.argv:
        raise SystemExit(0 if comprobar() else 1)

    posts = load_posts()
    if len(sys.argv) > 1 and sys.argv[1].endswith('.json'):
        one = json.load(open(sys.argv[1], encoding='utf-8'))
        posts = [p for p in posts if p['slug'] != one['slug']] + [one]
        posts.sort(key=lambda p: p['date'], reverse=True)

    for lang in LANGS:
        d = os.path.dirname(path_of('x', lang))
        if d:
            os.makedirs(d, exist_ok=True)

    for p in posts:
        for lang in LANGS:
            open(path_of(p['slug'], lang), 'w', encoding='utf-8', newline='\n').write(
                build_article(p, lang))
        print('[articulo] %s' % p['slug'])

    for lang in LANGS:
        open(index_path(lang), 'w', encoding='utf-8', newline='\n').write(
            build_index(posts, lang))
    print('[indice] %d articulos listados' % len(posts))
    update_nav()
    print('')
    print('Ahora comprueba lo que ha salido, antes de publicar nada:')
    print('    python tools/publicar-articulo.py --comprobar')


if __name__ == '__main__':
    main()
