"""Usage : python3 outils/build_partie3.py

Partie 3 (le choral) : figures du cours (chapitres 13 à 17), exercices interactifs avec rythme,
et la série du cahier d'exercices consacrée au choral. Tout est vérifié."""
import json, os
from graveur import Figure, SONS, BLUE, GREEN, RED, ORANGE, MUTED
from choral import (classer, verifier_choral, cellules_en_voix, harmonies_cellules, orner, ROLE)
from generateur import phrase, accord, parse, chiffre
from verif import etat, triad
from lire_mxl import lire

ICI = os.path.dirname(os.path.abspath(__file__))
COURS = os.path.join(ICI, '..', 'cours')
CAHIER = os.path.join(ICI, '..', 'cahier')
IMGC, IMGK = os.path.join(COURS, 'images'), os.path.join(CAHIER, 'images')
DEGN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
ABR = {'p': 'p', 'b': 'b', 'r': 'r', 'app': 'app', 'e': 'é', 'ant': 'ant', '?': '?'}
FR = ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si']


def vide(n):
    return [[{'b': None, 'lie': False} for v in range(4)] for i in range(n)]


def roles_par_attaque(voix, harm):
    R = classer(voix, harm)
    out = {}
    for vi in range(4):
        for nt, ro in R[vi]:
            out[(vi, round(nt[0], 4))] = ro
    return out


def figure(notes, extra, durees, armure=0, harm=None, labels=None, mesure=4, anacrouse=0, nct=True, rows=None,
           cacher=(), num=None, unit=40, fermatas=()):
    """Grave une réalisation « en cellules » ; les notes étrangères sont colorées et nommées."""
    roles = roles_par_attaque(cellules_en_voix(notes, extra, durees), harm) if (harm and nct) else {}
    voices = []
    for v, (st, stem) in enumerate([(0, 'up'), (0, 'down'), (1, 'up'), (1, 'down')]):
        ev, t = [], 0
        for i, d in enumerate(durees):
            a, x = notes[i][v], extra[i][v]
            parts = [(a, d / 2), (x['b'], d / 2)] if x['b'] else [(a, d)]
            for k, (n, dd) in enumerate(parts):
                op = {}
                if n is None or v in cacher:
                    op['hide'] = True
                    n = None
                ro = roles.get((v, round(t, 4)))
                if n and ro and ro != 'R':
                    op.update(color=RED if ro == '?' else GREEN, lab=(num.pop(0) if num else ABR[ro]))
                if (i, v) in fermatas and k == len(parts) - 1:
                    op['fermata'] = True
                if k == 0 and x.get('lie') and ev and n:
                    ev[-1] = (ev[-1][0], ev[-1][1], dict(ev[-1][2], tie=True))
                ev.append((n, dd, op))
                t += dd
        voices.append({'staff': st, 'stem': stem, 'events': ev})
    return Figure([{'clef': 'treble'}, {'clef': 'bass'}], voices, key=armure, brace=(0, 1), gap=110, unit=unit,
                  beats_per_bar=mesure, time=(mesure, 4), pickup=anacrouse, labels=labels or [], rows=rows)


def labs(durees, degs=None, chifs=None):
    out, t = [], 0
    for i, d in enumerate(durees):
        if degs and degs[i]:
            out.append((t, degs[i], 0, BLUE, False))
        if chifs and chifs[i]:
            out.append((t, chifs[i], 1, BLUE, False))
        t += d
    return out


def deg_chif(sol, tonique, armure):
    degs, chifs = [], []
    for c in sol:
        d = (triad(c)[0] - FR.index(tonique.rstrip('b#'))) % 7
        degs.append(DEGN[d])
        chifs.append(chiffre(tonique, armure, d, etat(c)))
    return degs, chifs


def verifier(notes, extra, durees, accords, tonique, allow=()):
    e, r, s = verifier_choral(cellules_en_voix(notes, extra, durees), harmonies_cellules(accords, durees), tonique, allow_third=allow)
    assert not e, e
    return r


