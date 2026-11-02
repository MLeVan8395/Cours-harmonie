"""Données des entraînements de l'appli (accords à chiffrer, chasse aux fautes, cadences à l'oreille).

Tout est calculé ici, avec le générateur et le vérificateur du cours, puis inclus dans app/index.html.
"""
import random, re
from graveur import N, midi, dpos, FR
from verif import check, TESS, VOIX, triad, etat
from recherche import voicings
from generateur import accord, phrase, mode, note_degre, chiffre, DEG
from accords4 import phrase4, spec

DEGN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
LETTRE = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
TONS = [('Do', 0), ('Sol', 1), ('Fa', -1), ('Ré', 2), ('La', 3), ('La', 0), ('Mi', 1), ('Ré', -1)]


def joli(n):
    """'Fa#4' -> 'Fa♯' (une note seule s'écrit en solfège)."""
    m = re.match(r"([A-Za-zé]+?)([#b]?)(\d)?$", n)
    return m.group(1) + {'#': '♯', 'b': '♭', '': ''}[m.group(2)]


def nom_ton(t, a):
    return f'{t} majeur' if mode(t, a) == 'majeur' else f'{t.lower()} mineur'


def nom_accord(names, d, t, a):
    """Nom de l'accord en lettres (C, Am, B°…)."""
    r = N(names[0] + '4')
    q = {('M'): ''}
    base = LETTRE[r['s']] + ('♯' if r['a'] == 1 else '♭' if r['a'] == -1 else '')
    t3 = (midi(N(names[1] + '4')) - midi(N(names[0] + '4'))) % 12
    t5 = (midi(N(names[2] + '4')) - midi(N(names[0] + '4'))) % 12
    return base + ('m' if t3 == 3 and t5 == 7 else '°' if t3 == 3 else '+' if t5 == 8 else '')


# ------------------------------------------------------------------ 1. accords à chiffrer
def accords(rng, total=160):
    plans_maj = [(0, '5'), (0, '6'), (0, '64'), (1, '5'), (1, '6'), (2, '5'), (3, '5'), (3, '6'), (3, '64'),
                 (4, '5'), (4, '6'), (4, '64'), (5, '5'), (5, '6'), (6, '6')]
    plans_min = [(0, '5'), (0, '6'), (0, '64'), (1, '6'), (3, '5'), (3, '6'), (4, '5'), (4, '6'), (5, '5'), (6, '6')]
    out, vus = [], set()
    while len(out) < total:
        t, a = rng.choice(TONS)
        mineur = mode(t, a) == 'mineur'
        d, e = rng.choice(plans_min if mineur else plans_maj)
        names = accord(t, a, d)
        bnote = names[{'5': 0, '6': 1, '64': 2}[e]]
        basses = [b for b in (bnote + str(o) for o in (2, 3, 4)) if midi(N(TESS['basse'][0])) <= midi(N(b)) <= midi(N(TESS['basse'][1]))]
        rng.shuffle(basses)
        vs = voicings(names, bass=basses[0], tonic=t)
        vs = [v for v in vs if {N(x)['s'] for x in v} >= {N(names[0] + '4')['s'], N(names[1] + '4')['s']}
              and (e == '5' or N(names[2] + '4')['s'] in {N(x)['s'] for x in v})]
        if not vs:
            continue
        v = rng.choice(vs)
        cle = (t, a, tuple(v))
        if cle in vus:
            continue
        vus.add(cle)
        role = {'5': 'la fondamentale', '6': 'la tierce', '64': 'la quinte'}[e]
        notes = ', '.join(dict.fromkeys(joli(x) for x in (names[0], names[1], names[2])))
        expl = (f"Accord {nom_accord(names, d, t, a)} : {notes}. La fondamentale est {joli(names[0])}, "
                f"donc c'est le {DEGN[d]} de {nom_ton(t, a)}. À la basse, {joli(bnote)}, {role} : "
                + {'5': 'état fondamental, chiffré 5.', '6': '1er renversement, chiffré 6.', '64': '2e renversement, chiffré 6/4.'}[e])
        out.append({'t': t, 'a': a, 'n': [list(v)], 'd': d, 'e': e, 'x': expl})
    return out


