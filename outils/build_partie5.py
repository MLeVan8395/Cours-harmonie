"""Usage : python3 outils/build_partie5.py

Partie 5 (le style classique) : figures des chapitres 24 à 29, exercices interactifs du cours,
exercices du cahier (chapitres 24 à 26) et leurs pages."""
import json, os, re, sys
from graveur import Figure, satb, RED, GREEN, BLUE, ORANGE, MUTED, SONS, N, midi, dpos
from verif import check, sixte_aug
from accords4 import phrase4, spec, diagnostic4
import build_partie4 as P4     # réutilise faire_exo, labs, expect… (et reconstruit la partie 4, sans effet de bord)

ICI = os.path.dirname(os.path.abspath(__file__))
COURS = os.path.join(ICI, '..', 'cours')
CAHIER = os.path.join(ICI, '..', 'cahier')
IMG, IMGK = os.path.join(COURS, 'images'), os.path.join(CAHIER, 'images')
DEG = ['degrés', 'chiffrage']
labs = P4.labs
SONS.clear()


def save(fig, name, dossier=IMG):
    fig.save(os.path.join(dossier, name + '.png'))


def expect(chords, n_err=0, contains=(), tonic='Do', allow_third=(), pedales=()):
    e = check([c[:4] for c in chords], tonic, allow_third=allow_third, pedales=pedales)
    assert len(e) == n_err, (chords, e)
    for c in contains:
        assert any(c in x for x in e), (c, e)
    return e


def couleurs(seq, ch):
    """Notes chromatiques à surveiller : napolitaine (2e degré abaissé) en rouge, sixte augmentée en rouge et orange,
    septièmes en rouge, sensibles en orange."""
    col = P4.en_rouge(seq, ch)
    for i, s in enumerate(seq):
        if s['label'] == 'N':
            for v in range(4):
                if ch[i][v][:-1] == s['names'][0]:
                    col[(v, i)] = RED
        if s.get('q') == 'aug6':
            for v in range(4):
                n = ch[i][v][:-1]
                if n == s['names'][0]:
                    col[(v, i)] = RED
                elif n == s['names'][-1]:
                    col[(v, i)] = ORANGE
                else:
                    col.pop((v, i), None)
    return col


def realise(plan, t='Do', a=0, durees=None, **kw):
    ps, allow, seq = phrase4(plan, t, a, **kw)
    p = ps[0]
    durees = durees or [4] * len(p)
    ch = [tuple(c) + (d,) for c, d in zip(p, durees)]
    tons = [s['ton'][0] for s in seq]
    ped = {i for i, s in enumerate(seq) if s.get('pedale')}
    expect(ch, tonic=tons, allow_third=allow, pedales=ped)
    return ch, [s['label'] for s in seq], [s['chiffre'] for s in seq], seq, ped


def avec_pedale(ch, ped, col=MUTED):
    """Grande portée SATB où la basse tenue est liée d'un accord à l'autre."""
    voices = []
    for vi, (st, stem) in enumerate([(0, 'up'), (0, 'down'), (1, 'up'), (1, 'down')]):
        ev = []
        for i, c in enumerate(ch):
            op = {}
            if vi == 3 and (i + 1) in ped:
                op['tie'] = True
            if vi == 3 and (i in ped or (i + 1) in ped):
                op['color'] = col
            ev.append((c[vi], c[4], op))
        voices.append({'staff': st, 'stem': stem, 'events': ev})
    return voices


# ======================================================================== chapitre 24 : napolitaine, sixtes augmentées
vv = [{'staff': 0, 'stem': None, 'events': [(n, 4, {'color': c} if c else {}) for n, c in zip(x, cs)]} for x, cs in
      [(['Ré4', 'Ré4'], [None, RED]), (['Fa4', 'Fa4'], [None, None]), (['La4', 'Sib4'], [None, RED])]]
save(Figure([{'clef': 'treble'}], vv, key=0, unit=22,
            labels=[(0, 'IV', 0, BLUE), (4, 'N', 0, BLUE), (0, 'Dm', 1, MUTED), (4, 'B♭', 1, MUTED)], rows=['degrés', 'accord']), 'h24-napo-accord')