# ======================================================================== chapitre 13 : les sortes de notes étrangères
C_I, C_IV, C_V = ['Do', 'Mi', 'Sol'], ['Fa', 'La', 'Do'], ['Sol', 'Si', 'Ré']
paires = [
    ('passage', [['Do5', 'Mi4', 'Do4', 'Do3'], ['La4', 'Fa4', 'Do4', 'Fa2']], [C_I, C_IV], {(0, 0): {'b': 'Si4'}}, 'p'),
    ('broderie', [['Do5', 'Mi4', 'Do4', 'Do3'], ['La4', 'Fa4', 'Do4', 'Fa2']], [C_I, C_IV], {(0, 2): {'b': 'Si3'}}, 'b'),
    ('échappée', [['Mi5', 'Sol4', 'Do4', 'Do3'], ['Ré5', 'Sol4', 'Si3', 'Sol2']], [C_I, C_V], {(0, 0): {'b': 'Fa5'}}, 'e'),
    ('anticipation', [['Ré5', 'Sol4', 'Si3', 'Sol2'], ['Do5', 'Mi4', 'Do4', 'Do3']], [C_V, C_I], {(0, 0): {'b': 'Do5'}}, 'ant'),
    ('retard', [['Do5', 'La4', 'Fa4', 'Fa3'], ['Si4', 'Sol4', 'Ré4', 'Sol3']], [C_IV, C_V], {(1, 0): {'b': 'Si4', 'lie': True, 'a': 'Do5'}}, 'r'),
    ('appoggiature', [['La4', 'Fa4', 'Do4', 'Fa2'], ['Si4', 'Ré4', 'Sol3', 'Sol2']], [C_IV, C_V], {(1, 0): {'b': 'Si4', 'a': 'Do5'}}, 'app'),
]
notes, extra, accs, durs, boxes, degl = [], [], [], [], [], []
for k, (nom, ch, ac, deco, attendu_) in enumerate(paires):
    n = [c[:] for c in ch]
    x = vide(2)
    for (i, v), dd in deco.items():
        if 'a' in dd:
            n[i][v] = dd['a']
        x[i][v] = {'b': dd['b'], 'lie': dd.get('lie', False)}
    r = verifier(n, x, [1, 1], ac, 'Do')
    trouves = [ro for vi in range(4) for nt, ro in r[vi] if ro != 'R']
    assert trouves == [attendu_], (nom, trouves)
    notes += n
    extra += x
    accs += ac
    durs += [1, 1]
    boxes.append((4 * k, 4 * k + 2, nom))
degl = ['I', 'IV', 'I', 'IV', 'I', 'V', 'V', 'I', 'IV', 'V', 'IV', 'V']
# deux temps de silence entre les exemples : chaque paire dans sa mesure (2 noires + 1 blanche vide)
N2, X2, D2, A2, DG = [], [], [], [], []
for k in range(6):
    N2 += notes[2 * k:2 * k + 2] + [[None] * 4]
    X2 += extra[2 * k:2 * k + 2] + vide(1)
    D2 += [1, 1, 2]
    A2 += accs[2 * k:2 * k + 2] + [[]]
    DG += degl[2 * k:2 * k + 2] + ['']
f = figure(N2, X2, D2, harm=harmonies_cellules(A2, D2), labels=labs(D2, DG), rows=['degrés'], unit=34)
f.boxes = [(4 * k, 4 * k + 2.4, [GREEN, GREEN, ORANGE, ORANGE, RED, RED][k], nom) for k, (a, b, nom) in enumerate(boxes)]
f.save(os.path.join(IMGC, 'h13-sortes.png'))

# une phrase ornée : passages, broderie, retard à la cadence
ps, allow, seq = phrase('I V6 I IV II6 V I', 'Do', 0, sop=['Mi5', 'Ré5', 'Do5', 'Do5', 'La4', 'Si4', 'Do5'])
sol = [list(c) for c in ps[0]]
acc = [accord('Do', 0, d) for d, e in seq]
dur = [1] * 6 + [2]
nu = [c[:] for c in sol]
xo, faits = orner(nu, dur, acc, 'Do', 0, voulu=5)
verifier(nu, xo, dur, acc, 'Do')
dg, cf = deg_chif(sol, 'Do', 0)
figure(sol, vide(7), dur, harm=harmonies_cellules(acc, dur), labels=labs(dur, dg, cf), rows=['degrés', 'chiffrage']).save(os.path.join(IMGC, 'h13-avant.png'))
figure(nu, xo, dur, harm=harmonies_cellules(acc, dur), labels=labs(dur, dg, cf), rows=['degrés', 'chiffrage']).save(os.path.join(IMGC, 'h13-apres.png'))
P13 = {'faits': faits, 'notes': nu, 'extra': xo}

