"""Écriture avec rythme : notes étrangères et vérification d'un choral.

voix : 4 listes d'événements (note | None, durée en temps[, options]) ; options : {'tie': True}
        lie la note à la suivante (même hauteur).
harmonies : liste de (début, durée, [noms des notes de l'accord sans octave]) ;
        chaque note est confrontée à l'harmonie qui sonne à son attaque.

classer(...) -> pour chaque voix, la liste des notes avec leur rôle :
  'R' note réelle, 'p' passage, 'b' broderie, 'r' retard, 'app' appoggiature,
  'e' échappée, 'ant' anticipation, '?' note étrangère mal traitée.
verifier_choral(...) -> fautes (notes étrangères + règles d'écriture sur les notes réelles
  + quintes et octaves consécutives entre attaques successives).
"""
from graveur import N, midi, dpos
from verif import check, VOIX, is_p5, is_p8

ROLE = {'p': 'note de passage', 'b': 'broderie', 'r': 'retard', 'app': 'appoggiature',
        'e': 'échappée', 'ant': 'anticipation'}
SEMI = [0, 2, 4, 5, 7, 9, 11]


def pcn(nom):
    n = N(nom + '4') if nom[-1] not in '0123456789' else N(nom)
    return (SEMI[n['s']] + n['a']) % 12


def notes_voix(voix):
    """[(attaque, durée, note, lié_à_la_précédente)] en fusionnant les notes liées."""
    out, t = [], 0.0
    prec_lie = False
    for ev in voix:
        n, d = ev[0], ev[1]
        op = ev[2] if len(ev) > 2 else {}
        if n is not None:
            out.append([t, d, n, prec_lie])
        prec_lie = bool(op.get('tie'))
        t += d
    return out


def harmonie_a(harm, t):
    for (a, d, ns) in harm:
        if a - 1e-9 <= t < a + d - 1e-9:
            return (a, d, ns)
    return None


def couper(nv, harm):
    """Une note tenue par-dessus un changement d'harmonie est coupée (la suite est « liée »)."""
    out = []
    bornes = sorted({a for a, d, ns in harm})
    for t, d, n, lie in nv:
        cuts = [b for b in bornes if t + 1e-9 < b < t + d - 1e-9]
        debut = t
        for b in cuts + [t + d]:
            out.append([debut, b - debut, n, lie if debut == t else True])
            debut = b
    return out


def classer(voix, harm):
    roles = []
    for vi, v in enumerate(voix):
        nv = couper(notes_voix(v), harm)
        r = []
        for k, (t, d, n, lie) in enumerate(nv):
            h = harmonie_a(harm, t)
            pc = (SEMI[N(n)['s']] + N(n)['a']) % 12
            if h is None or pc in [pcn(x) for x in h[2]]:
                r.append('R')
                continue
            prev = nv[k - 1] if k > 0 and abs(nv[k - 1][0] + nv[k - 1][1] - t) < 1e-9 else None
            nxt = nv[k + 1] if k < len(nv) - 1 and abs(t + d - nv[k + 1][0]) < 1e-9 else None
            accent = abs(t - round(t)) < 1e-9 and abs(t - h[0]) < 1e-9
            dp = dpos(N(n)) - dpos(N(prev[2])) if prev else None
            dn = dpos(N(nxt[2])) - dpos(N(n)) if nxt else None
            nxt_reel = False
            if nxt:
                hn = harmonie_a(harm, nxt[0])
                nxt_reel = hn is None or (SEMI[N(nxt[2])['s']] + N(nxt[2])['a']) % 12 in [pcn(x) for x in hn[2]]
            role = '?'
            if accent and prev and (lie or midi(N(prev[2])) == midi(N(n))) and dn is not None and abs(dn) == 1 and nxt_reel:
                role = 'r'
            elif not accent and nxt and midi(N(nxt[2])) == midi(N(n)):
                role = 'ant'
            elif dp is not None and dn is not None and abs(dp) == 1 and abs(dn) == 1 and dp == dn:
                role = 'p'
            elif dp is not None and dn is not None and abs(dp) == 1 and dn == -dp:
                role = 'b'
            elif accent and dn is not None and abs(dn) == 1 and nxt_reel:
                role = 'app'
            elif not accent and dp is not None and abs(dp) == 1 and dn is not None and abs(dn) >= 2 and (dn > 0) != (dp > 0) and nxt_reel:
                role = 'e'
            r.append(role)
        roles.append(list(zip(nv, r)))
    return roles


def squelette(voix, harm):
    """Pour chaque harmonie, la note réelle de chaque voix."""
    roles = classer(voix, harm)
    sq = []
    for (a, d, ns) in harm:
        ch = []
        for vi in range(4):
            dedans = [(nt, ro) for (nt, ro) in roles[vi] if nt[0] < a + d - 1e-9 and nt[0] + nt[1] > a + 1e-9]
            reel = [nt for nt, ro in dedans if ro == 'R']
            ch.append(reel[0][2] if reel else (dedans[0][0][2] if dedans else None))
        sq.append(tuple(ch))
    return sq, roles


