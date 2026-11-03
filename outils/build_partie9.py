"""Usage : python3 outils/build_partie9.py

Partie 9 (le XXe siècle : Scriabine, Bartók, Stravinsky, Prokofiev, Messiaen, Dutilleux) : figures des chapitres 49 à 56,
exercices du cours et du cahier (chapitres 49 à 54). (Reconstruit aussi les parties 4 à 8.)"""
import json, os, re
from graveur import Figure, satb, RED, GREEN, BLUE, ORANGE, MUTED, SONS, N, midi
import build_partie8 as P8
import libre as L

ICI = os.path.dirname(os.path.abspath(__file__))
COURS = os.path.join(ICI, '..', 'cours')
CAHIER = os.path.join(ICI, '..', 'cahier')
IMG, IMGK = os.path.join(COURS, 'images'), os.path.join(CAHIER, 'images')
save, empile, gamme, portee_simple, lab2, jazz = P8.save, P8.empile, P8.gamme, P8.portee_simple, P8.lab2, P8.jazz
SONS.clear()


def miroir(notes, axe, bemol=False):
    """renverse une ligne autour d'une hauteur (midi) : chaque intervalle montant devient descendant"""
    out = []
    for x in notes:
        m = 2 * axe - midi(N(x))
        out.append(L.transpose_reel('Do4', m - 60, bemol))
    return out


# ======================================================================== chapitre 49 : Scriabine
empile([['Do3', 'Fa#3', 'Sib3', 'Mi4', 'La4', 'Ré5'], ['Do3', 'Mi3', 'Sib3', 'Ré4', 'Fa#4', 'La4']], 'h49-mystique',
       ['en quartes', 'en tierces : C9(♯11, 13)'], unit=40, coul={(0, 'Fa#3'): RED, (1, 'Fa#4'): RED})
Q5 = [('Fa5', 'Si4', 'Réb4', 'Sol2', 4), ('Mi5', 'Do5', 'Do4', 'Do3', 4)]
save(satb(Q5, unit=28, colors={(2, 0): RED, (2, 1): RED}, labels=lab2(0, [('G7(♭5)', 'V7'), ('C', 'I')]), rows=['accord', 'degré']), 'h49-quinte-alteree')
MY = L.planing_reel(('Mi5', 'Sib4', 'Fa#4', 'Do4'), ['Mi5', 'Do#5', 'Sib4', 'Sol4', 'Sib4', 'Do#5', 'Mi5'], bemols=[True, False, True, True, True, False, True])
save(satb([c + (2,) for c in MY[:-1]] + [MY[-1] + (4,)], unit=24, time=(4, 4),
          labels=[(i * 2, s, 0, BLUE) for i, s in enumerate(['Do', 'La', 'Sol♭', 'Mi♭', 'Sol♭', 'La', 'Do'])],
          rows=['basse']), 'h49-transpositions')

# ======================================================================== chapitre 50 : Bartók
ac = ['Do4', 'Ré4', 'Mi4', 'Fa#4', 'Sol4', 'La4', 'Sib4', 'Do5']
oc = ['Do4', 'Réb4', 'Mib4', 'Mi4', 'Fa#4', 'Sol4', 'La4', 'Sib4', 'Do5']
portee_simple(gamme(ac, coul={3: RED, 6: RED}) + gamme(oc), 'h50-echelles', unit=22,
              boxes=[(0, 8, BLUE, 'échelle acoustique'), (8, 17, GREEN, 'échelle octatonique')])
axes = ['Do4', 'Mib4', 'Fa#4', 'La4', 'Sol4', 'Sib4', 'Do#5', 'Mi5', 'Fa4', 'Lab4', 'Si4', 'Ré5']
portee_simple(gamme(axes, dur=2), 'h50-axes', unit=16,
              boxes=[(0, 8, BLUE, 'tonique'), (8, 16, GREEN, 'dominante'), (16, 24, ORANGE, 'sous-dominante')])
empile([['Do4', 'Mib4', 'Mi4', 'Sol4'], ['Mi3', 'La3', 'Ré4', 'Sol4']], 'h50-accords', ['C majeur-mineur', 'accord de quartes'], unit=34,
       coul={(0, 'Mib4'): RED, (0, 'Mi4'): RED})
