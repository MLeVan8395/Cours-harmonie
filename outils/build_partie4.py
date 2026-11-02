"""Usage : python3 outils/build_partie4.py

Partie 4 (les accords de quatre sons) : figures des chapitres 18 à 23, exercices interactifs du cours,
exercices du cahier (chapitres 18 à 21) et leurs pages. Chaque exemple « juste » passe le vérificateur,
chaque exemple « faux » contient exactement les fautes annoncées."""
import json, os, re, sys
from graveur import Figure, satb, RED, GREEN, BLUE, ORANGE, MUTED, SONS
from verif import check
from accords4 import phrase4, lire, spec, nom_ton, RX, diagnostic4

ICI = os.path.dirname(os.path.abspath(__file__))
COURS = os.path.join(ICI, '..', 'cours')
CAHIER = os.path.join(ICI, '..', 'cahier')
IMG, IMGK = os.path.join(COURS, 'images'), os.path.join(CAHIER, 'images')
DEG = ['degrés', 'chiffrage']
VERT = GREEN


def save(fig, name, dossier=IMG):
    fig.save(os.path.join(dossier, name + '.png'))


def expect(chords, n_err=0, contains=(), tonic='Do', allow_third=(), libres=()):
    e = check([c[:4] for c in chords], tonic, allow_third=allow_third, libres=libres)
    assert len(e) == n_err, (chords, e)
    for c in contains:
        assert any(c in x for x in e), (c, e)
    return e


def labs(chords, degs, chifs=None, dur=4):
    out, t = [], 0
    for i, c in enumerate(chords):
        d = c[4] if len(c) > 4 else dur
        ctr = d >= 4
        if degs and degs[i]:
            out.append((t, degs[i], 0, BLUE, ctr))
        if chifs and chifs[i]:
            out.append((t, chifs[i], 1, BLUE, ctr))
        t += d
    return out


def realise(plan, t='Do', a=0, durees=None, **kw):
    """Réalisation d'un plan ; renvoie (accords avec durées, degrés, chiffres, seq, tierce, tons, libres)."""
    ps, allow, seq = phrase4(plan, t, a, **kw)
    p = ps[0]
    durees = durees or [4] * len(p)
    ch = [tuple(c) + (d,) for c, d in zip(p, durees)]
    tons = [s['ton'][0] for s in seq]
    libres = {i for i, s in enumerate(seq) if s['marche']}
    expect(ch, tonic=tons, allow_third=allow, libres=libres)
    return ch, [s['label'] for s in seq], [s['chiffre'] for s in seq], seq, allow, tons, libres


def en_rouge(seq, ch, voix_sept=True):
    """Couleurs : septièmes (et neuvièmes) en rouge, sensibles des accords de dominante en orange."""
    from graveur import N
    col = {}
    for i, s in enumerate(seq):
        names = s['names']
        for v in range(4):
            n = ch[i][v][:-1]
            if len(names) >= 4 and n == names[3]:
                col[(v, i)] = RED
            if len(names) == 5 and n == names[4]:
                col[(v, i)] = RED
            if s['q'] in ('dom', 'dom9') and n == names[1]:
                col[(v, i)] = ORANGE
            if s['q'] == 'o7' and n == names[0]:
                col[(v, i)] = ORANGE
    return col


# ======================================================================== chapitre 18 : la 7e de dominante
vv = [{'staff': 0, 'stem': None, 'events': [(n, 4, {'color': c} if c else {}) for n, c in zip(x, cs)]} for x, cs in
      [(['Sol4', 'Sol4'], [None, None]), (['Si4', 'Si4'], [ORANGE, ORANGE]), (['Ré5', 'Ré5'], [None, None]), ([None, 'Fa5'], [None, RED])]]
vv[3]['events'][0] = (None, 4, {'hide': True})
save(Figure([{'clef': 'treble'}], vv, unit=22,
            labels=[(0, 'V', 0, BLUE), (4, 'V7', 0, BLUE), (0, 'G', 1, MUTED), (4, 'G7', 1, MUTED)], rows=['degrés', 'accord']), 'h18-accord')

res_a = [('Si4', 'Fa4', 'Ré4', 'Sol2'), ('Do5', 'Mi4', 'Do4', 'Do3')]
res_b = [('Si4', 'Fa4', 'Sol3', 'Sol2'), ('Do5', 'Mi4', 'Sol3', 'Do3')]
expect(res_a); expect(res_b)
r = res_a + res_b
save(satb(r, unit=20, boxes=[(0, 8, BLUE, 'V7 complet'), (8, 16, GREEN, 'V7 sans quinte')],
          colors={(0, 0): ORANGE, (0, 1): ORANGE, (1, 0): RED, (1, 1): RED, (0, 2): ORANGE, (0, 3): ORANGE, (1, 2): RED, (1, 3): RED},
          lines=[((0, 0), (0, 1), ORANGE), ((1, 0), (1, 1), RED), ((0, 2), (0, 3), ORANGE), ((1, 2), (1, 3), RED)],
          labels=labs(r, ['V', 'I', 'V', 'I'], ['7+', '5', '7+', '5']), rows=DEG), 'h18-resolution')

