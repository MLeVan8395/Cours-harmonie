"""Vérificateur des règles d'écriture à 4 voix (style choral, accords de 3 et de 4 sons).

check(chords, tonic='Do', allow_third=set()) -> liste de fautes (texte).
chords : liste de (S, A, T, B) en notation "Do4".
tonic : nom de la tonique (« Do », « La »…), sert à trouver la sensible
        (un demi-ton sous la tonique : Si en Do majeur, Sol♯ en la mineur).
        On peut aussi donner une tonique par accord (liste), pour une modulation.
allow_third : indices des accords où la tierce doublée est voulue
        (VI de la cadence rompue).
libres : indices des accords pris dans une marche harmonique : leur sensible n'est pas obligée de monter.
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


def tetrade(ch):
    """Accord de 7e (ou de 9e) : (fondamentale, tierce, quinte, septième, neuvième ou None), en degrés diatoniques."""
    steps = set(N(x)['s'] for x in ch[:4] if x)
    for r in sorted(steps):
        t, f, s, nn = (r + 2) % 7, (r + 4) % 7, (r + 6) % 7, (r + 1) % 7
        if t in steps and s in steps and steps <= {r, t, f, s, nn}:
            return r, t, f, s, (nn if nn in steps else None)
    return None


def info4(ch):
    """Description d'un accord de 4 sons : dict(r, t, f, s, nn, q, etat, pcs) ou None.
    q : 'dom' (7e de dominante), 'M7', 'm7', 'ø' (7e de sensible, mineure), 'o7' (7e diminuée), '?'."""
    te = tetrade(ch)
    if te is None or triad(ch) is not None:
        return None
    r, t, f, s, nn = te
    notes = {N(x)['s']: N(x) for x in ch[:4]}
    pr = pc(notes[r])
    t3 = (pc(notes[t]) - pr) % 12
    t7 = (pc(notes[s]) - pr) % 12
    t5 = (pc(notes[f]) - pr) % 12 if f in notes else None
    if t3 == 4 and t7 == 10 and t5 in (7, None):
        q = 'dom'
    elif t3 == 4 and t7 == 11 and t5 in (7, None):
        q = 'M7'
    elif t3 == 3 and t7 == 10 and t5 in (7, None):
        q = 'm7'
    elif t3 == 3 and t7 == 10 and t5 == 6:
        q = 'ø'
    elif t3 == 3 and t7 == 9 and t5 in (6, None):
        q = 'o7'
    else:
        q = '?'
    b = N(ch[3])['s']
    e = {r: '7', t: '65', f: '43', s: '2'}.get(b, '9b')
    if nn is not None and b == r:
        e = '9'
    return {'r': r, 't': t, 'f': f, 's': s, 'nn': nn, 'q': q, 'etat': e, 'pr': pr}


def sensible_de(tonic):
    return (pc(N(tonic + '4')) + 11) % 12


def famille_dominante(A, sens):
    """Accords « de dominante » : leur 7e n'a pas besoin d'être préparée ; renvoie le pc de leur sensible, ou None."""
    if A is None:
        return None
    if A['q'] == 'dom':
        return (A['pr'] + 4) % 12
    if A['q'] == 'o7' or (A['q'] == 'ø' and A['pr'] == sens):
        return A['pr']
    return None


def check(chords, tonic='Do', allow_third=(), libres=(), **_):
    errs = []
    P = [[N(x) for x in ch[:4]] for ch in chords]
    tons = list(tonic) if isinstance(tonic, (list, tuple)) else [tonic] * len(chords)
    SENS = [sensible_de(t) for t in tons]
    INFO = [info4(ch) for ch in chords]
    for i, ch in enumerate(P):
        m = f'accord {i + 1}'
        sens_pc = SENS[i]
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
        A = INFO[i]
        steps = [n['s'] for n in ch]
        if tr is not None:
            r, t, f = tr
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
        elif A is not None:
            if A['q'] == '?':
                errs.append(f'{m} : accord de septième inusité')
            if steps.count(A['s']) > 1:
                errs.append(f'{m} : septième doublée')
            if A['nn'] is not None:
                if A['etat'] != '9':
                    errs.append(f'{m} : accord de neuvième renversé (la fondamentale reste à la basse)')
                elif steps.count(A['nn']) > 1:
                    errs.append(f'{m} : neuvième doublée')
                else:
                    v9 = steps.index(A['nn'])
                    if dpos(ch[v9]) - dpos(ch[3]) < 8:
                        errs.append(f'{m} : neuvième trop près de la fondamentale (au moins une 9e au-dessus de la basse)')
                    if any(ch[w]['s'] == A['t'] and midi(ch[w]) > midi(ch[v9]) for w in range(4)):
                        errs.append(f'{m} : neuvième sous la sensible (elle se place au-dessus de la tierce)')
            elif A['etat'] == '7':
                if A['f'] not in steps and steps.count(A['r']) < 2:
                    errs.append(f'{m} : sans la quinte, il faut doubler la fondamentale')
            elif A['f'] not in steps or A['r'] not in steps:
                errs.append(f'{m} : accord de septième renversé incomplet')
            ls = famille_dominante(A, sens_pc)
            if ls is not None and ls != sens_pc and sum(1 for n in ch if pc(n) == ls) > 1:
                errs.append(f'{m} : sensible doublée')
        else:
            errs.append(f'{m} : accord non reconnu (vérifie la fondamentale et la tierce)')
        if sum(1 for n in ch if pc(n) == sens_pc) > 1:
            errs.append(f'{m} : sensible doublée')
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        A, B = INFO[i], INFO[i + 1]
        sens_pc = SENS[i]
        m = f'accords {i + 1}-{i + 2}'
        ra, rb = racine(chords[i]), racine(chords[i + 1])
        meme = ra is not None and ra == rb
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
            if pc(a[v]) == sens_pc and pc(b[v]) != (sens_pc + 1) % 12 and pc(b[v]) != sens_pc and not meme and i not in libres:
                errs.append(f'{m} : sensible ({VOIX[v]}) non résolue sur la tonique')
        # accords de 7e : la sensible de l'accord monte, la 7e (et la 9e) descendent
        ls = famille_dominante(A, sens_pc)
        if A is not None and not meme:
            for v in range(4):
                if a[v]['s'] == A['s']:
                    d = dpos(b[v]) - dpos(a[v])
                    monte43 = A['etat'] == '43' and d == 1 and dpos(b[3]) - dpos(a[3]) == 1
                    if d != -1 and not monte43:
                        errs.append(f'{m} : septième ({VOIX[v]}) non résolue (elle descend d\'un degré)')
                if A['nn'] is not None and a[v]['s'] == A['nn'] and dpos(b[v]) - dpos(a[v]) != -1:
                    errs.append(f'{m} : neuvième ({VOIX[v]}) non résolue (elle descend d\'un degré)')
            if ls is not None and ls != sens_pc:
                for v in (0, 3):
                    if pc(a[v]) == ls and pc(b[v]) != (ls + 1) % 12:
                        errs.append(f'{m} : sensible de l\'accord ({VOIX[v]}) non résolue (elle monte d\'un demi-ton)')
        # 7e d'espèce : préparée (même note, même voix, dans l'accord précédent)
        if B is not None and famille_dominante(B, SENS[i + 1]) is None and not meme:
            for v in range(4):
                if b[v]['s'] == B['s'] and midi(a[v]) != midi(b[v]):
                    errs.append(f'{m} : septième ({VOIX[v]}) non préparée')
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


def racine(ch):
    """pc de la fondamentale (accord de 3 ou de 4 sons), ou None."""
    tr = triad(ch)
    if tr is not None:
        return next(pc(N(x)) for x in ch[:4] if N(x)['s'] == tr[0])
    A = info4(ch)
    return A['pr'] if A else None