sop = ['Ré5', 'Mi5', 'Fa5', 'Sol5', 'La5', 'Sol5', 'Fa5', 'Mi5', 'Ré5']
bas = miroir(sop, 62)
save(Figure([{'clef': 'treble'}, {'clef': 'bass'}], [{'staff': 0, 'stem': None, 'events': [(x, 1) for x in sop[:-1]] + [(sop[-1], 4)]},
                                                   {'staff': 1, 'stem': None, 'events': [(x, 1) for x in bas[:-1]] + [(bas[-1], 4)]}],
            brace=(0, 1), gap=104, unit=24, time=(4, 4), lines=[((0, 4), (1, 4), RED)]), 'h50-miroir')
v1 = [('Ré5', 1), ('Mi5', 1), ('Fa5', 1), ('Sol5', 1), ('La5', 4)]
vc = [(x, d) for x, (_, d) in zip(miroir([n for n, _ in v1], 62), v1)]
vv = [{'staff': 0, 'stem': None, 'events': v1}, {'staff': 1, 'stem': None, 'events': [('Fa4', 8)]},
      {'staff': 2, 'stem': None, 'events': [('Si3', 8)]}, {'staff': 3, 'stem': None, 'events': vc}]
save(Figure(P8.P7.P5.QUAT, vv, gap=96, unit=26, time=(4, 4)), 'h50-quatuor')

# ======================================================================== chapitre 51 : Stravinsky
empile([['Do3', 'Mi3', 'Sol3'], ['Fa#4', 'La#4', 'Do#5'], ['Do3', 'Mi3', 'Sol3', 'Fa#4', 'La#4', 'Do#5']], 'h51-petrouchka',
       ['C', 'F♯', 'C + F♯'], unit=34, coul={(1, 'Fa#4'): RED, (1, 'La#4'): RED, (1, 'Do#5'): RED, (2, 'Fa#4'): RED, (2, 'La#4'): RED, (2, 'Do#5'): RED})
empile([['Mib2', 'Sib2', 'Réb3', 'Sol3', 'Fab4', 'Lab4', 'Dob5']], 'h51-augures', ['F♭ sur E♭7'], unit=44,
       coul={(0, 'Fab4'): RED, (0, 'Lab4'): RED, (0, 'Dob5'): RED})
OST = [('Sol4', 'Ré4', 'La3', 'Ré3', 1), ('La4', 'Mi4', 'Si3', 'La2', 1), ('Sol4', 'Ré4', 'La3', 'Ré3', 1), ('Fa4', 'Do4', 'Sol3', 'La2', 1),
       ('Sol4', 'Ré4', 'La3', 'Ré3', 1), ('La4', 'Mi4', 'Si3', 'La2', 1), ('Sol4', 'Ré4', 'La3', 'Ré3', 2)]
save(satb(OST, unit=26, time=(4, 4), colors={(3, i): GREEN for i in range(7)}), 'h51-ostinato')

# ======================================================================== chapitre 52 : Prokofiev
PK = [('Mi5', 'Sol4', 'Do4', 'Do3', 2), ('Sol5', 'Do5', 'Mi4', 'Do3', 2), ('Lab5', 'Réb5', 'Fa4', 'Réb3', 4), ('Fa5', 'Si4', 'Ré4', 'Sol2', 4),
      ('Mi5', 'Do5', 'Sol4', 'Do3', 4)]
# corrige les positions des étiquettes (durées inégales)
PKL = []
t = 0
for (a, d), c in zip([('C', 'I'), ('C', 'I'), ('D♭', 'II♭'), ('G7', 'V7'), ('C', 'I')], PK):
    PKL += [(t, a, 0, BLUE), (t, d, 1, MUTED)]
    t += c[4]
save(satb(PK, unit=24, time=(4, 4), colors={(v, 2): RED for v in range(4)}, labels=PKL, rows=['accord', 'degré']), 'h52-a-cote')
PM = [('Mi5', 'Do5', 'Sol4', 'Do3', 4), ('Ré#5', 'Si4', 'Fa#4', 'Si2', 4), ('Ré5', 'Si4', 'Fa4', 'Sol2', 4), ('Do5', 'Sol4', 'Mi4', 'Do3', 4)]
save(satb(PM, unit=26, colors={(0, 1): RED, (2, 1): RED}, labels=lab2(0, [('C', 'I'), ('B', 'VII♮ (majeur !)'), ('G7', 'V7'), ('C', 'I')]),
          rows=['accord', 'degré']), 'h52-demi-ton')