db = [('Si4', 'Fa4', 'Ré4', 'Sol2'), ('Si4', 'Fa4', 'Sol3', 'Sol2'), ('Si4', 'Fa4', 'Si3', 'Sol2'), ('Fa5', 'Si4', 'Fa4', 'Sol3')]
expect([db[0]]); expect([db[1]])
expect([db[2]], 2, ['sensible doublée'])
expect([db[3]], 2, ['septième doublée'])
save(satb(db, unit=24, colors={(0, 2): RED, (2, 2): RED, (0, 3): RED, (2, 3): RED},
          top_texts=[(0, 'a) ✔', GREEN), (4, 'b) ✔', GREEN), (8, 'c) ✘', RED), (12, 'd) ✘', RED)],
          labels=labs(db, ['V', 'V', 'V', 'V'], ['7+', '7+', '7+', '7+']), rows=DEG), 'h18-doublures')

rv = [('Si4', 'Fa4', 'Ré4', 'Sol2'), ('Do5', 'Mi4', 'Do4', 'Do3'), ('Ré5', 'Fa4', 'Sol3', 'Si2'), ('Do5', 'Mi4', 'Sol3', 'Do3'),
      ('Si4', 'Fa4', 'Sol3', 'Ré3'), ('Do5', 'Mi4', 'Sol3', 'Do3'), ('Si4', 'Ré4', 'Sol3', 'Fa3'), ('Do5', 'Do4', 'Sol3', 'Mi3')]
for k in range(0, 8, 2):
    expect(rv[k:k + 2])
save(satb(rv, unit=16, boxes=[(0, 8, BLUE, '7+'), (8, 16, BLUE, '6/5'), (16, 24, BLUE, '+6'), (24, 32, BLUE, '+4')],
          colors={(3, 0): BLUE, (3, 2): ORANGE, (3, 4): MUTED, (3, 6): RED},
          labels=labs(rv, ['V', 'I', 'V', 'I', 'V', 'I', 'V', 'I'], ['7+', '5', '6/5', '5', '+6', '5', '+4', '6']), rows=DEG), 'h18-renversements')

mt = [('Fa5', 'Si4', 'Sol4', 'Ré3'), ('Sol5', 'Do5', 'Sol4', 'Mi3')]
expect(mt)
mt_faux = [('Fa5', 'Si4', 'Sol4', 'Ré3'), ('Mi5', 'Do5', 'Sol4', 'Mi3')]
expect(mt_faux, 1, ['accord 2 : basse doublée dans un accord de sixte majeur'])
save(satb(mt_faux + mt, unit=20, boxes=[(0, 8, RED, 'la 7e descend'), (8, 16, GREEN, 'la 7e monte')],
          colors={(0, 0): RED, (0, 1): RED, (3, 1): RED, (0, 2): RED, (0, 3): GREEN},
          lines=[((0, 2), (0, 3), GREEN)],
          labels=labs(mt_faux + mt, ['V', 'I', 'V', 'I'], ['+6', '6', '+6', '6']), rows=DEG), 'h18-monte')

ro = [('Si4', 'Fa4', 'Ré4', 'Sol2'), ('Do5', 'Mi4', 'Do4', 'La2')]
expect(ro, allow_third={1})
save(satb(ro, unit=22, colors={(0, 0): ORANGE, (0, 1): ORANGE, (1, 0): RED, (1, 1): RED, (2, 1): GREEN, (0, 1): GREEN},
          lines=[((0, 0), (0, 1), ORANGE), ((1, 0), (1, 1), RED)],
          labels=labs(ro, ['V', 'VI'], ['7+', '5']), rows=DEG), 'h18-rompue')

ph18, d18, c18, s18, al18, *_ = realise('I V65 I IV V43 I6 II6 V7 I', durees=[2, 2, 2, 2, 2, 2, 2, 2, 4])
save(satb(ph18, unit=22, time=(4, 4), colors=en_rouge(s18, ph18), labels=labs(ph18, d18, c18), rows=DEG), 'h18-phrase')
mi18, dm18, cm18, sm18, alm, *_ = realise('I IV V65 I VI II6 V7 I', 'La', 0, durees=[2, 2, 2, 2, 2, 2, 4, 4])
save(satb(mi18, unit=22, time=(4, 4), colors=en_rouge(sm18, mi18), labels=labs(mi18, dm18, cm18), rows=DEG), 'h18-mineur')

# ======================================================================== chapitre 19 : les 7es d'espèce, les marches
D7 = [('Do', 'Mi', 'Sol', 'Si'), ('Ré', 'Fa', 'La', 'Do'), ('Mi', 'Sol', 'Si', 'Ré'), ('Fa', 'La', 'Do', 'Mi'),
      ('Sol', 'Si', 'Ré', 'Fa'), ('La', 'Do', 'Mi', 'Sol'), ('Si', 'Ré', 'Fa', 'La')]
oct_ = lambda k, n: n + ('4' if ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si'].index(n) >= ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si'].index(D7[k][0]) else '5')
vv = [{'staff': 0, 'stem': None, 'events': [(oct_(k, D7[k][j]), 4, {'color': RED} if j == 3 else ({'color': BLUE} if k == 4 else {})) for k in range(7)]} for j in range(4)]
save(Figure([{'clef': 'treble'}], vv, unit=18,
            labels=[(i * 4, d, 0, BLUE) for i, d in enumerate(['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'])] +
                   [(i * 4, l, 1, BLUE if l == 'G7' else MUTED) for i, l in enumerate(['Cmaj7', 'Dm7', 'Em7', 'Fmaj7', 'G7', 'Am7', 'Bm7♭5'])],
            rows=['degrés', 'accord']), 'h19-degres')

