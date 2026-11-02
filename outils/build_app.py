"""Construit l'appli « Atelier d'harmonie » (app/) : une seule page installable (PWA), qui marche hors connexion.

    python3 outils/build_app.py

Onglets : Cours, Cahier d'exercices, Chiffrer, Chasse aux fautes, Cadences à l'oreille, Quiz.
Les images et les sons de secours sont pris dans cours/ et cahier/ ; les sons de la banque
General MIDI viennent de https://gleitz.github.io/midi-js-soundfonts/ et sont gardés en cache.
"""
import glob, hashlib, json, os, re, sys
import markdown

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.normpath(os.path.join(ICI, '..'))
APP = os.path.join(RACINE, 'app')
sys.path.insert(0, ICI)
from donnees_app import tout
from quiz_app import QUIZ



def charger(dossier):
    d = os.path.join(RACINE, dossier)
    sons, exos = {}, {}
    for f in sorted(glob.glob(os.path.join(d, 'audio', 'sons-*.json'))):
        sons.update(json.load(open(f)))
    for f in sorted(glob.glob(os.path.join(d, 'exercices-*.json'))):
        exos.update(json.load(open(f)))
    return sons, exos


def sections(dossier, pre, sons, exos):
    cahier = dossier == 'cahier'
    d = os.path.join(RACINE, dossier)

    def figure(m):
        alt, nom = m.group(1), m.group(2)
        img = os.path.join(d, 'images', nom + '.png')
        src = f'../{dossier}/images/{nom}.png'
        mp3 = os.path.join(d, 'audio', nom + '.mp3')
        secours = f'../{dossier}/audio/{nom}.mp3' if os.path.exists(mp3) else ''
        lecteur = ''
        if nom in sons:
            lecteur = (f'<div class="lecteur"><button class="jouer" data-ex="{nom}" data-mp3="{secours}">▶ Écouter</button>'
                       f'<a class="midi" href="../{dossier}/audio/{nom}.mid" download>MIDI</a></div>')
        w = int.from_bytes(open(img, 'rb').read()[16:20], 'big') // 2
        fig = f'<figure><img alt="{alt}" src="{src}" width="{w}" loading="lazy">{lecteur}</figure>'
        if cahier:
            if nom in exos:
                return f'<div class="atelier guide" id="at-{nom}" data-exo="{nom}"></div>'
            if nom.endswith('-c'):
                return f'<details class="corrige"><summary>Voir le corrigé</summary>{fig}</details>'
        at = ''
        if nom in exos:
            if exos[nom].get('guide'):
                at = f'<div class="atelier guide" id="at-{nom}" data-exo="{nom}"></div>'
            else:
                at = (f'<div class="ouvrir"><button class="faire" data-exo="{nom}">✏️ Faire l\'exercice ici</button></div>'
                      f'<div class="atelier" id="at-{nom}" hidden></div>')
        return fig + at

    out = []
    for f in sorted(glob.glob(os.path.join(d, '[0-9][0-9]-*.md'))):
        num = os.path.basename(f)[:2]
        s = open(f).read()
        s = re.sub(r'^\[.*\]\(.*\)\s*$', '', s, flags=re.M)
        s = re.sub(r'^🔊 .*$', '', s, flags=re.M)
        s = re.sub(r'\n---\s*\n', '\n', s)
        titre = re.search(r'^## (.*)$', s, flags=re.M).group(1)
        s = re.sub(r'!\[([^\]]*)\]\(images/([a-z0-9-]+)\.png\)', lambda m: '\n\n@@FIG@@' + m.group(0) + '@@\n\n', s)
        html = markdown.markdown(s, extensions=['tables'])
        html = re.sub(r'<p>@@FIG@@<img alt="([^"]*)" src="images/([a-z0-9-]+)\.png" />@@</p>', figure, html)
        html = re.sub(r'href="\.\./cours/(\d\d)-[^"]+\.md"', lambda m: f'href="#co-{m.group(1)}"', html)
        html = re.sub(r'href="(\d\d)-[^"]+\.md"', lambda m: f'href="#{pre}-{m.group(1)}"', html)
        html = html.replace('href="../README.md#sommaire"', f'href="#{pre}-{num}"').replace('href="README.md"', f'href="#{pre}-{num}"')
        html = html.replace('Dans la version web (<code>cahier.html</code>), chaque exercice se fait', 'Ici, chaque exercice se fait')
        html = html.replace('Dans la version web (<code>cahier.html</code>), on écrit', 'Ici, on écrit')
        html = html.replace(' Sur papier, recopie l\'énoncé et réalise-le au crayon.', '')
        ids = re.findall(r'data-exo="([^"]+)"', html)
        out.append({'id': f'{pre}-{num}', 'titre': titre, 'html': html, 'exos': ids})
    return out