# une faute : des quintes cachées par une note de passage
fq_n = [['Mi5', 'Sol4', 'Do4', 'Do3'], ['Ré5', 'Sol4', 'Si3', 'Sol2']]
fq_x = vide(2)
fq_x[0][1] = {'b': 'La4', 'lie': False}          # alto Sol-La / basse Do... on vérifie ci-dessous
e, r, s = verifier_choral(cellules_en_voix(fq_n, fq_x, [1, 1]), harmonies_cellules([C_I, C_V], [1, 1]), 'Do')
# ======================================================================== chapitre 14 : un choral de Bach
titre, P = lire(os.path.join(ICI, 'bach', 'bwv269.mxl'))
BW = []
for vi, p in enumerate(P):
    ev, tot = [], 0
    for n, d, tie, ferm, m in p['ev']:
        if tot >= 21:
            break
        if tie and ev:
            ev[-1][2]['tie'] = True
        ev.append([n, d, {'fermata': True} if ferm and vi in (0, 3) else {}])
        tot += d
    BW.append(ev)
G_I, G_V, G_VI, G_IV, G_II = ['Sol', 'Si', 'Ré'], ['Ré', 'Fa#', 'La'], ['Mi', 'Sol', 'Si'], ['Do', 'Mi', 'Sol'], ['La', 'Do', 'Mi']
HB = [(0, 1, G_I), (1, 1, G_I), (2, 1, G_VI), (3, 1, G_V), (4, 1, G_I), (5, 1, G_V), (6, 1, G_VI), (7, 2, G_IV), (9, 1, G_I),
      (10, 2, G_V), (12, 1, G_I), (13, 1, G_V), (14, 1, G_I), (15, 1, G_II), (16, 1, G_I), (17, 1, G_II + ['Sol']), (18, 1, G_V), (19, 2, G_I)]
RB = classer([[tuple(e) for e in v] for v in BW], HB)
nct = {(vi, round(nt[0], 3)): ro for vi in range(4) for nt, ro in RB[vi] if ro != 'R'}
assert set(nct.values()) <= {'p', 'b', 'r'}, nct
BACH_NCT = sorted((t, vi, ro) for (vi, t), ro in nct.items())
DB = ['I', 'I', 'VI', 'V', 'I', 'V', 'VI', 'IV', 'I', 'V', 'I', 'V', 'I', 'II', 'I', 'II', 'V', 'I']
CB = ['5', '5', '5', '6', '5', '6 5', '5', '5', '5', '5', '5', '6', '5', '5', '6', '6/5', '5', '5']


def bach_fig(t0, t1, nom):
    voices = []
    for vi, ev in enumerate(BW):
        out, t = [], 0
        for n, d, op in ev:
            if t >= t0 - 1e-9 and t < t1 - 1e-9:
                o = dict(op)
                ro = nct.get((vi, round(t, 3)))
                if not ro:   # un retard commence pendant la note (note tenue par-dessus le changement d'accord)
                    ro = next((r for (v2, t2), r in nct.items() if v2 == vi and r == 'r' and t < t2 < t + d), None)
                if ro:
                    o.update(color=GREEN, lab=ABR[ro])
                # la partie de note tenue au-delà d'un changement d'harmonie (retard)
                out.append((n, d, o))
            t += d
        voices.append({'staff': 0 if vi < 2 else 1, 'stem': 'up' if vi % 2 == 0 else 'down', 'events': out})
    lab = [(a - t0, DB[k], 0, BLUE, False) for k, (a, d, ns) in enumerate(HB) if t0 <= a < t1]
    lab += [(a - t0, CB[k], 1, BLUE, False) for k, (a, d, ns) in enumerate(HB) if t0 <= a < t1]
    Figure([{'clef': 'treble'}, {'clef': 'bass'}], voices, key=1, beats_per_bar=3, time=(3, 4), pickup=1, brace=(0, 1), gap=110,
           unit=40, labels=lab, rows=['degrés', 'chiffrage']).save(os.path.join(IMGC, nom + '.png'))


bach_fig(0, 12, 'h14-phrase1')
bach_fig(11.999, 21, 'h14-phrase2')
# la seconde phrase commence par une anacrouse d'un temps elle aussi : on recale
SONS['h14-phrase2']['voix'] = SONS['h14-phrase2']['voix']