n1, dn1, cn1, sn1, _ = realise('I IV N6 V7 I', 'La', 0)
save(satb(n1, unit=22, colors=couleurs(sn1, n1), labels=labs(n1, dn1, cn1), rows=DEG), 'h24-napo')
n2, dn2, cn2, sn2, _ = realise('I N6 I64 V7 I', 'Do', 0)
save(satb(n2, unit=22, colors=couleurs(sn2, n2), labels=labs(n2, dn2, cn2), rows=DEG), 'h24-napo-majeur')

six = []
for plan in ('It6 V', 'Fr6 V', 'Al6 I64 V'):
    c, d, chf, s, _ = realise(plan, 'La', 0, soprano_fin=False)
    six.append((c, d, chf, s))
allc = sum([x[0] for x in six], [])
cols = {}
off = 0
for x in six:
    for (v, i), cc in couleurs(x[3], x[0]).items():
        cols[(v, off + i)] = cc
    off += len(x[0])
save(satb(allc, unit=18, colors=cols, boxes=[(0, 8, BLUE, 'italienne'), (8, 16, BLUE, 'française'), (16, 28, BLUE, 'allemande')],
          labels=labs(allc, sum([x[1] for x in six], []), sum([x[2] for x in six], [])), rows=DEG), 'h24-sixtes')
# l'allemande directement sur V : quintes « de Mozart »
from recherche import voicings
al = six[2][0][0]
qm = None
for b in ('Mi2', 'Mi3'):
    for v in voicings(['Mi', 'Sol#', 'Si'], bass=b, tonic='La'):
        eq = check([al[:4], v], 'La')
        if eq and all('5tes consécutives' in x for x in eq):
            qm = [al, tuple(v) + (4,)]
            break
    if qm:
        break
assert qm, 'pas de quintes de Mozart'
VX = ['soprano', 'alto', 'ténor', 'basse']
vq = {VX.index(w) for x in eq for w in re.findall(r'(soprano|alto|ténor|basse)', x)}
save(satb(qm + six[2][0], unit=18, colors={(v, i): RED for v in vq for i in (0, 1)},
          boxes=[(0, 8, RED, 'Al+6 - V : quintes'), (8, 20, GREEN, 'Al+6 - I6/4 - V')],
          labels=labs(qm + six[2][0], ['Al+6', 'V'] + six[2][1], ['6+/5', '♯'] + six[2][2]), rows=DEG), 'h24-quintes')
QM = eq

ph24, d24, c24, s24, _ = realise('I IV6 V I VI It6 V I', 'Ré', -1, durees=[2, 2, 2, 2, 2, 2, 2, 2])
save(satb(ph24, key=-1, unit=22, time=(4, 4), colors=couleurs(s24, ph24), labels=labs(ph24, d24, c24), rows=DEG), 'h24-phrase')

# ======================================================================== chapitre 25 : pédales et cadences classiques
pt, dpt, cpt, spt, ppt = realise('I IV@Do V7@Do I IV V7 I', 'Do', 0, durees=[2, 2, 2, 2, 2, 2, 4])
save(Figure([{'clef': 'treble'}, {'clef': 'bass'}], avec_pedale(pt, ppt), brace=(0, 1), gap=104, unit=22, time=(4, 4),
            labels=labs(pt, dpt, ['5', 'péd.', 'péd.', '5', '5', '7+', '5']), rows=DEG,
            boxes=[(0, 8, MUTED, 'pédale de tonique')], top=64), 'h25-pedale-tonique')
pdo, dpd, cpd, spd, ppd = realise('I IV V I64@Sol V VIIo7@Sol V7 I', 'Do', 0, durees=[2, 2, 2, 2, 2, 2, 2, 2])
save(Figure([{'clef': 'treble'}, {'clef': 'bass'}], avec_pedale(pdo, ppd), brace=(0, 1), gap=104, unit=22, time=(4, 4),
            labels=labs(pdo, dpd, [c if c else 'péd.' for c in cpd]), rows=DEG,
            boxes=[(4, 14, MUTED, 'pédale de dominante')], top=70), 'h25-pedale-dominante')

