"""Vérificateur des règles d'écriture à 4 voix (style choral, accords de 3 sons).

check(chords, tonic='Do', allow_third=set()) -> liste de fautes (texte).
chords : liste de (S, A, T, B) en notation "Do4".
tonic : nom de la tonique (« Do », « La »…), sert à trouver la sensible
        (un demi-ton sous la tonique : Si en Do majeur, Sol♯ en la mineur).
allow_third : indices des accords où la tierce doublée est voulue
        (VI de la cadence rompue).
"""
from graveur import N, dpos, midi, FR, SEMI

VOIX = ['soprano', 'alto', 'ténor', 'basse']
# tessitures (incluses) : chaque voix couvre une douzième
TESS = {'soprano': ('Do4', 'Sol5'), 'alto': ('Sol3', 'Ré5'), 'ténor': ('Do3', 'Sol4'), 'basse': ('Fa2', 'Do4')}


def pc(n):
    return (SEMI[n['s']] + n['a']) % 12


def name(n):
    return FR[n['s']] + ('♯' if n['a'] == 1 else '♭' if n['a'] == -1 else '')


def interval(lo, hi):
    return dpos(hi) - dpos(lo), midi(hi) - midi(lo)


def is_p5(lo, hi):
    d, st = interval(lo, hi)
    return d > 0 and d % 7 == 4 and st % 12 == 7


def is_p8(lo, hi):
    d, st = interval(lo, hi)
    return d % 7 == 0 and st % 12 == 0


def triad(ch):
    """Fondamentale, tierce, quinte (degrés diatoniques) d'un accord de 3 sons."""
    notes = [N(x) for x in ch[:4] if x]
    steps = sorted(set(n['s'] for n in notes))
    for r in steps:
        third, fifth = (r + 2) % 7, (r + 4) % 7
        if set(steps) <= {r, third, fifth}:
            return r, third, fifth
    return None


def etat(ch):
    """'5' (état fondamental), '6' (1er renversement) ou '64' (2e renversement)."""
    tr = triad(ch)
    if tr is None:
        return None
    b = N(ch[3])['s']
    return {tr[0]: '5', tr[1]: '6', tr[2]: '64'}[b]


def qualite(ch):
    """'M' majeur, 'm' mineur, 'd' diminué, 'A' augmenté."""
    tr = triad(ch)
    notes = {N(x)['s']: N(x) for x in ch[:4]}
    r, t, f = (notes[s] if s in notes else None for s in tr)
    if t is None:
        return None
    t3 = (pc(t) - pc(r)) % 12
    if f is None:
        return 'M' if t3 == 4 else 'm'
    t5 = (pc(f) - pc(r)) % 12
    return {(4, 7): 'M', (3, 7): 'm', (3, 6): 'd', (4, 8): 'A'}.get((t3, t5), '?')