# ======================================================================== chapitre 15 : harmoniser une mélodie de choral
MEL = ['Sol4', 'La4', 'Si4', 'Do5', 'Ré5', 'Si4', 'Do5', 'La4', 'Si4', 'La4', 'Sol4']
PLAN = 'I V6 I IV6 V I IV II6 I64 V I'
ps, allow, seq = phrase(PLAN, 'Sol', 1, sop=MEL)
s15 = [list(c) for c in ps[0]]
a15 = [accord('Sol', 1, d) for d, e in seq]
d15 = [1] * 10 + [2]
dg15, cf15 = deg_chif(s15, 'Sol', 1)
n15 = [c[:] for c in s15]
x15, f15 = orner(n15, d15, a15, 'Sol', 1, voix=(1, 2, 3), voulu=4, retard=False)
verifier(n15, x15, d15, a15, 'Sol')
H15 = harmonies_cellules(a15, d15)
figure([[c[0], None, None, None] for c in s15], vide(11), d15, armure=1, harm=H15).save(os.path.join(IMGC, 'h15-melodie.png'))
figure([[c[0], None, None, c[3]] for c in s15], vide(11), d15, armure=1, harm=H15, labels=labs(d15, dg15, cf15), rows=['degrés', 'chiffrage']).save(os.path.join(IMGC, 'h15-basse.png'))
figure(s15, vide(11), d15, armure=1, harm=H15, labels=labs(d15, dg15, cf15), rows=['degrés', 'chiffrage']).save(os.path.join(IMGC, 'h15-complet.png'))
figure(n15, x15, d15, armure=1, harm=H15, labels=labs(d15, dg15, cf15), rows=['degrés', 'chiffrage']).save(os.path.join(IMGC, 'h15-orne.png'))

# ======================================================================== exercices interactifs
EXOS_C, EXOS_K = {}, {}
GUIDE_CHORAL = [
    {'type': 'degres', 'titre': 'Choisis les accords',
     'consigne': "Un accord par temps. Pour chaque temps, choisis un accord qui contient la note réelle du soprano (une croche de passage ou un retard dans la mélodie ne comptent pas). Commence sur I, finis par V-I."},
    {'type': 'voix', 'voix': [3], 'titre': 'Écris la basse',
     'consigne': "En noires : la fondamentale ou la tierce de chaque accord, en mouvement contraire avec le soprano autant que possible."},
    {'type': 'voix', 'voix': [1, 2], 'titre': "Complète l'alto et le ténor",
     'consigne': "En noires : notes communes, plus court chemin, bonnes doublures."},
    {'type': 'voix', 'voix': [1, 2, 3], 'titre': 'Ajoute des notes de passage', 'objectif': {'total': 2},
     'consigne': "Là où une voix fait une tierce, sélectionne la note et clique sur « ♪♪ croches » : la deuxième croche devient une note de passage. Ajoute au moins deux notes étrangères, sans créer de quintes ni d'octaves."},
]


def exo_orner(dest, nom, plan, tonique, armure, sop=None, objectif=None, voulu=4, retard=True, durees=None):
    ps, allow, seq = phrase(plan, tonique, armure, sop=sop, n=12)
    acc = [accord(tonique, armure, d) for d, e in seq]
    meilleur = None
    for p in ps:       # parmi les meilleures réalisations, celle qui se prête le mieux aux ornements
        sol = [list(c) for c in p]
        dur = durees or [1] * (len(sol) - 1) + [2]
        nu = [c[:] for c in sol]
        xo, faits = orner(nu, dur, acc, tonique, armure, voulu=voulu, retard=retard, allow=allow)
        roles = [ro for vi in range(4) for nt, ro in classer(cellules_en_voix(nu, xo, dur), harmonies_cellules(acc, dur))[vi] if ro not in ('R', '?')]
        okobj = all((len(roles) if k == 'total' else roles.count(k)) >= need for k, need in (objectif or {}).items())
        if okobj:
            meilleur = (sol, dur, nu, xo, faits)
            break
    assert meilleur, (nom, 'objectif impossible')
    assert sum(meilleur[1]) % 4 == 0, (nom, 'mesures incomplètes')
    sol, dur, nu, xo, faits = meilleur
    verifier(nu, xo, dur, acc, tonique, allow)
    dg, cf = deg_chif(sol, tonique, armure)
    for k, need in (objectif or {}).items():
        roles = [ro for vi in range(4) for nt, ro in classer(cellules_en_voix(nu, xo, dur), harmonies_cellules(acc, dur))[vi] if ro not in ('R', '?')]
        assert (len(roles) if k == 'total' else roles.count(k)) >= need, (nom, roles, objectif)
    dest[nom] = {'rythme': True, 'donne': sol, 'donneX': vide(len(sol)), 'solution': nu, 'solutionX': xo, 'durees': dur,
                 'voix': [0, 1, 2, 3], 'tonique': tonique, 'armure': armure, 'degres': dg, 'chiffres': cf,
                 'harmonie': [(triad(c)[0] - FR.index(tonique)) % 7 for c in sol], 'tierce': sorted(allow),
                 'chant': False, 'corriger': False, 'guide': None, 'objectif': objectif, 'isoles': False}
    return sol, xo, nu, dur, acc, dg, cf


