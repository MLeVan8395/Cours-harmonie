"""Usage : python3 outils/build_partie2.py [dossier_images]

Construit les figures de la partie 2 (renversements et cadences) et vérifie chaque exemple."""
import os, sys
from graveur import Figure, satb, RED, GREEN, BLUE, ORANGE, MUTED
from verif import check, etat

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cours', 'images')
os.makedirs(OUT, exist_ok=True)
DEG = ['degrés', 'chiffrage']


def save(fig, name):
    fig.save(os.path.join(OUT, name + '.png'))


def expect(chords, n_err=0, contains=(), tonic='Do', allow_third=()):
    e = check([c[:4] for c in chords], tonic, allow_third=allow_third)
    assert len(e) == n_err, (chords, e)
    for c in contains:
        assert any(c in x for x in e), (c, e)
    return e


def labs(chords, degs, chifs=None, dur=4):
    """Étiquettes degrés/chiffrage alignées sur les notes (rondes centrées, blanches à gauche)."""
    out, t = [], 0
    for i, c in enumerate(chords):
        d = c[4] if len(c) > 4 else dur
        ctr = d >= 4
        if degs and degs[i]:
            out.append((t, degs[i], 0, BLUE, ctr))
        if chifs and chifs[i]:
            out.append((t, chifs[i], 1, BLUE, ctr))
        t += d
    return out


def chif(chords):
    return [{'5': '5', '6': '6', '64': '6/4'}[etat(c[:4])] for c in chords]


# ================================================================ chapitre 6 : le premier renversement
et = [('Do5', 'Sol4', 'Mi4', 'Do3'), ('Do5', 'Sol4', 'Do4', 'Mi3'), ('Do5', 'Mi4', 'Sol3', 'Sol2')]
for c in et:
    expect([c])
assert chif(et) == ['5', '6', '6/4']
save(satb(et, unit=24, colors={(3, 0): BLUE, (3, 1): ORANGE, (3, 2): RED},
          labels=labs(et, ['I', 'I', 'I'], chif(et)) + [(0, 'fondamentale', 2, BLUE), (4, 'tierce', 2, ORANGE), (8, 'quinte', 2, RED)],
          rows=['degrés', 'chiffrage', 'basse']), 'h06-etats')

d6 = [('Do5', 'Sol4', 'Do4', 'Mi3'), ('Sol4', 'Do4', 'Sol3', 'Mi3'), ('Do5', 'Sol4', 'Mi4', 'Mi3'), ('Ré5', 'La4', 'Fa4', 'Fa3')]
expect([d6[0]]); expect([d6[1]]); expect([d6[3]])
expect([d6[2]], 1, ['basse doublée dans un accord de sixte majeur'])
save(satb(d6, unit=24, colors={(0, 0): GREEN, (2, 0): GREEN, (0, 1): GREEN, (2, 1): GREEN, (2, 2): RED, (3, 2): RED, (2, 3): GREEN, (3, 3): GREEN},
          top_texts=[(0, 'a) ✔', GREEN), (4, 'b) ✔', GREEN), (8, 'c) ✘', RED), (12, 'd) ✔', GREEN)],
          labels=labs(d6, ['I', 'I', 'I', 'II'], chif(d6)), rows=DEG), 'h06-doublures')

v6 = [('Do5', 'Mi4', 'Sol3', 'Do3'), ('Ré5', 'Ré4', 'Sol3', 'Si2'), ('Do5', 'Mi4', 'Sol3', 'Do3'), ('Do5', 'Fa4', 'La3', 'Fa2'), ('Si4', 'Ré4', 'Sol3', 'Sol2'), ('Do5', 'Mi4', 'Sol3', 'Do3')]
expect(v6)
save(satb(v6, unit=20, colors={(3, 1): ORANGE}, labels=labs(v6, ['I', 'V', 'I', 'IV', 'V', 'I'], chif(v6)), rows=DEG), 'h06-v6')

