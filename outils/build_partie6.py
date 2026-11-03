"""Usage : python3 outils/build_partie6.py

Partie 6 (le premier romantisme) : figures des chapitres 30 à 35, exercices interactifs du cours,
exercices du cahier (chapitres 30 à 32) et leurs pages. (Reconstruit aussi les parties 4 et 5, dont il réutilise les outils.)"""
import json, os, re
from graveur import Figure, satb, RED, GREEN, BLUE, ORANGE, MUTED, SONS, N, midi, dpos
from verif import check
from accords4 import phrase4, spec
from recherche import voicings
import build_partie4 as P4
import build_partie5 as P5

ICI = os.path.dirname(os.path.abspath(__file__))
COURS = os.path.join(ICI, '..', 'cours')
CAHIER = os.path.join(ICI, '..', 'cahier')
IMG, IMGK = os.path.join(COURS, 'images'), os.path.join(CAHIER, 'images')
DEG = ['degrés', 'chiffrage']
labs, realise, save, expect = P4.labs, P5.realise, P5.save, P5.expect
SONS.clear()


def couleurs(seq, ch):
    """Notes étrangères à la gamme du ton (emprunts, altérations) en rouge ; septièmes en rouge, sensibles en orange."""
    from generateur import alts
    from accords4 import TONS
    col = P5.couleurs(seq, ch)
    for i, s in enumerate(seq):
        t, a = s['ton']
        al = alts(a)
        for v in range(4):
            n = N(ch[i][v])
            if n['a'] != al.get(n['s'], 0) and s['label'] in ('IVm', 'VI♭', 'III♭', 'VII♭', 'IIø', 'V+'):
                col[(v, i)] = RED
    return col


# ======================================================================== chapitre 30 : emprunt au mineur, modulations par tierces
noms = [('I', 'C', ['Do4', 'Mi4', 'Sol4']), ('IV', 'F', ['Fa4', 'La4', 'Do5']), ('IVm', 'Fm', ['Fa4', 'Lab4', 'Do5']),
        ('VI', 'Am', ['La4', 'Do5', 'Mi5']), ('VI♭', 'A♭', ['Lab4', 'Do5', 'Mib5']), ('III♭', 'E♭', ['Mib4', 'Sol4', 'Sib4']),
        ('VII♭', 'B♭', ['Sib3', 'Ré4', 'Fa4']), ('IIø7', 'Dm7♭5', ['Ré4', 'Fa4', 'Lab4', 'Do5'])]
vv = []
for j in range(4):
    ev = []
    for d, nm, ns in noms:
        if j < len(ns):
            ev.append((ns[j], 4, {'color': RED} if ('b' in ns[j]) else {}))
        else:
            ev.append((None, 4, {'hide': True}))
    vv.append({'staff': 0, 'stem': None, 'events': ev})
save(Figure([{'clef': 'treble'}], vv, unit=18,
            labels=[(i * 4, d, 0, BLUE if d in ('I', 'IV', 'VI') else RED) for i, (d, nm, ns) in enumerate(noms)] +
                   [(i * 4, nm, 1, MUTED) for i, (d, nm, ns) in enumerate(noms)], rows=['degrés', 'accord']), 'h30-emprunts')

iv, div, civ, siv, _ = realise('I IV IVm I', 'Do', 0)
save(satb(iv, unit=22, colors={(1, 1): GREEN, (1, 2): RED}, lines=[((1, 1), (1, 2), RED)], labels=labs(iv, div, civ), rows=DEG), 'h30-ivm')
ro, dro, cro, sro, _ = realise('I IV V7 VIb IIø65 V7 I', 'Do', 0, durees=[2, 2, 2, 2, 2, 2, 4])
save(satb(ro, unit=22, time=(4, 4), colors=couleurs(sro, ro), labels=labs(ro, dro, cro), rows=DEG), 'h30-rompue')