def check(chords, tonic='Do', allow_third=(), **_):
    errs = []
    P = [[N(x) for x in ch[:4]] for ch in chords]
    ton = N(tonic + '4')
    sens_pc = (pc(ton) + 11) % 12
    for i, ch in enumerate(P):
        m = f'accord {i + 1}'
        for v, n in enumerate(ch):
            lo, hi = (N(x) for x in TESS[VOIX[v]])
            if midi(n) < midi(lo) or midi(n) > midi(hi):
                errs.append(f'{m} : {VOIX[v]} hors tessiture ({name(n)})')
        for v in range(3):
            if midi(ch[v]) < midi(ch[v + 1]):
                errs.append(f'{m} : croisement {VOIX[v]}/{VOIX[v + 1]}')
        if dpos(ch[0]) - dpos(ch[1]) > 7:
            errs.append(f'{m} : écart soprano-alto supérieur à l\'octave')
        if dpos(ch[1]) - dpos(ch[2]) > 7:
            errs.append(f'{m} : écart alto-ténor supérieur à l\'octave')
        if dpos(ch[2]) - dpos(ch[3]) > 11:
            errs.append(f'{m} : écart ténor-basse supérieur à la douzième')
        tr = triad(chords[i])
        if tr is None:
            errs.append(f'{m} : pas un accord parfait')
        else:
            r, t, f = tr
            steps = [n['s'] for n in ch]
            e = etat(chords[i])
            q = qualite(chords[i])
            if t not in steps:
                errs.append(f'{m} : tierce absente')
            if e == '5':
                if steps.count(t) > 1 and i not in allow_third:
                    errs.append(f'{m} : tierce doublée')
                if steps.count(r) < 2 and i not in allow_third and not (steps.count(f) >= 2 and q == 'd'):
                    errs.append(f'{m} : fondamentale non doublée à l\'état fondamental')
                if steps.count(r) > 3:
                    errs.append(f'{m} : fondamentale quadruplée')
            elif e == '6':
                if f not in steps or r not in steps:
                    errs.append(f'{m} : accord de sixte incomplet')
                if steps.count(t) > 1 and q == 'M':
                    errs.append(f'{m} : basse doublée dans un accord de sixte majeur')
            elif e == '64':
                if steps.count(f) < 2:
                    errs.append(f'{m} : basse non doublée dans un accord de quarte et sixte')
                if r not in steps:
                    errs.append(f'{m} : accord de quarte et sixte incomplet')
            if q == 'A':
                errs.append(f'{m} : accord augmenté')
        if sum(1 for n in ch if pc(n) == sens_pc) > 1:
            errs.append(f'{m} : sensible doublée')
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        m = f'accords {i + 1}-{i + 2}'
        for u in range(4):
            for l in range(u + 1, 4):
                if midi(a[u]) == midi(b[u]) and midi(a[l]) == midi(b[l]):
                    continue  # notes tenues
                for test, nom in ((is_p5, '5tes'), (is_p8, '8ves')):
                    if test(a[l], a[u]) and test(b[l], b[u]):
                        same = (midi(b[u]) - midi(a[u])) * (midi(b[l]) - midi(a[l])) > 0
                        kind = 'consécutives' if same else 'par mouvement contraire'
                        if midi(a[u]) == midi(a[l]) and midi(b[u]) == midi(b[l]):
                            nom = 'unissons'
                        errs.append(f'{m} : {nom} {kind} {VOIX[u]}/{VOIX[l]}')
        # directes entre extrêmes : mouvement direct vers 5te/8ve, soprano par saut
        du, dl = midi(b[0]) - midi(a[0]), midi(b[3]) - midi(a[3])
        if du * dl > 0:
            for test, nom in ((is_p5, '5te'), (is_p8, '8ve')):
                if test(b[3], b[0]) and not test(a[3], a[0]):
                    if abs(dpos(b[0]) - dpos(a[0])) > 1:
                        errs.append(f'{m} : {nom} directe soprano/basse (soprano par saut)')
        for v in range(3):
            if midi(b[v]) < midi(a[v + 1]) or midi(b[v + 1]) > midi(a[v]):
                errs.append(f'{m} : chevauchement {VOIX[v]}/{VOIX[v + 1]}')
        # la sensible des voix extrêmes monte à la tonique
        for v in (0, 3):
            if pc(a[v]) == sens_pc and pc(b[v]) != (sens_pc + 1) % 12 and pc(b[v]) != sens_pc:
                errs.append(f'{m} : sensible ({VOIX[v]}) non résolue sur la tonique')
        # mélodie : intervalles augmentés, septièmes, sauts de plus d'une octave
        for v in range(4):
            d, st = dpos(b[v]) - dpos(a[v]), midi(b[v]) - midi(a[v])
            ad, ast = abs(d), abs(st)
            if ad == 1 and ast == 3:
                errs.append(f'{m} : seconde augmentée ({VOIX[v]})')
            if ad == 3 and ast == 6:
                errs.append(f'{m} : quarte augmentée ({VOIX[v]})')
            if ad == 6:
                errs.append(f'{m} : saut de septième ({VOIX[v]})')
            if ad > 7:
                errs.append(f'{m} : saut de plus d\'une octave ({VOIX[v]})')
            if v < 3 and ad > 4 and not (ad == 7 and ast == 12) and not (ad == 5 and st > 0):
                errs.append(f'{m} : saut trop grand ({VOIX[v]})')
    return errs