def extraire(src, debut, fin):
    i = src.index(debut)
    return src[i:src.index(fin, i)]


def main():
    os.makedirs(APP, exist_ok=True)
    sons_co, exos_co = charger('cours')
    sons_ca, exos_ca = charger('cahier')
    co = sections('cours', 'co', sons_co, exos_co)
    ca = sections('cahier', 'ca', sons_ca, exos_ca)
    sons = {**sons_co, **sons_ca}
    exos = {**exos_co, **exos_ca}
    data = tout()
    quiz = [{'c': c, 'q': q, 'r': r, 'x': x} for c, q, r, x in QUIZ]

    site = open(os.path.join(ICI, 'build_site.py')).read()
    css_atelier = extraire(site, '.ouvrir{', '</style>')
    lecteur = extraire(site, "const BANQUE", "function jouer(b)")
    verifjs = open(os.path.join(ICI, 'verif.js')).read().replace("if (typeof module !== 'undefined') module.exports = HV;", '')
    atelierjs = open(os.path.join(ICI, 'atelier.js')).read()
    glyphs = json.load(open(os.path.join(ICI, 'glyphs.json')))

    def corps(liste):
        return '\n'.join(f'<section class="chap" id="{s["id"]}" hidden>{s["html"]}</section>' for s in liste)

    page = open(os.path.join(ICI, 'app_modele.html')).read()
    rempl = {
        '@@CSSATELIER@@': css_atelier,
        '@@COURS@@': corps(co), '@@CAHIER@@': corps(ca),
        '@@CHAPS@@': json.dumps({'co': [[s['id'], s['titre'], s['exos']] for s in co],
                                 'ca': [[s['id'], s['titre'], s['exos']] for s in ca]}, ensure_ascii=False),
        '@@SONS@@': json.dumps(sons), '@@EXOS@@': json.dumps(exos, ensure_ascii=False),
        '@@DATA@@': json.dumps(data, ensure_ascii=False), '@@QUIZ@@': json.dumps(quiz, ensure_ascii=False),
        '@@GLYPH@@': json.dumps(glyphs), '@@LECTEUR@@': lecteur, '@@VERIFJS@@': verifjs, '@@ATELIERJS@@': atelierjs,
    }
    for k, v in rempl.items():
        page = page.replace(k, v)
    open(os.path.join(APP, 'index.html'), 'w').write(page)

    # service worker : l'appli et toutes les images en cache dès l'installation
    images = sorted(f'../{d}/images/' + os.path.basename(p) for d in ('cours', 'cahier')
                    for p in glob.glob(os.path.join(RACINE, d, 'images', '*.png')))
    version = hashlib.sha1(page.encode()).hexdigest()[:10]   # nouvelle version de l'appli -> nouveau cache
    sw = open(os.path.join(ICI, 'app_sw.js')).read().replace('@@VERSION@@', version).replace('@@IMAGES@@', json.dumps(images))
    open(os.path.join(APP, 'sw.js'), 'w').write(sw)
    json.dump({
        'name': "Atelier d'harmonie", 'short_name': 'Harmonie',
        'description': "Cours d'écriture et d'harmonie à 4 voix : cours, cahier d'exercices sur la portée, chiffrage, chasse aux fautes, cadences à l'oreille, quiz.",
        'lang': 'fr', 'start_url': './index.html', 'scope': './', 'display': 'standalone',
        'background_color': '#f4f6f8', 'theme_color': '#1f4e8c',
        'icons': [{'src': 'icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any maskable'},
                  {'src': 'icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'}],
    }, open(os.path.join(APP, 'manifest.webmanifest'), 'w'), ensure_ascii=False, indent=2)
    print('écrit : app/index.html', f'({len(page) // 1024} Ko),', len(images), 'images en cache,',
          len(data['accords']), 'accords,', len(data['fautes']), 'fautes,', len(data['cadences']), 'cadences,', len(quiz), 'questions')


if __name__ == '__main__':
    main()