gc, dgc, cgc, sgc, _ = realise('I I6 IV II6 I64 V7 I', 'Sol', 1, durees=[2, 2, 2, 2, 2, 2, 4])
save(satb(gc, key=1, unit=22, time=(4, 4), colors=P4.en_rouge(sgc, gc), labels=labs(gc, dgc, cgc), rows=DEG,
          boxes=[(8, 16, GREEN, 'formule de cadence')]), 'h25-cadence')
ph, dph, cph, sph, _ = realise('I V6 I IV6 V', 'La', 0, soprano_fin=False)
save(satb(ph, unit=20, colors={(3, 3): ORANGE, (3, 4): ORANGE}, lines=[((3, 3), (3, 4), ORANGE)],
          labels=labs(ph, dph, cph), rows=DEG), 'h25-phrygienne')
fin, dfi, cfi, sfi, pfi = realise('I V7 I V7 I IV@Ré I', 'Ré', 2, durees=[2, 2, 2, 2, 2, 2, 4])
save(Figure([{'clef': 'treble'}, {'clef': 'bass'}], avec_pedale(fin, pfi), key=2, brace=(0, 1), gap=104, unit=22, time=(4, 4),
            labels=labs(fin, dfi, [c if c else 'péd.' for c in cfi]), rows=DEG), 'h25-coda')

# ======================================================================== chapitre 26 : écrire pour quatuor à cordes
QUAT = [{'clef': 'treble', 'label': 'Violon 1'}, {'clef': 'treble', 'label': 'Violon 2'},
        {'clef': 'alto', 'label': 'Alto'}, {'clef': 'bass', 'label': 'Violoncelle'}]


def quatuor(voices, nom, key=0, unit=22, time=(4, 4), labels=None, rows=None, bar=4, groupe=1, dossier=IMG, boxes=None):
    save(Figure(QUAT, voices, key=key, gap=96, unit=unit, time=time, beats_per_bar=bar, groupe=groupe,
                labels=labels, rows=rows, boxes=boxes), nom, dossier)


def texture(ch, style):
    """Transforme un choral (accords avec durées) en écriture de quatuor."""
    V = [[] for _ in range(4)]
    n = len(ch)
    for i, c in enumerate(ch):
        d = c[4]
        if style == 'choral':
            for v in range(4):
                V[v].append((c[v], d))
        elif style == 'batteries':
            V[0].append((c[0], d))
            for v in (1, 2):
                if i == n - 1:
                    V[v].append((c[v], d))
                else:
                    V[v] += [(c[v], 0.5)] * int(d * 2)
            V[3] += [(c[3], 1)] * int(d) if i < n - 1 else [(c[3], d)]
        elif style == 'basse':
            V[0].append((c[0], d))
            V[1].append((c[1], d))
            V[2].append((c[2], d))
            if i == n - 1:
                V[3].append((c[3], d))
            else:
                bas = c[3][:-1] + str(int(c[3][-1]) - 1)
                if midi(N(bas)) < midi(N('Do2')):
                    bas, haut = c[3], c[3][:-1] + str(int(c[3][-1]) + 1)
                else:
                    haut = c[3]
                V[3] += [(bas, 0.5), (haut, 0.5)] * int(d)
    return [{'staff': v, 'stem': None, 'events': V[v]} for v in range(4)]


ch26, d26, c26, s26, _ = realise('I IV II6 I64 V7 I', 'Ré', 2, durees=[2, 2, 2, 2, 2, 2])
lab26 = [l for l in labs(ch26, d26, c26) if l[2] == 0]
quatuor(texture(ch26, 'choral'), 'h26-choral', key=2, labels=lab26, rows=['degrés'])
quatuor(texture(ch26, 'batteries'), 'h26-batteries', key=2, labels=lab26, rows=['degrés'])
quatuor(texture(ch26, 'basse'), 'h26-basse', key=2, labels=lab26, rows=['degrés'])
# doubles cordes à la cadence finale : le 2e violon et l'alto jouent deux notes
cad = ch26[-2:]
dc = [[(cad[0][0], 2), (cad[1][0], 2)],
      [(cad[0][1], 2), (cad[1][1], 2)], [(cad[0][2], 2), (cad[1][2], 2)], [(cad[0][3], 2), (cad[1][3], 2)]]
