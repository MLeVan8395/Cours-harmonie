"""Usage : python3 outils/build_partie7.py

Partie 7 (le romantisme tardif) : figures des chapitres 36 à 42, exercices interactifs du cours,
exercices du cahier (chapitres 36 à 39) et leurs pages. (Reconstruit aussi les parties 4 à 6.)"""
import json, os, re
from graveur import Figure, satb, RED, GREEN, BLUE, ORANGE, MUTED, SONS, N, midi, dpos
from verif import check
from accords4 import phrase4, spec
import build_partie4 as P4
import build_partie5 as P5
import build_partie6 as P6

ICI = os.path.dirname(os.path.abspath(__file__))
COURS = os.path.join(ICI, '..', 'cours')
CAHIER = os.path.join(ICI, '..', 'cahier')
IMG, IMGK = os.path.join(COURS, 'images'), os.path.join(CAHIER, 'images')
DEG = ['degrés', 'chiffrage']
labs, realise, save, expect, couleurs = P4.labs, P5.realise, P5.save, P5.expect, P6.couleurs
SONS.clear()


def concat(parties):
    """Plusieurs petites réalisations côte à côte : accords, degrés, chiffres, couleurs, boîtes."""
    ch, dg, cf, col, box = [], [], [], {}, []
    t = 0
    for (c, d, f, s, titre, coul) in parties:
        for (v, i), cc in couleurs(s, c).items():
            col[(v, len(ch) + i)] = cc
        ch += c; dg += d; cf += f
        dur = sum(x[4] for x in c)
        box.append((t, t + dur, coul, titre))
        t += dur
    return ch, dg, cf, col, box


# ======================================================================== chapitre 36 : enharmonie
parts = []
for ton, arm, nom in (('Do', -3, 'do mineur'), ('Mib', -6, 'mi♭ mineur'), ('Fa#', 3, 'fa♯ mineur'), ('La', 0, 'la mineur')):
    c, d, f, s, _ = realise('VII7 I', ton, arm, soprano_fin=False)
    parts.append((c, ['VII°7', 'I'], f, s, nom, BLUE))
ch, dg, cf, col, box = concat(parts)
pcs = [frozenset(midi(N(x)) % 12 for x in p[0][0][:4]) for p in parts]
assert len(set(pcs)) == 1, pcs
save(satb(ch, unit=16, colors=col, labels=labs(ch, dg, cf), rows=DEG, boxes=box), 'h36-dim-quatre')
DIM4 = [p[0][0][:4] for p in parts]

c1, d1, f1, s1, _ = realise('Al6 I64 V', 'Do', 0, soprano_fin=False)
c2, d2, f2, s2, _ = realise('V7 I', 'Réb', -5, soprano_fin=False)
ch, dg, cf, col, box = concat([(c1, d1, f1, s1, 'Do majeur : sixte allemande', BLUE), (c2, d2, f2, s2, 'Ré♭ majeur : V7', GREEN)])
assert frozenset(midi(N(x + '4')) % 12 for x in s1[0]['names']) == frozenset(midi(N(x + '4')) % 12 for x in s2[0]['names'])
save(satb(ch, unit=18, colors=col, labels=labs(ch, dg, cf), rows=DEG, boxes=box), 'h36-al-v7')

mo, dmo, cmo, smo, _ = realise('I II6 VIIo65=[la]VII65 I V7 I', 'Do', 0, durees=[2, 2, 4, 2, 2, 4])
dmo = ['I', 'II', 'VII°', 'I', 'V', 'I']
save(satb(mo, unit=24, time=(4, 4), colors=couleurs(smo, mo), labels=labs(mo, dmo, cmo), rows=DEG,
          boxes=[(0, 4, BLUE, 'Do majeur'), (4, 8, MUTED, 'pivot'), (8, 16, GREEN, 'la mineur')]), 'h36-modulation')
mr, dmr, cmr, smr, _ = realise('I Al6=[Réb]V7 I IV V7 I', 'Do', 0, durees=[4, 4, 2, 2, 2, 2])
save(satb(mr, unit=24, time=(4, 4), colors=couleurs(smr, mr), labels=labs(mr, dmr, cmr), rows=DEG,
          boxes=[(0, 4, BLUE, 'Do majeur'), (4, 8, MUTED, 'pivot'), (8, 16, GREEN, 'Ré♭ majeur')]), 'h36-modulation-reb')

