"""Construit la version web du cours (index.html), avec un lecteur sous chaque exemple.

Usage :
  python3 outils/build_site.py                 -> index.html à la racine du dépôt (GitHub Pages)
  python3 outils/build_site.py --autonome F    -> un seul fichier F, images et sons de secours inclus

Le lecteur joue les notes de chaque exemple avec les sons de la banque General MIDI
FluidR3_GM (piano, chœur, orgue, cordes), chargés depuis
https://gleitz.github.io/midi-js-soundfonts/. Sans connexion, il se rabat sur le MP3
de l'exemple (cours/audio/).
"""
import base64, glob, json, os, re, sys
import markdown

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.normpath(os.path.join(ICI, '..'))
CAHIER = '--cahier' in sys.argv          # version web du cahier d'exercices
DOSSIER = 'cahier' if CAHIER else 'cours'
COURS = os.path.join(RACINE, DOSSIER)
autonome = '--autonome' in sys.argv
sortie = sys.argv[sys.argv.index('--autonome') + 1] if autonome else os.path.join(RACINE, 'cahier.html' if CAHIER else 'index.html')

sons = {}
for f in sorted(glob.glob(os.path.join(COURS, 'audio', 'sons-*.json'))):
    sons.update(json.load(open(f)))

exos = {}
for f in sorted(glob.glob(os.path.join(COURS, 'exercices-*.json'))):
    exos.update(json.load(open(f)))

chapitres = sorted(f for f in glob.glob(os.path.join(COURS, '[0-9][0-9]-*.md')))


def b64(chemin, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(chemin, 'rb').read()).decode()


def cid(nom):
    return 'ch-' + os.path.basename(nom)[:2]


def figure(m):
    alt, nom = m.group(1), m.group(2)
    img = os.path.join(COURS, 'images', nom + '.png')
    src = b64(img, 'image/png') if autonome else f'{DOSSIER}/images/{nom}.png'
    mp3 = os.path.join(COURS, 'audio', nom + '.mp3')
    secours = (b64(mp3, 'audio/mpeg') if autonome else f'{DOSSIER}/audio/{nom}.mp3') if os.path.exists(mp3) else ''
    lecteur = ''
    if nom in sons:
        lecteur = (f'<div class="lecteur"><button class="jouer" data-ex="{nom}" data-mp3="{secours}">▶ Écouter</button>'
                   f'<a class="midi" href="{DOSSIER}/audio/{nom}.mid" download>MIDI</a></div>')
        if autonome:
            lecteur = lecteur.replace(f'<a class="midi" href="{DOSSIER}/audio/{nom}.mid" download>MIDI</a>', '')
    w = int.from_bytes(open(img, 'rb').read()[16:20], 'big') // 2
    if CAHIER:
        if nom in exos:     # énoncé : directement la portée interactive
            return f'<div class="atelier guide" id="at-{nom}" data-exo="{nom}"></div>'
        if nom.endswith('-c'):   # corrigé : replié
            return f'<details class="corrige"><summary>Voir le corrigé</summary><figure><img alt="{alt}" src="{src}" width="{w}">{lecteur}</figure></details>'
    atelier = ''
    if nom in exos:
        if exos[nom].get('guide'):   # exercice guidé : ouvert d'emblée
            atelier = f'<div class="atelier guide" id="at-{nom}" data-exo="{nom}"></div>'
        else:
            atelier = (f'<div class="ouvrir"><button class="faire" data-exo="{nom}">✏️ Faire l\'exercice ici</button></div>'
                       f'<div class="atelier" id="at-{nom}" hidden></div>')
    return f'<figure><img alt="{alt}" src="{src}" width="{w}">{lecteur}</figure>{atelier}'