# fausse relation : La à l'alto, puis La♭ au soprano
fr = ok = av = None
for b in ('Fa3', 'Fa2'):
    for a0 in sorted(voicings(['Fa', 'La', 'Do'], bass=b, tonic='Do'), key=P4.penal if hasattr(P4, 'penal') else len):
        if len({midi(N(x)) for x in a0}) < 4:
            continue
        vla = [k for k in range(3) if a0[k][:-1] == 'La']
        if not vla:
            continue
        f1 = o1 = None
        for v in voicings(['Fa', 'Lab', 'Do'], bass=b, tonic='Do'):
            if len({midi(N(x)) for x in v}) < 4:
                continue
            e = check([a0, v], 'Do')
            if len(e) == 1 and 'fausse relation' in e[0] and f1 is None:
                f1 = v
            if not e and v[vla[0]][:-1] == 'Lab' and o1 is None:
                o1 = v
        if f1 and o1:
            av, fr, ok = a0, f1, o1
            break
    if av:
        break
assert fr and ok, 'pas de fausse relation'
FR_MSG = check([av, fr], 'Do')
uf = [k for k in range(4) if fr[k][:-1] == 'Lab'][0]
ua = [k for k in range(4) if av[k][:-1] == 'La'][0]
fig = [tuple(av) + (4,), tuple(fr) + (4,), tuple(av) + (4,), tuple(ok) + (4,)]
save(satb(fig, unit=20, boxes=[(0, 8, RED, 'fausse relation'), (8, 16, GREEN, 'même voix')],
          colors={(ua, 0): RED, (uf, 1): RED, (ua, 2): GREEN, (ua, 3): GREEN}, lines=[((ua, 0), (uf, 1), RED), ((ua, 2), (ua, 3), GREEN)],
          labels=labs(fig, ['IV', 'IVm', 'IV', 'IVm'], ['5', '5', '5', '5']), rows=DEG), 'h30-fausse')

t1, dt1, ct1, st1, _ = realise('I IV I [Lab] I IV V7 I', 'Do', 0, durees=[2, 2, 4, 2, 2, 2, 2])
save(satb(t1, unit=22, time=(4, 4), labels=labs(t1, dt1, ct1), rows=DEG,
          colors={(v, 3): RED for v in range(4) if 'b' in t1[3][v]},
          boxes=[(0, 8, BLUE, 'Do majeur'), (8, 16, GREEN, 'La♭ majeur')]), 'h30-tierce-lab')
t2, dt2, ct2, st2, _ = realise('I V I [Mi] I IV V7 I', 'Do', 0, durees=[2, 2, 4, 2, 2, 2, 2])
save(satb(t2, unit=22, time=(4, 4), labels=labs(t2, dt2, ct2), rows=DEG,
          colors={(v, 3): RED for v in range(4) if '#' in t2[3][v]},
          boxes=[(0, 8, BLUE, 'Do majeur'), (8, 16, GREEN, 'Mi majeur')]), 'h30-tierce-mi')

# ======================================================================== chapitre 31 : le chromatisme
def passages(ch, durees, plus=None):
    """Ajoute des notes de passage chromatiques : dans une voix qui monte (ou descend) d'un ton, on coupe la note en deux
    et on insère la note altérée. Renvoie les voix pour le graveur et la liste des notes ajoutées."""
    voices = [[] for _ in range(4)]
    ajout = []
    deja = set()
    for i, c in enumerate(ch):
        d = durees[i]
        coupe = None
        if i + 1 < len(ch):
            for v in (2, 1, 0, 3):
                a, b = N(c[v]), N(ch[i + 1][v])
                st = midi(b) - midi(a)
                if abs(dpos(b) - dpos(a)) == 1 and abs(st) == 2 and v not in deja and (plus is None or i in plus):
                    if st > 0:
                        x = dict(a); x['a'] += 1
                    else:
                        x = dict(b); x['a'] += 1
                    from graveur import FR
                    nn = FR[x['s']] + {1: '#', -1: 'b', 0: '', 2: '##', -2: 'bb'}[x['a']] + str(x['o'])
                    coupe = (v, nn)
                    break
        for v in range(4):
            if coupe and coupe[0] == v:
                voices[v] += [(c[v], d / 2, {}), (coupe[1], d / 2, {'color': RED})]
                ajout.append((i, v, coupe[1]))
            else:
                voices[v].append((c[v], d, {}))
        if coupe:
            deja = {coupe[0]}
        else:
            deja = set()
    return [{'staff': st, 'stem': stem, 'events': voices[k]} for k, (st, stem) in enumerate([(0, 'up'), (0, 'down'), (1, 'up'), (1, 'down')])], ajout


