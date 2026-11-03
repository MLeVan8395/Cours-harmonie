"""Usage : python3 outils/build_partie8.py

Partie 8 (vers l'harmonie moderne : Fauré, Debussy, Ravel, le pont vers le jazz) : figures des chapitres 43 à 48,
exercices du cours et du cahier (chapitres 43 à 46). (Reconstruit aussi les parties 4 à 7.)"""
import json, os, re
from graveur import Figure, satb, RED, GREEN, BLUE, ORANGE, MUTED, SONS, N, midi
import build_partie7 as P7
import libre as L

ICI = os.path.dirname(os.path.abspath(__file__))
COURS = os.path.join(ICI, '..', 'cours')
CAHIER = os.path.join(ICI, '..', 'cahier')
IMG, IMGK = os.path.join(COURS, 'images'), os.path.join(CAHIER, 'images')
SONS.clear()


def save(fig, name, dossier=IMG):
    fig.save(os.path.join(dossier, name + '.png'))


def lab2(t0, items, dur=4):
    """étiquettes sur deux rangées : [(accord, degré)…]"""
    out = []
    for k, (a, d) in enumerate(items):
        if a:
            out.append((t0 + k * dur, a, 0, BLUE))
        if d:
            out.append((t0 + k * dur, d, 1, MUTED))
    return out


def gamme(notes, dur=1, coul=None):
    return [(n, dur, {'color': coul[k]} if coul and coul.get(k) else {}) for k, n in enumerate(notes)]


def portee_simple(evs, nom, unit=16, boxes=None, labels=None, rows=None, top_texts=None, clef='treble', dossier=IMG):
    save(Figure([{'clef': clef}], [{'staff': 0, 'stem': None, 'events': evs}], unit=unit, bars=False, boxes=boxes,
                labels=labels, rows=rows, top_texts=top_texts), nom, dossier)


def empile(accords, nom, symb, unit=26, rows=('accord',), dossier=IMG, coul=None):
    """accords plaqués sur la grande portée (jusqu'à 7 notes) ; coul : {(i, note): couleur}"""
    n = max(len(a) for a in accords)
    voices = []
    for j in range(n):
        for st in (0, 1):
            ev, util = [], False
            for i, a in enumerate(accords):
                x = a[j] if j < len(a) else None
                bon = x and ((midi(N(x)) >= 60) == (st == 0))
                o = {} if bon else {'hide': True}
                if bon and coul and (i, x) in coul:
                    o['color'] = coul[(i, x)]
                ev.append((x if bon else None, 4, o))
                util |= bool(bon)
            if util:
                voices.append({'staff': st, 'stem': None, 'events': ev})
    save(Figure([{'clef': 'treble'}, {'clef': 'bass'}], voices, brace=(0, 1), gap=104, unit=unit,
                labels=[(i * 4, s, 0, BLUE) for i, s in enumerate(symb)], rows=list(rows)), nom, dossier)


def rouges(ch):
    """notes qui changent d'un accord au suivant, en rouge"""
    col = {}
    for i in range(1, len(ch)):
        for v in range(4):
            if ch[i][v] != ch[i - 1][v]:
                col[(v, i)] = RED
    return col


# ======================================================================== chapitre 43 : Fauré
dor = [('Fa4', 'Ré4', 'La3', 'Ré3'), ('Sol4', 'Ré4', 'Si3', 'Sol2'), ('Fa4', 'Ré4', 'La3', 'Ré3')]
eol = [('Do5', 'Mi4', 'La3', 'La2'), ('Ré5', 'Fa4', 'La3', 'Ré3'), ('Si4', 'Mi4', 'Sol3', 'Mi3'), ('Do5', 'Mi4', 'La3', 'La2')]
mix = [('Sol4', 'Mi4', 'Do4', 'Do3'), ('Sib4', 'Fa4', 'Ré4', 'Sib2'), ('Sol4', 'Mi4', 'Do4', 'Do3')]
ch = [c + (4,) for c in dor + eol + mix]
col = {(2, 1): RED, (2, 5): RED, (0, 8): RED, (3, 8): RED}
lab = lab2(0, [('Dm', 'I'), ('G', 'IV'), ('Dm', 'I'), ('Am', 'I'), ('Dm', 'IV'), ('Em', 'V'), ('Am', 'I'), ('C', 'I'), ('B♭', 'VII♭'), ('C', 'I')])
save(satb(ch, unit=20, colors=col, labels=lab, rows=['accord', 'degré'],
          boxes=[(0, 12, BLUE, 'ré dorien'), (12, 28, GREEN, 'la éolien'), (28, 40, ORANGE, 'Do mixolydien')]), 'h43-modal')