from recherche import notes_in_range, chord_notes
ajout = {1: [], 2: []}
for v, bas in ((1, 'Sol3'), (2, 'Do3')):
    for k in range(2):
        haut = dc[v][k][0]
        cands = [x for x in notes_in_range(chord_notes(s26[4 + k]['names']), bas, haut) if 3 <= midi(N(haut)) - midi(N(x)) <= 9]
        cands.sort(key=lambda x: midi(N(haut)) - midi(N(x)))
        ajout[v].append((cands[0], 2))
dvoix = [{'staff': 0, 'events': dc[0]}, {'staff': 1, 'stem': 'up', 'events': dc[1]}, {'staff': 1, 'stem': 'down', 'events': ajout[1]},
         {'staff': 2, 'stem': 'up', 'events': dc[2]}, {'staff': 2, 'stem': 'down', 'events': ajout[2]}, {'staff': 3, 'events': dc[3]}]
save(Figure(QUAT, dvoix, key=2, gap=96, unit=26, time=(4, 4), labels=[(0, 'V', 0, BLUE), (2, 'I', 0, BLUE)], rows=['degrés']), 'h26-doubles-cordes')
DC = (cad, ajout)

# ======================================================================== chapitre 27 : analyse, Beethoven op. 18 n° 1, Adagio
from lire_mxl2 import lire
BEETH = os.path.join(ICI, 'beethoven', 'op18n1-adagio.mxl')
os.makedirs(os.path.dirname(BEETH), exist_ok=True)
SRC = '/home/claude/m21/music21/corpus/beethoven/opus18no1/movement2.mxl'
if not os.path.exists(BEETH) and os.path.exists(SRC):
    import shutil
    shutil.copy(SRC, BEETH)
PARTS = lire(BEETH)


def extrait(parts, t0, t1, bar=4.5):
    """Voix pour le graveur entre t0 et t1 (en noires) : une couche principale par instrument, plus une couche
    pour les doubles cordes ; les silences comblent les vides (coupés aux barres de mesure)."""
    voices = []
    for k, p in enumerate(parts):
        ns = [x for x in p['notes'] if t0 - 1e-6 <= x['t'] < t1 - 1e-6]
        par = {}
        for x in ns:
            par.setdefault(round(x['t'], 4), []).append(x)
        haut, bas = [], []
        for t in sorted(par):
            g = sorted(par[t], key=lambda x: midi(N(x['n'])), reverse=(k != 3))
            haut.append(g[0])
            if len(g) > 1:
                bas.append(g[1])

        def couche(lst, cache):
            ev, t = [], t0
            for x in lst:
                if x['t'] > t + 1e-6:
                    trou = x['t'] - t
                    while trou > 1e-6:
                        fin_mes = (int((t - t0) / bar + 1e-9) + 1) * bar + t0
                        d = min(trou, fin_mes - t)
                        ev.append((None, d, {'hide': True} if cache else {}))
                        t += d; trou -= d
                if x['lie'] and ev and ev[-1][0] == x['n']:
                    ev[-1] = (ev[-1][0], ev[-1][1], dict(ev[-1][2], tie=True))
                ev.append((x['n'], min(x['d'], t1 - x['t']), {}))
                t = x['t'] + x['d']
            if t < t1 - 1e-6:
                ev.append((None, t1 - t, {'hide': True} if cache else {}))
            return ev
        voices.append({'staff': k, 'stem': 'up' if bas else None, 'events': couche(haut, False)})
        if bas:
            voices.append({'staff': k, 'stem': 'down', 'events': couche(bas, True)})
    return voices