# ======================================================================== chapitre 37 : l'accord augmenté, les tierces
aug = [['Do4', 'Mi4', 'Sol#4'], ['Si3', 'Ré#4', 'Sol4'], ['Sib3', 'Ré4', 'Fa#4'], ['La3', 'Do#4', 'Mi#4']]
vv = [{'staff': 0, 'stem': None, 'events': [(a[j], 4, {'color': RED} if j == 2 else {}) for a in aug]} for j in range(3)]
save(Figure([{'clef': 'treble'}], vv, unit=20, labels=[(i * 4, n, 0, MUTED) for i, n in enumerate(['C+', 'B+ (= G+)', 'B♭+', 'A+'])],
            rows=['accord']), 'h37-augmentes')
cy, dcy, ccy, scy, _ = realise('I [Mi] I [Lab] I [Do] I', 'Do', 0)
dcy = ['C', 'E', 'A♭', 'C']
save(satb(cy, unit=24, labels=labs(cy, dcy, None), rows=['accord'],
          colors={(v, i): RED for i in (1, 2) for v in range(4) if ('#' in cy[i][v] or 'b' in cy[i][v])}), 'h37-tierces')
CY = cy
va, dva, cva, sva, _ = realise('I [Mi] I V7 I [Lab] I V7 I', 'Do', 0, durees=[2, 2, 2, 2, 2, 2, 4])
save(satb(va, unit=22, time=(4, 4), colors=couleurs(sva, va), labels=labs(va, dva, cva), rows=DEG,
          boxes=[(0, 2, BLUE, 'Do'), (2, 8, GREEN, 'Mi'), (8, 16, ORANGE, 'La♭')]), 'h37-tierces-cadences')

# ======================================================================== chapitre 38 : Wagner
# les deux lignes du début du Prélude de Tristan (réduction : hauteurs exactes, rythme simplifié)
lig = [{'staff': 0, 'stem': None, 'events': [(None, 5, {'hide': True}), ('Sol#4', 1, {'color': RED}), ('La4', 1), ('La#4', 1), ('Si4', 4)]},
       {'staff': 1, 'stem': None, 'events': [('La3', 1), ('Fa4', 3), ('Mi4', 1), ('Ré#4', 3, {'color': RED}), (None, 4, {'hide': True})]}]
save(Figure([{'clef': 'treble', 'label': 'hautbois'}, {'clef': 'bass', 'label': 'violoncelles'}], lig, key=0, brace=(0, 1), gap=104, unit=26,
            bars=False), 'h38-lignes')
tri = [{'staff': 0, 'stem': None, 'events': [('Sol#4', 4, {'color': RED}), ('Si4', 4)]},
       {'staff': 0, 'stem': None, 'events': [('Ré#4', 4, {'color': RED}), ('Sol#4', 4)]},
       {'staff': 1, 'stem': None, 'events': [('Si3', 4, {'color': RED}), ('Ré4', 4)]},
       {'staff': 1, 'stem': None, 'events': [('Fa3', 4, {'color': RED}), ('Mi3', 4)]}]
save(Figure([{'clef': 'treble'}, {'clef': 'bass'}], tri, brace=(0, 1), gap=104, unit=28,
            labels=[(0, "accord de Tristan", 0, RED), (4, 'E7', 0, BLUE)], rows=['']), 'h38-accords')
# lecture « scolaire » : une sixte française (Fa-La-Si-Ré♯) avec l'appoggiature Sol♯, résolue normalement sur V
fr6, dfr, cfr, sfr, _ = realise('Fr6 V', 'La', 0, soprano_fin=False)
save(satb(fr6, unit=26, colors=couleurs(sfr, fr6), labels=labs(fr6, dfr, cfr), rows=DEG), 'h38-sixte-francaise')
FR6 = fr6
ev, dev, cev, sev, _ = realise('I IV V7 V7/IV IV V7/V V7 I', 'Do', 0, durees=[2, 2, 2, 2, 2, 2, 2, 2])
save(satb(ev, unit=22, time=(4, 4), colors=couleurs(sev, ev), labels=labs(ev, dev, cev), rows=DEG,
          boxes=[(4, 8, RED, 'cadence évitée')]), 'h38-evitee')