ps, dps, cps, sps, _ = realise('I VI II V I', 'Do', 0, durees=[2, 2, 2, 2, 4])
vps, aj = passages(ps, [2, 2, 2, 2, 4])
assert aj, 'pas de passage chromatique'
save(Figure([{'clef': 'treble'}, {'clef': 'bass'}], vps, brace=(0, 1), gap=104, unit=26, time=(4, 4),
            labels=labs(ps, dps, cps), rows=DEG), 'h31-passage')
AJ = aj

ch1, dch, cch, sch, _ = realise('I V7/VI V7/II V7/V V7 I', 'Do', 0, durees=[2, 2, 2, 2, 2, 2])
save(satb(ch1, unit=22, time=(4, 4), colors=couleurs(sch, ch1), labels=labs(ch1, dch, cch), rows=DEG), 'h31-chaine')
au, dau, cau, sau, _ = realise('I IV Vaug I', 'Do', 0)
au2, dau2, cau2, sau2, _ = realise('I VI IV V7aug I', 'Do', 0, soprano_fin=False)
both = au + au2
cols = couleurs(sau, au)
for (v, i), c in couleurs(sau2, au2).items():
    cols[(v, i + 4)] = c
save(satb(both, unit=18, colors=cols, labels=labs(both, dau + dau2, cau + cau2), rows=DEG,
          boxes=[(0, 16, BLUE, 'V+'), (16, 36, BLUE, 'V7+ (quinte augmentée)')]), 'h31-augmentee')

# ======================================================================== chapitre 32 : du piano aux quatre voix
pi, dpi, cpi, spi, _ = realise('I IV V7 I VI II65 V7 I', 'Fa', -1, durees=[2, 2, 2, 2, 2, 2, 2, 2])
save(satb(pi, key=-1, unit=22, time=(4, 4), labels=labs(pi, dpi, cpi), rows=DEG), 'h32-choral')


def piano_arpeges(ch):
    """Main droite : soprano et alto ; main gauche : basse, ténor, octave de la basse, ténor (croches)."""
    rh_s, rh_a, lh = [], [], []
    for i, c in enumerate(ch):
        d = c[4]
        rh_s.append((c[0], d)); rh_a.append((c[1], d))
        if i == len(ch) - 1:
            lh.append((c[3], d)); continue
        haut = c[3][:-1] + str(int(c[3][-1]) + 1)
        motif = [c[3], c[2], haut, c[2]]
        lh += [(motif[k % 4], 0.5) for k in range(int(d * 2))]
    return [{'staff': 0, 'stem': 'up', 'events': rh_s}, {'staff': 0, 'stem': 'down', 'events': rh_a}, {'staff': 1, 'stem': None, 'events': lh}]


save(Figure([{'clef': 'treble'}, {'clef': 'bass'}], piano_arpeges(pi), key=-1, brace=(0, 1), gap=104, unit=26, time=(4, 4),
            labels=[l for l in labs(pi, dpi, cpi) if l[2] == 0], rows=['degrés']), 'h32-arpeges')

va, dva, cva, sva, _ = realise('I IV V7 I II6 V7 I', 'Do', 0, durees=[3] * 7)


def piano_valse(ch):
    """À la Chopin : la mélodie en blanches pointées, la main gauche fait basse - accord - accord."""
    rh, lh1, lh2 = [], [], []
    for i, c in enumerate(ch):
        rh.append((c[0], 3))
        if i == len(ch) - 1:
            lh1.append((c[3], 3)); lh2.append((None, 3, {'hide': True})); continue
        haut_a = c[1][:-1] + str(int(c[1][-1]) - 1) if midi(N(c[1])) > midi(N('Mi4')) else c[1]
        lh1 += [(c[3], 1), (c[2], 1), (c[2], 1)]
        lh2 += [(None, 1, {'hide': True}), (haut_a, 1), (haut_a, 1)]
    return [{'staff': 0, 'stem': None, 'events': rh}, {'staff': 1, 'stem': 'down', 'events': lh1}, {'staff': 1, 'stem': 'up', 'events': lh2}]