pr = [('Mi5', 'Sol4', 'Do4', 'Do3'), ('Ré5', 'La4', 'Do4', 'Fa2'), ('Ré5', 'Fa4', 'Si3', 'Sol2'), ('Do5', 'Mi4', 'Do4', 'Do3')]
expect(pr)
save(satb(pr, unit=24, colors={(2, 0): GREEN, (2, 1): RED, (2, 2): BLUE},
          lines=[((2, 0), (2, 1), GREEN), ((2, 1), (2, 2), RED)],
          top_texts=[(0, 'préparation', GREEN), (4, 'dissonance', RED), (8, 'résolution', BLUE)],
          labels=labs(pr, ['I', 'II', 'V', 'I'], ['5', '6/5', '7+', '5']), rows=DEG), 'h19-preparation')

nf = [('Mi5', 'Sol4', 'Do4', 'Do3'), ('Do5', 'Fa4', 'La3', 'Ré3'), ('Si4', 'Fa4', 'Sol3', 'Sol2'), ('Do5', 'Mi4', 'Sol3', 'Do3')]
expect(nf, 1, ['accords 1-2 : septième (soprano) non préparée'])
nok = [('Do5', 'Sol4', 'Mi4', 'Do3'), ('Do5', 'Fa4', 'La3', 'Ré3'), ('Si4', 'Fa4', 'Sol3', 'Sol2'), ('Do5', 'Mi4', 'Sol3', 'Do3')]
expect(nok)
save(satb(nf[:2] + nok[:2], unit=22, boxes=[(0, 8, RED, 'non préparée'), (8, 16, GREEN, 'préparée')],
          colors={(0, 0): RED, (0, 1): RED, (0, 2): GREEN, (0, 3): GREEN}, lines=[((0, 0), (0, 1), RED), ((0, 2), (0, 3), GREEN)],
          labels=labs(nf[:2] + nok[:2], ['I', 'II', 'I', 'II'], ['5', '7', '5', '7']), rows=DEG), 'h19-faux')

m1, dm1, cm1, sq1, *_ = realise('I IV VII* III VI II V I')
save(satb(m1, unit=18, boxes=[(0, 8, BLUE, 'modèle'), (8, 16, MUTED, 'copie'), (16, 24, MUTED, 'copie'), (24, 32, GREEN, 'cadence')],
          labels=labs(m1, dm1, cm1), rows=DEG), 'h19-marche1')
m2, dm2, cm2, sq2, *_ = realise('I IV7 VII7* III7 VI7 II7 V7 I')
col2 = en_rouge(sq2, m2)
for i in range(1, 7):     # préparations en vert
    for v in range(4):
        if col2.get((v, i)) == RED and (v, i - 1) not in col2:
            col2[(v, i - 1)] = GREEN
save(satb(m2, unit=18, colors=col2, labels=labs(m2, dm2, cm2), rows=DEG), 'h19-marche2')

ii65, d65, c65, s65, *_ = realise('I VI II65 V7 I', 'Sol', 1)
save(satb(ii65, unit=22, key=1, colors=en_rouge(s65, ii65), labels=labs(ii65, d65, c65), rows=DEG), 'h19-ii65')

# ======================================================================== chapitre 20 : 7e diminuée, 9e de dominante
n9 = [('La4', 'Fa4', 'Si3', 'Sol2'), ('Sol4', 'Mi4', 'Do4', 'Do3')]
expect(n9)
n9b = [('La4', 'Fa4', 'Si3', 'Sol2'), ('Sol4', 'Fa4', 'Si3', 'Sol2'), ('Sol4', 'Mi4', 'Do4', 'Do3')]
expect(n9b)
n9f = [('Si4', 'Fa4', 'La3', 'Sol2'), ('Do5', 'Mi4', 'Sol3', 'Do3')]
expect(n9f, 1, ['neuvième sous la sensible'])
r9 = n9 + n9b
save(satb(r9, unit=18, boxes=[(0, 8, BLUE, 'V9 - I'), (8, 20, GREEN, 'V9 - V7 - I')],
          colors={(0, 0): RED, (0, 1): BLUE, (2, 0): ORANGE, (2, 1): ORANGE, (1, 0): RED, (1, 1): RED,
                  (0, 2): RED, (0, 3): BLUE, (1, 2): RED, (1, 3): RED, (2, 2): ORANGE, (2, 3): ORANGE, (1, 4): RED},
          lines=[((0, 0), (0, 1), RED), ((0, 2), (0, 3), RED)],
          labels=labs(r9, ['V', 'I', 'V', 'V', 'I'], ['9+', '5', '9+', '7+', '5']), rows=DEG), 'h20-neuvieme')

se, dse, cse, sse, *_ = realise('I IV VII7 I', 'Do', 0)
save(satb(se, unit=22, colors=en_rouge(sse, se), labels=labs(se, dse, cse), rows=DEG), 'h20-sensible')
dm, ddm, cdm, sdm, *_ = realise('I IV VII7 I V65 I', 'La', 0)
save(satb(dm, unit=22, colors=en_rouge(sdm, dm), labels=labs(dm, ddm, cdm), rows=DEG), 'h20-diminuee')
dmM, ddM, cdM, sdM, *_ = realise('I II6 VIIo7 I', 'Do', 0)
save(satb(dmM, unit=22, colors=en_rouge(sdM, dmM), labels=labs(dmM, ddM, cdM), rows=DEG), 'h20-diminuee-majeur')

