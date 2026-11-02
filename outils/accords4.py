"""Accords de 4 sons, dominantes secondaires et modulation : symboles, notes, chiffrage, et réalisation d'une phrase.

Symboles d'une phrase (séparés par des espaces) :
    I  V6  I64          accords de 3 sons, comme dans generateur.py
    V7 V65 V43 V2       7e de dominante et ses renversements (chiffrés 7+, 6/5, +6, +4)
    II7 II65 IV7        7es d'espèce (chiffrées 7, 6/5, 4/3, 2)
    VIIo7 VIIo65        7e diminuée (en majeur, le 6e degré est abaissé)
    VII7                7e de sensible (en majeur)
    V9                  9e de dominante (sans quinte, à 4 voix)
    V/V  V7/V  V65/IV   dominante (avec ou sans 7e) d'un autre degré
    VIIo7/V             7e diminuée d'un autre degré
    [Sol] [mi]          les accords suivants sont dans cette tonalité (modulation)

phrase4('I II65 V7 I', 'Do', 0) -> (réalisations, tierces doublées permises, liste des accords)
"""
import re
from functools import lru_cache
from graveur import N, midi, dpos, FR, SEMI
from verif import check, TESS, info4, triad
from recherche import notes_in_range, voicings, penal
from generateur import note_degre, mode, chiffre, DEG

TONS = {'Do': ('Do', 0), 'Sol': ('Sol', 1), 'Ré': ('Ré', 2), 'La': ('La', 3), 'Mi': ('Mi', 4), 'Fa': ('Fa', -1), 'Sib': ('Sib', -2),
        'la': ('La', 0), 'mi': ('Mi', 1), 'si': ('Si', 2), 'ré': ('Ré', -1), 'sol': ('Sol', -2), 'do': ('Do', -3), 'fa#': ('Fa#', 3)}
DEGN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
RX = re.compile(r'^(VII|VI|V|IV|III|II|I)(o)?(9|7|65|43|2|64|6)?(?:/(VII|VI|V|IV|III|II|I))?$')
BASSE = {'5': 0, '6': 1, '64': 2, '7': 0, '65': 1, '43': 2, '2': 3, '9': 0}


def nom(step, p):
    """Nom d'une note à partir de son degré diatonique (0 = Do) et de sa classe de hauteur."""
    a = (p - SEMI[step] + 6) % 12 - 6
    return FR[step] + {0: '', 1: '#', -1: 'b', 2: '##', -2: 'bb'}[a]


def pc_nom(n):
    return midi(N(n + '4')) % 12


def nom_ton(t, a):
    return f'{t} majeur' if mode(t, a) == 'majeur' else f'{t.lower()} mineur'


def spec(tok, tonique, armure):
    m = RX.match(tok)
    assert m, tok
    deg, dim, chif, cible = m.group(1), m.group(2), m.group(3) or '5', m.group(4)
    d = DEG[deg]
    nsons = 5 if chif == '9' else 4 if chif in ('7', '65', '43', '2') else 3
    if cible is None:
        names = [note_degre(tonique, armure, d + 2 * k) for k in range(nsons)]
        if dim:   # 7e diminuée en majeur : on abaisse la 7e de l'accord (6e degré)
            r = N(names[0] + '4')
            names[3] = nom((r['s'] + 6) % 7, (pc_nom(names[0]) + 9) % 12)
        label = deg
    else:
        c = DEG[cible]
        cn = note_degre(tonique, armure, c)
        cs, cp = FR.index(cn.rstrip('#b')), pc_nom(cn)
        if deg == 'V':
            rs, rp, ivs = (cs + 4) % 7, (cp + 7) % 12, [0, 4, 7, 10, 14]
        else:
            assert deg == 'VII' and dim, tok
            rs, rp, ivs = (cs + 6) % 7, (cp + 11) % 12, [0, 3, 6, 9]
        names = [nom((rs + 2 * k) % 7, (rp + ivs[k]) % 12) for k in range(nsons)]
        label = f'{deg}/{cible}'
    if nsons >= 4:
        q = qualite4(names)
        dom = q in ('dom', 'o7', 'dom9') or (q == 'ø' and pc_nom(names[0]) == (pc_nom(tonique) + 11) % 12)
        if chif == '9':
            ch = '9+'
        elif q == 'o7':
            ch = {'7': '7°', '65': '6/5', '43': '4/3', '2': '2'}[chif]
        elif q == 'dom':
            ch = {'7': '7+', '65': '6/5', '43': '+6', '2': '+4'}[chif]
        else:
            ch = {'7': '7', '65': '6/5', '43': '4/3', '2': '2'}[chif]
    else:
        q = None
        if cible is None:
            ch = chiffre(tonique, armure, d, chif)
        else:
            ch = {'5': '5', '6': '6', '64': '6/4'}[chif]
        if cible is not None and chif == '5':
            ch = '5'
    return {'tok': tok, 'names': names, 'etat': chif, 'label': label, 'chiffre': ch, 'ton': (tonique, armure),
            'deg': d if cible is None else None, 'q': q, 'basse': names[BASSE[chif]]}


def qualite4(names):
    p = [pc_nom(n) for n in names]
    iv = tuple((x - p[0]) % 12 for x in p[1:4])
    q = {(4, 7, 10): 'dom', (4, 7, 11): 'M7', (3, 7, 10): 'm7', (3, 6, 10): 'ø', (3, 6, 9): 'o7'}.get(iv, '?')
    if len(names) == 5 and q == 'dom':
        q = 'dom9'
    return q