HEXA = [('Sol4', 'Mi4', 'Do4', 'Do3'), ('Sol4', 'Mib4', 'Do4', 'Do3'), ('Lab4', 'Mib4', 'Do4', 'Lab2'), ('Sol#4', 'Ré#4', 'Si3', 'Sol#2'),
        ('Sol#4', 'Mi4', 'Si3', 'Mi3'), ('Sol4', 'Mi4', 'Si3', 'Mi3'), ('Sol4', 'Mi4', 'Do4', 'Do3')]
col = rouges(HEXA)
for i in range(1, 7):
    col.pop((3, i), None)
col.pop((0, 3), None); col.pop((1, 3), None); col.pop((2, 3), None)   # enharmonie : mêmes touches
col[(2, 3)] = RED
save(satb([c + (4,) for c in HEXA], unit=22, colors=col, labels=[(i * 4, s, 0, BLUE) for i, s in enumerate(['C', 'Cm', 'A♭', 'G♯m', 'E', 'Em', 'C'])],
          rows=['accord']), 'h43-glissements')
# la « modulation éclair » : un accord lointain, puis retour
ECL = [('Mi5', 'Do5', 'Sol4', 'Do3', 4), ('Mib5', 'Do5', 'Lab4', 'Lab2', 4), ('Ré5', 'Sib4', 'Fa4', 'Sib2', 4), ('Ré5', 'Si4', 'Fa4', 'Sol2', 4),
       ('Do5', 'Sol4', 'Mi4', 'Do3', 4)]
save(satb(ECL, unit=22, colors={(v, i): RED for i in (1, 2) for v in range(4) if 'b' in ECL[i][v][2:]}, labels=lab2(0, [('C', 'I'), ('A♭', 'VI♭'), ('B♭', 'VII♭'), ('G7', 'V7'), ('C', 'I')]),
          rows=['accord', 'degré'], boxes=[(4, 12, ORANGE, 'emprunts')]), 'h43-eclair')

# ======================================================================== chapitre 44 : Debussy
tons = ['Do4', 'Ré4', 'Mi4', 'Fa#4', 'Sol#4', 'La#4', 'Do5', 'Réb4', 'Mib4', 'Fa4', 'Sol4', 'La4', 'Si4', 'Réb5']
portee_simple(gamme(tons), 'h44-tons', unit=24, boxes=[(0, 7, BLUE, 'sur Do'), (7, 14, GREEN, 'sur Ré♭')])
penta = ['Do4', 'Ré4', 'Mi4', 'Sol4', 'La4', 'Do5', 'Solb4', 'Lab4', 'Sib4', 'Réb5', 'Mib5', 'Solb5']
portee_simple(gamme(penta), 'h44-penta', unit=24, boxes=[(0, 6, BLUE, 'sur Do'), (6, 12, GREEN, 'les touches noires')])
modes = ['Ré4', 'Mi4', 'Fa4', 'Sol4', 'La4', 'Si4', 'Do5', 'Ré5', 'Mi4', 'Fa4', 'Sol4', 'La4', 'Si4', 'Do5', 'Ré5', 'Mi5',
         'Fa4', 'Sol4', 'La4', 'Si4', 'Do5', 'Ré5', 'Mi5', 'Fa5', 'Sol4', 'La4', 'Si4', 'Do5', 'Ré5', 'Mi5', 'Fa5', 'Sol5']
cm = {5: RED, 9: RED, 19: RED, 30: RED}
portee_simple(gamme(modes, coul=cm), 'h44-modes', unit=17,
              boxes=[(0, 8, BLUE, 'Ré dorien'), (8, 16, GREEN, 'Mi phrygien'), (16, 24, ORANGE, 'Fa lydien'), (24, 32, RED, 'Sol mixolydien')])
PL = L.planing_reel(('Ré5', 'Mi4', 'Sib3', 'Do3'), ['Ré5', 'Do5', 'Sib4', 'La4', 'Sol4'], bemols=[True] * 5)
sy = ['C9', 'B♭9', 'A♭9', 'G9', 'F9']
save(satb([c + (4,) for c in PL], unit=22, labels=[(i * 4, s, 0, BLUE) for i, s in enumerate(sy)], rows=['accord']), 'h44-paralleles-reels')
PD = L.planing_diato(('Sol4', 'Mi4', 'Do4', 'Do3'), ['Sol4', 'La4', 'Si4', 'Do5', 'Si4', 'La4', 'Sol4'], {})
assert not L.controle(PD, [[L.sans_oct(x) for x in c] for c in PD], None, [0, 1, 2, 3], 'diato')
save(satb([c + (2,) for c in PD], unit=24, time=(4, 4), labels=[(i * 2, s, 0, BLUE) for i, s in enumerate(['C', 'Dm', 'Em', 'F', 'Em', 'Dm', 'C'])],
          rows=['accord'], lines=[((2, k), (2, k + 1), RED) for k in range(6)]), 'h44-paralleles-diatoniques')