i6 = [('Mi5', 'Sol4', 'Do4', 'Do3'), ('Sol5', 'Sol4', 'Do4', 'Mi3'), ('Fa5', 'La4', 'Do4', 'Fa3'), ('Ré5', 'Sol4', 'Si3', 'Sol3'), ('Do5', 'Mi4', 'Do4', 'Do3')]
expect(i6)
save(satb(i6, unit=20, colors={(3, i): ORANGE for i in range(4)}, labels=labs(i6, ['I', 'I', 'IV', 'V', 'I'], chif(i6)), rows=DEG), 'h06-i6')

# ================================================================ chapitre 7 : les cadences
parfaite = [('Si4', 'Ré4', 'Sol3', 'Sol2'), ('Do5', 'Mi4', 'Sol3', 'Do3')]
imparfaite = [('Ré5', 'Sol4', 'Ré4', 'Si2'), ('Do5', 'Sol4', 'Mi4', 'Do3')]
demi = [('Do5', 'Fa4', 'La3', 'Fa2'), ('Si4', 'Ré4', 'Sol3', 'Sol2')]
plagale = [('Do5', 'Fa4', 'La3', 'Fa2'), ('Do5', 'Mi4', 'Sol3', 'Do3')]
rompue = [('Si4', 'Sol4', 'Ré4', 'Sol2'), ('Do5', 'Mi4', 'Do4', 'La2')]
for p in (parfaite, imparfaite, demi, plagale):
    expect(p)
expect(rompue, allow_third={1})
assert 'accord 2 : tierce doublée' in check(rompue)   # doublure voulue
c1 = parfaite + imparfaite + demi
save(satb(c1, unit=18, boxes=[(0, 8, BLUE, 'parfaite'), (8, 16, ORANGE, 'imparfaite'), (16, 24, MUTED, 'demi-cadence')],
          labels=labs(c1, ['V', 'I', 'V', 'I', 'IV', 'V'], chif(c1)), rows=DEG), 'h07-cadences1')
c2 = plagale + rompue
save(satb(c2, unit=18, boxes=[(0, 8, GREEN, 'plagale'), (8, 16, RED, 'rompue')],
          colors={(0, 3): RED, (2, 3): RED, (0, 2): ORANGE},
          lines=[((0, 2), (0, 3), ORANGE)],
          labels=labs(c2, ['IV', 'I', 'V', 'VI'], chif(c2)), rows=DEG), 'h07-cadences2')

ii6 = [('Ré5', 'La4', 'Fa4', 'Fa3'), ('Ré5', 'Sol4', 'Si3', 'Sol3'), ('Do5', 'Sol4', 'Mi4', 'Do3')]
expect(ii6)
save(satb(ii6, unit=22, labels=labs(ii6, ['II', 'V', 'I'], chif(ii6)), rows=DEG), 'h07-ii6')

# ================================================================ chapitre 8 : la quarte et sixte
cad = [('Do5', 'Mi4', 'Sol3', 'Do3', 2), ('Ré5', 'Fa4', 'La3', 'Fa2', 2), ('Do5', 'Mi4', 'Sol3', 'Sol2', 2), ('Si4', 'Ré4', 'Sol3', 'Sol2', 2), ('Do5', 'Mi4', 'Sol3', 'Do3', 4)]
expect(cad)
save(satb(cad, unit=24, time=(4, 4), colors={(0, 2): RED, (0, 3): RED, (1, 2): ORANGE, (1, 3): ORANGE},
          lines=[((0, 2), (0, 3), RED), ((1, 2), (1, 3), ORANGE)],
          labels=labs(cad, ['I', 'II', 'I', 'V', 'I'], chif(cad)), rows=DEG), 'h08-cadentielle')
