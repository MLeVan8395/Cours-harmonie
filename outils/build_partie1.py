"""Usage : python3 outils/build_partie1.py [dossier_images]

Construit les figures de la partie 1 et vérifie chaque exemple avec verif.check."""
import os, sys
from graveur import Figure, satb, RED, GREEN, BLUE, ORANGE, MUTED, N, dpos
from verif import check
from recherche import chord_notes

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cours', 'images')
os.makedirs(OUT, exist_ok=True)
DEG = ['degrés', 'chiffrage']


def save(fig, name):
    fig.save(os.path.join(OUT, name + '.png'))


def expect(chords, n_err=0, contains=(), tonic='Do'):
    e = check(chords, tonic)
    assert len(e) == n_err, (chords, e)
    for c in contains:
        assert any(c in x for x in e), (c, e)
    return e


def deg_labels(degs, step=4, chif='5'):
    lab = []
    for i, d in enumerate(degs):
        if d is None:
            continue
        lab.append((i * step, d, 0, BLUE))
        if chif:
            lab.append((i * step, chif, 1, BLUE))
    return lab


def disposition(ch, names):
    """serrée si aucune note de l'accord ne tient entre S-A et A-T."""
    steps = [s for s, a in chord_notes(names)]
    S, A, T = (N(x) for x in ch[:3])
    def room(hi, lo):
        return any(dpos(lo) < p < dpos(hi) and p % 7 in steps for p in range(dpos(lo) + 1, dpos(hi)))
    return 'large' if room(S, A) or room(A, T) else 'serrée'


# ---------------------------------------------------------------- chapitre 1
# 1. tessitures
# figure construite à la main : un seul flux d'événements par portée
top = {'staff': 0, 'events': [('Do4', 4, {'color': RED}), ('Sol5', 4, {'color': RED}),
                              ('Sol3', 4, {'color': ORANGE}), ('Ré5', 4, {'color': ORANGE})]}
bot = {'staff': 1, 'events': [('Do3', 4, {'color': GREEN}), ('Sol4', 4, {'color': GREEN}),
                              ('Fa2', 4, {'color': BLUE}), ('Do4', 4, {'color': BLUE})]}
fig = Figure([{'clef': 'treble'}, {'clef': 'bass'}],
             [{'staff': 0, 'events': top['events'][:4] + [(None, 16, {'hide': True})]},
              {'staff': 1, 'events': [(None, 16, {'hide': True})] + bot['events']}],
             brace=(0, 1), gap=84, unit=15,
             labels=[(2, 'Soprano', 1, RED), (10, 'Alto', 1, ORANGE), (18, 'Ténor', 1, GREEN), (26, 'Basse', 1, BLUE)])
save(fig, 'h01-tessitures')

# 2. un enchaînement en blanches : I IV V I avec les hampes
cad = [('Do5', 'Mi4', 'Sol3', 'Do3'), ('Do5', 'Fa4', 'La3', 'Fa2'), ('Si4', 'Ré4', 'Sol3', 'Sol2'), ('Do5', 'Mi4', 'Sol3', 'Do3')]
expect(cad)
save(satb([c + (2,) for c in cad], time=(4, 4), labels=[(i * 2, d, 0, BLUE, False) for i, d in enumerate(['I', 'IV', 'V', 'I'])] +
          [(i * 2, '5', 1, BLUE, False) for i in range(4)], rows=DEG, unit=22), 'h01-hampes')

# 3. écarts et croisements
ec = [('Do5', 'Sol4', 'Mi4', 'Do3'), ('Sol5', 'Mi4', 'Do4', 'Do3'), ('Mi5', 'Do5', 'Sol3', 'Do3'),
      ('Sol4', 'Do5', 'Mi4', 'Do3'), ('Mi5', 'Do5', 'Sol4', 'Do3')]
assert check([ec[0]]) == [] and check([ec[4]]) == []
assert len(check([ec[1]])) == 1 and 'soprano-alto' in check([ec[1]])[0]
assert len(check([ec[2]])) == 1 and 'alto-ténor' in check([ec[2]])[0]
assert len(check([ec[3]])) == 1 and 'croisement' in check([ec[3]])[0]
col = {(0, 1): RED, (1, 1): RED, (1, 2): RED, (2, 2): RED, (0, 3): RED, (1, 3): RED, (2, 4): GREEN, (3, 4): GREEN}
save(satb([c + (2,) for c in ec], colors=col, unit=34, beats_per_bar=2,
          top_texts=[(0, 'a) ✔', GREEN), (2, 'b) ✘', RED), (4, 'c) ✘', RED), (6, 'd) ✘', RED), (8, 'e) ✔', GREEN)]), 'h01-ecarts')