# ======================================================================== chapitre 21 : dominantes secondaires, modulation
vv5, dvv, cvv, svv, *_ = realise('I IV V7/V V I')
save(satb(vv5, unit=22, colors=en_rouge(svv, vv5), labels=labs(vv5, dvv, cvv), rows=DEG), 'h21-vv')
pairs = []
for plan in ('V7/IV IV', 'V7/II II', 'V7/VI VI', 'V7/V V'):
    c, d, ch, s, *_ = realise(plan, soprano_fin=False)
    pairs.append((c, d, ch, s, plan))
allc = sum([p[0] for p in pairs], [])
cols = {}
for k, p in enumerate(pairs):
    for (v, i), cc in en_rouge(p[3], p[0]).items():
        cols[(v, 2 * k + i)] = cc
save(satb(allc, unit=17, colors=cols, boxes=[(8 * k, 8 * k + 8, BLUE, f'vers {p[4].split()[1]}') for k, p in enumerate(pairs)],
          labels=labs(allc, sum([p[1] for p in pairs], []), sum([p[2] for p in pairs], [])), rows=DEG), 'h21-secondaires')

mo, dmo, cmo, smo, almo, tmo, _ = realise('I IV I VI=[Sol]II V7 I', durees=[2, 2, 2, 2, 2, 2, 4])
save(satb(mo, unit=24, time=(4, 4), colors=en_rouge(smo, mo), labels=labs(mo, dmo, cmo), rows=DEG,
          boxes=[(0, 6, BLUE, 'Do majeur'), (6, 8, MUTED, 'pivot'), (8, 12, GREEN, 'Sol majeur')]), 'h21-mod-sol')
ml, dml, cml, sml, alml, tml, _ = realise('I V6 I IV=[la]VI V7 I', durees=[2, 2, 2, 2, 2, 2, 4])
save(satb(ml, unit=24, time=(4, 4), colors=en_rouge(sml, ml), labels=labs(ml, dml, cml), rows=DEG,
          boxes=[(0, 6, BLUE, 'Do majeur'), (6, 8, MUTED, 'pivot'), (8, 12, GREEN, 'la mineur')]), 'h21-mod-la')

# ======================================================================== exercices interactifs du cours (chapitre 22)
EXOS = {}
EXOS_K = {}


def base(tok):
    m = RX.match(tok.rstrip('*').split(']')[-1])
    deg, dim, chif, cible = m.group(1), m.group(2), m.group(3) or '5', m.group(4)
    b = deg + ('o' if dim else '') + ('7' if chif in ('7', '65', '43', '2') else '9' if chif == '9' else '')
    return b + (f'/{cible}' if cible else '')


def joli(tok):
    return tok.replace('o7', '°7')


GUIDE4 = {
    'bc': [
        {'type': 'degres', 'titre': 'Trouve les accords',
         'consigne': "Sous chaque note de la basse, choisis l'accord. Chiffrage d'un accord de 7e : 7 (ou 7+) = la basse est la fondamentale ; 6/5 = la tierce ; 4/3 (ou +6) = la quinte ; 2 (ou +4) = la septième. Le + marque la sensible : c'est un V7."},
        {'type': 'voix', 'voix': [0], 'titre': 'Écris le soprano',
         'consigne': "Une ligne simple, surtout par degrés conjoints. Chaque note doit appartenir à l'accord. Pense déjà à la 7e : si le soprano la chante, il descend ensuite d'un degré."},
        {'type': 'voix', 'voix': [1, 2], 'titre': "Complète l'alto et le ténor",
         'consigne': "La 7e descend d'un degré, la sensible monte. Ne double ni l'une ni l'autre ; sans la quinte, double la fondamentale."}],
    'bd': [
        {'type': 'voix', 'voix': [0], 'titre': 'Écris le soprano',
         'consigne': "Les accords sont donnés. Écris une ligne simple, surtout par degrés conjoints, dont chaque note appartient à l'accord."},
        {'type': 'voix', 'voix': [1, 2], 'titre': "Complète l'alto et le ténor",
         'consigne': "La 7e (en rouge dans les corrigés) descend d'un degré, la sensible monte. Une 7e d'espèce doit être préparée."}],
    'cd': [
        {'type': 'degres', 'titre': 'Choisis les accords',
         'consigne': "Pour chaque note du soprano, choisis un accord qui la contient. Finis par V7-I (ou V-I). Un II7 (ou II6/5) prépare très bien la cadence ; sa 7e doit être dans l'accord précédent."},
        {'type': 'voix', 'voix': [3], 'titre': 'Écris la basse',
         'consigne': "Fondamentale, tierce, et pour un accord de 7e aussi la quinte ou la septième (le chiffrage s'affiche tout seul). À la cadence, la fondamentale à la basse."},
        {'type': 'voix', 'voix': [1, 2], 'titre': "Complète l'alto et le ténor",
         'consigne': "La 7e descend d'un degré, la sensible monte ; ne double ni l'une ni l'autre."}],
}
CONSIGNE4 = {
    'bc': "Basse chiffrée : trouve les accords, écris le soprano, puis l'alto et le ténor.",
    'bd': "Basse donnée avec ses accords : écris le soprano, puis l'alto et le ténor.",
    'sb': "Le soprano et la basse sont donnés. Écris l'alto et le ténor : la 7e descend, la sensible monte.",
    'cd': "Chant donné : choisis les accords, écris la basse, puis l'alto et le ténor.",
    'corriger': "Cet enchaînement contient **trois fautes**. Trouve-les et corrige-les en changeant le moins de notes possible (la basse ne bouge pas).",
}
MENU_DEF = ['I', 'II', 'IV', 'V', 'VI', 'V7', 'II7']