save(Figure([{'clef': 'treble'}, {'clef': 'bass'}], piano_valse(va), brace=(0, 1), gap=104, unit=22, time=(3, 4), beats_per_bar=3,
            labels=[l for l in labs(va, dva, cva, dur=3) if l[2] == 0], rows=['degrés']), 'h32-valse')
save(satb(va, unit=22, time=(3, 4), beats_per_bar=3, labels=labs(va, dva, cva), rows=DEG), 'h32-valse-reduction')

# ======================================================================== chapitre 33 : analyse, Schumann op. 41 n° 1, Intermezzo
from lire_mxl2 import lire
SCH = os.path.join(ICI, 'schumann', 'op41n1-intermezzo.mxl')
os.makedirs(os.path.dirname(SCH), exist_ok=True)
SRC = '/home/claude/m21/music21/corpus/schumann_robert/opus41no1/movement3.mxl'
if not os.path.exists(SCH) and os.path.exists(SRC):
    import shutil
    shutil.copy(SRC, SCH)
PS = lire(SCH)
SH = [(0, 'I', '5'), (2, 'VII°/II', 'péd.'), (4, 'V/V', 'péd.'), (6, 'VII°7', ''),
      (8, 'I', '5'), (10, 'VII°/II', 'péd.'), (12, 'V/V', 'péd.'), (14, 'VII°7', ''),
      (16, 'I', '5'), (18, 'V7/IV', 'péd.'), (20, 'V/V', 'péd.'), (22, 'VII°7', 'péd.'),
      (24, 'I', 'péd.'), (26, 'VII°7/V', 'péd.'), (28, 'II', 'péd.'), (30, 'VII°', 'péd.')]
for a_, b_, nom in ((0, 16, 'h33-mes1-4'), (16, 32, 'h33-mes5-8')):
    vo = P5.extrait(PS, a_, b_, bar=4)
    lb = []
    for (t, dg, chf) in SH:
        if a_ <= t < b_:
            lb.append((t - a_, dg, 0, BLUE))
            if chf:
                lb.append((t - a_, chf, 1, BLUE))
    save(Figure(P5.QUAT, vo, key=0, gap=96, unit=34, time=(2, 2) if a_ == 0 else None, beats_per_bar=4,
                labels=lb, rows=DEG, final=False), nom)


def sonne(t):
    return [x['n'] for p in PS for x in p['notes'] if x['t'] <= t + 1e-6 < x['t'] + x['d']]


# lignes chromatiques des voix intérieures (mesures 5 à 8)
LIGNES = {k: [sonne(16 + 2 * j)[k] for j in range(8)] for k in (1, 2)}

# ======================================================================== exercices du cours (chapitre 34)
EXOS, EXOS_K = {}, {}
an = [('Do5', 'Lab4', 'Fa4', 'Fa3'), ('Do5', 'Mib4', 'Lab3', 'Lab2'), ('Do5', 'Lab4', 'Fa4', 'Ré3'), ('Sib4', 'Fa4', 'Ré4', 'Sib2'),
      ('Ré#5', 'Fa4', 'Si3', 'Sol2'), ('Mi5', 'Sol#4', 'Si3', 'Mi3')]
for c in an:
    assert not check([c], 'Do'), (c, check([c], 'Do'))
tt = [(i * 4, x, MUTED) for i, x in enumerate(['a) Do', 'b) Do', 'c) Do', 'd) Do', 'e) Do', 'f) Do'])]
save(satb(an, unit=22, top_texts=tt), 'h34-ex1')
save(satb(an, unit=22, top_texts=tt, labels=labs(an, ['IVm', 'VI♭', 'IIø', 'VII♭', 'V+', 'V/VI'], ['5', '5', '7', '5', '7+ 5♯', '5']), rows=DEG), 'h35-c1')