gl, dgl, cgl, sgl, _ = realise('I V7 I [Réb] V7 I [Ré] V7 I', 'Do', 0, durees=[2, 2, 4, 2, 2, 2, 2])
save(satb(gl, unit=22, time=(4, 4), colors=couleurs(sgl, gl), labels=labs(gl, dgl, cgl), rows=DEG,
          boxes=[(0, 8, BLUE, 'Do'), (8, 12, GREEN, 'Ré♭'), (12, 16, ORANGE, 'Ré')]), 'h38-glissement')

# ======================================================================== chapitre 39 : Franck et Mahler
mo6 = [('Do#5', 'Mi4', 'La3', 'La2', 4), ('Do5', 'Mi4', 'La3', 'La2', 4)]
expect(mo6, tonic='La')
save(satb(mo6, unit=28, colors={(0, 0): GREEN, (0, 1): RED}, lines=[((0, 0), (0, 1), RED)],
          labels=[(0, 'A', 0, GREEN), (4, 'Am', 0, RED)], rows=['accord']), 'h39-majeur-mineur')
mx, dmx, cmx, smx, _ = realise('I VIb IVm I64 V7 I', 'Fa', -1, durees=[2, 2, 2, 2, 4, 4])
save(satb(mx, key=-1, unit=22, time=(4, 4), colors=couleurs(smx, mx), labels=labs(mx, dmx, cmx), rows=DEG), 'h39-melange')
# Franck : une même phrase répétée un demi-ton plus haut (Do, puis Ré♭)
fk, dfk, cfk, sfk, _ = realise('I IV6 V7 I [Réb] IV6 V7 I', 'Do', 0, durees=[2, 2, 2, 2, 2, 2, 2, 2])
save(satb(fk, unit=22, time=(4, 4), colors=couleurs(sfk, fk), labels=labs(fk, dfk, cfk), rows=DEG,
          boxes=[(0, 8, BLUE, 'Do majeur'), (8, 16, GREEN, 'Ré♭ majeur')]), 'h39-franck')

# ======================================================================== exercices du cours (chapitre 41)
EXOS, EXOS_K = {}, {}
an = [('Ré5', 'Fa4', 'Si3', 'Lab2'), ('Mib5', 'Solb4', 'Do4', 'Lab2'), ('Do5', 'Mi4', 'Sol#3', 'Do3'), ('Si4', 'Ré#4', 'Sol#3', 'Fa3')]
tt = [(i * 4, x, MUTED) for i, x in enumerate(['a)', 'b)', 'c)', 'd)'])]
save(satb(an, unit=24, top_texts=tt), 'h41-ex1')
save(satb(an, unit=24, top_texts=tt, labels=[(0, 'VII°7', 0, BLUE), (4, 'Al+6 / V7', 0, BLUE), (8, 'C+', 0, BLUE), (12, 'Tristan', 0, BLUE)], rows=['accord']), 'h42-c1')

P4.faire_exo(EXOS, 'h41-ex2', 'bd', 'I II6 VIIo65=[la]VII65 I V7 I', 'Do', 0, durees=[2, 2, 4, 2, 2, 4], dossier=IMG)
P4.faire_exo(EXOS, 'h41-ex3', 'bd', 'I Al6=[Réb]V7 I IV V7 I', 'Do', 0, durees=[4, 4, 2, 2, 2, 2], dossier=IMG)
P4.faire_exo(EXOS, 'h41-ex4', 'bc', 'I IV V7 V7/IV IV V7/V V7 I', 'Sol', 1, durees=[2] * 8, dossier=IMG,
             menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'V7/IV', 'V7/V'])
P4.faire_exo(EXOS, 'h41-ex5', 'cd', 'I VIb IVm I64 V7 I', 'Ré', 2, dossier=IMG, menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'IVm', 'VIb'], sop_min='Ré4')
for k in range(2, 6):
    os.replace(os.path.join(IMG, f'h41-ex{k}-c.png'), os.path.join(IMG, f'h42-c{k}.png'))
    SONS[f'h42-c{k}'] = SONS.pop(f'h41-ex{k}-c')
# libellés des pivots dans les exercices
for k in ('h41-ex2',):
    EXOS[k]['degres'] = ['I', 'II', 'VII°', 'I', 'V', 'I']