VO = [('Ré5', 'Sib4', 'Ré4', 'Sib2'), ('Do5', 'Lab4', 'Ré4', 'Sib2'), ('Sib4', 'Solb4', 'Ré4', 'Sib2'), ('Lab4', 'Mi4', 'Ré4', 'Sib2'),
      ('Sib4', 'Solb4', 'Ré4', 'Sib2'), ('Do5', 'Lab4', 'Ré4', 'Sib2'), ('Ré5', 'Sib4', 'Ré4', 'Sib2')]
assert all(midi(N(x)) % 2 == 0 for c in VO for x in c)   # tout dans la gamme par tons de Sib (= Do)
save(satb([c + (2,) for c in VO[:-1]] + [VO[-1] + (4,)], unit=24, time=(4, 4), colors={(3, i): GREEN for i in range(7)}), 'h44-tons-pedale')
AJ = [('La4', 'Mi4', 'Sol3', 'Do3', 4), ('Ré5', 'La4', 'Mi4', 'Do3', 4), ('Sol5', 'Ré5', 'La4', 'Do3', 4)]
save(satb(AJ, unit=26, colors={(0, 0): RED, (0, 1): RED, (1, 1): RED, (1, 2): RED, (0, 2): MUTED},
          labels=[(0, 'C6', 0, BLUE), (4, 'C6/9', 0, BLUE), (8, 'C6/9 (en quartes)', 0, BLUE)], rows=['accord']), 'h44-sixte-ajoutee')

# ======================================================================== chapitre 45 : Ravel
pile = ['Sol2', 'Si2', 'Ré3', 'Fa3', 'La3', 'Do4', 'Mi4']
acc = [pile[:4], pile[:5], ['Sol2', 'Ré3', 'Fa3', 'La3', 'Do4'], ['Sol2', 'Si2', 'Fa3', 'La3', 'Mi4']]
empile(acc, 'h45-superposition', ['G7', 'G9', 'G11 (sans tierce)', 'G13'], coul={(1, 'La3'): RED, (2, 'Do4'): RED, (3, 'Mi4'): RED})
R13 = [('Mi5', 'Do5', 'Fa4', 'Ré3', 4), ('Mi5', 'Si4', 'Fa4', 'Sol2', 4), ('Ré5', 'Si4', 'Mi4', 'Do3', 4)]
save(satb(R13, unit=22, colors={(0, 0): RED, (0, 1): RED, (0, 2): RED}, labels=lab2(0, [('Dm9', 'II'), ('G13', 'V'), ('Cmaj9', 'I')])
          , rows=['accord', 'degré']), 'h45-neuvieme-treizieme')
APP = [('Mi5', 'La4', 'Do4', 'Fa3', 4), ('Ré5', 'La4', 'Fa4', 'Ré3', 4), ('Ré5', 'Fa4', 'Sib3', 'Sib2', 4), ('Do5', 'Mi4', 'Sib3', 'Do3', 4),
       ('Mi5', 'La4', 'Do4', 'Fa2', 4)]
save(satb(APP, unit=22, key=-1, colors={(0, 0): RED, (0, 4): RED}, labels=lab2(0, [('Fmaj7', 'I'), ('Dm', 'VI'), ('B♭', 'IV'), ('C7', 'V7'), ('Fmaj7', 'I')]),
          rows=['accord', 'degré']), 'h45-septieme-majeure')
# écriture pour quatuor, « dans l'esprit » du Quatuor en fa (exemple original)
v1 = [('Mi5', 2), ('Sol5', 1), ('La5', 1), ('Mi5', 2), ('Ré5', 2), ('Ré5', 2), ('Do5', 1), ('Sib4', 1), ('Do5', 2), ('Ré5', 2), ('Mi5', 4)]
v2 = [('La4', 4), ('Fa4', 4), ('Fa4', 4), ('Sib4', 4), ('Sol4', 4)]
al = [('Do4', 4), ('La3', 4), ('Ré4', 4), ('Mi4', 4), ('La3', 4)]
vc = [('Fa2', 4), ('Ré3', 4), ('Sib2', 4), ('Do3', 4), ('Fa2', 4)]
vv = [{'staff': k, 'stem': None, 'events': [(n, d, {'color': RED} if (k == 0 and n in ('Mi5',) ) else {}) for n, d in p]} for k, p in enumerate((v1, v2, al, vc))]
save(Figure(P7.P5.QUAT, vv, key=-1, gap=96, unit=20, time=(4, 4), labels=lab2(0, [('Fmaj7', ''), ('Dm9', ''), ('B♭', ''), ('C9', ''), ('Fmaj9', '')]),
            rows=['accord']), 'h45-quatuor')