# 4. le quatuor à cordes
qv = []
for v in range(4):
    qv.append({'staff': v, 'events': [(c[v], 2) for c in cad]})
save(Figure([{'clef': 'treble', 'label': 'Violon 1'}, {'clef': 'treble', 'label': 'Violon 2'},
             {'clef': 'alto', 'label': 'Alto'}, {'clef': 'bass', 'label': 'Violoncelle'}], qv, gap=78, unit=22,
            time=(4, 4), labels=[(i * 2, d, 0, BLUE, False) for i, d in enumerate(['I', 'IV', 'V', 'I'])]),
     'h01-quatuor')

# ---------------------------------------------------------------- chapitre 2
# accords sur chaque degré
names = ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si']
tri = []
for i in range(7):
    o = 4
    r = names[i] + '4'
    t = names[(i + 2) % 7] + ('5' if i + 2 >= 7 else '4')
    f = names[(i + 4) % 7] + ('5' if i + 4 >= 7 else '4')
    tri.append((f, t, r))
vv = [{'staff': 0, 'stem': None, 'events': [(c[k], 4) for c in tri]} for k in range(3)]
degs = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
lets = ['C', 'Dm', 'Em', 'F', 'G', 'Am', 'B°']
save(Figure([{'clef': 'treble'}], vv, unit=18,
            labels=[(i * 4, d, 0, BLUE) for i, d in enumerate(degs)] + [(i * 4, l, 1, MUTED) for i, l in enumerate(lets)],
            rows=['degrés', 'accord']), 'h02-degres')

# doublures
db = [('Do5', 'Sol4', 'Mi4', 'Do3'), ('Mi5', 'Do5', 'Do4', 'Do3'), ('Mi5', 'Sol4', 'Mi4', 'Do3'), ('Do5', 'Sol4', 'Do4', 'Do3')]
assert check([db[0]]) == [] and check([db[1]]) == []
assert 'accord 1 : tierce doublée' in check([db[2]]), check([db[2]])
assert 'accord 1 : tierce absente' in check([db[3]]), check([db[3]])
col = {(0, 0): GREEN, (3, 0): GREEN, (1, 1): GREEN, (2, 1): GREEN, (3, 1): GREEN,
       (0, 2): RED, (2, 2): RED, (0, 3): RED, (2, 3): RED, (3, 3): RED}
save(satb(db, colors=col, unit=22, top_texts=[(0, 'a) ✔', GREEN), (4, 'b) ✔', GREEN), (8, 'c) ✘', RED), (12, 'd) ✘', RED)],
          labels=[(0, 'Do ×2', 0, GREEN), (4, 'Do ×3', 0, GREEN), (8, 'Mi ×2', 0, RED), (12, 'pas de Mi', 0, RED)]),
     'h02-doublures')

# dispositions
dp = [('Do5', 'Sol4', 'Mi4', 'Do3'), ('Mi5', 'Do5', 'Sol4', 'Do3'), ('Sol4', 'Mi4', 'Do4', 'Do3'),
      ('Mi5', 'Sol4', 'Do4', 'Do3'), ('Do5', 'Mi4', 'Sol3', 'Do3')]
for c in dp:
    assert check([c]) == [], (c, check([c]))
dis = [disposition(c, ['Do', 'Mi', 'Sol']) for c in dp]
assert dis == ['serrée', 'serrée', 'serrée', 'large', 'large'], dis
save(satb(dp, unit=22, labels=[(i * 4, d, 0, BLUE if d == 'serrée' else ORANGE) for i, d in enumerate(dis)] +
          [(i * 4, p, 1, MUTED) for i, p in enumerate(['S : Do', 'S : Mi', 'S : Sol', 'S : Mi', 'S : Do'])],
          rows=['', '']), 'h02-dispositions')

# ---------------------------------------------------------------- chapitre 3
# quintes et octaves consécutives : IV-V
bad = [('Do5', 'La4', 'Fa4', 'Fa3'), ('Ré5', 'Si4', 'Sol4', 'Sol3')]
good = [('Do5', 'La4', 'Fa4', 'Fa3'), ('Si4', 'Sol4', 'Ré4', 'Sol3')]
expect(bad, 3, ['5tes consécutives soprano/ténor', '5tes consécutives soprano/basse', '8ves consécutives ténor/basse'])
expect(good)
save(satb(bad + good, unit=20, boxes=[(0, 8, RED, 'faux'), (8, 16, GREEN, 'juste')],
          lines=[((0, 0), (0, 1), RED), ((3, 0), (3, 1), RED), ((2, 0), (2, 1), ORANGE)],
          labels=[(0, 'IV', 0, BLUE), (4, 'V', 0, BLUE), (8, 'IV', 0, BLUE), (12, 'V', 0, BLUE)]), 'h03-paralleles')

