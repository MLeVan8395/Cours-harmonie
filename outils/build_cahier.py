"""Usage : python3 outils/build_cahier.py

Construit le cahier d'exercices : pour chaque exercice, une réalisation sans faute est
calculée (générateur + vérificateur), puis on écrit l'énoncé gravé, le corrigé gravé,
les données de l'exercice interactif (cahier/exercices.json), la musique des corrigés
et les fichiers Markdown, chapitre par chapitre.
"""
import itertools, json, os, random
from graveur import Figure, satb, SONS, BLUE, MUTED, ORANGE, RED, N, midi
from verif import check, etat
from generateur import phrase, accord, chiffre, mode, DEG, parse
from recherche import voicings, harmonise, penal, notes_in_range, chord_notes
from verif import TESS, VOIX

ICI = os.path.dirname(os.path.abspath(__file__))
RAC = os.path.join(ICI, '..', 'cahier')
IMG = os.path.join(RAC, 'images')
os.makedirs(IMG, exist_ok=True)
os.makedirs(os.path.join(RAC, 'audio'), exist_ok=True)
DEGN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
TON = {('Do', 0): 'Do majeur', ('Sol', 1): 'Sol majeur', ('Fa', -1): 'Fa majeur', ('Ré', 2): 'Ré majeur',
       ('La', 0): 'la mineur', ('Mi', 1): 'mi mineur', ('Ré', -1): 'ré mineur', ('Sol', -2): 'sol mineur'}

GUIDES = {
    'bc': [
        {'type': 'degres', 'titre': 'Trouve les accords',
         'consigne': "Sous chaque note de la basse, choisis le degré. Avec 5 (ou ♯), la fondamentale est la basse ; avec 6, elle est une 3ce sous la basse ; avec 6/4, une 4te au-dessus."},
        {'type': 'voix', 'voix': [0], 'titre': 'Écris le soprano',
         'consigne': "Une ligne simple, surtout par degrés conjoints, qui finit sur la tonique. Chaque note doit appartenir à l'accord. Surveille les 5tes et les 8ves avec la basse."},
        {'type': 'voix', 'voix': [1, 2], 'titre': "Complète l'alto et le ténor",
         'consigne': "Garde les notes communes, va au plus près, et double la bonne note."}],
    'bd': [
        {'type': 'voix', 'voix': [0], 'titre': 'Écris le soprano',
         'consigne': "Une ligne simple, surtout par degrés conjoints, qui finit sur la tonique. Chaque note doit appartenir à l'accord. Surveille les 5tes et les 8ves avec la basse."},
        {'type': 'voix', 'voix': [1, 2], 'titre': "Complète l'alto et le ténor",
         'consigne': "Garde les notes communes, va au plus près, et double la fondamentale."}],
    'cd': [
        {'type': 'degres', 'titre': 'Choisis les accords',
         'consigne': "Pour chaque note du soprano, choisis un accord qui la contient. Commence sur I et finis par V-I. Préfère les enchaînements forts : IV ou II vers V, V vers I, VI vers II, IV ou V."},
        {'type': 'voix', 'voix': [3], 'titre': 'Écris la basse',
         'consigne': "Mets la fondamentale ou la tierce de chaque accord (le chiffrage s'affiche tout seul). Cherche le mouvement contraire avec le soprano. À la cadence, la fondamentale à la basse."},
        {'type': 'voix', 'voix': [1, 2], 'titre': "Complète l'alto et le ténor",
         'consigne': "Garde les notes communes, va au plus près, et vérifie les doublures."}],
}
CONSIGNE = {
    'iso_at': "Accords séparés (pas d'enchaînement) : le soprano et la basse sont donnés, écris l'alto et le ténor de chaque accord.",
    'iso_sat': "Accords séparés (pas d'enchaînement) : sur chaque basse, écris l'accord demandé (soprano, alto, ténor), en doublant la fondamentale.",
    'sb': "Le soprano et la basse sont donnés. Écris l'alto et le ténor : garde les notes communes, va au plus près.",
    'bd': "Basse donnée avec ses degrés : écris le soprano, puis l'alto et le ténor.",
    'bc': "Basse chiffrée : trouve les degrés, écris le soprano, puis l'alto et le ténor.",
    'cd': "Chant donné : choisis les accords, écris la basse, puis l'alto et le ténor.",
    'corriger': "Cet enchaînement contient **trois fautes**. Trouve-les et corrige-les en changeant le moins de notes possible (la basse ne bouge pas).",
}


