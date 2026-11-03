"""Exercices « libres » pour l'harmonie moderne (parties 8 et 9).

Pas de règles d'enchaînement classiques : chaque accord doit contenir les notes demandées (cibles),
et, pour les accords parallèles, garder la même disposition. Le même contrôle existe en JS (atelier.js, fautesLibre)."""
import itertools, os
from graveur import Figure, satb, N, midi, dpos, FR, SEMI, BLUE, RED, MUTED

TESS = [('Do4', 'Sol5'), ('Sol3', 'Ré5'), ('Do3', 'Sol4'), ('Fa2', 'Do4')]
VOIX = ['soprano', 'alto', 'ténor', 'basse']
LETTRE = ['C', 'D', 'E', 'F', 'G', 'A', 'B']


def pc(x):
    """classe de hauteur d'un nom avec ou sans octave"""
    if x[-1].isdigit():
        return midi(N(x)) % 12
    return midi(N(x + '4')) % 12


def sans_oct(x):
    return x[:-1]


def nom(s, a, o):
    return FR[s] + ('#' if a == 1 else 'b' if a == -1 else '') + str(o)


def transpose_diato(x, pas, alts):
    """monte une note de « pas » degrés dans la gamme définie par alts {degré: altération}"""
    n = N(x)
    d = dpos(n) + pas
    s, o = d % 7, d // 7
    return nom(s, alts.get(s, 0), o)


def transpose_reel(x, demi, bemol=None):
    """monte une note de « demi » demi-tons ; garde le même nom de note si possible (même intervalle écrit),
    sinon choisit l'orthographe la plus simple"""
    m = midi(N(x)) + demi
    if bemol is None:
        bemol = N(x)['a'] == -1
    o = m // 12 - 1
    p = m % 12
    if p in SEMI:
        return nom(SEMI.index(p), 0, o)
    if bemol:
        s = SEMI.index(p + 1)
        return nom(s, -1, o)
    return nom(SEMI.index(p - 1), 1, o)


def planing_reel(premier, sop, bemols=None):
    """accords parallèles exacts : la disposition du premier accord est recopiée sous chaque note du soprano"""
    ref = midi(N(premier[0]))
    out = []
    for k, s in enumerate(sop):
        d = midi(N(s)) - ref
        b = bemols[k] if bemols else None
        out.append(tuple([s] + [transpose_reel(x, d, b) for x in premier[1:]]))
    return out


def planing_diato(premier, sop, alts):
    ref = dpos(N(premier[0]))
    return [tuple([s] + [transpose_diato(x, dpos(N(s)) - ref, alts) for x in premier[1:]]) for s in sop]


def voicer(cibles, fixe, requis=None, ecart=(12, 12, 19), min_tb=5, centre=72):
    """Cherche une réalisation (S, A, T, B) : notes des cibles, requis présents, pas de croisement,
    écarts raisonnables ; minimise le mouvement des voix. fixe : liste de 4-uplets (None = à trouver)."""
    requis = requis or cibles
    cand_all = []
    for i, cib in enumerate(cibles):
        par_voix = []
        for v in range(4):
            if fixe[i][v]:
                par_voix.append([fixe[i][v]])
                continue
            lo, hi = (midi(N(t)) for t in TESS[v])
            l = []
            for c in cib:
                for o in range(2, 6):
                    x = c + str(o)
                    if lo <= midi(N(x)) <= hi:
                        l.append(x)
            par_voix.append(l)
        ok = []
        req = {pc(r) for r in requis[i]}
        for combo in itertools.product(*par_voix):
            m = [midi(N(x)) for x in combo]
            if not (m[0] > m[1] > m[2] > m[3]):
                continue
            if m[0] - m[1] > ecart[0] or m[1] - m[2] > ecart[1] or m[2] - m[3] > ecart[2]:
                continue
            if m[2] - m[3] < min_tb and not fixe[i][2]:
                continue
            if not req <= {x % 12 for x in m}:
                continue
            ok.append(combo)
        if not ok:
            raise ValueError(f'accord {i + 1} : aucune disposition ({cib}, {fixe[i]})')
        cand_all.append(ok)
    # programmation dynamique
    cout = [{c: abs(midi(N(c[0])) - centre) * 0.5 for c in cand_all[0]}]
    prev = [{}]
    for i in range(1, len(cand_all)):
        d, p = {}, {}
        for c in cand_all[i]:
            mc = [midi(N(x)) for x in c]
            best = None
            for a, ca in cout[-1].items():
                ma = [midi(N(x)) for x in a]
                k = ca + sum(abs(x - y) for x, y in zip(ma[:3], mc[:3]))
                if best is None or k < best[0]:
                    best = (k, a)
            d[c], p[c] = best
        cout.append(d); prev.append(p)
    c = min(cout[-1], key=cout[-1].get)
    sol = [c]
    for i in range(len(cand_all) - 1, 0, -1):
        c = prev[i][c]
        sol.append(c)
    return sol[::-1]