sections, sommaire = [], []
for f in chapitres:
    s = open(f).read()
    s = re.sub(r'^\[.*\]\(.*\)\s*$', '', s, flags=re.M)            # barres de navigation
    s = re.sub(r'^🔊 .*$', '', s, flags=re.M)                       # liens audio (remplacés par le lecteur)
    s = re.sub(r'\n---\s*\n', '\n', s)
    titre = re.search(r'^## (.*)$', s, flags=re.M).group(1)
    sommaire.append((cid(f), titre))
    s = re.sub(r'!\[([^\]]*)\]\(images/([a-z0-9-]+)\.png\)', lambda m: '\n\n@@FIG@@' + m.group(0) + '@@\n\n', s)
    html = markdown.markdown(s, extensions=['tables'])
    html = re.sub(r'<p>@@FIG@@<img alt="([^"]*)" src="images/([a-z0-9-]+)\.png" />@@</p>', figure, html)
    html = re.sub(r'href="(\d\d)-[^"]+\.md"', lambda m: f'href="#ch-{m.group(1)}"', html)
    html = html.replace('href="../README.md#sommaire"', 'href="#sommaire"').replace('href="README.md"', 'href="#sommaire"')
    html = re.sub(r'href="\.\./cours/(\d\d)-[^"]+\.md"', lambda m: f'href="index.html#ch-{m.group(1)}"', html)
    sections.append(f'<section id="{cid(f)}">{html}</section>')

parties = [] if CAHIER else [('01', 'Les bases du 4 voix'), ('06', 'Renversements et cadences'), ('13', 'Le choral'), ('18', 'Les accords de quatre sons'), ('24', 'Le style classique'), ('30', 'Le premier romantisme'), ('36', 'Le romantisme tardif')]
som = '<nav id="sommaire"><h2>Sommaire</h2>'
for i, (c, t) in enumerate(sommaire):
    for p, nomp in parties:
        if c == 'ch-' + p:
            som += f'<h3>{nomp}</h3>'
    som += f'<a href="#{c}">{t}</a>'
som += '</nav>'