BH = [  # (début en noires, degré, chiffrage) — ré mineur, 9/8
    (0, 'I', '5'), (1.5, 'I', '6'), (3, 'VII', '6'), (4.5, 'I', '5'), (6, 'I', '6'), (7.5, 'VII', '6'),
    (9, 'I', '5'), (10.5, 'I', '6'), (12, 'V', '♯'), (13.5, 'I', '5'), (16.5, 'VI', '6'),
    (18, 'II', '7'), (19.5, 'VII', '6/5'), (27, 'I', '6'), (31.5, 'IV', '7'), (33, 'II', '6/5'), (34.5, 'V/V', '6/5'), (36, 'V', '♯')]
for t1a, t2a, nom in ((0, 13.5, 'h27-mes1-3'), (13.5, 27, 'h27-mes4-6'), (27, 40.5, 'h27-mes7-9')):
    vo = extrait(PARTS, t1a, t2a)
    lb = []
    for (t, dg, chf) in BH:
        if t1a <= t < t2a:
            lb += [(t - t1a, dg, 0, BLUE), (t - t1a, chf, 1, BLUE)]
    save(Figure(QUAT, vo, key=-1, gap=96, unit=62, time=(9, 8) if t1a == 0 else None, beats_per_bar=4.5, groupe=1.5,
                labels=lb, rows=DEG, final=t2a > 40), nom)
# réduction harmonique (un accord par noire pointée, mesures 1 à 9)
def sonne(t):
    return [x['n'] for p in PARTS for x in p['notes'] if x['t'] <= t + 1e-6 < x['t'] + x['d']]


# ======================================================================== exercices du cours (chapitre 28)
EXOS, EXOS_K = {}, {}
an = [('Fa5', 'Sib4', 'Ré4', 'Ré3'), ('Do5', 'Mib4', 'Fa#3', 'Lab2'), ('Fa#4', 'Do4', 'Do4', 'Lab2'),
      ('Réb5', 'Lab4', 'Fa4', 'Fa3'), ('Do5', 'Fa#4', 'Ré4', 'Lab2'), ('Si4', 'Fa4', 'Sol3', 'Ré3')]
TONS_AN = ['La', 'Do', 'Do', 'Do', 'Do', 'Do']
for c, t in zip(an, TONS_AN):
    expect([c], tonic=t)
assert sixte_aug(an[1])['type'] == 'al' and sixte_aug(an[2])['type'] == 'it' and sixte_aug(an[4])['type'] == 'fr'
tt = [(i * 4, x, MUTED) for i, x in enumerate(['a) la', 'b) Do', 'c) Do', 'd) Do', 'e) Do', 'f) Do'])]
save(satb(an, unit=22, top_texts=tt), 'h28-ex1')
save(satb(an, unit=22, top_texts=tt, labels=labs(an, ['N', 'Al+6', 'It+6', 'N', 'Fr+6', 'V'], ['6', '6+/5', '6+', '6', '6+/4', '+6']), rows=DEG), 'h29-c1')
AN_ERR = None

MENU5 = ['I', 'II', 'IV', 'V', 'VI', 'V7', 'N', 'It6', 'Fr6', 'Al6']
P4.faire_exo(EXOS, 'h28-ex2', 'bc', 'I IV N6 V7 I VI II6 V7 I', 'La', 0, durees=[2, 2, 2, 2, 2, 2, 2, 2, 4], dossier=IMG,
             menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'N'])
P4.faire_exo(EXOS, 'h28-ex3', 'bc', 'I VI It6 V I IV Al6 I64 V7 I', 'Ré', -1, durees=[2, 2, 2, 2, 2, 2, 2, 2, 4, 4], dossier=IMG, menu=MENU5)
P4.faire_exo(EXOS, 'h28-ex4', 'bd', 'I IV@Do V7@Do I II6 I64 V7 I', 'Do', 0, durees=[2, 2, 2, 2, 2, 2, 2, 2], dossier=IMG)
P4.faire_exo(EXOS, 'h28-ex5', 'cd', 'I IV N6 I64 V7 I', 'Mi', 1, dossier=IMG, menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'N'], sop_min='Ré4')
for k in range(2, 6):
    os.replace(os.path.join(IMG, f'h28-ex{k}-c.png'), os.path.join(IMG, f'h29-c{k}.png'))
    SONS[f'h29-c{k}'] = SONS.pop(f'h28-ex{k}-c')
