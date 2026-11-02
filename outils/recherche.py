"""Recherche automatique de réalisations sans faute (utilisée pour préparer exemples et corrigés)."""
import itertools
from graveur import N, midi, dpos, FR
from verif import check, TESS, VOIX

def notes_in_range(steps_alts, lo, hi):
    out=[]
    for o in range(1,7):
        for s,a in steps_alts:
            n=FR[s]+('#' if a==1 else 'b' if a==-1 else '')+str(o)
            if midi(N(lo))<=midi(N(n))<=midi(N(hi)): out.append(n)
    return out

def chord_notes(names):
    res=[]
    for nm in names:
        a=0
        if nm.endswith('#'): a=1; nm=nm[:-1]
        elif nm.endswith('b'): a=-1; nm=nm[:-1]
        res.append((FR.index(nm),a))
    return res

def voicings(names, bass=None, sop=None, tonic='Do', allow=False):
    sa=chord_notes(names)
    pools=[notes_in_range(sa,*TESS[v]) for v in VOIX]
    if bass: pools[3]=[bass]
    if sop: pools[0]=[sop]
    res=[]
    for S,A,T,B in itertools.product(*pools):
        v=(S,A,T,B)
        if not check([v], tonic, allow_third={0} if allow else ()): res.append(v)
    return res

def penal(v):
    """Pénalité de « confort » : unissons entre voix voisines, soprano trop grave."""
    m = [midi(N(x)) for x in v[:4]]
    p = 4 * sum(1 for k in range(3) if m[k] == m[k + 1])
    p += max(0, midi(N('La4')) - m[0]) * 0.5
    return p


def motion(a, b):
    return sum(abs(midi(N(x)) - midi(N(y))) for x, y in zip(a[:3], b[:3])) + penal(b)

def realise(chords, basses, sops=None, tonic='Do', fixed=None, allow_third=(), n=5):
    """Programmation dynamique : réalisation sans faute, mouvement minimal des voix supérieures."""
    sops = sops or [None] * len(chords)
    cand = []
    for i, (c, b, s) in enumerate(zip(chords, basses, sops)):
        vs = voicings(c, bass=b, sop=s, tonic=tonic, allow=i in allow_third)
        if fixed and fixed[i]:
            vs = [v for v in vs if all(f is None or f == x for f, x in zip(fixed[i], v))]
        cand.append(vs)
    best = {v: (penal(v), [v]) for v in cand[0]}
    for i in range(1, len(chords)):
        nb = {}
        for v in cand[i]:
            opts = []
            for u, (cost, path) in best.items():
                if check([u, v], tonic, allow_third={k for k, j in ((0, i - 1), (1, i)) if j in allow_third}):
                    continue
                opts.append((cost + motion(u, v), path + [v]))
            if opts:
                nb[v] = min(opts)
        best = nb
    res = sorted(best.values())[:n]
    for cost, path in res:   # contrôle final sur toute la phrase
        assert not check(path, tonic, allow_third=allow_third), check(path, tonic, allow_third=allow_third)
    return res


GRAMMAIRE = {'I': ('II', 'IV', 'V', 'VI'), 'II': ('V',), 'IV': ('I', 'II', 'V'), 'V': ('I', 'VI'), 'VI': ('II', 'IV', 'V')}


def harmonise(sop, degres, tonic='Do', fixed_deg=None, etats=('5', '6'), n=3):
    """Choisit les accords sous un chant donné. degres : {'I': ['Do','Mi','Sol'], ...}.
    fixed_deg : liste (même longueur) de (degré, état) imposés ou None."""
    from verif import etat
    fixed_deg = fixed_deg or [None] * len(sop)
    cand = []
    for i, s in enumerate(sop):
        opts = []
        for dg, names in degres.items():
            if fixed_deg[i] and fixed_deg[i][0] != dg:
                continue
            if N(s)['s'] not in [st for st, a in chord_notes(names)]:
                continue
            for b in notes_in_range(chord_notes(names), *TESS['basse']):
                for v in voicings(names, bass=b, sop=s, tonic=tonic):
                    e = etat(v)
                    if (fixed_deg[i] and fixed_deg[i][1] != e) or (not fixed_deg[i] and e not in etats):
                        continue
                    opts.append((dg, e, v))
        cand.append(opts)
    def cost(u, v):
        (du, eu, a), (dv, ev, b) = u, v
        c = motion(a, b)
        leap = abs(midi(N(a[3])) - midi(N(b[3])))
        c += leap * 0.4 + (4 if leap > 7 else 0) + (2 if leap == 0 else 0)
        c += (2 if eu != ev else 30) if du == dv else 0
        if GRAMMAIRE and du != dv and dv not in GRAMMAIRE.get(du, ()):
            c += 30
        c += 1.5 if ev != '5' else 0
        return c
    best = {u: (penal(u[2]), [u]) for u in cand[0]}
    for i in range(1, len(sop)):
        nb = {}
        for v in cand[i]:
            o = [(c + cost(u, v), p + [v]) for u, (c, p) in best.items() if not check([u[2], v[2]], tonic)]
            if o:
                nb[v] = min(o)
        best = nb
    res = sorted(best.values())[:n]
    for c, p in res:
        assert not check([x[2] for x in p], tonic)
    return res