pas = [('Do5', 'Mi4', 'Sol3', 'Do3'), ('Si4', 'Ré4', 'Sol3', 'Ré3'), ('Do5', 'Do4', 'Sol3', 'Mi3')]
bro = [('Do5', 'Mi4', 'Sol3', 'Do3'), ('Do5', 'Fa4', 'La3', 'Do3'), ('Do5', 'Mi4', 'Sol3', 'Do3')]
expect(pas); expect(bro)
save(satb(pas, unit=22, colors={(3, i): ORANGE for i in range(3)}, labels=labs(pas, ['I', 'V', 'I'], chif(pas)), rows=DEG), 'h08-passage')
save(satb(bro, unit=22, colors={(1, 1): ORANGE, (2, 1): ORANGE}, labels=labs(bro, ['I', 'IV', 'I'], chif(bro)), rows=DEG), 'h08-broderie')

# ================================================================ chapitre 9 : basse donnée, chant donné
bc = [('Do5', 'Mi4', 'Sol3', 'Do3', 2), ('Do5', 'Sol4', 'Sol3', 'Mi3', 2), ('Do5', 'Fa4', 'La3', 'Fa3', 2), ('Ré5', 'Fa4', 'La3', 'Ré3', 2),
      ('Do5', 'Mi4', 'Sol3', 'Sol2', 2), ('Si4', 'Ré4', 'Sol3', 'Sol2', 2), ('Do5', 'Mi4', 'Sol3', 'Do3', 4)]
expect(bc)
bdeg = ['I', 'I', 'IV', 'II', 'I', 'V', 'I']
bass_only = Figure([{'clef': 'bass'}], [{'staff': 0, 'events': [(c[3], c[4]) for c in bc]}], unit=24, time=(4, 4),
                   labels=[l for l in labs(bc, None, chif(bc)) if l[2] == 1])
save(bass_only, 'h09-bc1')
sb = Figure([{'clef': 'treble'}, {'clef': 'bass'}],
            [{'staff': 0, 'events': [(c[0], c[4]) for c in bc]}, {'staff': 1, 'events': [(c[3], c[4]) for c in bc]}],
            brace=(0, 1), gap=104, unit=24, time=(4, 4), labels=labs(bc, bdeg, chif(bc)), rows=DEG)
save(sb, 'h09-bc2')
save(satb(bc, unit=24, time=(4, 4), colors={(v, i): BLUE for v in (1, 2) for i in range(7)}, labels=labs(bc, bdeg, chif(bc)), rows=DEG), 'h09-bc3')

cd = [('Mi5', 'Sol4', 'Do4', 'Do3'), ('Fa5', 'Fa4', 'Do4', 'La2'), ('Mi5', 'Sol4', 'Do4', 'Do3'), ('Ré5', 'Sol4', 'Ré4', 'Si2'),
      ('Do5', 'Sol4', 'Mi4', 'Do3'), ('La4', 'Fa4', 'Ré4', 'Ré3'), ('Si4', 'Sol4', 'Ré4', 'Sol2'), ('Do5', 'Sol4', 'Mi4', 'Do3')]
expect(cd)
cdeg = ['I', 'IV', 'I', 'V', 'I', 'II', 'V', 'I']
save(Figure([{'clef': 'treble'}], [{'staff': 0, 'events': [(c[0], 4) for c in cd]}], unit=18), 'h09-cd1')
save(Figure([{'clef': 'treble'}, {'clef': 'bass'}],
            [{'staff': 0, 'events': [(c[0], 4) for c in cd]}, {'staff': 1, 'events': [(c[3], 4, {'color': ORANGE}) for c in cd]}],
            brace=(0, 1), gap=104, unit=18, labels=labs(cd, cdeg, chif(cd)), rows=DEG), 'h09-cd2')
save(satb(cd, unit=18, colors={(v, i): BLUE for v in (1, 2) for i in range(8)}, labels=labs(cd, cdeg, chif(cd)), rows=DEG), 'h09-cd3')