page = '''<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITRE@@</title>
<style>
:root{--bleu:#1f4e8c;--gris:#666}
*{box-sizing:border-box}
body{font-family:Verdana,Geneva,"DejaVu Sans",sans-serif;margin:0;color:#222;line-height:1.6;background:#fafafa}
header{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid #ddd;padding:.6em 1em;display:flex;gap:1em;align-items:center;flex-wrap:wrap}
header h1{font-size:1.05em;margin:0;color:var(--bleu);flex:1;min-width:12em}
header label{font-size:.85em;color:var(--gris)}
select{font:inherit;font-size:.85em;padding:.2em .4em;border:1px solid #bbb;border-radius:6px;background:#fff}
main{max-width:880px;margin:0 auto;padding:1em 1.2em 4em;background:#fff}
nav#sommaire a{display:block;padding:.15em 0;color:var(--bleu);text-decoration:none}
nav#sommaire h3{margin:1em 0 .2em;font-size:1em}
section{border-top:3px solid var(--bleu);margin-top:2.5em;padding-top:.5em}
h2{color:var(--bleu)}
figure{margin:1.2em 0;text-align:left}
figure img{max-width:100%;display:block}
.lecteur{display:flex;gap:.6em;align-items:center;margin-top:.3em}
.jouer{font:inherit;font-size:.85em;padding:.25em .9em;border-radius:999px;border:1px solid var(--bleu);background:#fff;color:var(--bleu);cursor:pointer}
.jouer.actif{background:var(--bleu);color:#fff}
.midi{font-size:.75em;color:var(--gris)}
.autre{font-size:.85em;color:var(--bleu)}
details.corrige{margin:.2em 0 1.5em}
details.corrige summary{cursor:pointer;color:var(--bleu);font-size:.9em}
table{border-collapse:collapse;font-size:.92em}td,th{border:1px solid #ccc;padding:4px 8px}
code{background:#f0f0f0;padding:0 .3em;border-radius:4px}
#etat{font-size:.8em;color:var(--gris)}
.ouvrir{margin:-.4em 0 1em}
.faire{font:inherit;font-size:.85em;padding:.3em 1em;border-radius:999px;border:1px solid #1e7b34;background:#fff;color:#1e7b34;cursor:pointer}
.faire.on{background:#1e7b34;color:#fff}
.atelier{border:1px solid #d6dde6;border-radius:12px;padding:.8em;margin:0 0 1.5em;background:#fbfcfe}
.atelier .barre{display:flex;flex-wrap:wrap;gap:.4em;align-items:center;margin:.3em 0}
.atelier .lbl{font-size:.85em;color:var(--gris)}
.atelier .sep{width:.8em}
.atelier button{font:inherit;font-size:.85em;cursor:pointer;border-radius:8px;border:1px solid #bbb;background:#fff;padding:.25em .7em}
.atelier button.voix{border-color:var(--c);color:var(--c);font-weight:700}
.atelier button.voix.on{background:var(--c);color:#fff}
.atelier button.petit{min-width:2.2em;font-size:1em;padding:.1em .4em}
.atelier button.petit.large{font-size:.85em;padding:.2em .6em}
.atelier button.prim{background:var(--bleu);color:#fff;border-color:var(--bleu)}
.atelier button.actif{background:var(--bleu);color:#fff}
.atelier .portee{background:#fff;border-radius:8px;cursor:crosshair;outline:none;overflow-x:auto}
.atelier .portee:focus-visible{box-shadow:0 0 0 3px #8cb4ee}
.atelier .aide{font-size:.8em;color:var(--gris);margin:.3em 0}
.atelier .fb:empty{display:none}
.atelier .fb{border-radius:8px;padding:.5em .9em;margin-top:.5em;font-size:.9em}
.atelier .fb h4{margin:.2em 0}
.atelier .fb.good{background:#e8f5ec;border:1px solid #1e7b34}
.atelier .fb.bad{background:#fbeceb;border:1px solid #c0392b}
.atelier .fb.info{background:#e3ecf7;border:1px solid #1f4e8c}
.atelier .fb ul{margin:.3em 0;padding-left:1.2em}
.atelier .fb li.cons{color:#8a5a00}
.atelier .fb li.cons::marker{content:'💡 '}
.atelier .titre{margin:.2em 0 .5em;font-size:.92em;background:#eef3fa;border-left:4px solid var(--bleu);padding:.4em .7em;border-radius:4px}
.atelier.guide{border-color:#1f4e8c}
</style></head><body>
<header><h1>@@TITRE@@</h1><a class="autre" href="@@AUTRE@@">@@AUTRETXT@@</a><a class="autre" href="app/">📱 L'appli</a>
<label>Son <select id="son"><option value="auto">Automatique</option><option value="piano">Piano</option><option value="choeur">Chœur</option><option value="orgue">Orgue</option><option value="cordes">Quatuor à cordes</option></select></label>
<label>Tempo <select id="tempo"><option value="60">Lent</option><option value="90" selected>Normal</option><option value="120">Rapide</option></select></label>
<span id="etat"></span></header>
<main>
@@INTRO@@
@@SOMMAIRE@@
@@SECTIONS@@
</main>
<script>
const SONS = @@SONS@@;
const BANQUE = 'https://gleitz.github.io/midi-js-soundfonts/FluidR3_GM/';
const NOMS = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B'];
const INST = {piano:'acoustic_grand_piano', choeur:'choir_aahs', orgue:'church_organ'};
let ctx = null, encours = [], bouton = null, audioSecours = null;
const tampons = {};
const LOCAL = window.SONS_LOCAUX || {};

function nomNote(m){ return NOMS[m % 12] + (Math.floor(m / 12) - 1); }
function instrument(son, voix, i, n){
  if (son !== 'cordes') return INST[son];
  if (n === 4) return ['violin','violin','viola','cello'][i];
  const notes = voix.filter(e => e[0] !== null).map(e => e[0]);
  const moy = notes.reduce((a, b) => a + b, 0) / Math.max(1, notes.length);
  return moy >= 64 ? 'violin' : moy >= 52 ? 'viola' : 'cello';
}
function echantillon(inst, m){
  const cle = inst + m;
  if (!tampons[cle]) {
    const url = LOCAL[cle] || (BANQUE + inst + '-mp3/' + nomNote(m) + '.mp3');
    tampons[cle] = fetch(url).then(r => { if (!r.ok) throw new Error('son'); return r.arrayBuffer(); })
      .then(b => ctx.decodeAudioData(b)).catch(e => { delete tampons[cle]; throw e; });
  }
  return tampons[cle];
}
function arreter(){
  encours.forEach(s => { try { s.stop(); } catch(e){} });
  encours = [];
  if (audioSecours){ audioSecours.pause(); audioSecours = null; }
  if (bouton){ bouton.classList.remove('actif'); bouton.textContent = bouton.dataset.texte || '▶ Écouter'; bouton = null; }
}
function sonChoisi(genre){
  const s = document.getElementById('son').value;
  return s === 'auto' ? (genre === 'quatuor' ? 'cordes' : 'choeur') : s;
}
async function demarrer(){
  ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
  if (ctx.state === 'suspended') await ctx.resume();
}
// joue une liste de notes {inst, m, t, d, i} ; renvoie l'heure de fin
async function programmer(plan, sec, verifier){
  const tamp = await Promise.all(plan.map(p => echantillon(p.inst, p.m)));
  if (verifier && !verifier()) return 0;
  const t0 = ctx.currentTime + 0.06;
  let fin = 0;
  plan.forEach((p, k) => {
    const src = ctx.createBufferSource(), g = ctx.createGain();
    src.buffer = tamp[k];
    const debut = t0 + p.t * sec, duree = p.d * sec, vol = (p.i === 0 ? 0.32 : 0.26);
    g.gain.setValueAtTime(vol, debut);
    g.gain.setValueAtTime(vol, debut + duree);
    g.gain.linearRampToValueAtTime(0.0001, debut + duree + 0.15);
    src.connect(g).connect(ctx.destination);
    src.start(debut); src.stop(debut + duree + 0.2);
    encours.push(src);
    fin = Math.max(fin, debut + duree + 0.2);
  });
  return fin;
}
// lit un exemple complet ; mp3 = fichier de secours si les sons ne se chargent pas
async function lireMusique(mus, b, mp3){
  const etaitActif = b === bouton;
  arreter();
  if (etaitActif) return;
  bouton = b; b.dataset.texte = b.dataset.texte || b.textContent; b.classList.add('actif'); b.textContent = '■ Arrêter';
  const son = sonChoisi(mus.genre), sec = 60 / +document.getElementById('tempo').value;
  try {
    await demarrer();
    document.getElementById('etat').textContent = 'chargement des sons…';
    const plan = [];
    mus.voix.forEach((voix, i) => {
      const inst = instrument(son, voix, i, mus.voix.length);
      let t = 0;
      voix.forEach(([m, d]) => { if (m !== null) plan.push({inst, m, t, d, i}); t += d; });
    });
    const fin = await programmer(plan, sec, () => bouton === b);
    document.getElementById('etat').textContent = '';
    if (fin) setTimeout(() => { if (bouton === b) arreter(); }, (fin - ctx.currentTime) * 1000 + 50);
  } catch (e) {
    document.getElementById('etat').textContent = '';
    if (mp3 && bouton === b){
      audioSecours = new Audio(mp3);
      audioSecours.onended = () => { if (bouton === b) arreter(); };
      audioSecours.play();
    } else { arreter(); document.getElementById('etat').textContent = 'sons indisponibles (pas de connexion ?)'; }
  }
}
// joue quelques notes tout de suite (quand on pose une note dans un exercice)
async function jouerNotes(notes){
  try {
    await demarrer();
    const son = sonChoisi('choeur');
    await programmer(notes.map((n, k) => ({inst: INST[son] || 'choir_aahs', m: n.m, t: n.t, d: n.d, i: k})), 0.5);
  } catch (e) {}
}
function jouer(b){ lireMusique(SONS[b.dataset.ex], b, b.dataset.mp3); }
document.querySelectorAll('.jouer').forEach(b => b.addEventListener('click', () => jouer(b)));
const EXOS = @@EXOS@@;
const GLYPH = @@GLYPH@@;
@@VERIFJS@@
@@ATELIERJS@@
const montes = {};
document.querySelectorAll('.faire').forEach(b => b.addEventListener('click', () => {
  const id = b.dataset.exo, el = document.getElementById('at-' + id);
  el.hidden = !el.hidden; b.classList.toggle('on', !el.hidden);
  b.textContent = el.hidden ? "✏️ Faire l'exercice ici" : "✏️ Fermer l'exercice";
  if (!el.hidden && !montes[id]) montes[id] = Atelier.monter(el, id, EXOS[id]);
}));
document.querySelectorAll('.atelier.guide').forEach(el => { montes[el.dataset.exo] = Atelier.monter(el, el.dataset.exo, EXOS[el.dataset.exo]); });
</script>
</body></html>
'''
glyphs = json.load(open(os.path.join(ICI, 'glyphs.json')))
verifjs = open(os.path.join(ICI, 'verif.js')).read().replace("if (typeof module !== 'undefined') module.exports = HV;", '')
atelierjs = open(os.path.join(ICI, 'atelier.js')).read()
locaux = ''
if autonome:   # sons de la banque inclus dans le fichier, pour l'écoute hors connexion
    banque = os.environ.get('BANQUE', os.path.join(RACINE, '..', 'FluidR3_GM'))
    noms = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    d = {}
    for inst, lo, hi in (('choir_aahs', 40, 81), ('violin', 55, 81), ('viola', 48, 77), ('cello', 36, 66)):
        for m in range(lo, hi + 1):
            f = os.path.join(banque, inst + '-mp3', f'{noms[m % 12]}{m // 12 - 1}.mp3')
            if os.path.exists(f):
                d[inst + str(m)] = b64(f, 'audio/mpeg')
    locaux = '<script>window.SONS_LOCAUX = ' + json.dumps(d) + ';</script>'