# exercice 6 : un choral à récrire pour quatuor (sur papier) ; le corrigé en batteries
ch6, d6, c6, s6, _ = realise('I VI II65 V7 I IV V7 I', 'Sol', 1, durees=[2, 2, 2, 2, 2, 2, 2, 2])
save(satb(ch6, key=1, unit=22, time=(4, 4), labels=labs(ch6, d6, c6), rows=DEG), 'h28-ex6')
quatuor(texture(ch6, 'batteries'), 'h29-c6', key=1, labels=[l for l in labs(ch6, d6, c6) if l[2] == 0], rows=['degrés'])

# ======================================================================== cahier : chapitres 24 à 26
PAGES = {24: [], 25: [], 26: []}


def ajouter(chap, typ, plan, t, a, titre, quatuor_corrige=False, **kw):
    num = len(PAGES[chap]) + 1
    nom = f'c{chap}-{num:02d}'
    sol, seq, degs, chifs = P4.faire_exo(EXOS_K, nom, typ, plan, t, a, **kw)
    if any(s.get('pedale') for s in seq):
        EXOS_K[nom]['pedales'] = [i for i, s in enumerate(seq) if s.get('pedale')]
    if quatuor_corrige:
        durees = kw.get('durees') or [4] * len(sol)
        ch = [tuple(c) + (d,) for c, d in zip(sol, durees)]
        quatuor(texture(ch, quatuor_corrige), nom + '-q', key=a, labels=[l for l in labs(ch, degs, chifs) if l[2] == 0],
                rows=['degrés'], dossier=IMGK)
    PAGES[chap].append((nom, typ, t, a, titre, quatuor_corrige))


H8 = [2, 2, 2, 2, 2, 2, 2, 2]
ajouter(24, 'bc', 'I IV N6 V I', 'La', 0, 'la sixte napolitaine', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'N'])
ajouter(24, 'bc', 'I VI N6 I64 V7 I', 'Ré', -1, 'napolitaine et quarte et sixte', durees=[2, 2, 2, 2, 4, 4], menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'N'])
ajouter(24, 'bc', 'I N6 V7 I', 'Do', 0, 'napolitaine en majeur', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'N'])
ajouter(24, 'bc', 'I IV It6 V I', 'Mi', 1, 'sixte italienne', menu=MENU5)
ajouter(24, 'bc', 'I VI Fr6 V I', 'La', 0, 'sixte française', menu=MENU5)
ajouter(24, 'bc', 'I IV Al6 I64 V7 I', 'Ré', -1, 'sixte allemande', durees=[2, 2, 2, 2, 4, 4], menu=MENU5)
ajouter(24, 'cd', 'I IV N6 I64 V7 I', 'La', 0, '', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'N'])
ajouter(25, 'bd', 'I IV@Do V7@Do I V I', 'Do', 0, 'pédale de tonique')
ajouter(25, 'bd', 'I IV V I64@Ré V7 I', 'Sol', 1, 'pédale de dominante')
ajouter(25, 'bc', 'I I6 IV II6 I64 V7 I', 'Fa', -1, 'la grande cadence', durees=[2, 2, 2, 2, 2, 2, 4], menu=['I', 'II', 'IV', 'V', 'VI', 'V7'])
ajouter(25, 'bc', 'I V6 I IV6 V', 'Mi', 1, 'demi-cadence phrygienne', menu=['I', 'II', 'IV', 'V', 'VI', 'V7'])
ajouter(25, 'cd', 'I VI II6 I64 V7 I', 'Ré', 2, '', menu=['I', 'II', 'IV', 'V', 'VI', 'V7'], sop_min='Ré4')
ajouter(26, 'bc', 'I IV II6 I64 V7 I', 'Sol', 1, 'puis en batteries', quatuor_corrige='batteries', durees=[2, 2, 2, 2, 4, 4], menu=['I', 'II', 'IV', 'V', 'VI', 'V7'])
ajouter(26, 'bc', 'I VI II65 V7 I', 'Ré', 2, 'puis avec une basse en octaves', quatuor_corrige='basse', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'II7'])
ajouter(26, 'bd', 'I V65 I IV V7/V V I', 'La', 3, 'puis en batteries', quatuor_corrige='batteries', durees=[2, 2, 2, 2, 2, 2, 4])
ajouter(26, 'cd', 'I IV I6 II6 V7 I', 'Do', 0, 'puis en batteries', quatuor_corrige='batteries', menu=['I', 'II', 'IV', 'V', 'VI', 'V7'])