# ================================================================ chapitre 10 : le mode mineur
mn = [('Mi4', 'Do4', 'La3'), ('Fa4', 'Ré4', 'Si3'), ('Sol#4', 'Mi4', 'Do4'), ('La4', 'Fa4', 'Ré4'), ('Si4', 'Sol#4', 'Mi4'), ('Do5', 'La4', 'Fa4'), ('Ré5', 'Si4', 'Sol#4')]
vv = [{'staff': 0, 'stem': None, 'events': [(c[k], 4) for c in mn]} for k in range(3)]
save(Figure([{'clef': 'treble'}], vv, unit=18,
            labels=[(i * 4, d, 0, BLUE) for i, d in enumerate(['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'])] +
                   [(i * 4, l, 1, RED if l in ('B°', 'C+', 'G♯°') else MUTED) for i, l in enumerate(['Am', 'B°', 'C+', 'Dm', 'E', 'F', 'G♯°'])],
            rows=['degrés', 'accord']), 'h10-degres')

sec_faux = [('Fa4', 'Do4', 'La3', 'Fa3'), ('Sol#4', 'Mi4', 'Si3', 'Mi3')]
sec_ok = [('La4', 'Do4', 'La3', 'Fa3'), ('Sol#4', 'Mi4', 'Si3', 'Mi3')]
expect(sec_faux, 1, ['seconde augmentée (soprano)'], tonic='La')
expect(sec_ok, tonic='La', allow_third={0})
save(satb(sec_faux + sec_ok, unit=20, boxes=[(0, 8, RED, 'faux'), (8, 16, GREEN, 'juste')],
          colors={(0, 0): RED, (0, 1): RED, (0, 2): GREEN, (2, 2): GREEN}, lines=[((0, 0), (0, 1), RED)],
          labels=[(0, 'VI', 0, BLUE), (4, 'V', 0, BLUE), (8, 'VI', 0, BLUE), (12, 'V', 0, BLUE)]), 'h10-seconde')

ph = [('Mi5', 'La4', 'Do4', 'La2', 2), ('Fa5', 'La4', 'Ré4', 'Ré3', 2), ('Mi5', 'Sol#4', 'Si3', 'Mi3', 2), ('Do5', 'La4', 'La3', 'Fa3', 2),
      ('Si4', 'Fa4', 'Si3', 'Ré3', 4), ('Do5', 'Mi4', 'La3', 'Mi3', 2), ('Si4', 'Mi4', 'Sol#3', 'Mi3', 2), ('Do5', 'Mi4', 'La3', 'La2', 4)]
expect(ph, tonic='La', allow_third={3})
phc = ['5', '5', '♯', '5', '6', '6/4', '♯', '5']
save(satb(ph, unit=22, time=(4, 4), colors={(1, 2): RED, (1, 3): RED, (2, 6): RED, (2, 7): RED, (2, 3): ORANGE, (1, 3): ORANGE},
          labels=labs(ph, ['I', 'IV', 'V', 'VI', 'II', 'I', 'V', 'I'], phc), rows=DEG), 'h10-phrase')

# ================================================================ exercices
ex1 = [('Ré5', 'Sol4', 'Ré4', 'Si2'), ('Do5', 'La4', 'Fa4', 'Do3'), ('La4', 'Fa4', 'Ré4', 'Fa3'), ('Mi5', 'La4', 'Do4', 'La2'), ('Mi5', 'Do5', 'Sol4', 'Sol3')]
for c in ex1:
    expect([c])
assert chif(ex1) == ['6', '6/4', '6', '5', '6/4'], chif(ex1)
tt = [(i * 4, x, MUTED) for i, x in enumerate('abcde')]
save(satb(ex1, unit=22, top_texts=tt), 'h11-ex1')
save(satb(ex1, unit=22, top_texts=tt, labels=labs(ex1, ['V', 'IV', 'II', 'VI', 'I'], chif(ex1)), rows=DEG), 'h12-c1')