page = page.replace('<script>\nconst SONS', locaux + '<script>\nconst SONS')
page = page.replace('@@EXOS@@', json.dumps(exos, ensure_ascii=False)).replace('@@GLYPH@@', json.dumps(glyphs))
page = page.replace('@@VERIFJS@@', verifjs).replace('@@ATELIERJS@@', atelierjs)
if CAHIER:
    intro = ("<p>Ce cahier suit le cours chapitre par chapitre. Chaque exercice se fait <b>directement sur la portée</b> : "
             "tu choisis une voix, tu cliques pour poser les notes, et les corrections s'affichent au fur et à mesure. "
             "Les basses données et les chants donnés se font en plusieurs étapes, chacune se débloque quand la précédente est juste. "
             "Ton travail est gardé dans ton navigateur.</p>")
    page = page.replace('@@TITRE@@', "Cahier d'exercices d'harmonie").replace('@@AUTRE@@', 'index.html').replace('@@AUTRETXT@@', '← Le cours')
else:
    intro = ("<p>Sous chaque exemple, le bouton <b>▶ Écouter</b> joue l'exemple avec des sons de la banque General MIDI. "
             "En mode <b>Automatique</b>, les exemples pour quatuor vocal sont chantés par un chœur, et ceux pour quatuor à cordes joués par des cordes. "
             "Pour t'entraîner, ouvre le <a href=\"cahier.html\">cahier d'exercices</a>.</p>")
    page = page.replace('@@TITRE@@', "Cours d'écriture et d'harmonie").replace('@@AUTRE@@', 'cahier.html').replace('@@AUTRETXT@@', "Cahier d'exercices →")
if autonome:
    page = page.replace('<a class="autre" href="app/">📱 L\'appli</a>', '')
    page = page.replace('<a class="autre" href="index.html">← Le cours</a>', '').replace('<a class="autre" href="cahier.html">Cahier d\'exercices →</a>', '')
page = page.replace('@@INTRO@@', intro)
page = page.replace('@@SOMMAIRE@@', som).replace('@@SECTIONS@@', '\n'.join(sections)).replace('@@SONS@@', json.dumps(sons))
open(sortie, 'w').write(page)
print('écrit :', sortie, f'({len(page) // 1024} Ko)')