# ======================================================================== chapitre 53 : Messiaen
m2 = ['Do4', 'Réb4', 'Mib4', 'Mi4', 'Fa#4', 'Sol4', 'La4', 'Sib4', 'Do5']
m3 = ['Do4', 'Ré4', 'Mib4', 'Mi4', 'Fa#4', 'Sol4', 'Lab4', 'Sib4', 'Si4', 'Do5']
portee_simple(gamme(m2) + gamme(m3), 'h53-modes', unit=20, boxes=[(0, 9, BLUE, 'mode 2 (octatonique)'), (9, 19, GREEN, 'mode 3')])
empile([['Do3', 'Sol3', 'Mi4', 'La4', 'Fa#5'], ['Sol2', 'Ré3', 'Fa3', 'Si3', 'Mi4', 'La4', 'Do5']], 'h53-accords',
       ['6te ajoutée + 4te aug.', 'sur dominante'], unit=56, coul={(0, 'La4'): RED, (0, 'Fa#5'): RED})
ry = [0.5, 1, 1.5, 1, 0.5]
save(Figure([{'clef': 'treble'}], [{'staff': 0, 'stem': 'up', 'events': [('La4', d) for d in ry]}], unit=40, bars=False,
            top_texts=[(0, '½', MUTED), (0.5, '1', MUTED), (1.5, '1 ½', RED), (3, '1', MUTED), (4, '½', MUTED)]), 'h53-rythme')