def degres_dict(tonique, armure):
    d = {}
    for k in range(6):
        if k == 2:          # III : pas encore étudié
            continue
        d[DEGN[k]] = accord(tonique, armure, k)
    return d


def chiffres_de(sol, tonique, armure):
    out = []
    for c in sol:
        e = etat(c)
        tr = [n for n in accord(tonique, armure, 0)]
        # degré de l'accord : fondamentale par rapport à la tonique
        from verif import triad
        r = triad(c)[0]
        d = (r - ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si'].index(tonique)) % 7
        out.append(chiffre(tonique, armure, d, e))
    return out


def degres_de(sol, tonique):
    from verif import triad
    return [DEGN[(triad(c)[0] - ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si'].index(tonique)) % 7] for c in sol]


def chasse(sol, tonique, graine):
    """Trois fautes de trois sortes, chacune en changeant une note (la basse reste)."""
    rnd = random.Random(graine)
    muts = []
    for i, ch in enumerate(sol):
        from verif import triad
        names = [n[:-1] for n in ch]
        for v in range(3):
            for n in notes_in_range(chord_notes(list(set(names))), *TESS[VOIX[v]]):
                if n != ch[v] and abs(midi(N(n)) - midi(N(ch[v]))) <= 7:
                    muts.append((i, v, n))
    rnd.shuffle(muts)
    for ms in itertools.combinations(muts, 3):
        if len({m[0] for m in ms}) < 3:
            continue
        seq = [list(c) for c in sol]
        for i, v, n in ms:
            seq[i][v] = n
        e = check([tuple(c) for c in seq], tonique)
        if len(e) == 3:
            sortes = {x.split(' : ')[1].split(' (')[0].split(' ')[0] for x in e}
            if len(sortes) == 3 and not any('hors tessiture' in x for x in e):
                return [tuple(c) for c in seq], e
    raise ValueError('pas de chasse aux fautes')


EXOS, PAGES = {}, []


def ajouter(chap, num, typ, tonique, armure, plan=None, basse=None, sop=None, durees=None, titre=None, graine=0):
    nom = f'c{chap:02d}-{num:02d}'
    ton = TON[(tonique, armure)]
    isoles = typ.startswith('iso')
    tierce = set()
    if typ == 'cd':
        ps, tierce, seq = phrase(plan, tonique, armure, sop=sop)
        sol = ps[0]
    elif isoles:
        sol = []
        for k, (d, e) in enumerate(parse(plan)):
            names = accord(tonique, armure, d)
            vs = voicings(names, bass=basse[k], sop=sop[k] if sop else None, tonic=tonique)
            vs = [v for v in vs if midi(N(v[0])) >= midi(N('La4')) and midi(N(v[0])) <= midi(N('Mi5'))] or vs
            sol.append(min(vs, key=penal))
    else:
        ps, tierce, seq = phrase(plan, tonique, armure, basse=basse)
        sol = ps[0]
    sol = [tuple(c) for c in sol]
    if isoles:
        for c in sol:
            assert not check([c], tonique), (nom, c, check([c], tonique))
    else:
        assert not check(sol, tonique, allow_third=tierce), (nom, check(sol, tonique, allow_third=tierce))
    n = len(sol)
    durees = durees or [4] * n
    degs = degres_de(sol, tonique)
    chifs = chiffres_de(sol, tonique, armure)
    voix = {'iso_at': [1, 2], 'iso_sat': [0, 1, 2], 'sb': [1, 2], 'bd': [0, 1, 2], 'bc': [0, 1, 2], 'cd': [1, 2, 3], 'corriger': [0, 1, 2]}[typ]
    depart, fautes = None, None
    if typ == 'corriger':
        depart, fautes = chasse(sol, tonique, graine)
    donne = [list(c) for c in depart] if depart else [[None if v in voix else c[v] for v in range(4)] for c in sol]
    montrer_deg = typ in ('iso_at', 'iso_sat', 'sb', 'bd', 'corriger')
    montrer_chif = typ != 'cd'
    EXOS[nom] = {'donne': donne, 'solution': [list(c) for c in sol], 'durees': durees, 'voix': voix,
                 'tonique': tonique, 'armure': armure, 'degres': degs if montrer_deg else None,
                 'chiffres': chifs if montrer_chif else None, 'tierce': sorted(tierce), 'chant': typ == 'cd',
                 'corriger': typ == 'corriger', 'guide': GUIDES.get(typ), 'isoles': isoles}
    # énoncé et corrigé gravés
    lab = []
    t = 0
    for i, d in enumerate(durees):
        if montrer_deg:
            lab.append((t, degs[i], 0, BLUE, d >= 4))
        if montrer_chif:
            lab.append((t, chifs[i], 1, BLUE, d >= 4))
        t += d
    temps = (4, 4) if any(d < 4 for d in durees) else None
    voices = []
    for v, (st, stem) in enumerate([(0, 'up'), (0, 'down'), (1, 'up'), (1, 'down')]):
        ev = [((donne[i][v] if donne[i][v] else None), durees[i], {} if donne[i][v] else {'hide': True}) for i in range(n)]
        voices.append({'staff': st, 'stem': stem, 'events': ev})
    Figure([{'clef': 'treble'}, {'clef': 'bass'}], voices, key=armure, brace=(0, 1), gap=104, unit=22, time=temps,
           labels=lab, rows=['degrés', 'chiffrage'] if montrer_deg else (['', 'chiffrage'] if montrer_chif else None)).save(os.path.join(IMG, nom + '.png'))
    labc = []
    t = 0
    for i, d in enumerate(durees):
        labc += [(t, degs[i], 0, BLUE, d >= 4), (t, chifs[i], 1, BLUE, d >= 4)]
        t += d
    col = {(v, i): BLUE for v in voix for i in range(n)}
    satb([c + (d,) for c, d in zip(sol, durees)], key=armure, unit=22, time=temps, labels=labc, rows=['degrés', 'chiffrage'],
         colors=col).save(os.path.join(IMG, nom + '-c.png'))
    SONS.pop(nom, None)   # on n'écoute que le corrigé
    PAGES.append((chap, num, typ, ton, nom, titre, fautes))


# ======================================================================== le catalogue
# chapitres 1 et 2 : les voix, l'accord parfait (accords séparés)
ajouter(1, 1, 'iso_at', 'Do', 0, 'I IV V VI II I', basse=['Do3', 'Fa3', 'Sol2', 'La2', 'Ré3', 'Do3'], sop=['Mi5', 'La4', 'Ré5', 'Do5', 'Fa4', 'Sol4'])
ajouter(1, 2, 'iso_sat', 'Sol', 1, 'I IV V II VI I', basse=['Sol2', 'Do3', 'Ré3', 'La2', 'Mi3', 'Sol2'])
ajouter(1, 3, 'iso_sat', 'Fa', -1, 'I VI II V IV I', basse=['Fa2', 'Ré3', 'Sol2', 'Do3', 'Sib2', 'Fa3'])
ajouter(1, 4, 'iso_sat', 'Ré', 2, 'I IV V VI II I', basse=['Ré3', 'Sol2', 'La2', 'Si2', 'Mi3', 'Ré3'])
# chapitre 3 : enchaîner à l'état fondamental
ajouter(3, 1, 'sb', 'Do', 0, 'I IV V I', basse=['Do3', 'Fa2', 'Sol2', 'Do3'])
ajouter(3, 2, 'sb', 'Sol', 1, 'I IV I V I', basse=['Sol2', 'Do3', 'Sol2', 'Ré3', 'Sol2'])
ajouter(3, 3, 'sb', 'Fa', -1, 'I VI IV V I', basse=['Fa2', 'Ré3', 'Sib2', 'Do3', 'Fa2'])
ajouter(3, 4, 'sb', 'Ré', 2, 'I II V I VI IV V I', basse=['Ré3', 'Mi3', 'La2', 'Ré3', 'Si2', 'Sol2', 'La2', 'Ré3'])
ajouter(3, 5, 'bd', 'Do', 0, 'I VI II V I IV V I', basse=['Do3', 'La2', 'Ré3', 'Sol2', 'Do3', 'Fa2', 'Sol2', 'Do3'])
ajouter(3, 6, 'bd', 'Sol', 1, 'I IV II V VI IV V I', basse=['Sol2', 'Do3', 'La2', 'Ré3', 'Mi3', 'Do3', 'Ré3', 'Sol2'])
ajouter(3, 7, 'bd', 'Fa', -1, 'I IV V VI II V I', basse=['Fa2', 'Sib2', 'Do3', 'Ré3', 'Sol2', 'Do3', 'Fa2'])
ajouter(3, 8, 'bd', 'Ré', 2, 'I IV I V VI II V I', basse=['Ré3', 'Sol2', 'Ré3', 'La2', 'Si2', 'Mi3', 'La2', 'Ré3'])
ajouter(3, 9, 'corriger', 'Do', 0, 'I IV II V I VI IV V I', basse=['Do3', 'Fa2', 'Ré3', 'Sol2', 'Do3', 'La2', 'Fa2', 'Sol2', 'Do3'], graine=3)
ajouter(3, 10, 'cd', 'Do', 0, 'I V I IV I V I', sop=['Do5', 'Ré5', 'Mi5', 'Fa5', 'Mi5', 'Ré5', 'Do5'])
ajouter(3, 11, 'cd', 'Sol', 1, 'I IV I V I V I', sop=['Ré5', 'Do5', 'Si4', 'La4', 'Si4', 'La4', 'Sol4'])
# chapitre 6 : le premier renversement
ajouter(6, 1, 'bc', 'Do', 0, 'I V6 I II6 V I', basse=['Do3', 'Si2', 'Do3', 'Fa2', 'Sol2', 'Do3'])
ajouter(6, 2, 'bc', 'Sol', 1, 'I I6 IV V I VI II6 V I', basse=['Sol2', 'Si2', 'Do3', 'Ré3', 'Sol2', 'Mi3', 'Do3', 'Ré3', 'Sol2'])
ajouter(6, 3, 'bc', 'Fa', -1, 'I V6 I IV I6 II6 V I', basse=['Fa3', 'Mi3', 'Fa3', 'Sib2', 'La2', 'Sib2', 'Do3', 'Fa2'])
ajouter(6, 4, 'bc', 'Ré', 2, 'I II6 V I6 IV V I', basse=['Ré3', 'Sol2', 'La2', 'Fa#2', 'Sol2', 'La2', 'Ré3'])
ajouter(6, 5, 'cd', 'Do', 0, 'I V6 I IV6 II6 V I', sop=['Mi5', 'Ré5', 'Do5', 'Do5', 'La4', 'Si4', 'Do5'])
ajouter(6, 6, 'cd', 'Sol', 1, 'I IV I V6 I II6 V I', sop=['Ré5', 'Do5', 'Si4', 'La4', 'Si4', 'Do5', 'La4', 'Sol4'])
# chapitre 7 : les cadences
ajouter(7, 1, 'bc', 'Do', 0, 'I IV V I VI II6 V I', basse=['Do3', 'Fa3', 'Sol3', 'Do3', 'La2', 'Fa2', 'Sol2', 'Do3'], titre='demi-cadence, puis cadence parfaite')
ajouter(7, 2, 'bc', 'Sol', 1, 'I IV V VI II6 V I', basse=['Sol2', 'Do3', 'Ré3', 'Mi3', 'Do3', 'Ré3', 'Sol2'], titre='cadence rompue')
ajouter(7, 3, 'bc', 'Fa', -1, 'I II6 V I IV I', basse=['Fa2', 'Sib2', 'Do3', 'Fa2', 'Sib2', 'Fa2'], titre='cadence parfaite, puis plagale')
ajouter(7, 4, 'bc', 'Ré', 2, 'I VI V6 I II6 V I', basse=['Ré3', 'Si2', 'Do#3', 'Ré3', 'Sol2', 'La2', 'Ré3'], titre='cadence imparfaite, puis parfaite')
ajouter(7, 5, 'cd', 'Do', 0, 'I II V VI II6 V I', sop=['Mi5', 'Ré5', 'Si4', 'Do5', 'La4', 'Si4', 'Do5'], titre='avec une cadence rompue')
# chapitre 8 : la quarte et sixte (blanches : la 6/4 de cadence tombe sur un temps fort)
B = [2] * 6 + [4]
ajouter(8, 1, 'bc', 'Do', 0, 'I I6 IV II6 I64 V I', basse=['Do3', 'Mi3', 'Fa3', 'Fa2', 'Sol2', 'Sol2', 'Do3'], durees=B, titre='quarte et sixte de cadence')
ajouter(8, 2, 'bc', 'Sol', 1, 'I V64 I6 IV I64 V I', basse=['Sol2', 'La2', 'Si2', 'Do3', 'Ré3', 'Ré3', 'Sol2'], durees=B, titre='de passage et de cadence')
ajouter(8, 3, 'bc', 'Fa', -1, 'I IV64 I V6 I II6 I64 V I', basse=['Fa3', 'Fa3', 'Fa3', 'Mi3', 'Fa3', 'Sib2', 'Do3', 'Do3', 'Fa2'], durees=[2] * 8 + [4], titre='de broderie et de cadence')
ajouter(8, 4, 'bc', 'Ré', 2, 'I IV6 V I VI II6 I64 V I', basse=['Ré3', 'Si2', 'La2', 'Ré3', 'Si2', 'Sol2', 'La2', 'La2', 'Ré3'], durees=[2] * 8 + [4])
ajouter(8, 5, 'cd', 'Fa', -1, 'I V6 I IV I6 II6 I64 V I', sop=['Fa4', 'Sol4', 'La4', 'Sib4', 'Do5', 'Sib4', 'La4', 'Sol4', 'Fa4'], durees=[2] * 8 + [4], titre='avec une quarte et sixte de cadence')
# chapitre 9 : basse donnée et chant donné, des phrases plus longues
ajouter(9, 1, 'bc', 'Do', 0, 'I VI IV II6 I64 V I', basse=['Do3', 'La2', 'Fa3', 'Fa2', 'Sol2', 'Sol2', 'Do3'], durees=B)
ajouter(9, 2, 'cd', 'Do', 0, 'I VI V I V6 I V I', sop=['Sol4', 'Do5', 'Si4', 'Do5', 'Ré5', 'Mi5', 'Ré5', 'Do5'])
ajouter(9, 3, 'bc', 'Sol', 1, 'I V6 I IV6 I6 II6 I64 V I', basse=['Sol2', 'Fa#2', 'Sol2', 'Mi3', 'Si2', 'Do3', 'Ré3', 'Ré3', 'Sol2'], durees=[2] * 8 + [4])
ajouter(9, 4, 'bc', 'Fa', -1, 'I I6 IV V I VI IV II6 V I', basse=['Fa2', 'La2', 'Sib2', 'Do3', 'Fa2', 'Ré3', 'Sib2', 'Sib2', 'Do3', 'Fa2'])
ajouter(9, 5, 'cd', 'Sol', 1, 'I IV I6 VI V6 I II6 I64 V I', sop=['Si4', 'Do5', 'Ré5', 'Si4', 'La4', 'Sol4', 'La4', 'Si4', 'La4', 'Sol4'])
ajouter(9, 6, 'cd', 'Fa', -1, 'I IV I V6 I II6 V I', sop=['Do5', 'Sib4', 'La4', 'Sol4', 'La4', 'Sib4', 'Sol4', 'Fa4'])
ajouter(9, 7, 'cd', 'Ré', 2, 'I IV I6 IV V I II6 V I', sop=['Fa#4', 'Sol4', 'La4', 'Si4', 'La4', 'Fa#4', 'Sol4', 'Mi4', 'Ré4'])
# chapitre 10 : le mode mineur
ajouter(10, 1, 'bc', 'La', 0, 'I V6 I IV VI II6 V I', basse=['La2', 'Sol#2', 'La2', 'Ré3', 'Fa3', 'Ré3', 'Mi3', 'La2'])
ajouter(10, 2, 'bc', 'Mi', 1, 'I IV6 V I VI II6 I64 V I', basse=['Mi3', 'Do3', 'Si2', 'Mi3', 'Do3', 'La2', 'Si2', 'Si2', 'Mi3'], durees=[2] * 8 + [4])
ajouter(10, 3, 'bc', 'Ré', -1, 'I VI IV V I II6 V I', basse=['Ré3', 'Sib2', 'Sol2', 'La2', 'Ré3', 'Sol2', 'La2', 'Ré3'])
ajouter(10, 4, 'cd', 'La', 0, 'I V6 I IV6 I6 V I', sop=['Do5', 'Si4', 'La4', 'Ré5', 'Do5', 'Si4', 'La4'])
ajouter(10, 5, 'cd', 'Sol', -2, 'I IV I6 II6 I64 V I', sop=['Ré5', 'Mib5', 'Ré5', 'Do5', 'Sib4', 'La4', 'Sol4'])
ajouter(10, 6, 'cd', 'Mi', 1, 'I IV I6 II6 I64 V I', sop=['Si4', 'Do5', 'Si4', 'La4', 'Sol4', 'Fa#4', 'Mi4'])

# ======================================================================== fichiers
json.dump(EXOS, open(os.path.join(RAC, 'exercices-cahier.json'), 'w'), ensure_ascii=False)
json.dump({k: v for k, v in SONS.items()}, open(os.path.join(RAC, 'audio', 'sons-cahier.json'), 'w'), indent=0)
print(len(EXOS), 'exercices, tous vérifiés')
json.dump(PAGES, open('/tmp/pages.json', 'w'), ensure_ascii=False)

# ======================================================================== pages Markdown
CHAP = {
    1: ('01-les-voix-et-l-accord-parfait', 'Les quatre voix et l\'accord parfait', ['01-les-quatre-voix', '02-l-accord-parfait-a-quatre-voix'], 'chapitres 1 et 2'),
    3: ('03-enchainer-deux-accords', 'Enchaîner les accords', ['03-enchainer-deux-accords'], 'chapitre 3'),
    6: ('06-le-premier-renversement', 'Le premier renversement', ['06-le-premier-renversement'], 'chapitre 6'),
    7: ('07-les-cadences', 'Les cadences', ['07-les-cadences'], 'chapitre 7'),
    8: ('08-la-quarte-et-sixte', 'La quarte et sixte', ['08-l-accord-de-quarte-et-sixte'], 'chapitre 8'),
    9: ('09-basses-donnees-et-chants-donnes', 'Basses données et chants donnés', ['09-basse-donnee-et-chant-donne'], 'chapitre 9'),
    10: ('10-le-mode-mineur', 'Le mode mineur', ['10-le-mode-mineur'], 'chapitre 10'),
    13: ('13-le-choral', 'Le choral : notes étrangères et harmonisation', ['13-les-notes-etrangeres', '14-analyse-un-choral-de-bach', '15-harmoniser-une-melodie-de-choral'], 'chapitres 13 à 15'),
}
NOMTYPE = {'iso_at': 'Accords séparés', 'iso_sat': 'Accords séparés sur une basse', 'sb': 'Compléter l\'alto et le ténor',
           'bd': 'Basse donnée', 'bc': 'Basse chiffrée', 'cd': 'Chant donné', 'corriger': 'Chasse aux fautes'}
ordre = list(CHAP)
for k, ch in enumerate(ordre):
    fichier, titre, refs, quoi = CHAP[ch]
    ex = [p for p in PAGES if p[0] == ch]
    if not ex:          # page écrite par build_partie3.py
        continue
    prev = CHAP[ordre[k - 1]] if k else None
    nxt = CHAP[ordre[k + 1]] if k < len(ordre) - 1 else None
    nav = ' · '.join(x for x in [
        f'[← {prev[1]}]({prev[0]}.md)' if prev else '',
        '[Sommaire du cahier](README.md)',
        f'[{nxt[1]} →]({nxt[0]}.md)' if nxt else ''] if x)
    L = [nav, '', f'## {titre}', '',
         'Ces exercices accompagnent ' + (' et '.join(f'le [chapitre {int(r[:2])}](../cours/{r}.md)' for r in refs)) + ' du cours.', '',
         "Dans la version web (`cahier.html`), chaque exercice se fait **directement sur la portée**, avec les corrections au fur et à mesure. "
         "Sur papier, recopie l'énoncé et réalise-le au crayon.", '']
    for (c, n, typ, ton, nom, tit, fautes) in ex:
        L += [f'### Exercice {c}.{n} · {NOMTYPE[typ]} en {ton}' + (f' ({tit})' if tit else ''), '',
              CONSIGNE[typ], '', f'![Exercice {c}.{n}](images/{nom}.png)', '']
    L += ['### Corrigés', '']
    for (c, n, typ, ton, nom, tit, fautes) in ex:
        L += [f'**Exercice {c}.{n}**' + (' : ' + ' ; '.join(f.split(' : ', 1)[0].capitalize() + ' · ' + f.split(' : ', 1)[1] for f in fautes) + '.' if fautes else
              (' : une solution parmi d\'autres.' if typ in ('bd', 'bc', 'cd', 'iso_sat') else '')), '',
              f'![Corrigé {c}.{n}](images/{nom}-c.png)', '',
              f'🔊 [Écouter](audio/{nom}-c.mp3) · [MIDI](audio/{nom}-c.mid)', '']
    L += ['---', '', nav, '']
    open(os.path.join(RAC, fichier + '.md'), 'w').write('\n'.join(L))

som = ["# Cahier d'exercices d'harmonie", '',
       "Ce cahier accompagne le [Cours d'écriture et d'harmonie](../README.md) : il suit le cours chapitre par chapitre, "
       "avec beaucoup de **basses données** et de **chants donnés**. Chaque exercice a son corrigé (une solution parmi d'autres), "
       "gravé et à écouter.", '',
       "Dans la version web (`cahier.html`), on fait les exercices **directement sur la portée** : on choisit une voix, on clique "
       "pour poser les notes, et les corrections s'affichent au fur et à mesure. Basses données et chants donnés se font par étapes "
       "(trouver les accords, écrire le soprano ou la basse, compléter l'alto et le ténor).", '', '## Sommaire', '']
for ch in ordre:
    fichier, titre, refs, quoi = CHAP[ch]
    ex = [p for p in PAGES if p[0] == ch]
    sortes = {}
    for p in ex:
        sortes[NOMTYPE[p[2]]] = sortes.get(NOMTYPE[p[2]], 0) + 1
    if not ex and ch == 13:
        try:
            n3 = json.load(open(os.path.join(RAC, 'exercices-cahier3.json')))
            o3 = sum(1 for e in n3.values() if not e['chant'])
            sortes = {'Orner une phrase (notes étrangères)': o3, 'Harmoniser une mélodie de choral': len(n3) - o3}
        except FileNotFoundError:
            continue
    som.append(f'- [{titre}]({fichier}.md) ({quoi} du cours) : ' + ', '.join(f'{v} × {k.lower()}' for k, v in sortes.items()))
try:
    n3 = len(json.load(open(os.path.join(RAC, 'exercices-cahier3.json'))))
except FileNotFoundError:
    n3 = 0
som += ['', f'**{len(PAGES) + n3} exercices** en tout, dont {sum(1 for p in PAGES if p[2] in ("bd", "bc"))} basses données, '
        f'{sum(1 for p in PAGES if p[2] == "cd")} chants donnés et {n3} exercices sur le choral. Tous les corrigés sont contrôlés par le vérificateur du cours.', '']
open(os.path.join(RAC, 'README.md'), 'w').write('\n'.join(som))
print('pages écrites')