# exercice 2 : basse chiffrée en Fa majeur
ex2 = [('La4', 'Do4', 'Fa3', 'Fa3', 2), ('Sib4', 'Sib3', 'Fa3', 'Ré3', 2), ('Sol4', 'Do4', 'Sol3', 'Mi3', 2), ('Fa4', 'Do4', 'La3', 'Fa3', 2),
       ('Sol4', 'Ré4', 'Sib3', 'Sib2', 4), ('Fa4', 'Do4', 'La3', 'Do3', 2), ('Mi4', 'Do4', 'Sol3', 'Do3', 2), ('Fa4', 'Do4', 'La3', 'Fa2', 4)]
EX2 = None  # remplacé plus bas par une réalisation plus chantante
from recherche import realise
Fb, Bb, Cm, Gm = ['Fa', 'La', 'Do'], ['Sib', 'Ré', 'Fa'], ['Do', 'Mi', 'Sol'], ['Sol', 'Sib', 'Ré']
r = realise([Fb, Bb, Cm, Fb, Gm, Fb, Cm, Fb], ['Fa3', 'Ré3', 'Mi3', 'Fa3', 'Sib2', 'Do3', 'Do3', 'Fa2'],
            ['Do5', 'Sib4', 'Do5', 'La4', 'Sib4', 'La4', 'Sol4', 'Fa4'], tonic='Fa')
ex2 = [c + (d,) for c, d in zip(r[0][1], [2, 2, 2, 2, 4, 2, 2, 4])]
expect(ex2, tonic='Fa')
ex2c = chif(ex2)
assert ex2c == ['5', '6', '6', '5', '6', '6/4', '5', '5'], ex2c
ex2d = ['I', 'IV', 'V', 'I', 'II', 'I', 'V', 'I']
save(Figure([{'clef': 'bass'}], [{'staff': 0, 'events': [(c[3], c[4]) for c in ex2]}], key=-1, unit=24, time=(4, 4),
            labels=[l for l in labs(ex2, None, ex2c) if l[2] == 1]), 'h11-ex2')
save(satb(ex2, key=-1, unit=24, time=(4, 4), labels=labs(ex2, ex2d, ex2c), rows=DEG), 'h12-c2')

# exercice 3 : chant donné en Sol majeur
from recherche import harmonise
DG = {'I': ['Sol', 'Si', 'Ré'], 'II': ['La', 'Do', 'Mi'], 'IV': ['Do', 'Mi', 'Sol'], 'V': ['Ré', 'Fa#', 'La'], 'VI': ['Mi', 'Sol', 'Si']}
S3 = ['Si4', 'Do5', 'Ré5', 'Si4', 'Do5', 'La4', 'La4', 'Sol4']
h = harmonise(S3, DG, tonic='Sol', fixed_deg=[('I', '5')] + [None] * 5 + [('V', '5'), ('I', '5')], n=1)[0][1]
ex3 = [v for d, e, v in h]
ex3d = [d for d, e, v in h]
expect(ex3, tonic='Sol')
save(Figure([{'clef': 'treble'}], [{'staff': 0, 'events': [(s, 4) for s in S3]}], key=1, unit=18), 'h11-ex3')
save(satb(ex3, key=1, unit=18, labels=labs(ex3, ex3d, chif(ex3)), rows=DEG, colors={(3, i): ORANGE for i in range(8)}), 'h12-c3')

# exercice 4 : basse chiffrée en ré mineur
Dmn, Gmn, A, Bbb, Ed = ['Ré', 'Fa', 'La'], ['Sol', 'Sib', 'Ré'], ['La', 'Do#', 'Mi'], ['Sib', 'Ré', 'Fa'], ['Mi', 'Sol', 'Sib']
fx = [None] * 9
r4 = realise([Dmn, Gmn, A, Bbb, Ed, Dmn, A, Dmn, Dmn], ['Ré3', 'Sib2', 'La2', 'Sib2', 'Sol2', 'La2', 'La2', 'Ré3', 'Ré3'],
             tonic='Ré', allow_third={3}, n=40)