def accords4(rng, total=140):
    """Accords de 7e à chiffrer : V7 et renversements, II7, IV7, VII7."""
    plans_maj = [('V', '7'), ('V', '65'), ('V', '43'), ('V', '2'), ('V', '7'), ('V', '65'), ('II', '7'), ('II', '65'), ('IV', '7'), ('VII', '7'), ('VI', '7')]
    plans_min = [('V', '7'), ('V', '65'), ('V', '43'), ('V', '2'), ('VII', '7'), ('II', '65'), ('IV', '7')]
    NOMQ = {'dom': '7', 'M7': 'maj7', 'm7': 'm7', 'ø': 'm7♭5', 'o7': '°7'}
    QTXT = {'dom': '7e de dominante', 'M7': '7e majeure', 'm7': '7e d\'espèce', 'ø': '7e de sensible', 'o7': '7e diminuée'}
    out, vus = [], set()
    while len(out) < total:
        t, a = rng.choice(TONS)
        mineur = mode(t, a) == 'mineur'
        d, e = rng.choice(plans_min if mineur else plans_maj)
        sp = spec(d + e if e != '7' else d + '7', t, a)
        names = sp['names']
        bnote = sp['basse']
        basses = [b for b in (bnote + str(o) for o in (2, 3, 4)) if midi(N(TESS['basse'][0])) <= midi(N(b)) <= midi(N(TESS['basse'][1]))]
        rng.shuffle(basses)
        vs = voicings(names, bass=basses[0], tonic=t)
        need = {N(x + '4')['s'] for x in (names if e != '7' else [names[0], names[1], names[3]])}
        vs = [v for v in vs if need <= {N(x)['s'] for x in v}]
        if not vs:
            continue
        v = rng.choice(vs)
        cle = (t, a, tuple(v))
        if cle in vus:
            continue
        vus.add(cle)
        r = N(names[0] + '4')
        nomac = LETTRE[r['s']] + ('♯' if r['a'] == 1 else '♭' if r['a'] == -1 else '') + NOMQ.get(sp['q'], '7')
        role = {'7': 'la fondamentale', '65': 'la tierce', '43': 'la quinte', '2': 'la septième'}[e]
        notes = ', '.join(joli(x) for x in names)
        expl = (f"Accord {nomac} ({QTXT.get(sp['q'], 'accord de 7e')}) : {notes}. La fondamentale est {joli(names[0])}, "
                f"donc c'est le {d}7 de {nom_ton(t, a)}. À la basse, {joli(bnote)}, {role} : chiffrage {sp['chiffre']}.")
        out.append({'t': t, 'a': a, 'n': [list(v)], 'd': DEGN.index(d), 'e': e, 'x': expl, 'c': sp['chiffre']})
    return out


# ------------------------------------------------------------------ 2. chasse aux fautes
CATS = [
    ('par', 'Quintes ou octaves consécutives'),
    ('contr', 'Quintes ou octaves par mouvement contraire'),
    ('dir', 'Quinte ou octave directe'),
    ('crois', 'Croisement ou chevauchement'),
    ('ecart', 'Écart trop grand entre deux voix'),
    ('doubl', 'Mauvaise doublure ou accord incomplet'),
    ('sens', 'Sensible non résolue'),
    ('melo', 'Mouvement mélodique interdit'),
    ('tess', 'Note hors tessiture'),
    ('sept', 'Septième mal traitée (non préparée, non résolue ou doublée)'),
]


def categorie(msg):
    if 'inusité' in msg: return None
    if 'renversé incomplet' in msg or 'sans la quinte' in msg: return 'doubl'
    if 'saut de septième' in msg: return 'melo'
    if 'septième' in msg or 'neuvième' in msg: return 'sept'
    if 'par mouvement contraire' in msg: return 'contr'
    if 'consécutives' in msg: return 'par'
    if 'directe' in msg: return 'dir'
    if 'croisement' in msg or 'chevauchement' in msg: return 'crois'
    if 'écart' in msg: return 'ecart'
    if 'non résolue' in msg: return 'sens'
    if 'hors tessiture' in msg: return 'tess'
    if any(k in msg for k in ('augmentée (', 'septième', 'saut')): return 'melo'
    if any(k in msg for k in ('doublé', 'doublée', 'incomplet', 'absente', 'quadruplée')): return 'doubl'
    return None


def message(msg):
    msg = msg.replace('septième', '7e').replace('neuvième', '9e')
    msg = msg.replace('5tes', 'quintes').replace('8ves', 'octaves').replace('5te', 'quinte').replace('8ve', 'octave')
    return re.sub(r'^(accords? [\d-]+) : ', lambda m: m.group(1)[0].upper() + m.group(1)[1:] + ' : ', msg)


PAIRES4 = ['V7 I', 'II7 V', 'II65 V7', 'V65 I', 'V43 I', 'V2 I6', 'IV V7', 'I II65', 'V7 VI', 'VI II7', 'IV7 V7', 'I V7']
PAIRES = ['I IV', 'I V', 'IV V', 'V I', 'II V', 'VI II', 'I VI', 'IV I', 'V VI', 'I II', 'II6 V', 'IV6 V', 'V6 I', 'I6 IV',
          'III VI', 'VI IV', 'I64 V', 'VI V', 'IV II']


_CACHE = {}


def phrase_c(plan, t, a):
    k = (plan, t, a)
    if k not in _CACHE:
        try:
            _CACHE[k] = phrase4(plan, t, a, soprano_fin=False, n=6)
        except (ValueError, AssertionError):
            _CACHE[k] = None
    return _CACHE[k]