def faire_exo(dico, nom, typ, plan, t, a, sop=None, basse=None, durees=None, menu=None, depart=None, dossier=IMGK, montrer_deg=None, n=1, sop_max='Fa5', sop_min='Fa4', force=None):
    kw = {}
    if sop:
        kw['sop'] = sop
    if basse:
        kw['basse'] = basse
    try:
        ps, allow, seq = phrase4(plan, t, a, n=n, sop_max=sop_max, sop_min=sop_min, **kw)
    except (ValueError, AssertionError) as e:
        raise SystemExit(f'{nom} : {e} -> {diagnostic4(plan, t, a, sop=sop, basse=basse)}')
    sol = ps[-1] if n > 1 else ps[0]
    if force:
        sol = [tuple(c) for c in force]
    tons = [s['ton'][0] for s in seq]
    libres = sorted(i for i, s in enumerate(seq) if s['marche'])
    assert not check(sol, tons, allow_third=allow, libres=libres)
    k = len(sol)
    durees = durees or [4] * k
    degs = [s['label'] for s in seq]
    chifs = [s['chiffre'] for s in seq]
    voix = {'bc': [0, 1, 2], 'bd': [0, 1, 2], 'sb': [1, 2], 'cd': [1, 2, 3], 'corriger': [0, 1, 2]}[typ]
    if depart in ('auto', 'auto7'):
        depart = chasse4(sol, seq, tons, allow, libres, sept=2 if depart == 'auto7' else 1)
    donne = [list(c) for c in depart] if depart else [[None if v in voix else c[v] for v in range(4)] for c in sol]
    ex = {'donne': donne, 'solution': [list(c) for c in sol], 'durees': durees, 'voix': voix, 'tonique': t, 'armure': a,
          'degres': None, 'chiffres': None, 'tierce': sorted(allow), 'chant': typ == 'cd', 'corriger': typ == 'corriger',
          'guide': GUIDE4.get(typ), 'isoles': False, 'accords': [s['names'] for s in seq]}
    if len(set(tons)) > 1:
        ex['tons'] = tons
    if libres:
        ex['libres'] = libres
    if typ in ('bd', 'sb', 'corriger'):
        ex['degres'], ex['chiffres'] = degs, chifs
    if typ == 'bc':
        ex['chiffres'] = chifs
    if typ in ('bc', 'cd'):
        menu = menu or MENU_DEF
        bases = [base(tk) for tk in plan.split() if not tk.startswith('[')]
        for b in bases:
            assert b in menu, (nom, b, menu)
        ex['menu'] = [[joli(m), spec(m, t, a)['names']] for m in menu]
        ex['harmonie'] = [menu.index(b) for b in bases]
        if typ == 'cd':
            ex['finLabel'] = joli(bases[-1])
    dico[nom] = ex
    # énoncé et corrigé gravés
    md = montrer_deg if montrer_deg is not None else typ in ('bd', 'sb', 'corriger')
    mc = typ != 'cd'
    lab = labs([c + (d,) for c, d in zip(sol, durees)], degs if md else None, chifs if mc else None)
    temps = (4, 4) if any(d < 4 for d in durees) else None
    voices = []
    for v, (st, stem) in enumerate([(0, 'up'), (0, 'down'), (1, 'up'), (1, 'down')]):
        ev = [((donne[i][v] if donne[i][v] else None), durees[i], {} if donne[i][v] else {'hide': True}) for i in range(k)]
        voices.append({'staff': st, 'stem': stem, 'events': ev})
    Figure([{'clef': 'treble'}, {'clef': 'bass'}], voices, key=a, brace=(0, 1), gap=104, unit=22, time=temps,
           labels=lab, rows=DEG if md else (['', 'chiffrage'] if mc else None)).save(os.path.join(dossier, nom + '.png'))
    SONS.pop(nom, None)
    ch = [c + (d,) for c, d in zip(sol, durees)]
    col = en_rouge(seq, ch)
    for v in voix:
        for i in range(k):
            col.setdefault((v, i), BLUE)
    satb(ch, key=a, unit=22, time=temps, labels=labs(ch, degs, chifs), rows=DEG, colors=col).save(os.path.join(dossier, nom + '-c.png'))
    return sol, seq, degs, chifs