MENU6 = ['I', 'II', 'IV', 'V', 'VI', 'V7', 'IVm', 'VIb', 'IIø7']
P4.faire_exo(EXOS, 'h34-ex2', 'bc', 'I IV IVm I VI IIø65 V7 I', 'Do', 0, durees=[2, 2, 2, 2, 2, 2, 2, 2], dossier=IMG, menu=MENU6,
             sop=['Mi5', 'Fa5', 'Fa5', 'Mi5', 'Mi5', 'Ré5', 'Ré5', 'Do5'])
P4.faire_exo(EXOS, 'h34-ex3', 'bc', 'I V7/VI V7/II V7/V V7 I', 'Fa', -1, durees=[2, 2, 2, 2, 4, 4], dossier=IMG,
             menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'V7/II', 'V7/V', 'V7/VI'])
P4.faire_exo(EXOS, 'h34-ex4', 'bd', 'I IV I [Lab] I IV V7 I', 'Do', 0, durees=[2, 2, 4, 2, 2, 2, 2], dossier=IMG)
P4.faire_exo(EXOS, 'h34-ex5', 'cd', 'I IV IVm I V7 I', 'Sol', 1, dossier=IMG, menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'IVm'])
for k in range(2, 6):
    os.replace(os.path.join(IMG, f'h34-ex{k}-c.png'), os.path.join(IMG, f'h35-c{k}.png'))
    SONS[f'h35-c{k}'] = SONS.pop(f'h34-ex{k}-c')
ch6, d6, c6, s6, _ = realise('I VI IV V7 I II65 V7 I', 'Sol', 1, durees=[3] * 8)
save(satb(ch6, key=1, unit=22, time=(3, 4), beats_per_bar=3, labels=labs(ch6, d6, c6), rows=DEG), 'h34-ex6')
save(Figure([{'clef': 'treble'}, {'clef': 'bass'}], piano_valse(ch6), key=1, brace=(0, 1), gap=104, unit=22, time=(3, 4), beats_per_bar=3,
            labels=[l for l in labs(ch6, d6, c6, dur=3) if l[2] == 0], rows=['degrés']), 'h35-c6')

# ======================================================================== cahier : chapitres 30 à 32
PAGES = {30: [], 31: [], 32: []}


def ajouter(chap, typ, plan, t, a, titre, piano=False, **kw):
    num = len(PAGES[chap]) + 1
    nom = f'c{chap}-{num:02d}'
    sol, seq, degs, chifs = P4.faire_exo(EXOS_K, nom, typ, plan, t, a, **kw)
    if piano:
        durees = kw.get('durees') or [4] * len(sol)
        ch = [tuple(c) + (d,) for c, d in zip(sol, durees)]
        if piano == 'valse':
            fig = Figure([{'clef': 'treble'}, {'clef': 'bass'}], piano_valse(ch), key=a, brace=(0, 1), gap=104, unit=22, time=(3, 4),
                         beats_per_bar=3, labels=[l for l in labs(ch, degs, chifs, dur=3) if l[2] == 0], rows=['degrés'])
        else:
            fig = Figure([{'clef': 'treble'}, {'clef': 'bass'}], piano_arpeges(ch), key=a, brace=(0, 1), gap=104, unit=26, time=(4, 4),
                         labels=[l for l in labs(ch, degs, chifs) if l[2] == 0], rows=['degrés'])
        save(fig, nom + '-p', IMGK)
    PAGES[chap].append((nom, typ, t, a, titre, piano))


M30 = ['I', 'II', 'IV', 'V', 'VI', 'V7', 'IVm', 'VIb', 'IIø7']
ajouter(30, 'bc', 'I IV IVm I', 'Fa', -1, 'IV mineur', menu=M30)
ajouter(30, 'bc', 'I II6 V7 VIb IIø65 V7 I', 'Ré', 2, 'cadence rompue sur VI♭', durees=[2, 2, 2, 2, 2, 2, 4], menu=M30)
ajouter(30, 'bc', 'I VI IIø65 V7 I', 'Sol', 1, 'IIø6/5', menu=M30)
ajouter(30, 'bd', 'I V I [Mi] I IV V7 I', 'Do', 0, 'modulation de Do à Mi majeur', durees=[2, 2, 4, 2, 2, 2, 2])
ajouter(30, 'cd', 'I IV IVm I II6 V7 I', 'Ré', 2, '', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'IVm'], sop_min='Ré4')
ajouter(31, 'bc', 'I V7/VI V7/II V7/V V7 I', 'Sol', 1, 'chaîne de dominantes', durees=[2, 2, 2, 2, 4, 4],
        menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'V7/II', 'V7/V', 'V7/VI'])