# ======================================================================== chapitre 54 : Dutilleux
sop = ['Si4', 'Do5', 'Ré5', 'Mib5', 'Ré5', 'Do5', 'Si4']
bas = miroir(sop, (71 + 51) // 2, bemol=True)
DU = [(s, 'Sol4', 'Sol3', b) for s, b in zip(sop, bas)]
save(satb([c + (2,) for c in DU[:-1]] + [DU[-1] + (4,)], unit=24, time=(4, 4), colors={(v, i): GREEN for i in range(7) for v in (1, 2)}), 'h54-pivot')
SY = [('Fa4', 'Si3', 'Fa#3', 'Do3'), ('Fa#4', 'Do#4', 'Sol3', 'Ré3')]
save(satb([c + (4,) for c in SY], unit=34, labels=[(0, '6 + 5 + 6', 0, BLUE), (4, '5 + 6 + 5', 0, BLUE)], rows=['demi-tons']), 'h54-symetrie')

# ======================================================================== exercices du cours (chapitre 55)
EXOS, EXOS_K = {}, {}
an = [['Do3', 'Mi3', 'Sol3', 'Fa#4', 'La#4', 'Do#5'], ['Do3', 'Sol3', 'Mib4', 'Mi4'], ['Do3', 'Sol3', 'Mi4', 'La4', 'Fa#5'], ['Do3', 'Fa#3', 'Sib3', 'Mi4', 'La4', 'Ré5']]
empile(an, 'h55-ex1', ['a)', 'b)', 'c)', 'd)'], unit=40, rows=('',))
empile(an, 'h48-tmp', ['C + F♯', 'C majeur-mineur', 'C6 + ♯4', 'mystique'], unit=40)
os.replace(os.path.join(IMG, 'h48-tmp.png'), os.path.join(IMG, 'h56-c1.png'))
SONS['h56-c1'] = SONS.pop('h48-tmp')

sop = ['Ré5', 'Mi5', 'Fa5', 'Sol5', 'Fa5', 'Mi5', 'Ré5', 'Do5', 'Ré5']
bas = miroir(sop, 62)
sol = [(s, 'Fa4', 'Si3', b) for s, b in zip(sop, bas)]
L.faire_libre(EXOS, 'h55-ex2', sol, [''] * 9, [3], IMG, cibles=[[b[:-1]] for b in bas], durees=[1] * 8 + [4], quoi='au miroir du soprano', montrer=False)
O7 = [['Do', 'Mi', 'Sol', 'Sib'], ['Mib', 'Sol', 'Sib', 'Réb'], ['Fa#', 'La#', 'Do#', 'Mi'], ['La', 'Do#', 'Mi', 'Sol'], ['Do', 'Mi', 'Sol', 'Sib']]
jazz(EXOS, 'h55-ex3', ['C7', 'E♭7', 'F♯7', 'A7', 'C7'], O7, [c[1:] for c in O7], ['Do3', 'Mib3', 'Fa#2', 'La2', 'Do3'], IMG)
PV = [['Do', 'Mi', 'Sol'], ['Mib', 'Sol', 'Sib'], ['Mi', 'Sol', 'Si'], ['Lab', 'Do', 'Mib', 'Sol'], ['Do', 'Mib', 'Sol'], ['Do', 'Mi', 'Sol']]
jazz(EXOS, 'h55-ex4', ['C', 'E♭', 'Em', 'A♭maj7', 'Cm', 'C'], PV, None, ['Do3', 'Mib3', 'Mi3', 'Lab2', 'Do3', 'Do3'], IMG, voix=(1, 2), sop=['Sol4'] * 6)
sol = L.planing_reel(('Mi5', 'Sib4', 'Fa#4', 'Do4'), ['Mi5', 'Do#5', 'Sib4', 'Do#5', 'Mi5'], bemols=[True, False, True, False, True])
L.faire_libre(EXOS, 'h55-ex5', sol, ['sur Do', 'sur La', 'sur Sol♭', 'sur La', 'sur Do'], [1, 2, 3], IMG, parallele='reel', donnes=(0,), titre_ligne='basse')
for k in range(2, 6):
    os.replace(os.path.join(IMG, f'h55-ex{k}-c.png'), os.path.join(IMG, f'h56-c{k}.png'))
    SONS[f'h56-c{k}'] = SONS.pop(f'h55-ex{k}-c')

# ======================================================================== cahier : chapitres 49 à 54
PAGES = {c: [] for c in range(49, 55)}


def page(chap, nom, titre, consigne):
    PAGES[chap].append((nom, titre, consigne))


CJ = P8.CJ
k = 'c49-01'
sol = L.planing_reel(('Mi5', 'Sib4', 'Fa#4', 'Do4'), ['Mi5', 'Ré#5', 'Ré5', 'Do#5', 'Ré5', 'Ré#5', 'Mi5'], bemols=[True, False, True, False, True, False, True])
L.faire_libre(EXOS_K, k, sol, ['sur Do', 'sur Si', 'sur Si♭', 'sur La', 'sur Si♭', 'sur Si', 'sur Do'], [1, 2, 3], IMGK, parallele='reel', donnes=(0,),
              titre_ligne='basse')
page(49, k, "l'accord de Scriabine glisse", "Le premier accord (quatre notes de l'accord mystique : Do, Fa♯, Si♭, Mi) est donné, avec la mélodie. Recopie la **même disposition** sous chaque note du soprano : les quatre voix glissent ensemble, par demi-tons.")
k = 'c49-02'
D5 = [['Sol', 'Si', 'Réb', 'Fa'], ['Do', 'Mi', 'Sol'], ['Ré', 'Fa#', 'Lab', 'Do'], ['Sol', 'Si', 'Ré'], ['Sol', 'Si', 'Réb', 'Fa'], ['Do', 'Mi', 'Sol']]
jazz(EXOS_K, k, ['G7(♭5)', 'C', 'D7(♭5)', 'G', 'G7(♭5)', 'C'], D5, None, ['Sol2', 'Do3', 'Ré3', 'Sol2', 'Sol2', 'Do3'], IMGK)
page(49, k, 'dominantes à quinte abaissée', CJ + " Toutes les notes de chaque accord sont obligatoires.")
k = 'c50-01'
sop = ['Ré5', 'Mib5', 'Mi5', 'Fa5', 'Mi5', 'Mib5', 'Ré5']
bas = miroir(sop, 62)
sol = [(s, 'Fa4', 'Si3', b) for s, b in zip(sop, bas)]
L.faire_libre(EXOS_K, k, sol, [''] * 7, [3], IMGK, cibles=[[b[:-1]] for b in bas], durees=[2] * 6 + [4], quoi='au miroir du soprano', montrer=False)
page(50, k, 'le miroir chromatique', "Le soprano, l'alto et le ténor sont donnés. Écris la basse **en miroir** du soprano, autour de Ré : quand le soprano monte d'un demi-ton, la basse descend d'un demi-ton. Point de départ : Ré3.")
k = 'c50-02'
AC = ['Ré', 'Mi', 'Fa#', 'Sol#', 'La', 'Si', 'Do']
sol = [('La4', 'Fa#4', 'Do4', 'Ré3'), ('Si4', 'Sol#4', 'Ré4', 'Mi3'), ('Do5', 'Sol#4', 'Mi4', 'Fa#3'), ('Si4', 'Fa#4', 'Ré4', 'Sol#2'),
       ('La4', 'Mi4', 'Do4', 'La2'), ('Fa#4', 'Ré4', 'Do4', 'Ré3')]
L.faire_libre(EXOS_K, k, sol, [''] * 6, [1, 2], IMGK, cibles=[AC] * 6, requis=[[c[0][:-1], c[3][:-1]] for c in sol], quoi="à l'échelle acoustique",
              montrer=False)
page(50, k, "l'échelle acoustique sur Ré", "Le soprano et la basse sont donnés. Écris l'alto et le ténor avec des notes de l'**échelle acoustique** sur Ré : Ré, Mi, Fa♯, Sol♯, La, Si, Do.")
k = 'c51-01'
PE = [['Do', 'Mi', 'Sol'], ['Fa#', 'La#', 'Do#'], ['Do', 'Mi', 'Sol'], ['Fa#', 'La#', 'Do#'], ['Do', 'Mi', 'Sol']]
jazz(EXOS_K, k, ['C', 'F♯', 'C', 'F♯', 'C'], PE, None, ['Do3', 'Do#3', 'Mi3', 'Fa#2', 'Do3'], IMGK)
page(51, k, 'C et F♯, à un triton', CJ + " Les deux accords de *Petrouchka* alternent : cherche les déplacements les plus courts (chaque note de C est à un demi-ton d'une note de F♯).")
k = 'c52-01'
PR = [['Do', 'Mi', 'Sol'], ['Lab', 'Do', 'Mib'], ['Réb', 'Fa', 'Lab'], ['Sol', 'Si', 'Ré', 'Fa'], ['Do', 'Mi', 'Sol'], ['Mi', 'Sol#', 'Si'],
      ['Ré', 'Fa', 'La'], ['Sol', 'Si', 'Ré', 'Fa'], ['Do', 'Mi', 'Sol']]
jazz(EXOS_K, k, ['C', 'A♭', 'D♭', 'G7', 'C', 'E', 'Dm', 'G7', 'C'], PR, [['Do', 'Mi', 'Sol'], ['Lab', 'Do', 'Mib'], ['Réb', 'Fa', 'Lab'], ['Sol', 'Si', 'Fa'],
     ['Do', 'Mi', 'Sol'], ['Mi', 'Sol#', 'Si'], ['Ré', 'Fa', 'La'], ['Sol', 'Si', 'Fa'], ['Do', 'Mi', 'Sol']],
     ['Do3', 'Lab2', 'Réb3', 'Sol2', 'Do3', 'Mi3', 'Ré3', 'Sol2', 'Do3'], IMGK, durees=[2] * 8 + [4])
page(52, k, 'des accords « à côté »', CJ)
k = 'c53-01'
O7b = [['Réb', 'Fa', 'Lab', 'Si'], ['Mi', 'Sol#', 'Si', 'Ré'], ['Sol', 'Si', 'Ré', 'Fa'], ['Sib', 'Ré', 'Fa', 'Lab'], ['Réb', 'Fa', 'Lab', 'Si']]
jazz(EXOS_K, k, ['D♭7', 'E7', 'G7', 'B♭7', 'D♭7'], O7b, [c[1:] for c in O7b], ['Réb3', 'Mi3', 'Sol2', 'Sib2', 'Réb3'], IMGK)
page(53, k, 'les quatre 7e de dominante du mode 2', CJ + " Les quatre accords appartiennent au même mode 2 (Ré♭, Ré, Mi, Fa, Sol, La♭, Si♭, Si).")
k = 'c53-02'
SQ = [['Do', 'Mi', 'Fa#', 'La'], ['Mib', 'Sol', 'La', 'Do'], ['Fa#', 'La#', 'Do', 'Ré#'], ['La', 'Do#', 'Ré#', 'Fa#'], ['Do', 'Mi', 'Fa#', 'La']]
jazz(EXOS_K, k, ['C6(♯4)', 'E♭6(♯4)', 'F♯6(♯4)', 'A6(♯4)', 'C6(♯4)'], SQ, [c[1:] for c in SQ], ['Do3', 'Mib3', 'Fa#2', 'La2', 'Do3'], IMGK)
page(53, k, "l'accord de Messiaen", CJ + " Chaque accord : la tierce, la quarte augmentée et la sixte, au-dessus de la basse.")
k = 'c54-01'
PI = [['Sib', 'Ré', 'Fa'], ['Sol', 'Si', 'Ré'], ['Ré', 'Fa', 'La'], ['Si', 'Ré', 'Fa#'], ['Sol', 'Sib', 'Ré'], ['Ré', 'Fa#', 'La']]
jazz(EXOS_K, k, ['B♭', 'G', 'Dm', 'Bm', 'Gm', 'D'], PI, None, ['Sib2', 'Sol2', 'Fa2', 'Si2', 'Sol2', 'Ré3'], IMGK, voix=(1, 2), sop=['Ré5'] * 6)
page(54, k, 'une note pivot', "Le soprano tient **Ré** du début à la fin ; la basse et les accords sont donnés. Écris l'alto et le ténor : les couleurs changent autour de la note qui reste.")

print('partie 9 :', len(EXOS), 'exercices du cours,', len(EXOS_K), 'exercices du cahier')
json.dump(EXOS, open(os.path.join(COURS, 'exercices-partie9.json'), 'w'), ensure_ascii=False)
json.dump(EXOS_K, open(os.path.join(CAHIER, 'exercices-cahier9.json'), 'w'), ensure_ascii=False)
json.dump({k: v for k, v in SONS.items() if k.startswith('h')}, open(os.path.join(COURS, 'audio', 'sons-partie9.json'), 'w'), indent=0)
json.dump({k: v for k, v in SONS.items() if k.startswith('c')}, open(os.path.join(CAHIER, 'audio', 'sons-cahier9.json'), 'w'), indent=0)
json.dump({k: [v['solution'], v['degres']] for k, v in list(EXOS.items()) + list(EXOS_K.items())}, open('/tmp/p9.json', 'w'), ensure_ascii=False)

# ======================================================================== pages du cahier
TITRES = {49: ('49-scriabine', "Scriabine : l'accord mystique", '49-scriabine.md'),
          50: ('50-bartok', 'Bartók : miroirs et échelles', '50-bartok-et-les-quatuors.md'),
          51: ('51-stravinsky', 'Stravinsky : deux accords à un triton', '51-stravinsky.md'),
          52: ('52-prokofiev', 'Prokofiev : les accords « à côté »', '52-prokofiev.md'),
          53: ('53-messiaen', 'Messiaen : le mode 2 et son accord', '53-messiaen.md'),
          54: ('54-dutilleux', 'Dutilleux : la note pivot', '54-dutilleux.md')}
CH9 = tuple(range(49, 55))
ordre = [(46, '46-vers-le-jazz', P8.TITRES[46][1])] + [(c, TITRES[c][0], TITRES[c][1]) for c in CH9]
P8.ecrire_pages(PAGES, TITRES, CH9, ordre)
P8.lier_precedent('46-vers-le-jazz.md', '49-scriabine', TITRES[49][1])
P8.sommaire(PAGES, TITRES, CH9, '46-vers', 'écriture libre')
readme = os.path.join(CAHIER, 'README.md')
txt = open(readme).read()
n9 = sum(len(v) for v in PAGES.values())
m = re.search(r'\*\*(\d+) exercices\*\*', txt)
txt = txt.replace(m.group(0), f'**{int(m.group(1)) + n9} exercices**')
txt = re.sub(r' et (\d+) sur Fauré, Debussy, Ravel et le jazz\. Tous les corrigés',
             lambda mm: f', {mm.group(1)} sur Fauré, Debussy, Ravel et le jazz, et {n9} sur le XXe siècle. Tous les corrigés', txt)
open(readme, 'w').write(txt)
print('pages du cahier écrites')