def chasse4(sol, seq, tons, allow, libres, graine=3, sept=0):
    """Trois fautes de trois sortes, chacune en changeant une note (la basse reste)."""
    import random, itertools
    from graveur import N, midi
    from recherche import notes_in_range, chord_notes
    from verif import TESS, VOIX
    from donnees_app import categorie
    rnd = random.Random(graine)
    muts = []
    for i, ch in enumerate(sol):
        for v in range(3):
            for nn in notes_in_range(chord_notes(seq[i]['names']), *TESS[VOIX[v]]):
                if nn == ch[v] or abs(midi(N(nn)) - midi(N(ch[v]))) > 7:
                    continue
                p = [list(c) for c in sol]
                p[i][v] = nn
                e = check(p, tons, allow_third=allow, libres=libres)
                if len(e) == 1 and categorie(e[0].replace('septième', '7e')) != 'tess':
                    muts.append((i, v, nn, e[0]))
    rnd.shuffle(muts)
    for a, b, c in itertools.combinations(muts, 3):
        if len({a[0], b[0], c[0]}) < 3:
            continue
        kinds = {re.sub(r'\(.*?\)|accords? [\d-]+ : ', '', x[3]).strip() for x in (a, b, c)}
        if len(kinds) < 3 or sum('septième' in k for k in kinds) < sept:
            continue
        p = [list(x) for x in sol]
        for i, v, nn, _ in (a, b, c):
            p[i][v] = nn
        if len(check(p, tons, allow_third=allow, libres=libres)) == 3:
            return [tuple(x) for x in p]
    raise ValueError('pas de chasse aux fautes')


# exercice 1 : chiffrer des accords de 4 sons (analyse, sans portée interactive)
an = [('Si4', 'Fa4', 'Ré4', 'Sol2'), ('Sol4', 'Ré4', 'Fa3', 'Si2'), ('Do5', 'La4', 'Fa4', 'Ré3'), ('Ré5', 'Sol4', 'Si3', 'Fa3'),
      ('Ré5', 'La4', 'Fa#4', 'Do4'), ('Fa5', 'Si4', 'Ré4', 'Sol#3')]
for c in an:
    expect([c], tonic='La' if 'Sol#3' in c else 'Do')
tt = [(i * 4, x, MUTED) for i, x in enumerate(['a) Do', 'b) Do', 'c) Do', 'd) Do', 'e) Do', 'f) la'])]
save(satb(an, unit=22, top_texts=tt), 'h22-ex1')
an_d = ['V', 'V', 'II', 'V', 'V/V', 'VII']
an_c = ['7+', '6/5', '7', '+4', '+4', '7°']
save(satb(an, unit=22, top_texts=tt, labels=labs(an, an_d, an_c), rows=DEG), 'h23-c1')

E2 = faire_exo(EXOS, 'h22-ex2', 'bc', 'I V65 I IV II65 V7 I', 'Do', 0, durees=[2, 2, 2, 2, 2, 2, 4], dossier=IMG)
E3 = faire_exo(EXOS, 'h22-ex3', 'bc', 'I V2 I6 IV II7 V7 I', 'Fa', -1, durees=[2, 2, 2, 2, 2, 2, 4], dossier=IMG)
# exercice 4 : chasse aux fautes (trois fautes sur les 7es)
ok4 = [('Do5', 'Mi4', 'Sol3', 'Do3'), ('Do5', 'La4', 'Ré4', 'Fa3'), ('Si4', 'Fa4', 'Ré4', 'Sol3'), ('Do5', 'Mi4', 'Do4', 'Do3')]
f4 = [('Do5', 'Mi4', 'Sol3', 'Do3'), ('Ré5', 'La4', 'Do4', 'Fa3'), ('Ré5', 'Fa4', 'Si3', 'Sol3'), ('Do5', 'Sol4', 'Mi4', 'Do3')]
expect(ok4)
expect(f4, 3, ['5tes consécutives ténor/basse', 'septième (ténor) non préparée', 'septième (alto) non résolue'])
E4 = faire_exo(EXOS, 'h22-ex4', 'corriger', 'I II65 V7 I', 'Do', 0, depart=f4, force=ok4, dossier=IMG)
E5 = faire_exo(EXOS, 'h22-ex5', 'cd', 'I IV I6 II65 V7 I', 'Sol', 1, sop=['Si4', 'Do5', 'Ré5', 'La4', 'La4', 'Sol4'], dossier=IMG,
               menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'II7'])
E6 = faire_exo(EXOS, 'h22-ex6', 'bd', 'I IV V7/V V I VI=[Sol]II V7 I', 'Do', 0, durees=[2, 2, 2, 2, 4, 2, 2, 4], dossier=IMG)
for k in range(2, 7):
    os.replace(os.path.join(IMG, f'h22-ex{k}-c.png'), os.path.join(IMG, f'h23-c{k}.png'))
    SONS[f'h23-c{k}'] = SONS.pop(f'h22-ex{k}-c')

# ======================================================================== cahier : chapitres 18 à 21
PAGES = {18: [], 19: [], 20: [], 21: []}


def ajouter(chap, typ, plan, t, a, titre, **kw):
    num = len(PAGES[chap]) + 1
    nom = f'c{chap}-{num:02d}'
    faire_exo(EXOS_K, nom, typ, plan, t, a, **kw)
    PAGES[chap].append((nom, typ, t, a, titre))