print('partie 5 :', len(EXOS), 'exercices du cours,', len(EXOS_K), 'exercices du cahier')
json.dump(EXOS, open(os.path.join(COURS, 'exercices-partie5.json'), 'w'), ensure_ascii=False)
json.dump(EXOS_K, open(os.path.join(CAHIER, 'exercices-cahier5.json'), 'w'), ensure_ascii=False)
json.dump({k: v for k, v in SONS.items() if k.startswith('h')}, open(os.path.join(COURS, 'audio', 'sons-partie5.json'), 'w'), indent=0)
json.dump({k: v for k, v in SONS.items() if k.startswith('c')}, open(os.path.join(CAHIER, 'audio', 'sons-cahier5.json'), 'w'), indent=0)
json.dump({'E': {k: [EXOS[k]['solution'], EXOS[k].get('degres'), EXOS[k].get('chiffres'), EXOS[k].get('harmonie')] for k in EXOS},
           'ph24': [ph24, d24, c24], 'gc': [gc, dgc], 'QM': QM, 'pdo': [pdo, dpd], 'ch26': [ch26, d26]}, open('/tmp/p5.json', 'w'), ensure_ascii=False)

# ======================================================================== pages du cahier
TON = {('Do', 0): 'Do majeur', ('Sol', 1): 'Sol majeur', ('Fa', -1): 'Fa majeur', ('Ré', 2): 'Ré majeur', ('La', 3): 'La majeur',
       ('La', 0): 'la mineur', ('Mi', 1): 'mi mineur', ('Ré', -1): 'ré mineur', ('Sol', -2): 'sol mineur'}
TITRES = {24: ('24-napolitaine-et-sixtes-augmentees', 'La sixte napolitaine et les sixtes augmentées', '24-la-sixte-napolitaine-et-les-sixtes-augmentees.md'),
          25: ('25-pedales-et-cadences', 'Pédales et cadences classiques', '25-pedales-et-formules-de-cadence.md'),
          26: ('26-ecrire-pour-quatuor', 'Écrire pour quatuor à cordes', '26-ecrire-pour-quatuor-a-cordes.md')}