# ======================================================================== chapitre 46 : vers le jazz
empile([['Do4', 'Mi4', 'Sol4', 'Si4'], ['Do4', 'Mi4', 'Sol4', 'Sib4'], ['Do4', 'Mib4', 'Sol4', 'Sib4'], ['Do4', 'Mib4', 'Solb4', 'Sib4'],
        ['Do4', 'Mib4', 'Solb4', 'Sibb4' if False else 'La4']], 'h46-septiemes', ['Cmaj7', 'C7', 'Cm7', 'Cm7♭5 (Cø)', 'C°7'], unit=24)
IIVI = [('Do5', 'Fa4', 'La3', 'Ré3', 4), ('Si4', 'Fa4', 'Sol3', 'Sol2', 4), ('Si4', 'Mi4', 'Sol3', 'Do3', 4)]
save(satb(IIVI, unit=24, colors={(0, 0): RED, (0, 1): RED, (1, 0): ORANGE, (1, 1): ORANGE, (1, 2): ORANGE, (0, 2): RED},
          lines=[((0, 0), (0, 1), RED), ((1, 1), (1, 2), ORANGE)], labels=lab2(0, [('Dm7', 'II7'), ('G7', 'V7'), ('Cmaj7', 'I')]),
          rows=['accord', 'degré']), 'h46-ii-v-i')
save(satb(R13, unit=24, colors={(v, i): BLUE for v in range(3) for i in range(3)}, labels=lab2(0, [('Dm9', 'II'), ('G13', 'V'), ('Cmaj9', 'I')]),
          rows=['accord', 'degré']), 'h46-sans-fondamentale')
TRI = [('Do5', 'Fa4', 'La3', 'Ré3', 4), ('Si4', 'Fa4', 'Lab3', 'Réb3', 4), ('Si4', 'Mi4', 'Sol3', 'Do3', 4)]
save(satb(TRI, unit=24, colors={(3, 1): RED, (2, 1): RED, (0, 1): ORANGE, (1, 1): ORANGE}, labels=lab2(0, [('Dm7', 'II7'), ('D♭7', 'subV7'), ('Cmaj7', 'I')]),
          rows=['accord', 'degré']), 'h46-triton')
empile([['Mi3', 'La3', 'Ré4', 'Sol4', 'Si4'], ['Ré3', 'Sol3', 'Do4', 'Fa4', 'La4']], 'h46-quartes', ['Dm11', 'Cm11'], unit=34)

# ======================================================================== exercices du cours (chapitre 47)
EXOS, EXOS_K = {}, {}
an = [('Ré5', 'Sib4', 'Mi4', 'Do3'), ('La4', 'Mi4', 'Sol3', 'Do3'), ('Sol#4', 'Ré4', 'Fa#3', 'Do3'), ('Mi5', 'La4', 'Do4', 'Fa2')]
tt = [(i * 4, x, MUTED) for i, x in enumerate(['a)', 'b)', 'c)', 'd)'])]
save(satb(an, unit=24, top_texts=tt), 'h47-ex1')
save(satb(an, unit=24, top_texts=tt, labels=[(0, 'C9', 0, BLUE), (4, 'C6', 0, BLUE), (8, 'par tons', 0, BLUE), (12, 'Fmaj7', 0, BLUE)], rows=['accord']), 'h48-c1')

sol = L.planing_reel(('Ré5', 'Mi4', 'Sib3', 'Do3'), ['Ré5', 'Do5', 'Ré5', 'Mi5', 'Ré5'], bemols=[True, True, True, False, True])
L.faire_libre(EXOS, 'h47-ex2', sol, ['C9', 'B♭9', 'C9', 'D9', 'C9'], [1, 2, 3], IMG, parallele='reel', donnes=(0,))
sol = L.planing_diato(('Ré5', 'La4', 'Fa4', 'Ré3'), ['Ré5', 'Do5', 'Sib4', 'La4', 'Sib4', 'Do5', 'Ré5'], {6: -1})
L.faire_libre(EXOS, 'h47-ex3', sol, ['Dm', 'C', 'B♭', 'Am', 'B♭', 'C', 'Dm'], [1, 2, 3], IMG, parallele='diato', donnes=(0,), armure=-1, tonique='Fa')


def jazz(dico, nom, symb, notes, req, basse, dossier, durees=None, armure=0, tonique='Do', voix=(0, 1, 2), sop=None, quoi=None):
    fixe = [(sop[i] if sop else None, None, None, b) for i, b in enumerate(basse)]
    sol = L.voicer(notes, fixe, req)
    return L.faire_libre(dico, nom, sol, symb, list(voix), dossier, cibles=notes, requis=req, durees=durees, armure=armure, tonique=tonique, quoi=quoi)