# octaves par mouvement contraire
oc = [('Do5', 'Mi4', 'Do4', 'Do3'), ('La4', 'Mi4', 'Do4', 'La3')]
expect(oc, 1, ['8ves par mouvement contraire soprano/basse'])
oc_ok = [('Do5', 'Mi4', 'Do4', 'Do3'), ('Do5', 'La4', 'Mi4', 'La2')]
expect(oc_ok)
save(satb(oc + oc_ok, unit=20, boxes=[(0, 8, RED, 'faux'), (8, 16, GREEN, 'juste')],
          lines=[((0, 0), (0, 1), RED), ((3, 0), (3, 1), RED)], colors={(0, 0): RED, (3, 0): RED, (0, 1): RED, (3, 1): RED},
          labels=[(0, 'I', 0, BLUE), (4, 'VI', 0, BLUE), (8, 'I', 0, BLUE), (12, 'VI', 0, BLUE)]), 'h03-contraire')

# octave directe
di_bad = [('La4', 'Fa4', 'Do4', 'Fa2'), ('Do5', 'Mi4', 'Do4', 'Do3')]
di_ok = [('La4', 'Fa4', 'Do4', 'Fa3'), ('Sol4', 'Mi4', 'Do4', 'Do3')]
expect(di_bad, 1, ['8ve directe soprano/basse'])
expect(di_ok)
save(satb(di_bad + di_ok, unit=20, boxes=[(0, 8, RED, 'faux'), (8, 16, GREEN, 'toléré')],
          colors={(0, 0): RED, (0, 1): RED, (3, 0): RED, (3, 1): RED, (0, 2): GREEN, (0, 3): GREEN, (3, 2): GREEN, (3, 3): GREEN},
          labels=[(0, 'IV', 0, BLUE), (4, 'I', 0, BLUE), (8, 'IV', 0, BLUE), (12, 'I', 0, BLUE)]), 'h03-directes')

# chevauchement
ch_bad = [('Mi5', 'Do5', 'Sol4', 'Do3'), ('Si4', 'Sol4', 'Mi4', 'Mi3')]
ch_ok = [('Mi5', 'Do5', 'Sol4', 'Do3'), ('Mi5', 'Si4', 'Sol4', 'Mi3')]
expect(ch_bad, 1, ['chevauchement soprano/alto'])
expect(ch_ok)
save(satb(ch_bad + ch_ok, unit=20, boxes=[(0, 8, RED, 'faux'), (8, 16, GREEN, 'juste')],
          colors={(1, 0): RED, (0, 1): RED, (0, 2): GREEN, (0, 3): GREEN, (2, 2): GREEN, (2, 3): GREEN},
          lines=[((1, 0), (0, 1), RED)],
          labels=[(0, 'I', 0, BLUE), (4, 'III', 0, BLUE), (8, 'I', 0, BLUE), (12, 'III', 0, BLUE)]), 'h03-chevauchement')

# méthode : notes communes (vert) et mouvement contraire
colc = {(0, 0): GREEN, (0, 1): GREEN, (2, 2): GREEN, (2, 3): GREEN}
save(satb(cad, colors=colc, unit=20, labels=deg_labels(['I', 'IV', 'V', 'I']), rows=DEG,
          lines=[((0, 0), (0, 1), GREEN), ((2, 2), (2, 3), GREEN)]), 'h03-cadence')

# ---------------------------------------------------------------- exercices
ex1 = [('La5', 'Do5', 'Mi4', 'La2'), ('Ré5', 'Si3', 'Sol3', 'Sol2'), ('La4', 'Do4', 'Fa4', 'Fa3'), ('Mi4', 'Do4', 'Sol3', 'Do2')]
attendu1 = ['hors tessiture', 'soprano-alto', 'croisement', 'hors tessiture']
for c, a in zip(ex1, attendu1):
    e = check([c])
    assert len(e) == 1 and a in e[0], (c, e)