def lire(plan, tonique, armure):
    """Liste des accords d'un plan, avec la tonalité de chacun."""
    t, a = tonique, armure
    out = []
    for tok in plan.split():
        if tok.startswith('['):
            t, a = TONS[tok.strip('[]')]
            continue
        marche = tok.endswith('*')
        if '=' in tok:   # accord pivot : « VI=[Sol]II »
            avant, apres = tok.rstrip('*').split('=')
            t, a = TONS[apres[1:apres.index(']')]]
            sp = spec(apres[apres.index(']') + 1:], t, a)
            sp['label'] = avant + ' = ' + sp['label']
            sp['pivot'] = True
        else:
            sp = spec(tok.rstrip('*'), t, a)
        sp['marche'] = marche
        out.append(sp)
    return out


def step_alt(name):
    n = N(name + '4')
    return n['s'], n['a']


def phrase4(plan, tonique='Do', armure=0, soprano_fin=True, n=1, sop_max='Fa5', sop_min='Fa4', sop=None, basse=None, eviter=None):
    seq = lire(plan, tonique, armure)
    tons = [s['ton'][0] for s in seq]
    libres = {i for i, s in enumerate(seq) if s['marche']}
    allow = set()
    for i, s in enumerate(seq):   # VI relié à V : tierce doublée permise
        if s['deg'] == 5 and s['q'] is None and s['etat'] == '5' and any(
                0 <= j < len(seq) and seq[j]['deg'] == 4 and seq[j]['label'] == 'V' for j in (i - 1, i + 1)):
            allow.add(i)
    cands = []
    for i, s in enumerate(seq):
        names = s['names']
        bnote = s['basse']
        if basse:
            assert basse[i][:-1] == bnote, f'basse {i + 1} : {basse[i]} au lieu de {bnote} ({plan})'
            bs = [basse[i]]
        else:
            bs = notes_in_range([step_alt(bnote)], *TESS['basse'])
        if sop:
            assert sop[i][:-1] in names, f'soprano {i + 1} : {sop[i]} hors de {names} ({plan})'
        besoin = {step_alt(names[0])[0], step_alt(names[1])[0]}
        if len(names) >= 4:
            besoin.add(step_alt(names[3])[0])
        if len(names) == 5:
            besoin.add(step_alt(names[4])[0])
        if s['etat'] not in ('5', '7', '9'):
            besoin.add(step_alt(names[2])[0])
        vs = []
        for b in bs:
            for v in voicings(names, bass=b, sop=sop[i] if sop else None, tonic=tons[i], allow=i in allow):
                if not sop and (midi(N(v[0])) > midi(N(sop_max)) or midi(N(v[0])) < midi(N(sop_min))):
                    continue
                if not besoin <= {N(x)['s'] for x in v}:
                    continue
                if eviter and eviter(i, v):
                    continue
                vs.append(v)
        cands.append(vs)

    @lru_cache(maxsize=None)
    def ok(i, u, v):
        al = {k for k, j in ((0, i - 1), (1, i)) if j in allow}
        return not check([u, v], [tons[i - 1], tons[i]], allow_third=al, libres={0} if i - 1 in libres else ())

    def cout(i, u, v):
        c = sum(abs(midi(N(x)) - midi(N(y))) for x, y in zip(u[1:3], v[1:3])) + penal(v)
        bs = abs(midi(N(u[3])) - midi(N(v[3])))
        c += bs * 0.3 + (3 if bs > 7 else 0)
        ss = abs(dpos(N(u[0])) - dpos(N(v[0])))
        c += {0: 5, 1: 0, 2: 1}.get(ss, 2 + ss * 1.5)
        c += max(0, midi(N(v[3])) - midi(N('Ré3'))) * 0.15
        if seq[i - 1]['etat'] == '64' and seq[i]['label'] == 'V' and u[3] != v[3]:
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
        t = note_degre(seq[-1]['ton'][0], seq[-1]['ton'][1], 0)
        res = [r for r in res if r[1][-1][0][:-1] == t] or res
    if not res:
        raise ValueError('pas de réalisation : ' + plan)
    out = res[:n]
    for c, p in out:
        assert not check(p, tons, allow_third=allow, libres=libres), check(p, tons, allow_third=allow, libres=libres)
    return [p for c, p in out], allow, seq


def diagnostic4(plan, tonique='Do', armure=0, sop=None, basse=None):
    toks = plan.split()
    k0 = 0
    for k in range(2, len(toks) + 1):
        try:
            phrase4(' '.join(toks[:k]), tonique, armure, soprano_fin=False, sop=sop[:k - sum(1 for t in toks[:k] if t.startswith('['))] if sop else None,
                    basse=basse[:k - sum(1 for t in toks[:k] if t.startswith('['))] if basse else None)
        except (ValueError, AssertionError) as e:
            return k, toks[k - 2:k], str(e)[:150]
    return None


if __name__ == '__main__':
    for plan, t, a in [('I IV V7 I', 'Do', 0), ('I II65 V7 I', 'Do', 0), ('I V65 I V43 I6 IV V7 I', 'Do', 0),
                       ('I V2 I6 II7 V7 I', 'Sol', 1), ('I IV VIIo7 I', 'La', 0), ('I V7/V V7 I', 'Do', 0),
                       ('I VI [Sol] II V7 I', 'Do', 0), ('I V9 I', 'Do', 0), ('I IV7 VII7 III VI II V7 I', 'Do', 0)]:
        try:
            ps, al, seq = phrase4(plan, t, a)
            print(plan, ' | ', [s['label'] + ' ' + s['chiffre'] for s in seq])
            print('   ', ps[0])
        except Exception as e:
            print('ÉCHEC', plan, e, diagnostic4(plan, t, a))