ajouter(31, 'bc', 'I IV Vaug I', 'Fa', -1, 'dominante à quinte augmentée', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'Vaug'])
ajouter(31, 'bd', 'I V7/IV IV IVm I V7 I', 'Do', 0, 'V7/IV puis IV mineur', durees=[2, 2, 2, 2, 2, 2, 4])
ajouter(32, 'bc', 'I IV V7 I VI II65 V7 I', 'Sib', -2, 'puis en arpèges', piano='arpeges', durees=[2] * 8, menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'II7'])
ajouter(32, 'bc', 'I IV V7 I II6 V7 I', 'Fa', -1, 'puis en valse', piano='valse', durees=[3] * 7, menu=['I', 'II', 'IV', 'V', 'VI', 'V7'])
ajouter(32, 'cd', 'I VI IV V7 I IVm I', 'Do', 0, 'puis en arpèges', piano='arpeges', durees=[2] * 6 + [4], menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'IVm'])

print('partie 6 :', len(EXOS), 'exercices du cours,', len(EXOS_K), 'exercices du cahier')
json.dump(EXOS, open(os.path.join(COURS, 'exercices-partie6.json'), 'w'), ensure_ascii=False)
json.dump(EXOS_K, open(os.path.join(CAHIER, 'exercices-cahier6.json'), 'w'), ensure_ascii=False)
json.dump({k: v for k, v in SONS.items() if k.startswith('h')}, open(os.path.join(COURS, 'audio', 'sons-partie6.json'), 'w'), indent=0)
json.dump({k: v for k, v in SONS.items() if k.startswith('c')}, open(os.path.join(CAHIER, 'audio', 'sons-cahier6.json'), 'w'), indent=0)
json.dump({'E': {k: [EXOS[k]['solution'], EXOS[k].get('degres'), EXOS[k].get('chiffres'), EXOS[k].get('harmonie')] for k in EXOS},
           'AJ': AJ, 'LIGNES': LIGNES, 'FR': FR_MSG, 'fr': fr, 'ok': ok, 'ro': [ro, dro], 't1': [t1, dt1], 't2': [t2, dt2], 'ch1': [ch1, dch],
           'pi': [pi, dpi], 'va': [va, dva], 'au': [au, au2]}, open('/tmp/p6.json', 'w'), ensure_ascii=False)

# ======================================================================== pages du cahier
TON = dict(P5.TON)
TON.update({('Sib', -2): 'Si♭ majeur'})
TITRES = {30: ('30-emprunts-et-modulations-par-tierces', "L'emprunt au mineur et les modulations par tierces", '30-l-emprunt-au-mode-mineur.md'),
          31: ('31-le-chromatisme', 'Le chromatisme', '31-le-chromatisme.md'),
          32: ('32-du-piano-aux-quatre-voix', 'Du piano aux quatre voix', '32-du-piano-aux-quatre-voix.md')}