# on veut la tierce (Ré) doublée dans le VI de la cadence rompue
r4 = [p for c, p in r4 if [n[:-1] for n in p[3]].count('Ré') == 2]
assert r4, 'pas de réalisation avec la tierce doublée'
ex4 = r4[0][:8]
ex4 = [c + (d,) for c, d in zip(ex4, [2, 2, 2, 2, 4, 2, 2, 4])]
expect(ex4, tonic='Ré', allow_third={3})
ex4c = ['5', '6', '♯', '5', '6', '6/4', '♯', '5']
assert chif(ex4) == ['5', '6', '5', '5', '6', '6/4', '5', '5'], chif(ex4)
ex4d = ['I', 'IV', 'V', 'VI', 'II', 'I', 'V', 'I']
save(Figure([{'clef': 'bass'}], [{'staff': 0, 'events': [(c[3], c[4]) for c in ex4]}], key=-1, unit=24, time=(4, 4),
            labels=[l for l in labs(ex4, None, ex4c) if l[2] == 1]), 'h11-ex4')
save(satb(ex4, key=-1, unit=24, time=(4, 4), labels=labs(ex4, ex4d, ex4c), rows=DEG), 'h12-c4')

# exercice 5 : chasse aux fautes en la mineur
ex5_ok = [('Do5', 'Mi4', 'La3', 'La2'), ('Do5', 'Fa4', 'La3', 'Fa2'), ('Ré5', 'Fa4', 'La3', 'Ré3'), ('Si4', 'Mi4', 'Sol#3', 'Mi3'), ('Do5', 'Mi4', 'La3', 'La2')]
expect(ex5_ok, tonic='La')
ex5 = [('Do5', 'Mi4', 'La3', 'La2'), ('Do5', 'Fa4', 'La3', 'Fa2'), ('Ré5', 'Fa4', 'Fa3', 'Ré3'), ('Mi5', 'Mi4', 'Sol#3', 'Mi3'), ('Do5', 'Mi4', 'La3', 'La2')]
expect(ex5, 3, ['accord 3 : tierce doublée', '8ves consécutives soprano/basse', 'seconde augmentée (ténor)'], tonic='La')
ex5d = ['I', 'VI', 'IV', 'V', 'I']
ex5c = ['5', '5', '5', '♯', '5']
save(satb(ex5, unit=20, labels=labs(ex5, ex5d, ex5c), rows=DEG), 'h11-ex5')
save(satb(ex5, unit=20, labels=labs(ex5, ex5d, ex5c), rows=DEG,
          colors={(2, 2): RED, (2, 3): RED, (1, 2): RED, (0, 2): ORANGE, (0, 3): ORANGE, (3, 2): ORANGE, (3, 3): ORANGE},
          lines=[((2, 2), (2, 3), RED), ((0, 2), (0, 3), ORANGE), ((3, 2), (3, 3), ORANGE)]), 'h12-c5a')
save(satb(ex5_ok, unit=20, labels=labs(ex5_ok, ex5d, ex5c), rows=DEG,
          colors={(2, 2): GREEN, (0, 3): GREEN}), 'h12-c5b')

# exercice 6 : l'exercice 2 pour quatuor
qv = [{'staff': v, 'events': [(c[v], c[4]) for c in ex2]} for v in range(4)]
save(Figure([{'clef': 'treble', 'label': 'Violon 1'}, {'clef': 'treble', 'label': 'Violon 2'},
             {'clef': 'alto', 'label': 'Alto'}, {'clef': 'bass', 'label': 'Violoncelle'}], qv, key=-1, gap=82, unit=24, time=(4, 4),
            labels=[l for l in labs(ex2, ex2d) if l[2] == 0]), 'h12-c6')