tt = [(i * 4, x, MUTED) for i, x in enumerate('abcd')]
save(satb(ex1, unit=22, top_texts=tt), 'h04-ex1')
save(satb(ex1, unit=22, top_texts=tt, colors={(0, 0): RED, (0, 1): RED, (1, 1): RED, (1, 2): RED, (2, 2): RED, (3, 3): RED},
          labels=[(0, 'S trop aigu', 0, RED), (4, 'S-A > 8ve', 0, RED), (8, 'A sous T', 0, RED), (12, 'B trop grave', 0, RED)]),
     'h05-c1')

ex2 = [('Si4', 'Sol4', 'Ré4', 'Sol3'), ('Do5', 'Mi4', 'La3', 'La2'), ('La4', 'Do4', 'La3', 'Fa3'), ('La4', 'Ré4', 'La3', 'Ré3')]
ex2n = [['Sol', 'Si', 'Ré'], ['La', 'Do', 'Mi'], ['Fa', 'La', 'Do'], ['Ré', 'Fa', 'La']]
r2 = [(disposition(c, n), check([c])) for c, n in zip(ex2, ex2n)]
assert r2 == [('serrée', []), ('large', []), ('large', ['accord 1 : tierce doublée', "accord 1 : fondamentale non doublée à l'état fondamental"]), ('large', ['accord 1 : tierce absente'])], r2
save(satb(ex2, unit=22, top_texts=tt), 'h04-ex2')
col2 = {(1, 0): GREEN, (3, 0): GREEN, (2, 1): GREEN, (3, 1): GREEN, (0, 2): RED, (2, 2): RED, (1, 3): RED, (3, 3): RED, (0, 3): MUTED, (2, 3): MUTED}
save(satb(ex2, unit=22, top_texts=tt, colors=col2,
          labels=[(0, 'V', 0, BLUE), (4, 'VI', 0, BLUE), (8, 'IV', 0, BLUE), (12, 'II', 0, BLUE),
                  (0, 'serrée', 1, MUTED), (4, 'large', 1, MUTED), (8, 'large', 1, MUTED), (12, 'large', 1, MUTED)]), 'h05-c2')

ex3 = [('Do5', 'Mi4', 'Do4', 'Do3'), ('La4', 'La4', 'Do4', 'La2'), ('La4', 'Fa4', 'Ré4', 'Ré3'), ('Si4', 'Sol4', 'Ré4', 'Sol2'), ('Do5', 'Sol4', 'Sol4', 'Do3')]
expect(ex3, 3, ['8ves consécutives soprano/basse', '5tes consécutives ténor/basse', 'accord 5 : tierce absente'])
ex3_ok = [('Sol4', 'Mi4', 'Do4', 'Do3'), ('La4', 'Mi4', 'Do4', 'La2'), ('La4', 'Fa4', 'Ré4', 'Ré3'), ('Si4', 'Sol4', 'Ré4', 'Sol2'), ('Do5', 'Sol4', 'Mi4', 'Do3')]
expect(ex3_ok)
d3 = ['I', 'VI', 'II', 'V', 'I']
save(satb(ex3, unit=20, labels=deg_labels(d3), rows=DEG), 'h04-ex3')
save(satb(ex3, unit=20, labels=deg_labels(d3), rows=DEG,
          colors={(0, 0): RED, (0, 1): RED, (3, 0): RED, (3, 1): RED, (2, 3): ORANGE, (2, 4): ORANGE, (3, 3): ORANGE, (3, 4): ORANGE},
          lines=[((0, 0), (0, 1), RED), ((3, 0), (3, 1), RED), ((2, 3), (2, 4), ORANGE), ((3, 3), (3, 4), ORANGE)],
          boxes=[(16, 20, RED, 'pas de Mi')]), 'h05-c3a')
save(satb(ex3_ok, unit=20, labels=deg_labels(d3), rows=DEG,
          colors={(0, 0): GREEN, (1, 1): GREEN, (2, 4): GREEN}), 'h05-c3b')

# exercice 4 : soprano et basse donnés
ex4 = [('Mi5', 'Sol4', 'Do4', 'Do3'), ('Fa5', 'La4', 'Do4', 'Fa2'), ('Mi5', 'Sol4', 'Do4', 'Do3'), ('Ré5', 'Sol4', 'Si3', 'Sol2'), ('Do5', 'Mi4', 'Do4', 'Do3')]
ex4b = ex4[:4] + [('Do5', 'Sol4', 'Mi4', 'Do3')]
expect(ex4)
expect(ex4b)
d4 = ['I', 'IV', 'I', 'V', 'I']
sb = Figure([{'clef': 'treble'}, {'clef': 'bass'}],
            [{'staff': 0, 'events': [(c[0], 4) for c in ex4]}, {'staff': 1, 'events': [(c[3], 4) for c in ex4]}],
            brace=(0, 1), gap=84, unit=20, labels=deg_labels(d4), rows=DEG)
