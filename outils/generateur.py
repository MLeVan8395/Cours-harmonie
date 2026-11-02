"""Réalise une phrase donnée par ses degrés et ses états, en choisissant aussi la basse et le soprano.

phrase('I IV V6 I', tonique='Do', armure=0) -> liste d'accords (S, A, T, B), sans faute.
Le coût favorise : peu de mouvement aux voix intérieures, une basse chantante,
un soprano conjoint et bien placé, et pas d'unissons entre voix voisines.
"""
from functools import lru_cache
from graveur import N, midi, dpos, FR
from verif import check, TESS, VOIX
from recherche import notes_in_range, voicings, penal

MAJ = {'Do': 0, 'Sol': 1, 'Ré': 2, 'La': 3, 'Mi': 4, 'Fa': -1, 'Sib': -2}
SHARP_ORDER = [3, 0, 4, 1, 5, 2, 6]
FLAT_ORDER = [6, 2, 5, 1, 4, 0, 3]
DEG = {'I': 0, 'II': 1, 'III': 2, 'IV': 3, 'V': 4, 'VI': 5, 'VII': 6}


def alts(armure):
    d = {}
    if armure > 0:
        for s in SHARP_ORDER[:armure]:
            d[s] = 1
    for s in FLAT_ORDER[:max(0, -armure)]:
        d[s] = -1
    return d


def mode(tonique, armure):
    return 'majeur' if MAJ.get(tonique) == armure else 'mineur'


def note_degre(tonique, armure, k):
    t = FR.index(tonique.rstrip('b#'))
    s = (t + k) % 7
    a = alts(armure).get(s, 0)
    if mode(tonique, armure) == 'mineur' and k % 7 == 6:
        a += 1
    return FR[s] + ('#' if a == 1 else 'b' if a == -1 else '')


def accord(tonique, armure, d):
    return [note_degre(tonique, armure, d + k) for k in (0, 2, 4)]


def parse(txt):
    """'I IV6 V64 I' -> [(0, '5'), (3, '6'), (4, '64'), (0, '5')]"""
    out = []
    for tok in txt.split():
        e = '64' if tok.endswith('64') else '6' if tok.endswith('6') else '5'
        out.append((DEG[tok.rstrip('64')], e))
    return out


def chiffre(tonique, armure, d, e):
    """Chiffrage français ; en mineur, le V (tierce haussée) s'écrit avec l'altération de la sensible."""
    if mode(tonique, armure) == 'mineur' and d == 4 and e == '5':
        return '♯' if note_degre(tonique, armure, 6).endswith('#') else '♮'
    return {'5': '5', '6': '6', '64': '6/4'}[e]


def phrase(txt, tonique='Do', armure=0, soprano_fin=True, n=1, sop_max='Fa5', sop_min='Fa4', sop=None, basse=None):
    seq = parse(txt)
    ton = tonique
    cands, allow = [], set()
    degres = [d for d, e in seq]
    for i, (d, e) in enumerate(seq):
        names = accord(tonique, armure, d)
        bnote = names[{'5': 0, '6': 1, '64': 2}[e]]
        # VI relié à V : tierce doublée permise (cadence rompue, VI-V en mineur)
        if d == 5 and ((i > 0 and degres[i - 1] == 4) or (i < len(seq) - 1 and degres[i + 1] == 4)):
            allow.add(i)
        vs = []
        bs = [basse[i]] if basse else notes_in_range([chord_step(bnote)], *TESS['basse'])
        if basse:
            assert basse[i][:-1] == bnote, f'basse {i + 1} : {basse[i]} au lieu de {bnote} ({txt})'
        if sop:
            assert sop[i][:-1] in names, f'soprano {i + 1} : {sop[i]} hors de {names} ({txt})'
        for b in bs:
            for v in voicings(names, bass=b, sop=sop[i] if sop else None, tonic=tonique, allow=i in allow):
                if not sop and (midi(N(v[0])) > midi(N(sop_max)) or midi(N(v[0])) < midi(N(sop_min))):
                    continue
                pas = {N(x)['s'] for x in v}
                besoin = [chord_step(names[0])[0], chord_step(names[1])[0]] + ([chord_step(names[2])[0]] if e != '5' else [])
                if not all(p in pas for p in besoin):     # l'accord voulu, pas un autre
                    continue
                vs.append(v)
        cands.append(vs)

    @lru_cache(maxsize=None)
    def ok(i, u, v):
        al = {k for k, j in ((0, i - 1), (1, i)) if j in allow}
        return not check([u, v], tonique, allow_third=al)

    def cout(i, u, v):
        c = sum(abs(midi(N(x)) - midi(N(y))) for x, y in zip(u[1:3], v[1:3])) + penal(v)
        bs = abs(midi(N(u[3])) - midi(N(v[3])))
        c += bs * 0.3 + (3 if bs > 7 else 0)
        ss = abs(dpos(N(u[0])) - dpos(N(v[0])))
        c += {0: 5, 1: 0, 2: 1}.get(ss, 2 + ss * 1.5)
        c += max(0, midi(N(v[3])) - midi(N('Ré3'))) * 0.15     # basse plutôt grave
        # 6/4 de cadence : même basse que le V qui suit
        if seq[i - 1][1] == '64' and seq[i][0] == 4 and u[3] != v[3]:
            c += 100
        return c

    best = {v: (penal(v), [v]) for v in cands[0]}
    for i in range(1, len(seq)):
        nb = {}
        for v in cands[i]:
            o = [(c + cout(i, u, v), p + [v]) for u, (c, p) in best.items() if ok(i, u, v)]
            if o:
                nb[v] = min(o)
        best = nb
    res = sorted(best.values())
    if soprano_fin:
        t = note_degre(tonique, armure, 0)
        res = [r for r in res if r[1][-1][0][:-1] == t] or res
    if not res:
        raise ValueError('pas de réalisation : ' + txt)
    out = res[:n]
    for c, p in out:
        assert not check(p, tonique, allow_third=allow), check(p, tonique, allow_third=allow)
    return [p for c, p in out], allow, seq


def chord_step(name):
    s = name.rstrip('#b')
    a = 1 if name.endswith('#') else -1 if name.endswith('b') and name != 'b' else 0
    return (FR.index(s), a)


def diagnostic(txt, tonique='Do', armure=0, sop=None, basse=None):
    """Indique à quel accord une phrase devient impossible."""
    toks = txt.split()
    for k in range(2, len(toks) + 1):
        try:
            phrase(' '.join(toks[:k]), tonique, armure, soprano_fin=False, sop=sop[:k] if sop else None, basse=basse[:k] if basse else None)
        except (ValueError, AssertionError) as e:
            return k, toks[k - 2:k], str(e)[:120]
    return None