jazz(EXOS, 'h47-ex4', ['Dm9', 'G13', 'Cmaj9', 'Am9', 'Dm9', 'G13', 'Cmaj9'],
     [['Ré', 'Fa', 'La', 'Do', 'Mi'], ['Sol', 'Si', 'Ré', 'Fa', 'La', 'Mi'], ['Do', 'Mi', 'Sol', 'Si', 'Ré'], ['La', 'Do', 'Mi', 'Sol', 'Si'],
      ['Ré', 'Fa', 'La', 'Do', 'Mi'], ['Sol', 'Si', 'Ré', 'Fa', 'La', 'Mi'], ['Do', 'Mi', 'Sol', 'Si', 'Ré']],
     [['Fa', 'Do', 'Mi'], ['Si', 'Fa', 'Mi'], ['Mi', 'Si', 'Ré'], ['Do', 'Sol', 'Si'], ['Fa', 'Do', 'Mi'], ['Si', 'Fa', 'Mi'], ['Mi', 'Si', 'Ré']],
     ['Ré3', 'Sol2', 'Do3', 'La2', 'Ré3', 'Sol2', 'Do3'], IMG)
jazz(EXOS, 'h47-ex5', ['Gm7', 'G♭7', 'Fmaj7', 'Dm7', 'Gm7', 'G♭7', 'Fmaj7'],
     [['Sol', 'Sib', 'Ré', 'Fa'], ['Solb', 'Sib', 'Réb', 'Mi'], ['Fa', 'La', 'Do', 'Mi'], ['Ré', 'Fa', 'La', 'Do'], ['Sol', 'Sib', 'Ré', 'Fa'],
      ['Solb', 'Sib', 'Réb', 'Mi'], ['Fa', 'La', 'Do', 'Mi']],
     [['Sib', 'Fa', 'Ré'], ['Sib', 'Mi', 'Réb'], ['La', 'Mi', 'Do'], ['Fa', 'Do', 'La'], ['Sib', 'Fa', 'Ré'], ['Sib', 'Mi', 'Réb'], ['La', 'Mi', 'Do']],
     ['Sol2', 'Solb2', 'Fa2', 'Ré3', 'Sol2', 'Solb2', 'Fa2'], IMG, armure=-1, tonique='Fa')
for k in range(2, 6):
    os.replace(os.path.join(IMG, f'h47-ex{k}-c.png'), os.path.join(IMG, f'h48-c{k}.png'))
    SONS[f'h48-c{k}'] = SONS.pop(f'h47-ex{k}-c')

# ======================================================================== cahier : chapitres 43 à 46
PAGES = {43: [], 44: [], 45: [], 46: []}


def page(chap, nom, titre, consigne):
    PAGES[chap].append((nom, titre, consigne))


CJ = "La basse et les accords sont donnés. Écris le soprano, l'alto et le ténor : chaque accord doit contenir les notes indiquées entre parenthèses. Pas de règle d'enchaînement ici, mais cherche le chemin le plus court pour chaque voix."
k = 'c43-01'
jazz(EXOS_K, k, ['C', 'Cm', 'A♭', 'G♯m', 'E', 'Em', 'C'],
     [['Do', 'Mi', 'Sol'], ['Do', 'Mib', 'Sol'], ['Lab', 'Do', 'Mib'], ['Sol#', 'Si', 'Ré#'], ['Mi', 'Sol#', 'Si'], ['Mi', 'Sol', 'Si'], ['Do', 'Mi', 'Sol']],
     None, ['Do3', 'Do3', 'Lab2', 'Sol#2', 'Mi3', 'Mi3', 'Do3'], IMGK)
page(43, k, 'les glissements (une voix bouge d\'un demi-ton)', "La basse et les accords sont donnés. Écris le soprano, l'alto et le ténor avec les trois notes de chaque accord. Le but : qu'à chaque changement, **une seule voix** bouge, d'un demi-ton (les autres restent ou changent seulement de nom, comme La♭ = Sol♯).")
k = 'c43-02'
jazz(EXOS_K, k, ['Gm', 'C', 'Gm', 'F', 'E♭', 'F', 'Gm'],
     [['Sol', 'Sib', 'Ré'], ['Do', 'Mi', 'Sol'], ['Sol', 'Sib', 'Ré'], ['Fa', 'La', 'Do'], ['Mib', 'Sol', 'Sib'], ['Fa', 'La', 'Do'], ['Sol', 'Sib', 'Ré']],
     None, ['Sol2', 'Do3', 'Sib2', 'La2', 'Sol2', 'Fa2', 'Sol2'], IMGK, armure=-2, tonique='Sol')
page(43, k, 'sol dorien (Mi naturel)', CJ)