def fautes(rng, total=180):
    out, vus = [], set()
    compte = {c: 0 for c, _ in CATS}
    compte[None] = 0
    essais = 0
    while len(out) < total and essais < 60000:
        essais += 1
        t, a = rng.choice(TONS)
        cible_sens = compte['sens'] < 12 and rng.random() < 0.35
        plan = rng.choice(['V I', 'V6 I', 'V VI', 'V I6']) if cible_sens else rng.choice(PAIRES4 if rng.random() < 0.35 else PAIRES)
        if mode(t, a) == 'mineur' and ('II ' in plan + ' ' and 'II6' not in plan or 'III' in plan):
            continue
        r = phrase_c(plan, t, a)
        if not r:
            continue
        res, allow, seq = r
        p = [list(c) for c in rng.choice(res)]
        sens = note_degre(t, a, 6)
        sans = rng.random() < 0.1
        if sans:
            cat, msgs = None, []
        else:
            i, v = rng.randrange(2), rng.randrange(4)
            if cible_sens:
                vv = [w for w in (0, 3) if p[0][w][:-1] == sens]
                if not vv:
                    continue
                i, v = 1, rng.choice(vv)
            names = seq[i]['names']
            cand = [n + str(o) for n in names for o in range(2, 6)]
            cand = [c for c in cand if c != p[i][v] and abs(midi(N(c)) - midi(N(p[i][v]))) <= 12]
            if v == 3:   # la basse garde son état
                cand = [c for c in cand if c[:-1] == p[i][3][:-1]]
            if not cand:
                continue
            p[i][v] = rng.choice(cand)
            errs = check([tuple(c) for c in p], t, allow_third=allow)
            if any('accord non reconnu' in m or 'inusité' in m for m in errs):
                continue
            if not errs:
                continue
            cats = {categorie(m) for m in errs}
            if len(cats) != 1 or None in cats:
                continue
            cat = cats.pop()
            msgs = [message(m) for m in errs]
        if compte[cat] >= total // 9 + 4:
            continue
        cle = tuple(map(tuple, p))
        if cle in vus:
            continue
        vus.add(cle)
        compte[cat] += 1
        mauvais = sorted({int(x) - 1 for m in msgs for x in re.findall(r'\d', m.split(':')[0])})
        out.append({'t': t, 'a': a, 'n': p, 'c': cat, 'm': msgs, 'k': mauvais, 'deg': [s['label'] for s in seq],
                    'ch': [s['chiffre'] for s in seq]})
    rng.shuffle(out)
    return out


# ------------------------------------------------------------------ 3. cadences à l'oreille
CADENCES = {
    'parfaite': ['I IV V I', 'I II6 V I', 'I IV I64 V I', 'I VI II6 V I', 'I VI IV V I', 'I IV6 V I', 'I II65 V7 I', 'I IV V7 I'],
    'imparfaite': ['I IV V6 I', 'I II V6 I', 'I VI IV V6 I', 'I IV I6 V6 I', 'I IV V65 I'],
    'demi': ['I IV I V', 'I VI IV V', 'I VI II6 V', 'I IV6 I64 V', 'I V6 I V'],
    'plagale': ['I V I IV I', 'I VI IV I', 'I V6 I IV I', 'I II6 V I IV I', 'I V7 I IV I'],
    'rompue': ['I IV V VI', 'I II6 V VI', 'I IV I64 V VI', 'I VI II6 V VI', 'I IV V7 VI'],
}


def cadences(rng, par_plan=2):
    out = []
    for cad, plans in CADENCES.items():
        for plan in plans:
            for t, a in rng.sample(TONS, 4):
                if len([o for o in out if o['p'] == plan]) >= par_plan:
                    break
                mineur = mode(t, a) == 'mineur'
                if mineur and (' II ' in f' {plan} ' or 'III' in plan):
                    continue
                try:
                    res, allow, seq = phrase4(plan, t, a, soprano_fin=cad in ('parfaite', 'plagale'), n=2)
                except (ValueError, AssertionError):
                    continue
                p = res[0]
                out.append({'t': t, 'a': a, 'n': [list(c) for c in p], 'c': cad, 'p': plan,
                            'deg': [s['label'] for s in seq], 'ch': [s['chiffre'] for s in seq]})
    rng.shuffle(out)
    return out


def tout(graine=7):
    rng = random.Random(graine)
    return {'accords': accords(rng), 'accords4': accords4(rng), 'fautes': fautes(rng), 'cadences': cadences(rng), 'cats': CATS}


if __name__ == '__main__':
    import json, collections
    d = tout()
    print(len(d['accords']), len(d['accords4']), len(d['fautes']), len(d['cadences']))
    print(d['accords4'][0]['x'])
    print(collections.Counter(f['c'] for f in d['fautes']))
    print(collections.Counter(c['c'] for c in d['cadences']))
    print(d['accords'][0]['x'])
    for f in d['fautes'][:6]:
        print(f['c'], f['m'], f['n'])