H = [2, 2, 2, 2, 2, 2, 4]
# 18 : la 7e de dominante
ajouter(18, 'sb', 'I IV V7 I', 'Do', 0, 'V7 à l\'état fondamental', sop=['Mi5', 'Fa5', 'Fa5', 'Mi5'])
ajouter(18, 'sb', 'I V65 I IV V7 I', 'Sol', 1, 'V7 et V6/5')
ajouter(18, 'bc', 'I V43 I6 IV V7 I', 'Do', 0, 'le V+6', durees=[2, 2, 2, 2, 4, 4])
ajouter(18, 'bc', 'I IV V2 I6 V65 I', 'Ré', 2, 'le V+4', durees=[2, 2, 2, 2, 4, 4])
ajouter(18, 'bc', 'I VI IV V7 VI II6 V7 I', 'Fa', -1, 'avec une cadence rompue', durees=[2, 2, 2, 2, 2, 2, 4, 4])
ajouter(18, 'bc', 'I IV V65 I VI II6 V7 I', 'La', 0, 'en la mineur', durees=[2, 2, 2, 2, 2, 2, 4, 4])
ajouter(18, 'cd', 'I IV V65 I II6 V7 I', 'Do', 0, '', menu=['I', 'II', 'IV', 'V', 'VI', 'V7'])
ajouter(18, 'cd', 'I V65 I IV V7 I', 'Ré', -1, 'en ré mineur', menu=['I', 'II', 'IV', 'V', 'VI', 'V7'])
# 19 : 7es d'espèce et marches
ajouter(19, 'bc', 'I VI II7 V7 I', 'Do', 0, 'II7', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'II7', 'IV7'])
ajouter(19, 'bc', 'I IV II65 V7 I', 'Sol', 1, 'II6/5', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'II7', 'IV7'])
ajouter(19, 'bc', 'I IV7 V7 I VI II65 V7 I', 'Fa', -1, 'IV7 et II6/5', durees=[2, 2, 2, 2, 2, 2, 4, 4], menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'II7', 'IV7'])
ajouter(19, 'bd', 'I IV VII* III VI II V I', 'Ré', 2, 'marche harmonique')
ajouter(19, 'bd', 'I IV7 VII7* III7 VI7 II7 V7 I', 'Do', 0, 'marche de septièmes')
ajouter(19, 'cd', 'I VI II65 V7 I', 'Fa', -1, '', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'II7'])
ajouter(19, 'corriger', 'I VI II65 V7 I', 'Ré', 2, '', sop=['Fa#5', 'Fa#5', 'Mi5', 'Mi5', 'Ré5'], depart='auto')
# 20 : 7e diminuée et 9e
ajouter(20, 'bc', 'I IV VII7 I V65 I', 'La', 0, '7e diminuée en la mineur', durees=[2, 2, 2, 2, 4, 4], menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'VII7'])
ajouter(20, 'bc', 'I II6 VIIo7 I IV V7 I', 'Sol', 1, '7e diminuée en majeur', durees=[2, 2, 2, 2, 2, 2, 4], menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'VIIo7'])
ajouter(20, 'bd', 'I IV V9 I', 'Do', 0, '9e de dominante', sop=['Mi5', 'Do5', 'La4', 'Sol4'], sop_min='Sol4')
ajouter(20, 'bd', 'I VI IV VII7 I', 'Fa', -1, '7e de sensible')
ajouter(20, 'cd', 'I IV VII7 I II6 V7 I', 'Ré', -1, 'en ré mineur', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'VII7'], sop_min='Ré4')
# 21 : dominantes secondaires et modulation
ajouter(21, 'bc', 'I IV V7/V V I', 'Do', 0, 'V7/V', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'V7/V'])
ajouter(21, 'bc', 'I V7/IV IV V7/V V7 I', 'Sol', 1, 'V7/IV et V7/V', durees=[2, 2, 2, 2, 4, 4], menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'V7/IV', 'V7/V'])
ajouter(21, 'bc', 'I V7/VI VI V7/II II V7 I', 'Fa', -1, 'V7/VI et V7/II', durees=[2, 2, 2, 2, 2, 2, 4], menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'V7/II', 'V7/VI'])
ajouter(21, 'cd', 'I IV V7/V V I', 'Ré', 2, '', menu=['I', 'II', 'IV', 'V', 'VI', 'V7', 'V7/V'], sop_min='Ré4')
ajouter(21, 'bd', 'I IV I VI=[Sol]II V7 I', 'Do', 0, 'modulation de Do à Sol', durees=[2, 2, 2, 2, 4, 4])
ajouter(21, 'bd', 'I II6 V I IV=[ré]VI V7 I', 'Fa', -1, 'modulation de Fa à ré mineur', durees=[2, 2, 2, 2, 2, 2, 4])

print('partie 4 :', len(EXOS), 'exercices du cours,', len(EXOS_K), 'exercices du cahier')
json.dump(EXOS, open(os.path.join(COURS, 'exercices-partie4.json'), 'w'), ensure_ascii=False)
json.dump(EXOS_K, open(os.path.join(CAHIER, 'exercices-cahier4.json'), 'w'), ensure_ascii=False)
json.dump({k: v for k, v in SONS.items() if k.startswith('h')}, open(os.path.join(COURS, 'audio', 'sons-partie4.json'), 'w'), indent=0)
json.dump({k: v for k, v in SONS.items() if k.startswith('c')}, open(os.path.join(CAHIER, 'audio', 'sons-cahier4.json'), 'w'), indent=0)
json.dump({'PAGES': PAGES, 'ph18': ph18, 'm2': m2, 'E': {k: [EXOS[k]['solution'], EXOS[k].get('degres'), EXOS[k].get('chiffres')] for k in EXOS}},
          open('/tmp/p4.json', 'w'), ensure_ascii=False)