# données pour la rédaction
import json
json.dump({'ex2': ex2, 'ex3': ex3, 'ex3d': ex3d, 'ex4': ex4}, open('/tmp/p2.json', 'w'), ensure_ascii=False)
print('OK : toutes les figures de la partie 2 sont vérifiées')


# ---------------------------------------------------------------- exercices interactifs (version web)
EXOS = {}


def exo(nom, solution, voix, tonic='Do', key=0, degs=None, chifs=None, depart=None, allow_third=(), chant=False, dur=4, guide=None):
    """voix : indices des voix que l'élève écrit (0 = S … 3 = B). depart : accords de départ (chasse aux fautes)."""
    sol = [list(c[:4]) for c in solution]
    durs = [c[4] if len(c) > 4 else dur for c in solution]
    if depart:
        donne = [list(c[:4]) for c in depart]
    else:
        donne = [[None if v in voix else c[v] for v in range(4)] for c in sol]
    assert not check([tuple(c) for c in sol], tonic, allow_third=allow_third), nom
    EXOS[nom] = {'donne': donne, 'solution': sol, 'durees': durs, 'voix': list(voix), 'tonique': tonic, 'armure': key,
                 'degres': degs, 'chiffres': chifs, 'tierce': list(allow_third), 'chant': chant, 'corriger': bool(depart), 'guide': guide}

GUIDE_BC = [
    {'type': 'degres', 'titre': 'Trouve les accords',
     'consigne': "Sous chaque note de la basse, choisis le degré. Rappel : avec 5, la fondamentale est la basse ; avec 6, elle est une 3ce sous la basse ; avec 6/4, une 4te au-dessus."},
    {'type': 'voix', 'voix': [0], 'titre': 'Écris le soprano',
     'consigne': "Une ligne simple, surtout par degrés conjoints, qui finit sur la tonique. Chaque note doit appartenir à l'accord. Surveille les 5tes et les 8ves avec la basse."},
    {'type': 'voix', 'voix': [1, 2], 'titre': "Complète l'alto et le ténor",
     'consigne': "Garde les notes communes, va au plus près, et double la bonne note : la fondamentale à l'état fondamental, la basse dans le 6/4."}]
GUIDE_CD = [
    {'type': 'degres', 'titre': 'Choisis les accords',
     'consigne': "Pour chaque note du soprano, choisis un accord qui la contient. Commence sur I et finis par V-I. Préfère les enchaînements forts : IV ou II vers V, V vers I, VI vers II, IV ou V."},
    {'type': 'voix', 'voix': [3], 'titre': 'Écris la basse',
     'consigne': "Mets la fondamentale ou la tierce de chaque accord (le chiffrage s'affiche tout seul). Cherche le mouvement contraire avec le soprano. À la cadence, la fondamentale à la basse."},
    {'type': 'voix', 'voix': [1, 2], 'titre': "Complète l'alto et le ténor",
     'consigne': "Garde les notes communes, va au plus près, et vérifie les doublures."}]
exo('h11-ex2', ex2, (0, 1, 2), tonic='Fa', key=-1, chifs=ex2c)
exo('h11-ex3', ex3, (1, 2, 3), tonic='Sol', key=1, chant=True)
exo('h11-ex4', ex4, (0, 1, 2), tonic='Ré', key=-1, chifs=ex4c, allow_third={3})
exo('h11-ex5', ex5_ok, (0, 1, 2), tonic='La', degs=ex5d, chifs=ex5c, depart=ex5)

# musique de chaque figure, pour le lecteur et les fichiers audio
import json
from graveur import SONS
AUD = os.path.join(os.path.dirname(os.path.abspath(OUT)), 'audio')
os.makedirs(AUD, exist_ok=True)
json.dump(SONS, open(os.path.join(AUD, 'sons-partie2.json'), 'w'), indent=0)
json.dump(EXOS, open(os.path.join(AUD, '..', 'exercices-partie2.json'), 'w'), ensure_ascii=False)