k = 'c44-01'
sol = L.planing_reel(('Mi5', 'Sib4', 'Sol4', 'Do4'), ['Mi5', 'Ré5', 'Do5', 'Ré5', 'Do5', 'Ré5', 'Mi5'], bemols=[True] * 7)
sol = [(s, a, t, L.transpose_reel(b, -12, N(b)['a'] == -1)) for s, a, t, b in sol]
L.faire_libre(EXOS_K, k, sol, ['C7', 'B♭7', 'A♭7', 'B♭7', 'A♭7', 'B♭7', 'C7'], [1, 2, 3], IMGK, parallele='reel', donnes=(0,))
page(44, k, 'accords de 7e parallèles', "Le premier accord est donné, ainsi que la mélodie. Recopie la **même disposition** sous chaque note du soprano : chaque voix bouge exactement du même intervalle (accords parallèles « réels », à la Debussy).")
k = 'c44-02'
sol = L.planing_diato(('Do5', 'La4', 'Mi4', 'La2'), ['Do5', 'Ré5', 'Mi5', 'Ré5', 'Do5', 'Si4', 'La4', 'Si4', 'Do5'], {})
L.faire_libre(EXOS_K, k, sol, ['Am', 'B°', 'C', 'B°', 'Am', 'G', 'F', 'G', 'Am'], [1, 2, 3], IMGK, parallele='diato', donnes=(0,), durees=[2] * 8 + [4],
              tonique='La')
page(44, k, 'accords parallèles dans la gamme (la éolien)', "Le premier accord est donné, ainsi que la mélodie. Les voix suivent le soprano **dans la gamme** (sans altération) : même nombre de degrés entre les voix, même si les tierces deviennent tantôt majeures, tantôt mineures.")
k = 'c44-03'
WT = ['Do', 'Ré', 'Mi', 'Fa#', 'Sol#', 'La#']
WT2 = ['Do', 'Ré', 'Mi', 'Solb', 'Lab', 'Sib']
sol = [('Mi5', 'Do5', 'Fa#4', 'Ré3'), ('Ré5', 'La#4', 'Mi4', 'Do3'), ('Do5', 'Sol#4', 'Ré4', 'La#2'), ('Ré5', 'La#4', 'Mi4', 'Do3'),
       ('Mi5', 'Do5', 'Fa#4', 'Ré3'), ('Fa#5', 'Ré5', 'Do4', 'Mi3')]
L.faire_libre(EXOS_K, k, sol, ['', '', '', '', '', ''], [1, 2], IMGK, cibles=[WT] * 6, requis=[[c[0][:-1], c[3][:-1]] for c in sol],
              quoi='à la gamme par tons', montrer=False)
page(44, k, 'la gamme par tons', "Le soprano et la basse sont donnés. Écris l'alto et le ténor avec des notes de la **gamme par tons** sur Do (Do, Ré, Mi, Fa♯, Sol♯, La♯). Toutes les combinaisons sonnent « en suspens » : il n'y a plus de tonique.")

k = 'c45-01'
jazz(EXOS_K, k, ['Fmaj9', 'Dm9', 'Gm9', 'C13', 'Fmaj9'],
     [['Fa', 'La', 'Do', 'Mi', 'Sol'], ['Ré', 'Fa', 'La', 'Do', 'Mi'], ['Sol', 'Sib', 'Ré', 'Fa', 'La'], ['Do', 'Mi', 'Sol', 'Sib', 'Ré', 'La'],
      ['Fa', 'La', 'Do', 'Mi', 'Sol']],
     [['La', 'Mi', 'Sol'], ['Fa', 'Do', 'Mi'], ['Sib', 'Fa', 'La'], ['Mi', 'Sib', 'La'], ['La', 'Mi', 'Sol']], ['Fa2', 'Ré3', 'Sol2', 'Do3', 'Fa2'], IMGK,
     armure=-1, tonique='Fa')
page(45, k, '9e et 13e', CJ)
k = 'c45-02'
jazz(EXOS_K, k, ['Dmaj7', 'Bm9', 'Em9', 'A13', 'Dmaj7'],
     [['Ré', 'Fa#', 'La', 'Do#'], ['Si', 'Ré', 'Fa#', 'La', 'Do#'], ['Mi', 'Sol', 'Si', 'Ré', 'Fa#'], ['La', 'Do#', 'Mi', 'Sol', 'Si', 'Fa#'],
      ['Ré', 'Fa#', 'La', 'Do#']],
     [['Fa#', 'La', 'Do#'], ['Ré', 'La', 'Do#'], ['Sol', 'Ré', 'Fa#'], ['Do#', 'Sol', 'Fa#'], ['Fa#', 'La', 'Do#']], ['Ré3', 'Si2', 'Mi3', 'La2', 'Ré3'], IMGK,
     armure=2, tonique='Ré')