# ======================================================================== pages du cahier
TON = {('Do', 0): 'Do majeur', ('Sol', 1): 'Sol majeur', ('Fa', -1): 'Fa majeur', ('Ré', 2): 'Ré majeur',
       ('La', 0): 'la mineur', ('Mi', 1): 'mi mineur', ('Ré', -1): 'ré mineur', ('Sol', -2): 'sol mineur'}
TITRES = {18: ('18-la-septieme-de-dominante', 'La septième de dominante', '18-la-septieme-de-dominante.md', '18'),
          19: ('19-les-septiemes-d-espece', "Les septièmes d'espèce et les marches", '19-les-septiemes-d-espece-et-les-marches.md', '19'),
          20: ('20-la-septieme-diminuee-et-la-neuvieme', 'La septième diminuée et la neuvième', '20-la-septieme-diminuee-et-la-neuvieme.md', '20'),
          21: ('21-dominantes-secondaires-et-modulation', 'Dominantes secondaires et modulation', '21-les-dominantes-secondaires-et-la-modulation.md', '21')}
TYPES = {'bc': 'Basse chiffrée', 'bd': 'Basse donnée', 'sb': 'Compléter l\'alto et le ténor', 'cd': 'Chant donné', 'corriger': 'Chasse aux fautes'}
ordre = [(13, '13-le-choral', 'Le choral')] + [(c, TITRES[c][0], TITRES[c][1]) for c in (18, 19, 20, 21)]
for k, chap in enumerate((18, 19, 20, 21)):
    fic, titre, cours_md, num = TITRES[chap]
    prev = ordre[k]
    nav = f"[← {prev[2]}]({prev[1]}.md) · [Sommaire du cahier](README.md)"
    if k < 3:
        nx = ordre[k + 2]
        nav += f" · [{nx[2]} →]({nx[1]}.md)"
    L = [nav, '', f'## {titre}', '', f"Ces exercices accompagnent le [chapitre {num}](../cours/{cours_md}) du cours.", '',
         "Dans la version web (`cahier.html`), chaque exercice se fait **directement sur la portée**, avec les corrections au fur et à mesure. "
         "Dans les basses chiffrées et les chants donnés, le menu propose aussi les accords de 7e : choisis-les d'après la basse et le chiffrage.", '']
    for j, (nom, typ, t, a, sous) in enumerate(PAGES[chap]):
        n = f'{chap}.{j + 1}'
        tt = f"{TYPES[typ]} en {TON[(t, a)]}" + (f' ({sous})' if sous and not sous.startswith('en ') else '')
        L += [f'### Exercice {n} · {tt}', '', CONSIGNE4[typ], '', f'![Exercice {n}](images/{nom}.png)', '']
    L += ['### Corrigés', '']
    for j, (nom, typ, t, a, sous) in enumerate(PAGES[chap]):
        n = f'{chap}.{j + 1}'
        L += [f"**Exercice {n}** : une solution parmi d'autres (septièmes en rouge, sensibles en orange).", '', f'![Corrigé {n}](images/{nom}-c.png)', '',
              f'🔊 [Écouter](audio/{nom}-c.mp3) · [MIDI](audio/{nom}-c.mid)', '']
    L += ['---', '', nav, '']
    open(os.path.join(CAHIER, fic + '.md'), 'w').write('\n'.join(L))
print('pages du cahier écrites')

# sommaire du cahier (écrit par build_cahier.py) : ajouter la partie 4
NT = {'bc': 'basse chiffrée', 'bd': 'basse donnée', 'sb': "compléter l'alto et le ténor", 'cd': 'chant donné', 'corriger': 'chasse aux fautes'}
readme = os.path.join(CAHIER, 'README.md')
R = [l for l in open(readme).read().split('\n') if not re.match(r'- \[.*\]\((18|19|20|21)-', l)]
i = next(k for k, l in enumerate(R) if '(13-le-choral.md)' in l)
add = []
for chap in (18, 19, 20, 21):
    sortes = {}
    for p in PAGES[chap]:
        sortes[NT[p[1]]] = sortes.get(NT[p[1]], 0) + 1
    add.append(f"- [{TITRES[chap][1]}]({TITRES[chap][0]}.md) (chapitre {chap} du cours) : " + ', '.join(f'{v} × {k}' for k, v in sortes.items()))
R = R[:i + 1] + add + R[i + 1:]
n4 = sum(len(v) for v in PAGES.values())
txt = '\n'.join(R)
m = re.search(r'\*\*(\d+) exercices\*\* en tout, dont (\d+) basses données, (\d+) chants donnés et (\d+) exercices sur le choral\.', txt)
if m:
    base_n = int(m.group(1)) - (int(re.search(r'et (\d+) sur les accords de quatre sons', txt).group(1)) if 'accords de quatre sons' in txt else 0)
    txt = re.sub(r'\*\*\d+ exercices\*\* en tout, dont .*?Tous les corrigés',
                 f"**{base_n + n4} exercices** en tout, dont {m.group(2)} basses données, {m.group(3)} chants donnés, {m.group(4)} exercices sur le choral "
                 f"et {n4} sur les accords de quatre sons. Tous les corrigés", txt)
open(readme, 'w').write(txt)
print('sommaire du cahier mis à jour')