save(sb, 'h04-ex4')
inner = {(v, i): BLUE for v in (1, 2) for i in range(5)}
save(satb(ex4, unit=20, labels=deg_labels(d4), rows=DEG, colors=inner, lines=[((2, 3), (2, 4), GREEN)]), 'h05-c4')

# exercice 5 : basse donnée en Sol majeur
ex5 = [('Si4', 'Ré4', 'Sol3', 'Sol2'), ('Si4', 'Mi4', 'Sol3', 'Mi3'), ('Do5', 'Mi4', 'Sol3', 'Do3'), ('La4', 'Ré4', 'Fa#3', 'Ré3'), ('Sol4', 'Si3', 'Sol3', 'Sol2')]
ex5b = [('Ré5', 'Sol4', 'Si3', 'Sol2'), ('Mi5', 'Sol4', 'Si3', 'Mi3'), ('Mi5', 'Sol4', 'Do4', 'Do3'), ('Ré5', 'Fa#4', 'La3', 'Ré3'), ('Si4', 'Sol4', 'Sol3', 'Sol2')]
expect(ex5, tonic='Sol')
expect(ex5b, tonic='Sol')
d5 = ['I', 'VI', 'IV', 'V', 'I']
save(Figure([{'clef': 'bass'}], [{'staff': 0, 'events': [(c[3], 4) for c in ex5]}], key=1, unit=20,
            labels=deg_labels(d5), rows=DEG), 'h04-ex5')
save(satb(ex5, key=1, unit=20, labels=deg_labels(d5), rows=DEG), 'h05-c5a')
save(satb(ex5b, key=1, unit=20, labels=deg_labels(d5), rows=DEG), 'h05-c5b')

# exercice 6 : l'exercice 4 pour quatuor à cordes
qv = [{'staff': v, 'events': [(c[v], 4) for c in ex4]} for v in range(4)]
save(Figure([{'clef': 'treble', 'label': 'Violon 1'}, {'clef': 'treble', 'label': 'Violon 2'},
             {'clef': 'alto', 'label': 'Alto'}, {'clef': 'bass', 'label': 'Violoncelle'}], qv, gap=78, unit=20,
            labels=[(i * 4, d, 0, BLUE) for i, d in enumerate(d4)]), 'h05-c6')
print('OK : toutes les figures sont vérifiées')


# ---------------------------------------------------------------- exercices interactifs (version web)
EXOS = {}


def exo(nom, solution, voix, tonic='Do', key=0, degs=None, chifs=None, depart=None, allow_third=(), chant=False, dur=4):
    """voix : indices des voix que l'élève écrit (0 = S … 3 = B). depart : accords de départ (chasse aux fautes)."""
    sol = [list(c[:4]) for c in solution]
    durs = [c[4] if len(c) > 4 else dur for c in solution]
    if depart:
        donne = [list(c[:4]) for c in depart]
    else:
        donne = [[None if v in voix else c[v] for v in range(4)] for c in sol]
    assert not check([tuple(c) for c in sol], tonic, allow_third=allow_third), nom
    EXOS[nom] = {'donne': donne, 'solution': sol, 'durees': durs, 'voix': list(voix), 'tonique': tonic, 'armure': key,
                 'degres': degs, 'chiffres': chifs, 'tierce': list(allow_third), 'chant': chant, 'corriger': bool(depart)}

exo('h04-ex3', ex3_ok, (0, 1, 2), degs=d3, chifs=['5'] * 5, depart=ex3)
exo('h04-ex4', ex4, (1, 2), degs=d4, chifs=['5'] * 5)
exo('h04-ex5', ex5, (0, 1, 2), tonic='Sol', key=1, degs=d5, chifs=['5'] * 5)

# musique de chaque figure, pour le lecteur et les fichiers audio
import json
from graveur import SONS
AUD = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'audio')
os.makedirs(AUD, exist_ok=True)
json.dump(SONS, open(os.path.join(AUD, 'sons-partie1.json'), 'w'), indent=0)
json.dump(EXOS, open(os.path.join(AUD, '..', 'exercices-partie1.json'), 'w'), ensure_ascii=False)