def exo_choral(dest, nom, plan, tonique, armure, melodie, durees=None, mesure=4, anacrouse=0, fermatas=()):
    """melodie : liste de (note, deuxième croche | None, lié à la précédente)."""
    reel = [m[3] if len(m) > 3 else (m[1] if (m[2] and m[1]) else m[0]) for m in melodie]
    melodie = [m[:3] for m in melodie]
    ps, allow, seq = phrase(plan, tonique, armure, sop=reel, n=12)
    acc = [accord(tonique, armure, d) for d, e in seq]
    choix = None
    for p in ps:
        sol = [list(c) for c in p]
        dur = durees or [1] * (len(sol) - 1) + [2]
        for i, (a, b, lie) in enumerate(melodie):
            sol[i][0] = a
        xs = vide(len(sol))
        for i, (a, b, lie) in enumerate(melodie):
            xs[i][0] = {'b': b, 'lie': lie}
        verifier(sol, xs, dur, acc, tonique, allow)
        nu = [c[:] for c in sol]
        xo2, faits = orner(nu, dur, acc, tonique, armure, voix=(1, 2, 3), voulu=3, retard=False, allow=allow, extra0=xs)
        if faits >= 2:
            choix = (p, sol, dur, xs, nu, xo2)
            break
    assert choix, (nom, 'pas assez de notes de passage possibles')
    p0, sol, dur, xs, nu, xo2 = choix
    verifier(nu, xo2, dur, acc, tonique, allow)
    donne = [[c[0], None, None, None] for c in sol]
    dg, cf = deg_chif([[r] + list(c[1:]) for r, c in zip(reel, p0)], tonique, armure)
    dest[nom] = {'rythme': True, 'donne': donne, 'donneX': xs, 'solution': nu, 'solutionX': xo2, 'durees': dur,
                 'voix': [1, 2, 3], 'tonique': tonique, 'armure': armure, 'degres': None, 'chiffres': None,
                 'tierce': sorted(allow), 'chant': True, 'corriger': False, 'guide': GUIDE_CHORAL, 'objectif': None,
                 'isoles': False, 'mesure': mesure, 'anacrouse': anacrouse,
                 'harmonie': [d for d, e in seq], 'sopReel': reel, 'fin': seq[-1][0]}
    return sol, xs, nu, xo2, dur, acc, dg, cf


def images_exo(img, nom, enonce, corrige, dur, acc, armure, dg=None, cf=None, mesure=4, anacrouse=0, montrer=True):
    H = harmonies_cellules(acc, dur)
    (n0, x0, cache) = enonce
    figure(n0, x0, dur, armure=armure, harm=H, nct=False, cacher=cache, labels=labs(dur, dg if montrer else None, cf if montrer else None),
           rows=['degrés', 'chiffrage'] if montrer else None, mesure=mesure, anacrouse=anacrouse).save(os.path.join(img, nom + '.png'))
    SONS.pop(nom, None)
    figure(corrige[0], corrige[1], dur, armure=armure, harm=H, labels=labs(dur, dg, cf), rows=['degrés', 'chiffrage'],
           mesure=mesure, anacrouse=anacrouse).save(os.path.join(img, nom + '-c.png'))


# --- exercices du cours (chapitre 16)
# 1. reconnaître : une phrase ornée, notes étrangères numérotées
ps, allow, seq = phrase('I IV V I II6 V I', 'Do', 0)
s1 = [list(c) for c in ps[0]]
a1 = [accord('Do', 0, d) for d, e in seq]
d1 = [1] * 6 + [2]
n1 = [c[:] for c in s1]
x1, _ = orner(n1, d1, a1, 'Do', 0, voulu=6)
# une broderie et une anticipation en plus, si possible sans faute
def essai(n, x, d, a, i, v, val):
    ancien = x[i][v]
    x[i][v] = val
    try:
        verifier(n, x, d, a, 'Do')
        return True
    except AssertionError:
        x[i][v] = ancien
        return False
fin = len(n1) - 2
if not x1[fin][0]['b'] and not x1[fin][0]['lie']:
    essai(n1, x1, d1, a1, fin, 0, {'b': n1[fin + 1][0], 'lie': False})       # anticipation