page(45, k, 'septièmes majeures et 9e', CJ)

k = 'c46-01'
jazz(EXOS_K, k, ['Gm7', 'C7', 'Fmaj7', 'Dm7', 'Gm7', 'C7', 'Fmaj7'],
     [['Sol', 'Sib', 'Ré', 'Fa'], ['Do', 'Mi', 'Sol', 'Sib'], ['Fa', 'La', 'Do', 'Mi'], ['Ré', 'Fa', 'La', 'Do'], ['Sol', 'Sib', 'Ré', 'Fa'],
      ['Do', 'Mi', 'Sol', 'Sib'], ['Fa', 'La', 'Do', 'Mi']],
     [['Sib', 'Fa'], ['Mi', 'Sib'], ['La', 'Mi'], ['Fa', 'Do'], ['Sib', 'Fa'], ['Mi', 'Sib'], ['La', 'Mi']], ['Sol2', 'Do3', 'Fa2', 'Ré3', 'Sol2', 'Do3', 'Fa2'],
     IMGK, armure=-1, tonique='Fa')
page(46, k, 'II-V-I, les notes guides', "La basse et les accords sont donnés. Écris le soprano, l'alto et le ténor. Dans chaque accord, la **tierce** et la **septième** (les notes guides) sont obligatoires ; la troisième note est libre (fondamentale ou quinte).")
k = 'c46-02'
jazz(EXOS_K, k, ['Cm7', 'B7', 'B♭maj7', 'Gm7', 'Cm7', 'B7', 'B♭maj7'],
     [['Do', 'Mib', 'Sol', 'Sib'], ['Si', 'Ré#', 'Fa#', 'La'], ['Sib', 'Ré', 'Fa', 'La'], ['Sol', 'Sib', 'Ré', 'Fa'], ['Do', 'Mib', 'Sol', 'Sib'],
      ['Si', 'Ré#', 'Fa#', 'La'], ['Sib', 'Ré', 'Fa', 'La']],
     [['Mib', 'Sib', 'Sol'], ['Ré#', 'La', 'Fa#'], ['Ré', 'La', 'Fa'], ['Sib', 'Fa', 'Ré'], ['Mib', 'Sib', 'Sol'], ['Ré#', 'La', 'Fa#'], ['Ré', 'La', 'Fa']],
     ['Do3', 'Si2', 'Sib2', 'Sol2', 'Do3', 'Si2', 'Sib2'], IMGK, armure=-2, tonique='Sib')
page(46, k, 'la substitution tritonique', "La basse et les accords sont donnés : le V7 (F7) est remplacé par B7, à un triton. Écris le soprano, l'alto et le ténor sans la fondamentale : **tierce, quinte et septième**. Compare les notes guides de B7 (Ré♯ = Mi♭, La) avec celles de F7 (La, Mi♭).")
k = 'c46-03'
jazz(EXOS_K, k, ['Eø', 'A7(♭9)', 'Dm6', 'Eø', 'A7(♭9)', 'Dm6'],
     [['Mi', 'Sol', 'Sib', 'Ré'], ['La', 'Do#', 'Mi', 'Sol', 'Sib'], ['Ré', 'Fa', 'La', 'Si'], ['Mi', 'Sol', 'Sib', 'Ré'], ['La', 'Do#', 'Mi', 'Sol', 'Sib'],
      ['Ré', 'Fa', 'La', 'Si']],
     [['Sol', 'Sib', 'Ré'], ['Do#', 'Sol', 'Sib'], ['Fa', 'Si', 'La'], ['Sol', 'Sib', 'Ré'], ['Do#', 'Sol', 'Sib'], ['Fa', 'Si', 'La']],
     ['Mi3', 'La2', 'Ré3', 'Mi3', 'La2', 'Ré3'], IMGK, armure=-1, tonique='Ré')
page(46, k, 'II-V-I mineur', CJ)

print('partie 8 :', len(EXOS), 'exercices du cours,', len(EXOS_K), 'exercices du cahier')
json.dump(EXOS, open(os.path.join(COURS, 'exercices-partie8.json'), 'w'), ensure_ascii=False)
json.dump(EXOS_K, open(os.path.join(CAHIER, 'exercices-cahier8.json'), 'w'), ensure_ascii=False)
json.dump({k: v for k, v in SONS.items() if k.startswith('h')}, open(os.path.join(COURS, 'audio', 'sons-partie8.json'), 'w'), indent=0)
json.dump({k: v for k, v in SONS.items() if k.startswith('c')}, open(os.path.join(CAHIER, 'audio', 'sons-cahier8.json'), 'w'), indent=0)
json.dump({k: [v['solution'], v['degres']] for k, v in list(EXOS.items()) + list(EXOS_K.items())}, open('/tmp/p8.json', 'w'), ensure_ascii=False)