TYPES = {'bc': 'Basse chiffrée', 'bd': 'Basse donnée', 'sb': "Compléter l'alto et le ténor", 'cd': 'Chant donné', 'corriger': 'Chasse aux fautes'}
ordre = [(21, '21-dominantes-secondaires-et-modulation', 'Dominantes secondaires et modulation')] + [(c, TITRES[c][0], TITRES[c][1]) for c in (24, 25, 26)]
for k, chap in enumerate((24, 25, 26)):
    fic, titre, cours_md = TITRES[chap]
    prev = ordre[k]
    nav = f"[← {prev[2]}]({prev[1]}.md) · [Sommaire du cahier](README.md)"
    if k < 2:
        nx = ordre[k + 2]
        nav += f" · [{nx[2]} →]({nx[1]}.md)"
    L = [nav, '', f'## {titre}', '', f"Ces exercices accompagnent le [chapitre {chap}](../cours/{cours_md}) du cours.", '',
         "Dans la version web (`cahier.html`), chaque exercice se fait **directement sur la portée**, avec les corrections au fur et à mesure. "
         "Le menu des accords propose aussi la sixte napolitaine (N) et les sixtes augmentées (It+6, Fr+6, Al+6).", '']
    if chap == 26:
        L += ["Ici, on réalise d'abord l'exercice à quatre voix, sur la grande portée, comme d'habitude. Puis, **sur papier**, on le récrit pour "
              "quatuor à cordes avec la texture demandée (voir le [chapitre 26](../cours/26-ecrire-pour-quatuor-a-cordes.md)). "
              "Les corrigés montrent les deux versions.", '']
    for j, (nom, typ, t, a, sous, q) in enumerate(PAGES[chap]):
        n = f'{chap}.{j + 1}'
        tt = f"{TYPES[typ]} en {TON[(t, a)]}" + (f' ({sous})' if sous else '')
        L += [f'### Exercice {n} · {tt}', '', P4.CONSIGNE4[typ], '', f'![Exercice {n}](images/{nom}.png)', '']
    L += ['### Corrigés', '']
    for j, (nom, typ, t, a, sous, q) in enumerate(PAGES[chap]):
        n = f'{chap}.{j + 1}'
        L += [f"**Exercice {n}** : une solution parmi d'autres.", '', f'![Corrigé {n}](images/{nom}-c.png)', '',
              f'🔊 [Écouter](audio/{nom}-c.mp3) · [MIDI](audio/{nom}-c.mid)', '']
        if q:
            L += [f'Pour quatuor à cordes ({ {"batteries": "en batteries", "basse": "avec une basse en octaves"}[q] }) :', '',
                  f'![Corrigé {n} pour quatuor](images/{nom}-q.png)', '', f'🔊 [Écouter](audio/{nom}-q.mp3) · [MIDI](audio/{nom}-q.mid)', '']
    L += ['---', '', nav, '']
    open(os.path.join(CAHIER, fic + '.md'), 'w').write('\n'.join(L))

# lien depuis la page 21
p21 = os.path.join(CAHIER, '21-dominantes-secondaires-et-modulation.md')
s = open(p21).read()
s = re.sub(r'\[Sommaire du cahier\]\(README\.md\)(?! ·)', '[Sommaire du cahier](README.md) · [La sixte napolitaine et les sixtes augmentées →](24-napolitaine-et-sixtes-augmentees.md)', s)
open(p21, 'w').write(s)

# sommaire du cahier
NT = {'bc': 'basse chiffrée', 'bd': 'basse donnée', 'sb': "compléter l'alto et le ténor", 'cd': 'chant donné', 'corriger': 'chasse aux fautes'}
readme = os.path.join(CAHIER, 'README.md')
R = [l for l in open(readme).read().split('\n') if not re.match(r'- \[.*\]\((24|25|26)-', l)]
i = next(k for k, l in enumerate(R) if '(21-dominantes' in l)
add = []
for chap in (24, 25, 26):
    sortes = {}
    for p in PAGES[chap]:
        sortes[NT[p[1]]] = sortes.get(NT[p[1]], 0) + 1
    add.append(f"- [{TITRES[chap][1]}]({TITRES[chap][0]}.md) (chapitre {chap} du cours) : " + ', '.join(f'{v} × {k}' for k, v in sortes.items()))
R = R[:i + 1] + add + R[i + 1:]
txt = '\n'.join(R)
n5 = sum(len(v) for v in PAGES.values())
m = re.search(r'dont (\d+) basses données, (\d+) chants donnés,? (?:et )?(\d+) exercices sur le choral(?:,| et) (\d+) sur les accords de quatre sons', txt)
base_n = 54 + int(m.group(4))
txt = re.sub(r'\*\*\d+ exercices\*\* en tout, dont .*?Tous les corrigés',
             f"**{base_n + n5} exercices** en tout, dont {m.group(1)} basses données, {m.group(2)} chants donnés, {m.group(3)} exercices sur le choral, "
             f"{m.group(4)} sur les accords de quatre sons et {n5} sur le style classique. Tous les corrigés", txt)
open(readme, 'w').write(txt)
print('pages du cahier écrites')