def controle(sol, cibles, requis, voix, parallele=None):
    """même contrôle que fautesLibre (atelier.js)"""
    errs = []
    for i, ch in enumerate(sol):
        p = {pc(c) for c in cibles[i]}
        for v, x in enumerate(ch):
            lo, hi = (midi(N(t)) for t in TESS[v])
            if not lo <= midi(N(x)) <= hi:
                errs.append(f'{i + 1} {VOIX[v]} hors tessiture {x}')
            if v in voix and pc(x) not in p:
                errs.append(f'{i + 1} {x} hors accord')
        for v in range(3):
            if midi(N(ch[v])) < midi(N(ch[v + 1])):
                errs.append(f'{i + 1} croisement')
        if not {pc(r) for r in (requis or cibles)[i]} <= {pc(x) for x in ch}:
            errs.append(f'{i + 1} il manque')
    if parallele:
        h = (lambda x: dpos(N(x))) if parallele == 'diato' else (lambda x: midi(N(x)))
        for i in range(1, len(sol)):
            a, b = sol[i - 1], sol[i]
            if [h(x) - h(a[3]) for x in a] != [h(x) - h(b[3]) for x in b]:
                errs.append(f'{i}-{i + 1} pas parallèle')
    return errs


def joli(x):
    return x.replace('#', '♯').replace('b', '♭') if len(x) > 1 and x[0] in 'ABCDEFG' else x


def labels(symb, durees, rang=0, couleur=BLUE):
    out, t = [], 0
    for s, d in zip(symb, durees):
        if s:
            out.append((t, s, rang, couleur))
        t += d
    return out


def faire_libre(dico, nom_ex, sol, symb, voix, dossier, cibles=None, requis=None, durees=None, parallele=None, quoi=None,
                armure=0, tonique='Do', titre_ligne='accords', montrer=True, cols=None, donnes=()):
    """Exercice libre : énoncé (voix données), corrigé, dict pour l'atelier."""
    k = len(sol)
    durees = durees or [4] * k
    cibles = cibles or [sorted({sans_oct(x) for x in ch}, key=lambda y: (pc(y) - pc(ch[3])) % 12) for ch in sol]
    req = requis or cibles
    e = controle(sol, cibles, req, voix, parallele)
    assert not e, (nom_ex, e)
    donne = [[None if (v in voix and i not in donnes) else c[v] for v in range(4)] for i, c in enumerate(sol)]
    ex = {'donne': donne, 'solution': [list(c) for c in sol], 'durees': durees, 'voix': voix, 'tonique': tonique, 'armure': armure,
          'degres': [s or '' for s in symb] if montrer else None, 'chiffres': None, 'tierce': [], 'chant': False, 'corriger': False,
          'guide': None, 'isoles': False, 'libre': True, 'cibles': [list(c) for c in cibles]}
    if requis:
        ex['requis'] = [list(r) for r in requis]
    if parallele:
        ex['parallele'] = parallele
    if quoi:
        ex['quoi'] = quoi
    dico[nom_ex] = ex
    temps = (4, 4) if any(d < 4 for d in durees) else None
    lab = labels(symb, durees) if montrer else None
    rows = [titre_ligne] if montrer else None
    voices = []
    for v, (st, stem) in enumerate([(0, 'up'), (0, 'down'), (1, 'up'), (1, 'down')]):
        ev = [((donne[i][v] if donne[i][v] else None), durees[i], {} if donne[i][v] else {'hide': True}) for i in range(k)]
        voices.append({'staff': st, 'stem': stem, 'events': ev})
    Figure([{'clef': 'treble'}, {'clef': 'bass'}], voices, key=armure, brace=(0, 1), gap=104, unit=22, time=temps,
           labels=lab, rows=rows).save(os.path.join(dossier, nom_ex + '.png'))
    ch = [tuple(c) + (d,) for c, d in zip(sol, durees)]
    col = dict(cols or {})
    for v in voix:
        for i in range(k):
            if i not in donnes:
                col.setdefault((v, i), BLUE)
    satb(ch, key=armure, unit=22, time=temps, labels=labels(symb, durees), rows=[titre_ligne], colors=col).save(
        os.path.join(dossier, nom_ex + '-c.png'))
    return sol