def verifier_choral(voix, harm, tonic='Do', allow_third=()):
    errs = []
    sq, roles = squelette(voix, harm)
    for vi in range(4):
        for (t, d, n, lie), ro in roles[vi]:
            if ro == '?':
                errs.append(f'temps {t + 1:g} : note étrangère mal traitée ({VOIX[vi]}, {n[:-1]})')
    if all(all(c) for c in sq):
        errs += check(sq, tonic, allow_third=allow_third)
    # quintes et octaves entre attaques successives (les notes étrangères ne doivent pas en créer)
    attaques = sorted({round(nt[0], 6) for vi in range(4) for nt, ro in roles[vi]})
    def son(vi, t):
        for nt, ro in roles[vi]:
            if nt[0] - 1e-9 <= t < nt[0] + nt[1] - 1e-9:
                return nt[2]
        return None
    deja = set(errs)
    for a, b in zip(attaques, attaques[1:]):
        if abs(a - round(a)) < 1e-9 and abs(b - round(b)) < 1e-9 and harmonie_a(harm, a) != harmonie_a(harm, b):
            continue   # déjà contrôlé sur les notes réelles
        for u in range(4):
            for l in range(u + 1, 4):
                A, B = (son(u, a), son(l, a)), (son(u, b), son(l, b))
                if None in A or None in B or (A[0] == B[0] and A[1] == B[1]):
                    continue
                for test, nom in ((is_p5, '5tes'), (is_p8, '8ves')):
                    if test(N(A[1]), N(A[0])) and test(N(B[1]), N(B[0])) and \
                            (midi(N(B[0])) - midi(N(A[0]))) * (midi(N(B[1])) - midi(N(A[1]))) > 0:
                        errs.append(f'temps {a + 1:g}-{b + 1:g} : {nom} consécutives {VOIX[u]}/{VOIX[l]} (à cause d\'une note étrangère)')
    return errs, roles, sq


# ---------------------------------------------------------------- cellules (format des exercices)
def cellules_en_voix(notes, extra, durees):
    """notes[i][v] = première note du temps ; extra[i][v] = {'b': deuxième croche | None, 'lie': bool}."""
    voix = []
    for v in range(4):
        ev = []
        for i, d in enumerate(durees):
            a = notes[i][v]
            x = extra[i][v]
            if x.get('lie') and ev:
                ev[-1] = (ev[-1][0], ev[-1][1], dict(ev[-1][2], tie=True))
            if x.get('b'):
                ev += [(a, d / 2, {}), (x['b'], d / 2, {})]
            else:
                ev.append((a, d, {}))
        voix.append(ev)
    return voix


def harmonies_cellules(accords, durees):
    out, t = [], 0
    for ns, d in zip(accords, durees):
        out.append((t, d, ns))
        t += d
    return out


def entre(n1, n2, tonique, armure):
    """La note diatonique entre deux notes à distance de tierce (dans la gamme de l'exercice)."""
    from generateur import alts, mode, note_degre
    from graveur import FR
    a, b = N(n1), N(n2)
    p = (dpos(a) + dpos(b)) // 2
    s, o = p % 7, p // 7
    al = alts(armure).get(s, 0)
    if mode(tonique, armure) == 'mineur':
        sens = note_degre(tonique, armure, 6)
        if sens[:-1] == FR[s] or sens.rstrip('#b') == FR[s]:
            al = 1 if sens.endswith('#') else 0
    return FR[s] + ('#' if al == 1 else 'b' if al == -1 else '') + str(o)


def orner(notes, durees, accords, tonique, armure, voix=(1, 2, 0, 3), voulu=4, retard=True, allow=(), extra0=None):
    """Ajoute des notes de passage (et un retard à la cadence) sans créer de faute."""
    from graveur import FR
    extra = [[dict(x) for x in c] for c in extra0] if extra0 else [[{'b': None, 'lie': False} for v in range(4)] for i in durees]
    harm = harmonies_cellules(accords, durees)
    def ok():
        e, r, s = verifier_choral(cellules_en_voix(notes, extra, durees), harm, tonique, allow_third=allow)
        return not e
    assert ok(), verifier_choral(cellules_en_voix(notes, extra, durees), harm, tonique, allow_third=allow)[0]
    faits = 0
    if retard and len(notes) >= 3:      # retard 4-3 ou 9-8 sur le V de la cadence
        i = len(notes) - 2
        for v in (0, 1, 2):
            a, b = notes[i - 1][v], notes[i][v]
            if dpos(N(a)) - dpos(N(b)) == 1 and durees[i] <= 1:
                sauve = notes[i][v]
                notes[i][v] = a
                extra[i][v] = {'b': sauve, 'lie': True}
                if ok():
                    faits += 1
                    break
                notes[i][v] = sauve
                extra[i][v] = {'b': None, 'lie': False}
    for v in voix:
        for i in range(len(notes) - 1):
            if faits >= voulu:
                break
            if extra[i][v]['b'] or extra[i][v]['lie'] or extra[i + 1][v]['lie'] or durees[i] > 1:
                continue
            a, b = notes[i][v], notes[i + 1][v]
            if abs(dpos(N(a)) - dpos(N(b))) == 2:
                extra[i][v] = {'b': entre(a, b, tonique, armure), 'lie': False}
                if ok():
                    faits += 1
                else:
                    extra[i][v] = {'b': None, 'lie': False}
    return extra, faits