TYPES = P5.TYPES
ordre = [(26, '26-ecrire-pour-quatuor', 'Écrire pour quatuor à cordes')] + [(c, TITRES[c][0], TITRES[c][1]) for c in (30, 31, 32)]
for k, chap in enumerate((30, 31, 32)):
    fic, titre, cours_md = TITRES[chap]
    prev = ordre[k]
    nav = f"[← {prev[2]}]({prev[1]}.md) · [Sommaire du cahier](README.md)"
    if k < 2:
        nx = ordre[k + 2]
        nav += f" · [{nx[2]} →]({nx[1]}.md)"
    L = [nav, '', f'## {titre}', '', f"Ces exercices accompagnent le [chapitre {chap}](../cours/{cours_md}) du cours.", '',
         "Dans la version web (`cahier.html`), chaque exercice se fait **directement sur la portée**, avec les corrections au fur et à mesure. "
         "Le menu des accords propose aussi les accords empruntés au mineur (IVm, VI♭, IIø7) et les dominantes secondaires. "
         "Attention aux **fausses relations** : une note altérée se prend dans la voix qui chantait la note naturelle.", '']
    if chap == 32:
        L += ["Ici, on réalise d'abord l'exercice à quatre voix, sur la grande portée. Puis, **sur papier**, on le récrit pour piano avec la "
              "texture demandée (voir le [chapitre 32](../cours/32-du-piano-aux-quatre-voix.md)). Les corrigés montrent les deux versions.", '']
    for j, (nom, typ, t, a, sous, pia) in enumerate(PAGES[chap]):
        n = f'{chap}.{j + 1}'
        tt = f"{TYPES[typ]} en {TON[(t, a)]}" + (f' ({sous})' if sous else '')
        L += [f'### Exercice {n} · {tt}', '', P4.CONSIGNE4[typ], '', f'![Exercice {n}](images/{nom}.png)', '']
    L += ['### Corrigés', '']
    for j, (nom, typ, t, a, sous, pia) in enumerate(PAGES[chap]):
        n = f'{chap}.{j + 1}'
        L += [f"**Exercice {n}** : une solution parmi d'autres.", '', f'![Corrigé {n}](images/{nom}-c.png)', '',
              f'🔊 [Écouter](audio/{nom}-c.mp3) · [MIDI](audio/{nom}-c.mid)', '']
        if pia:
            L += [f"Pour piano ({ {'arpeges': 'en arpèges', 'valse': 'en valse'}[pia] }) :", '', f'![Corrigé {n} pour piano](images/{nom}-p.png)', '',
                  f'🔊 [Écouter](audio/{nom}-p.mp3) · [MIDI](audio/{nom}-p.mid)', '']
    L += ['---', '', nav, '']
    open(os.path.join(CAHIER, fic + '.md'), 'w').write('\n'.join(L))

p26 = os.path.join(CAHIER, '26-ecrire-pour-quatuor.md')
s = open(p26).read()
s = re.sub(r'\[Sommaire du cahier\]\(README\.md\)(?! ·)', "[Sommaire du cahier](README.md) · [L'emprunt au mineur et les modulations par tierces →](30-emprunts-et-modulations-par-tierces.md)", s)
open(p26, 'w').write(s)

NT = {'bc': 'basse chiffrée', 'bd': 'basse donnée', 'sb': "compléter l'alto et le ténor", 'cd': 'chant donné', 'corriger': 'chasse aux fautes'}
readme = os.path.join(CAHIER, 'README.md')
R = [l for l in open(readme).read().split('\n') if not re.match(r'- \[.*\]\((30|31|32)-', l)]
i = next(k for k, l in enumerate(R) if '(26-ecrire' in l)
add = []
for chap in (30, 31, 32):
    sortes = {}
    for p in PAGES[chap]:
        sortes[NT[p[1]]] = sortes.get(NT[p[1]], 0) + 1
    add.append(f"- [{TITRES[chap][1]}]({TITRES[chap][0]}.md) (chapitre {chap} du cours) : " + ', '.join(f'{v} × {k}' for k, v in sortes.items()))
R = R[:i + 1] + add + R[i + 1:]
txt = '\n'.join(R)
n6 = sum(len(v) for v in PAGES.values())
m = re.search(r'dont (\d+) basses données, (\d+) chants donnés, (\d+) exercices sur le choral, (\d+) sur les accords de quatre sons et (\d+) sur le style classique', txt)
base_n = 54 + int(m.group(4)) + int(m.group(5))
txt = re.sub(r'\*\*\d+ exercices\*\* en tout, dont .*?Tous les corrigés',
             f"**{base_n + n6} exercices** en tout, dont {m.group(1)} basses données, {m.group(2)} chants donnés, {m.group(3)} exercices sur le choral, "
             f"{m.group(4)} sur les accords de quatre sons, {m.group(5)} sur le style classique et {n6} sur le premier romantisme. Tous les corrigés", txt)
open(readme, 'w').write(txt)
print('pages du cahier écrites')