# ======================================================================== cahier : chapitres 36 à 39
PAGES = {36: [], 37: [], 38: [], 39: []}


def ajouter(chap, typ, plan, t, a, titre, degs=None, **kw):
    num = len(PAGES[chap]) + 1
    nom = f'c{chap}-{num:02d}'
    P4.faire_exo(EXOS_K, nom, typ, plan, t, a, **kw)
    if degs:
        EXOS_K[nom]['degres'] = degs
    PAGES[chap].append((nom, typ, t, a, titre))


ajouter(36, 'bd', 'I IV VI II6 VIIo65=[la]VII65 I V7 I', 'Do', 0, 'de Do majeur à la mineur par une 7e diminuée', durees=[2] * 8,
        degs=['I', 'IV', 'VI', 'II', 'VII°', 'I', 'V', 'I'])
ajouter(36, 'bd', 'I Al6=[Réb]V7 I IV V7 I', 'Do', 0, 'de Do majeur à Ré♭ majeur : la sixte allemande devient V7', durees=[4, 4, 2, 2, 2, 2])
ajouter(36, 'bd', 'I II6 VIIo65=[la]VII65 I IV V7 I', 'Do', 0, 'de Do majeur à la mineur', durees=[2, 2, 4, 2, 2, 2, 2],
        degs=['I', 'II', 'VII°', 'I', 'IV', 'V', 'I'])
ajouter(37, 'bd', 'I [Mi] I V7 I', 'Do', 0, 'de Do à Mi par une tierce', durees=[4, 4, 4, 4])
ajouter(37, 'bd', 'I [Lab] I V7 I', 'Do', 0, 'de Do à La♭ par une tierce', durees=[4, 4, 4, 4])
ajouter(38, 'bc', 'I IV V7 V7/IV IV V7/V V7 I', 'Ré', 2, 'cadence évitée', durees=[2] * 8, menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'V7/IV', 'V7/V'])
ajouter(38, 'bd', 'I V7 I [Réb] V7 I', 'Do', 0, "glissement d'un demi-ton", durees=[2, 2, 4, 4, 4])
ajouter(39, 'cd', 'I VIb IVm I64 V7 I', 'Sol', 1, 'majeur et mineur mêlés', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'IVm', 'VIb'])
ajouter(39, 'bc', 'I IV IVm I VI II6 V7 I', 'Fa', -1, "l'ombre du mineur", durees=[2] * 8, menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'IVm', 'VIb'])

print('partie 7 :', len(EXOS), 'exercices du cours,', len(EXOS_K), 'exercices du cahier')
json.dump(EXOS, open(os.path.join(COURS, 'exercices-partie7.json'), 'w'), ensure_ascii=False)
json.dump(EXOS_K, open(os.path.join(CAHIER, 'exercices-cahier7.json'), 'w'), ensure_ascii=False)
json.dump({k: v for k, v in SONS.items() if k.startswith('h')}, open(os.path.join(COURS, 'audio', 'sons-partie7.json'), 'w'), indent=0)
json.dump({k: v for k, v in SONS.items() if k.startswith('c')}, open(os.path.join(CAHIER, 'audio', 'sons-cahier7.json'), 'w'), indent=0)
json.dump({'E': {k: [EXOS[k]['solution'], EXOS[k].get('degres'), EXOS[k].get('chiffres'), EXOS[k].get('harmonie')] for k in EXOS},
           'DIM4': DIM4, 'mo': mo, 'mr': mr, 'CY': CY, 'FR6': FR6, 'ev': ev, 'gl': gl, 'mx': mx, 'fk': fk, 'va': va},
          open('/tmp/p7.json', 'w'), ensure_ascii=False)

# ======================================================================== pages du cahier
TON = dict(P6.TON)
TITRES = {36: ('36-enharmonie', 'Enharmonie et modulations éloignées', '36-enharmonie-et-modulations-eloignees.md'),
          37: ('37-modulations-par-tierces', "L'accord augmenté et les tierces", '37-l-accord-augmente-et-les-tierces.md'),
          38: ('38-wagner', 'Wagner : cadences évitées et glissements', '38-wagner-l-accord-de-tristan.md'),
          39: ('39-majeur-et-mineur', 'Franck et Mahler : majeur et mineur', '39-franck-et-mahler.md')}