# ======================================================================== pages du cahier
TITRES = {43: ('43-faure', 'Fauré : modes et glissements', '43-faure-couleurs-modales.md'),
          44: ('44-debussy', 'Debussy : accords parallèles, gamme par tons', '44-debussy.md'),
          45: ('45-ravel', 'Ravel : 7e, 9e et 13e', '45-ravel.md'),
          46: ('46-vers-le-jazz', 'Vers le jazz : II-V-I et substitutions', '46-vers-le-jazz.md')}
CH8 = (43, 44, 45, 46)
ordre = [(39, '39-majeur-et-mineur', 'Franck et Mahler : majeur et mineur')] + [(c, TITRES[c][0], TITRES[c][1]) for c in CH8]


def ecrire_pages(PAGES, TITRES, chaps, ordre, suivant=None):
    for k, chap in enumerate(chaps):
        fic, titre, cours_md = TITRES[chap]
        prev = ordre[k]
        nav = f"[← {prev[2]}]({prev[1]}.md) · [Sommaire du cahier](README.md)"
        if k < len(chaps) - 1:
            nx = ordre[k + 2]
            nav += f" · [{nx[2]} →]({nx[1]}.md)"
        elif suivant:
            nav += f" · [{suivant[1]} →]({suivant[0]}.md)"
        Lg = [nav, '', f'## {titre}', '', f"Ces exercices accompagnent le [chapitre {chap}](../cours/{cours_md}) du cours.", '',
              "Dans la version web (`cahier.html`), chaque exercice se fait **directement sur la portée**, avec les corrections au fur et à mesure. "
              "Ici, plus de règles d'enchaînement classiques (les quintes parallèles sont permises) : on vérifie que chaque accord contient les bonnes notes, "
              "sans croisement et dans la tessiture de chaque voix.", '']
        for j, (nom, sous, consigne) in enumerate(PAGES[chap]):
            n = f'{chap}.{j + 1}'
            Lg += [f'### Exercice {n} · {sous}', '', consigne, '', f'![Exercice {n}](images/{nom}.png)', '']
        Lg += ['### Corrigés', '']
        for j, (nom, sous, consigne) in enumerate(PAGES[chap]):
            n = f'{chap}.{j + 1}'
            Lg += [f"**Exercice {n}** : une solution parmi d'autres.", '', f'![Corrigé {n}](images/{nom}-c.png)', '',
                   f'🔊 [Écouter](audio/{nom}-c.mp3) · [MIDI](audio/{nom}-c.mid)', '']
        Lg += ['---', '', nav, '']
        open(os.path.join(CAHIER, fic + '.md'), 'w').write('\n'.join(Lg))


def lier_precedent(fichier, cible, titre):
    p = os.path.join(CAHIER, fichier)
    s = open(p).read()
    s = re.sub(r'\[Sommaire du cahier\]\(README\.md\)(?! ·)', f"[Sommaire du cahier](README.md) · [{titre} →]({cible}.md)", s)
    open(p, 'w').write(s)


def sommaire(PAGES, TITRES, chaps, apres, desc):
    readme = os.path.join(CAHIER, 'README.md')
    R = [l for l in open(readme).read().split('\n') if not re.match(r'- \[.*\]\((%s)-' % '|'.join(map(str, chaps)), l)]
    i = next(k for k, l in enumerate(R) if f'({apres}' in l)
    add = [f"- [{TITRES[c][1]}]({TITRES[c][0]}.md) (chapitre {c} du cours) : {len(PAGES[c])} × {desc}" for c in chaps]
    R = R[:i + 1] + add + R[i + 1:]
    open(readme, 'w').write('\n'.join(R))


ecrire_pages(PAGES, TITRES, CH8, ordre)
lier_precedent('39-majeur-et-mineur.md', '43-faure', TITRES[43][1])
sommaire(PAGES, TITRES, CH8, '39-majeur', 'écriture libre')
readme = os.path.join(CAHIER, 'README.md')
txt = open(readme).read()
n8 = sum(len(v) for v in PAGES.values())
m = re.search(r'\*\*(\d+) exercices\*\*', txt)
txt = txt.replace(m.group(0), f'**{int(m.group(1)) + n8} exercices**')
txt = re.sub(r' et (\d+) sur le romantisme tardif\. Tous les corrigés',
             lambda mm: f', {mm.group(1)} sur le romantisme tardif et {n8} sur Fauré, Debussy, Ravel et le jazz. Tous les corrigés', txt)
open(readme, 'w').write(txt)
N8 = n8
print('pages du cahier écrites')