from graveur import N as _N, dpos as _dpos
for i in range(len(n1) - 1):
    fait = False
    for v in (1, 2, 3):
        if n1[i][v] == n1[i + 1][v] and not x1[i][v]['b'] and not x1[i + 1][v]['lie']:
            p = _dpos(_N(n1[i][v])) - 1
            if essai(n1, x1, d1, a1, i, v, {'b': FR[p % 7] + str(p // 7), 'lie': False}):
                fait = True
                break
    if fait:
        break
verifier(n1, x1, d1, a1, 'Do')
r1 = classer(cellules_en_voix(n1, x1, d1), harmonies_cellules(a1, d1))
liste1 = sorted((nt[0], vi, ro) for vi in range(4) for nt, ro in r1[vi] if ro != 'R')
dg1, cf1 = deg_chif(s1, 'Do', 0)
numeros = [str(k + 1) for k in range(len(liste1))]
# numérotation dans l'ordre des attaques (figure() parcourt voix par voix : on prépare l'ordre)
ordre = {}
for k, (t, vi, ro) in enumerate(liste1):
    ordre[(vi, round(t, 4))] = str(k + 1)
f = figure(n1, x1, d1, harm=harmonies_cellules(a1, d1), labels=labs(d1, dg1, cf1), rows=['degrés', 'chiffrage'])
for vv in f.voices:
    pass
# remplace les abréviations par les numéros
tt = {}
for vi, vv in enumerate(f.voices):
    t = 0
    ev2 = []
    for n, d, op in vv['events']:
        if op.get('lab'):
            op = dict(op, lab=ordre[(vi, round(t, 4))], color=ORANGE)
        ev2.append((n, d, op))
        t += d
    vv['events'] = ev2
f.save(os.path.join(IMGC, 'h16-ex1.png'))
SONS.pop('h16-ex1', None)
figure(n1, x1, d1, harm=harmonies_cellules(a1, d1), labels=labs(d1, dg1, cf1), rows=['degrés', 'chiffrage']).save(os.path.join(IMGC, 'h17-c1.png'))
EX1 = [(k + 1, ['soprano', 'alto', 'ténor', 'basse'][vi], ROLE[ro]) for k, (t, vi, ro) in enumerate(liste1)]

# 2. notes de passage
r = exo_orner(EXOS_C, 'h16-ex2', 'I V6 I IV II6 V I', 'Do', 0, objectif={'p': 3}, voulu=4, retard=False)
images_exo(IMGC, 'h16-ex2', (r[0], vide(len(r[0])), ()), (r[2], r[1]), r[3], r[4], 0, r[5], r[6])
os.replace(os.path.join(IMGC, 'h16-ex2-c.png'), os.path.join(IMGC, 'h17-c2.png')); SONS['h17-c2'] = SONS.pop('h16-ex2-c')
# 3. un retard à la cadence (et des passages)
r = exo_orner(EXOS_C, 'h16-ex3', 'I IV I6 II6 V I VI IV II6 V I', 'Sol', 1, objectif={'r': 1, 'total': 3}, voulu=3)
images_exo(IMGC, 'h16-ex3', (r[0], vide(len(r[0])), ()), (r[2], r[1]), r[3], r[4], 1, r[5], r[6])
os.replace(os.path.join(IMGC, 'h16-ex3-c.png'), os.path.join(IMGC, 'h17-c3.png')); SONS['h17-c3'] = SONS.pop('h16-ex3-c')
# 4. harmoniser une mélodie de choral (Fa majeur)
M4 = [('Fa4', None, False), ('Sol4', None, False), ('La4', None, False), ('Sib4', None, False), ('Do5', None, False), ('La4', None, False),
      ('Sib4', None, False), ('Sol4', None, False), ('La4', None, False), ('Sol4', None, False), ('Fa4', None, False)]
r = exo_choral(EXOS_C, 'h16-ex4', 'I V6 I IV I6 I IV II6 I64 V I', 'Fa', -1, M4)
images_exo(IMGC, 'h16-ex4', ([[c[0], None, None, None] for c in r[0]], r[1], (1, 2, 3)), (r[2], r[3]), r[4], r[5], -1, r[6], r[7], montrer=False)
os.replace(os.path.join(IMGC, 'h16-ex4-c.png'), os.path.join(IMGC, 'h17-c4.png')); SONS['h17-c4'] = SONS.pop('h16-ex4-c')
# 5. la première phrase du choral n°1 de Bach (3/4, anacrouse)
M5 = [('Sol4', None, False), ('Sol4', None, False), ('Sol4', None, True), ('Ré5', None, False), ('Si4', None, False), ('Si4', 'La4', True, 'La4'),
      ('Sol4', None, False), ('Sol4', None, False), ('Sol4', 'La4', True, 'Sol4'), ('Si4', None, False), ('La4', None, False)]
r = exo_choral(EXOS_C, 'h16-ex5', 'I I VI V6 I V VI IV IV I V', 'Sol', 1, M5, durees=[1] * 10 + [2], mesure=3, anacrouse=1)
EXOS_C['h16-ex5']['guide'][0] = dict(GUIDE_CHORAL[0])
images_exo(IMGC, 'h16-ex5', ([[c[0], None, None, None] for c in r[0]], r[1], (1, 2, 3)), (r[2], r[3]), r[4], r[5], 1, r[6], r[7], mesure=3, anacrouse=1, montrer=False)
os.replace(os.path.join(IMGC, 'h16-ex5-c.png'), os.path.join(IMGC, 'h17-c5.png')); SONS['h17-c5'] = SONS.pop('h16-ex5-c')

# --- cahier : série « le choral »
PAGE = []
k = 0
for (plan, ton, arm, obj, ret, titre) in (
        ('I VI IV II6 I64 V I', 'Do', 0, {'p': 3}, False, 'notes de passage'),
        ('I V6 I IV V I VI IV II6 V I', 'Ré', 2, {'p': 3, 'b': 1}, False, 'passages et broderie'),
        ('I V6 I IV6 V I VI II6 I64 V I', 'Fa', -1, {'r': 1, 'total': 3}, True, 'un retard à la cadence'),
        ('I V6 I IV II6 V I', 'La', 0, {'total': 3}, True, 'en la mineur')):
    k += 1
    nom = f'c13-{k:02d}'
    r = exo_orner(EXOS_K, nom, plan, ton, arm, objectif={k2: v2 for k2, v2 in obj.items() if k2 != 'b'}, voulu=sum(obj.values()) + 1, retard=ret)
    EXOS_K[nom]['objectif'] = obj
    if 'b' in obj:      # une broderie : sur une note répétée d'une voix intérieure
        nu, xo = r[2], r[1]
        ok = False
        for i in range(len(nu) - 1):
            for v in (1, 2):
                if nu[i][v] == nu[i + 1][v] and not xo[i][v]['b']:
                    from choral import entre
                    from graveur import N, dpos
                    p = dpos(N(nu[i][v])) - 1
                    cand = FR[p % 7] + str(p // 7)
                    from generateur import alts
                    al = alts(arm).get(p % 7, 0)
                    cand = FR[p % 7] + ('#' if al == 1 else 'b' if al == -1 else '') + str(p // 7)
                    xo[i][v] = {'b': cand, 'lie': False}
                    try:
                        verifier(nu, xo, r[3], r[4], ton)
                        ok = True
                        break
                    except AssertionError:
                        xo[i][v] = {'b': None, 'lie': False}
            if ok:
                break
        assert ok, 'pas de broderie possible'
        EXOS_K[nom]['solutionX'] = xo
    images_exo(IMGK, nom, (r[0], vide(len(r[0])), ()), (r[2], r[1]), r[3], r[4], arm, r[5], r[6])
    PAGE.append((nom, 'orner', ton, arm, titre, obj))
for (plan, ton, arm, mel, titre) in (
        ('I V6 I IV II6 V I', 'Do', 0, ['Do5', 'Ré5', 'Mi5', 'Do5', 'Ré5', 'Si4', 'Do5'], ''),
        ('I V6 I IV6 I V I II6 I64 V I', 'Sol', 1, ['Si4', 'La4', 'Sol4', 'Do5', 'Si4', 'La4', 'Si4', 'Do5', 'Si4', 'La4', 'Sol4'], ''),
        ('I IV I6 IV I64 V I', 'Ré', 2, ['Fa#4', 'Sol4', 'La4', 'Si4', 'La4', 'Mi4', 'Ré4'], ''),
        ('I IV6 V VI II6 V I', 'Fa', -1, ['La4', 'Sib4', 'Do5', 'La4', 'Sib4', 'Sol4', 'Fa4'], ''),
        ('I IV6 I6 V VI V I', 'La', 0, ['Mi5', 'Ré5', 'Do5', 'Si4', 'La4', 'Si4', 'La4'], 'mineur'),
        ('I IV6 I6 IV6 I64 V I', 'Ré', -1, ['La4', 'Sol4', 'Fa4', 'Sol4', 'La4', 'Mi4', 'Ré4'], 'mineur')):
    k += 1
    nom = f'c13-{k:02d}'
    n = len(mel)
    dur = [1] * (n - 1) + [2]
    assert sum(dur) % 4 == 0
    r = exo_choral(EXOS_K, nom, plan, ton, arm, [(m, None, False) for m in mel], durees=dur)
    images_exo(IMGK, nom, ([[c[0], None, None, None] for c in r[0]], r[1], (1, 2, 3)), (r[2], r[3]), r[4], r[5], arm, r[6], r[7], montrer=False)
    PAGE.append((nom, 'choral', ton, arm, titre, None))

json.dump(EXOS_C, open(os.path.join(COURS, 'exercices-partie3.json'), 'w'), ensure_ascii=False)
json.dump(EXOS_K, open(os.path.join(CAHIER, 'exercices-cahier3.json'), 'w'), ensure_ascii=False)
json.dump({k: v for k, v in SONS.items() if not k.startswith('c13')}, open(os.path.join(COURS, 'audio', 'sons-partie3.json'), 'w'), indent=0)
json.dump({k: v for k, v in SONS.items() if k.startswith('c13')}, open(os.path.join(CAHIER, 'audio', 'sons-cahier3.json'), 'w'), indent=0)
json.dump({'EX1': EX1, 'BACH': BACH_NCT, 'PAGE': PAGE, 'P13faits': faits, 'dg15': dg15, 'cf15': cf15, 'f15': f15}, open('/tmp/p3.json', 'w'), ensure_ascii=False)
print('partie 3 : figures et', len(EXOS_C), '+', len(EXOS_K), 'exercices vérifiés')

# ======================================================================== page du cahier
TON = {('Do', 0): 'Do majeur', ('Sol', 1): 'Sol majeur', ('Fa', -1): 'Fa majeur', ('Ré', 2): 'Ré majeur',
       ('La', 0): 'la mineur', ('Mi', 1): 'mi mineur', ('Ré', -1): 'ré mineur', ('Sol', -2): 'sol mineur'}
NOMOBJ = {'p': 'note de passage', 'b': 'broderie', 'r': 'retard', 'total': 'note étrangère'}
def objtxt(o):
    return ', '.join(f"{n} {NOMOBJ[k]}{'s' if n > 1 else ''}" for k, n in o.items())
nav = "[← Le mode mineur](10-le-mode-mineur.md) · [Sommaire du cahier](README.md) · [La septième de dominante →](18-la-septieme-de-dominante.md)"
L = [nav, '', '## Le choral : notes étrangères et harmonisation', '',
     "Ces exercices accompagnent les chapitres [13](../cours/13-les-notes-etrangeres.md), [14](../cours/14-analyse-un-choral-de-bach.md) "
     "et [15](../cours/15-harmoniser-une-melodie-de-choral.md) du cours.", '',
     "Dans la version web (`cahier.html`), on écrit directement sur la portée. Pour écrire deux croches, sélectionne une note et clique sur "
     "**♪♪ croches** ; pour préparer un retard, clique sur **⁀ lier**. Les notes étrangères reconnues s'affichent en vert (p, b, r…), "
     "celles qui sont mal traitées en rouge.", '']
for k, (nom, typ, ton, arm, titre, obj) in enumerate(PAGE):
    num = f'13.{k + 1}'
    if typ == 'orner':
        L += [f'### Exercice {num} · Orner une phrase en {TON[(ton, arm)]} ({titre})', '',
              f"Ajoute des notes étrangères à cette phrase écrite en noires : au moins {objtxt(obj)}. Ne change pas les accords, et ne crée ni quinte ni octave consécutive.", '',
              f'![Exercice {num}](images/{nom}.png)', '']
    else:
        L += [f'### Exercice {num} · Harmoniser une mélodie de choral en {TON[(ton, arm)]}', '',
              "Un accord par temps : choisis les accords, écris la basse, puis l'alto et le ténor en noires, puis ajoute au moins deux notes de passage.", '',
              f'![Exercice {num}](images/{nom}.png)', '']
L += ['### Corrigés', '']
for k, (nom, typ, ton, arm, titre, obj) in enumerate(PAGE):
    L += [f'**Exercice 13.{k + 1}** : une solution parmi d\'autres.', '', f'![Corrigé 13.{k + 1}](images/{nom}-c.png)', '',
          f'🔊 [Écouter](audio/{nom}-c.mp3) · [MIDI](audio/{nom}-c.mid)', '']
L += ['---', '', nav, '']
open(os.path.join(CAHIER, '13-le-choral.md'), 'w').write('\n'.join(L))
print('page du cahier écrite')