TYPES = P5.TYPES
ordre = [(32, '32-du-piano-aux-quatre-voix', 'Du piano aux quatre voix')] + [(c, TITRES[c][0], TITRES[c][1]) for c in (36, 37, 38, 39)]
for k, chap in enumerate((36, 37, 38, 39)):
    fic, titre, cours_md = TITRES[chap]
    prev = ordre[k]
    nav = f"[← {prev[2]}]({prev[1]}.md) · [Sommaire du cahier](README.md)"
    if k < 3:
        nx = ordre[k + 2]
        nav += f" · [{nx[2]} →]({nx[1]}.md)"
    L = [nav, '', f'## {titre}', '', f"Ces exercices accompagnent le [chapitre {chap}](../cours/{cours_md}) du cours.", '',
         "Dans la version web (`cahier.html`), chaque exercice se fait **directement sur la portée**, avec les corrections au fur et à mesure. "
         "Dans les modulations, les altérations se font dans la même voix (pas de fausse relation), et la nouvelle sensible monte.", '']
    for j, (nom, typ, t, a, sous) in enumerate(PAGES[chap]):
        n = f'{chap}.{j + 1}'
        tt = f"{TYPES[typ]} en {TON[(t, a)]}" + (f' ({sous})' if sous else '')
        L += [f'### Exercice {n} · {tt}', '', P4.CONSIGNE4[typ], '', f'![Exercice {n}](images/{nom}.png)', '']
    L += ['### Corrigés', '']
    for j, (nom, typ, t, a, sous) in enumerate(PAGES[chap]):
        n = f'{chap}.{j + 1}'
        L += [f"**Exercice {n}** : une solution parmi d'autres.", '', f'![Corrigé {n}](images/{nom}-c.png)', '',
              f'🔊 [Écouter](audio/{nom}-c.mp3) · [MIDI](audio/{nom}-c.mid)', '']
    L += ['---', '', nav, '']
    open(os.path.join(CAHIER, fic + '.md'), 'w').write('\n'.join(L))

p32 = os.path.join(CAHIER, '32-du-piano-aux-quatre-voix.md')
s = open(p32).read()
s = re.sub(r'\[Sommaire du cahier\]\(README\.md\)(?! ·)', "[Sommaire du cahier](README.md) · [Enharmonie et modulations éloignées →](36-enharmonie.md)", s)
open(p32, 'w').write(s)

NT = {'bc': 'basse chiffrée', 'bd': 'basse donnée', 'sb': "compléter l'alto et le ténor", 'cd': 'chant donné', 'corriger': 'chasse aux fautes'}
readme = os.path.join(CAHIER, 'README.md')
R = [l for l in open(readme).read().split('\n') if not re.match(r'- \[.*\]\((36|37|38|39)-', l)]
i = next(k for k, l in enumerate(R) if '(32-du-piano' in l)
add = []
for chap in (36, 37, 38, 39):
    sortes = {}
    for p in PAGES[chap]:
        sortes[NT[p[1]]] = sortes.get(NT[p[1]], 0) + 1
    add.append(f"- [{TITRES[chap][1]}]({TITRES[chap][0]}.md) (chapitre {chap} du cours) : " + ', '.join(f'{v} × {k}' for k, v in sortes.items()))
R = R[:i + 1] + add + R[i + 1:]
txt = '\n'.join(R)
n7 = sum(len(v) for v in PAGES.values())
m = re.search(r'dont (\d+) basses données, (\d+) chants donnés, (\d+) exercices sur le choral, (\d+) sur les accords de quatre sons, (\d+) sur le style classique et (\d+) sur le premier romantisme', txt)
base_n = 54 + int(m.group(4)) + int(m.group(5)) + int(m.group(6))
txt = re.sub(r'\*\*\d+ exercices\*\* en tout, dont .*?Tous les corrigés',
             f"**{base_n + n7} exercices** en tout, dont {m.group(1)} basses données, {m.group(2)} chants donnés, {m.group(3)} exercices sur le choral, "
             f"{m.group(4)} sur les accords de quatre sons, {m.group(5)} sur le style classique, {m.group(6)} sur le premier romantisme "
             f"et {n7} sur le romantisme tardif. Tous les corrigés", txt)
open(readme, 'w').write(txt)
print('pages du cahier écrites')
