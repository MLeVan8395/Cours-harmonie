"""Graveur SVG pour le cours d'harmonie (même style que le cours de contrepoint).

Une figure = une liste de portées + des voix posées sur ces portées.
Notes écrites en français : "Do4", "Sib3", "Fa#3" (Do4 = Do central).
"""
import json, os, subprocess

HERE = os.path.dirname(__file__)
GLYPH = json.load(open(os.path.join(HERE, 'glyphs.json')))
FR = ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si']
SEMI = [0, 2, 4, 5, 7, 9, 11]
SP, H = 10, 5
BOTTOM = {'treble': 30, 'bass': 18, 'alto': 24}   # position diatonique de la ligne du bas
INK, MUTED = '#111', '#666'
RED, BLUE, GREEN, ORANGE = '#c0392b', '#1f4e8c', '#1e7b34', '#c96a00'
FONT = 'Verdana, Geneva, DejaVu Sans, sans-serif'
SONS = {}   # nom de figure -> musique (rempli par Figure.save)


def N(s):
    import re
    m = re.match(r'^(Do|Ré|Mi|Fa|Sol|La|Si)(#|b)?(\d)$', s)
    if not m:
        raise ValueError(s)
    return {'s': FR.index(m.group(1)), 'a': 1 if m.group(2) == '#' else -1 if m.group(2) == 'b' else 0,
            'o': int(m.group(3))}


def dpos(n):
    return n['o'] * 7 + n['s']


def midi(n):
    return 12 * (n['o'] + 1) + SEMI[n['s']] + n['a']


def glyph(name, x, y, size, color=INK):
    g = GLYPH[name]
    k = size / g['upm']
    return f'<path d="{g["d"]}" transform="translate({x:.1f} {y:.1f}) scale({k:.5f} {-k:.5f})" fill="{color}"/>'


def alto_clef(x, top, color=INK):
    """Clé d'ut 3e ligne dessinée à la main (centre sur la 3e ligne)."""
    mid = top + 2 * SP
    b, t = top + 4 * SP + 1, top - 1
    o = [f'<rect x="{x}" y="{t}" width="4.5" height="{b - t}" fill="{color}"/>',
         f'<rect x="{x + 7}" y="{t}" width="1.6" height="{b - t}" fill="{color}"/>']
    # deux arcs (haut et bas) qui se rejoignent au centre
    for sgn in (-1, 1):
        y0 = mid + sgn * 20
        o.append(f'<path d="M{x + 8.6} {mid} L{x + 13} {mid + sgn * 6} C{x + 16} {mid + sgn * 2} {x + 18} {mid + sgn * 1} '
                 f'{x + 20} {mid + sgn * 2} C{x + 30} {mid + sgn * 4} {x + 30} {y0} {x + 21} {y0} '
                 f'C{x + 16} {y0} {x + 15} {mid + sgn * 15} {x + 18} {mid + sgn * 14} '
                 f'C{x + 21} {mid + sgn * 13} {x + 22} {mid + sgn * 16} {x + 20} {mid + sgn * 17.5} '
                 f'C{x + 26} {mid + sgn * 18} {x + 25} {mid + sgn * 4} {x + 19} {mid + sgn * 4.5} '
                 f'C{x + 16} {mid + sgn * 5} {x + 14} {mid + sgn * 8} {x + 13} {mid + sgn * 8} Z" fill="{color}"/>')
    return ''.join(o)


def brace(x, y1, y2, color=INK):
    h = y2 - y1
    m = (y1 + y2) / 2
    w = 9
    return (f'<path d="M{x + w} {y1} C{x} {y1 + h * 0.08} {x + w * 0.95} {m - h * 0.12} {x} {m} '
            f'C{x + w * 0.95} {m + h * 0.12} {x} {y2 - h * 0.08} {x + w} {y2} '
            f'C{x + 3} {y2 - h * 0.1} {x + w * 0.95 + 3.5} {m + h * 0.1} {x + 3.2} {m} '
            f'C{x + w * 0.95 + 3.5} {m - h * 0.1} {x + 3} {y1 + h * 0.1} {x + w} {y1} Z" fill="{color}"/>')


SHARP_POS = [38, 35, 39, 36, 33, 37, 34]   # Fa Do Sol Ré La Mi Si en clé de sol
FLAT_POS = [34, 37, 33, 36, 32, 35, 31]    # Si Mi La Ré Sol Do Fa
SHARP_ORDER = [3, 0, 4, 1, 5, 2, 6]
FLAT_ORDER = [6, 2, 5, 1, 4, 0, 3]
CLEF_SHIFT = {'treble': 0, 'bass': -14, 'alto': -7}


def key_alts(key):
    """key = nombre d'altérations : +2 = deux dièses, -3 = trois bémols."""
    d = {}
    if key > 0:
        for s in SHARP_ORDER[:key]:
            d[s] = 1
    elif key < 0:
        for s in FLAT_ORDER[:-key]:
            d[s] = -1
    return d


class Figure:
    """staves : liste de dicts {clef, label}
    voices : liste de dicts {staff, stem ('up'/'down'/None), events:[(note|None, durée en temps, options)]}
    """

    def __init__(self, staves, voices, beats_per_bar=4, key=0, unit=16, gap=96, final=True,
                 brace=None, labels=None, rows=None, top_texts=None, lines=None, boxes=None,
                 bars=True, left_labels=None, bottom=None, time=None, top=46, pickup=0):
        self.staves, self.voices = staves, voices
        self.bar, self.key, self.unit, self.gap = beats_per_bar, key, unit, gap
        self.final, self.brace = final, brace
        self.labels = labels or []     # [(t, texte, rangée, couleur)]
        self.top_texts = top_texts or []  # [(t, texte, couleur)]
        self.lines = lines or []       # [((voix, idx), (voix, idx), couleur)]
        self.boxes = boxes or []       # [(t1, t2, couleur, texte)]
        self.bars, self.left_labels = bars, left_labels
        self.bottom, self.time, self.top0 = bottom, time, top
        self.rows = rows
        self.pickup = pickup

    def svg(self):
        unit, bar = self.unit, self.bar
        nks = abs(self.key)
        left = 70 + nks * 11 + (22 if self.time else 0) + (18 if self.left_labels else 0)
        x0 = 16 + (18 if self.left_labels else 0)
        beats = max(sum(e[1] for e in v['events']) for v in self.voices)
        endX = left + beats * unit + 4
        W = endX + 14
        top0 = self.top0 + (14 if self.top_texts else 0)
        ys = [top0 + i * self.gap for i in range(len(self.staves))]
        o = []
        for i, st in enumerate(self.staves):
            top = ys[i]
            for l in range(5):
                o.append(f'<line x1="{x0}" y1="{top + l * SP}" x2="{endX}" y2="{top + l * SP}" stroke="{INK}" stroke-width="1"/>')
            c = st['clef']
            if c == 'treble':
                o.append(glyph('treble', x0 + 4, top + 31, 40))
            elif c == 'bass':
                o.append(glyph('bass', x0 + 6, top + 32.5, 34))
            else:
                o.append(alto_clef(x0 + 6, top))
            kx = x0 + 42
            alts = key_alts(self.key)
            order = SHARP_ORDER if self.key > 0 else FLAT_ORDER
            pos = SHARP_POS if self.key > 0 else FLAT_POS
            for j in range(nks):
                p = pos[j] + CLEF_SHIFT[c]
                y = top + 4 * SP - (p - BOTTOM['treble'] - CLEF_SHIFT[c]) * H if False else top + 4 * SP - (p - BOTTOM[c]) * H
                o.append(glyph('sharp' if self.key > 0 else 'flat', kx, y + (5 if self.key > 0 else 3), 15))
                kx += 11
            if self.time:
                for k, dy in ((self.time[0], 2), (self.time[1], 4)):
                    o.append(f'<text x="{kx + 8}" y="{top + dy * SP - 1}" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="21" fill="{INK}">{k}</text>')
            if st.get('label'):
                o.append(f'<text x="{left - 4}" y="{top - 9}" text-anchor="start" font-family="{FONT}" font-size="11" fill="{MUTED}">{st["label"]}</text>')
            if self.left_labels:
                o.append(f'<text x="{x0 - 6}" y="{top + 2 * SP + 4}" text-anchor="end" font-family="{FONT}" font-size="12" font-weight="700" fill="{MUTED}">{self.left_labels[i]}</text>')
        sysTop, sysBot = ys[0], ys[-1] + 4 * SP
        o.append(f'<line x1="{x0}" y1="{sysTop}" x2="{x0}" y2="{sysBot}" stroke="{INK}" stroke-width="1.3"/>')
        if self.brace:
            a, b = self.brace
            o.append(brace(x0 - 12, ys[a] - 1, ys[b] + 4 * SP + 1))
        titres_boites = []
        # boîtes de surlignage (derrière les notes)
        for (t1, t2, col, txt) in self.boxes:
            xa, xb = left + t1 * unit - 4, left + t2 * unit - 8
            o.insert(0, f'<rect x="{xa}" y="{sysTop - 22}" width="{xb - xa}" height="{sysBot - sysTop + 44}" rx="6" fill="{col}" fill-opacity="0.10" stroke="{col}" stroke-opacity="0.5"/>')
            if txt:
                titres_boites.append(((xa + xb) / 2, txt, col))
        # barres de mesure
        if self.bars:
            b = bar + (self.pickup or 0) if self.pickup else bar
            if self.pickup:
                b = self.pickup
            while b <= beats + 1e-9:
                x = left + b * unit - 6
                if abs(b - beats) < 1e-9 and self.final:
                    o.append(f'<line x1="{x - 4}" y1="{sysTop}" x2="{x - 4}" y2="{sysBot}" stroke="{INK}"/>'
                             f'<line x1="{x}" y1="{sysTop}" x2="{x}" y2="{sysBot}" stroke="{INK}" stroke-width="3.5"/>')
                else:
                    if self.brace:
                        o.append(f'<line x1="{x}" y1="{sysTop}" x2="{x}" y2="{sysBot}" stroke="{INK}"/>')
                    else:
                        for top in ys:
                            o.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top + 4 * SP}" stroke="{INK}"/>')
                b += bar
        else:
            # pas de mesure : double barre finale seulement
            x = left + beats * unit - 6
            if self.final:
                o.append(f'<line x1="{x - 4}" y1="{sysTop}" x2="{x - 4}" y2="{sysBot}" stroke="{INK}"/>'
                         f'<line x1="{x}" y1="{sysTop}" x2="{x}" y2="{sysBot}" stroke="{INK}" stroke-width="3.5"/>')
        # positions des têtes
        heads = {}   # (voix, idx) -> (x, y)
        ext = [sysTop, sysBot]
        placed = []  # toutes les têtes
        for vi, v in enumerate(self.voices):
            t = 0
            for ei, ev in enumerate(v['events']):
                n, d = ev[0], ev[1]
                opts = ev[2] if len(ev) > 2 else {}
                if n is not None:
                    placed.append(dict(vi=vi, ei=ei, t=t, d=d, n=N(n) if isinstance(n, str) else n,
                                       staff=v['staff'], stem=v.get('stem'), opts=opts))
                else:
                    placed.append(dict(vi=vi, ei=ei, t=t, d=d, n=None, staff=v['staff'], stem=v.get('stem'), opts=opts))
                t += d
        # décalages (secondes et unissons sur une même portée)
        for a in placed:
            a['dx'] = 0
            a['share'] = False
        for a in placed:
            for b in placed:
                if a is b or a['n'] is None or b['n'] is None or a['staff'] != b['staff'] or abs(a['t'] - b['t']) > 1e-9:
                    continue
                if a['vi'] < b['vi']:
                    da = dpos(a['n']) - dpos(b['n'])
                    if da == 1:
                        a['dx'] = 13          # seconde : la voix du haut décalée à droite
                    elif da == 0:
                        if a['d'] >= 4 or b['d'] >= 4 or (a['d'] >= 2) != (b['d'] >= 2) or a['n']['a'] != b['n']['a']:
                            a['dx'] = 15
                        else:
                            b['share'] = True   # même tête, deux hampes
        keyAlt = key_alts(self.key)
        accState = {}
        croches = []
        for p in sorted(placed, key=lambda q: (q['staff'], q['t'], q['vi'])):
            vi, top = p['vi'], ys[p['staff']]
            clef = self.staves[p['staff']]['clef']
            col = p['opts'].get('color', INK)
            centered = p['d'] >= bar or p['opts'].get('center')
            x = left + p['t'] * unit + (unit * min(p['d'], bar) / 2 - 6 if centered else unit * 0.5) + p['dx']
            if p['n'] is None:
                if p['opts'].get('hide'):
                    continue
                y = top + 2 * SP
                if p['d'] >= 4:
                    o.append(f'<rect x="{x - 7}" y="{top + SP}" width="14" height="{H}" fill="{col}"/>')
                elif p['d'] >= 2:
                    o.append(f'<rect x="{x - 7}" y="{top + 2 * SP - H}" width="14" height="{H}" fill="{col}"/>')
                else:
                    o.append(glyph('qrest', x - 5, top + 28, 32, col))
                continue
            n = p['n']
            pp, bot = dpos(n), BOTTOM[clef]
            y = top + 4 * SP - (pp - bot) * H
            heads[(vi, p['ei'])] = (x - p['dx'] if p['share'] else x, y)
            ext[0] = min(ext[0], y - 6); ext[1] = max(ext[1], y + 6)
            for q in range(bot - 2, pp - 1, -2):
                yy = top + 4 * SP - (q - bot) * H
                o.append(f'<line x1="{x - 11}" y1="{yy}" x2="{x + 11}" y2="{yy}" stroke="{INK}"/>')
            q = bot + 10
            while q <= pp:
                yy = top + 4 * SP - (q - bot) * H
                o.append(f'<line x1="{x - 11}" y1="{yy}" x2="{x + 11}" y2="{yy}" stroke="{INK}"/>')
                q += 2
            barIdx = int((p['t'] - (self.pickup or 0)) // bar) if self.bars else int(p['t'] // 4)
            stkey = (p['staff'], barIdx, n['s'], n['o'])
            prev = accState.get(stkey, keyAlt.get(n['s'], 0))
            if n['a'] != prev or p['opts'].get('courtesy'):
                ax = x - 19 - (12 if p['opts'].get('acc_shift') else 0)
                name = 'sharp' if n['a'] == 1 else 'flat' if n['a'] == -1 else 'natural'
                o.append(glyph(name, ax, y + (3 if n['a'] == -1 else 5), 15, col))
                accState[stkey] = n['a']
            if not p['share']:
                if p['d'] >= 4:
                    o.append(f'<ellipse cx="{x}" cy="{y}" rx="7" ry="4.6" fill="none" stroke="{col}" stroke-width="2.6" transform="rotate(-15 {x} {y})"/>')
                elif p['d'] >= 2:
                    o.append(f'<ellipse cx="{x}" cy="{y}" rx="6" ry="4.2" fill="none" stroke="{col}" stroke-width="1.8" transform="rotate(-25 {x} {y})"/>')
                else:
                    o.append(f'<ellipse cx="{x}" cy="{y}" rx="6" ry="4.2" fill="{col}" transform="rotate(-25 {x} {y})"/>')
                if p['d'] in (3, 1.5, 0.75):
                    o.append(f'<circle cx="{x + 11}" cy="{y - (0 if (pp - bot) % 2 else 5)}" r="1.9" fill="{col}"/>')
            hx = x - p['dx'] if p['share'] else x
            if p['d'] < 4:
                stem = p['stem'] or ('up' if y >= top + 2 * SP else 'down')
                if p['d'] < 1:
                    croches.append(dict(vi=vi, t=p['t'], d=p['d'], x=hx, y=y, up=stem == 'up', col=col))
                elif stem == 'up':
                    ext[0] = min(ext[0], y - 32)
                    o.append(f'<line x1="{hx + 5.6}" y1="{y}" x2="{hx + 5.6}" y2="{y - 32}" stroke="{col}" stroke-width="1.3"/>')
                else:
                    ext[1] = max(ext[1], y + 32)
                    o.append(f'<line x1="{hx - 5.6}" y1="{y}" x2="{hx - 5.6}" y2="{y + 32}" stroke="{col}" stroke-width="1.3"/>')
            if p['opts'].get('fermata'):
                up = p['stem'] != 'down'
                fy = (min(top - 14, y - 40) if up else max(top + 4 * SP + 14, y + 40))
                sg = -1 if up else 1
                o.append(f'<path d="M{x - 9} {fy} A9 9 0 0 {1 if up else 0} {x + 9} {fy}" fill="none" stroke="{INK}" stroke-width="2"/><circle cx="{x}" cy="{fy + sg * 3}" r="1.8" fill="{INK}"/>')
                ext[0] = min(ext[0], fy - 12); ext[1] = max(ext[1], fy + 12)
            if p['opts'].get('lab'):
                up = p['stem'] != 'down'
                ly = y - 8 if up else y + 15
                o.append(f'<text x="{x + 9}" y="{ly}" font-family="{FONT}" font-size="10" font-style="italic" font-weight="700" fill="{p["opts"].get("labcol", col)}">{p["opts"]["lab"]}</text>')
            if p['opts'].get('name'):
                o.append(f'<text x="{x + 12}" y="{y + 4}" font-family="{FONT}" font-size="10" fill="{col}">{p["opts"]["name"]}</text>')
        # croches : ligaturées par temps et par voix, sinon crochet
        from itertools import groupby
        croches.sort(key=lambda c: (c['vi'], c['t']))
        for (vi_, beat), grp in groupby(croches, key=lambda c: (c['vi'], int(c['t'] + 1e-9))):
            g = list(grp)
            up = g[0]['up']
            if len(g) == 1:
                c = g[0]
                sx = c['x'] + (5.6 if up else -5.6)
                y2 = c['y'] - 32 if up else c['y'] + 32
                o.append(f'<line x1="{sx}" y1="{c["y"]}" x2="{sx}" y2="{y2}" stroke="{c["col"]}" stroke-width="1.3"/>')
                o.append(f'<path d="M{sx} {y2} q 3 {8 if up else -8} 9 {12 if up else -12} q 2 {4 if up else -4} -1 {10 if up else -10}" fill="none" stroke="{c["col"]}" stroke-width="1.6"/>')
                ext[0] = min(ext[0], y2); ext[1] = max(ext[1], y2)
                continue
            by = (min(c['y'] for c in g) - 30) if up else (max(c['y'] for c in g) + 30)
            xs = [c['x'] + (5.6 if up else -5.6) for c in g]
            for c, sx in zip(g, xs):
                o.append(f'<line x1="{sx}" y1="{c["y"]}" x2="{sx}" y2="{by}" stroke="{c["col"]}" stroke-width="1.3"/>')
            o.append(f'<line x1="{xs[0]}" y1="{by}" x2="{xs[-1]}" y2="{by}" stroke="{g[0]["col"]}" stroke-width="4.5"/>')
            if any(c['d'] <= 0.25 for c in g):
                b2 = by + (6 if up else -6)
                o.append(f'<line x1="{xs[0]}" y1="{b2}" x2="{xs[-1]}" y2="{b2}" stroke="{g[0]["col"]}" stroke-width="4.5"/>')
            ext[0] = min(ext[0], by); ext[1] = max(ext[1], by)
        # liaisons de prolongation
        for vi_, v in enumerate(self.voices):
            for ei, ev in enumerate(v['events']):
                op = ev[2] if len(ev) > 2 else {}
                if op.get('tie') and (vi_, ei) in heads and (vi_, ei + 1) in heads:
                    (xa, ya), (xb, yb) = heads[(vi_, ei)], heads[(vi_, ei + 1)]
                    up = v.get('stem') == 'down'      # liaison du côté opposé à la hampe
                    dy = 7 if not up else -7
                    o.append(f'<path d="M{xa + 6} {ya + dy} Q{(xa + xb) / 2} {ya + dy * 2.6} {xb - 6} {yb + dy}" fill="none" stroke="{op.get("color", INK)}" stroke-width="1.6"/>')
        for (a, b, col) in self.lines:
            (xa, ya), (xb, yb) = heads[a], heads[b]
            o.append(f'<line x1="{xa + 8}" y1="{ya}" x2="{xb - 8}" y2="{yb}" stroke="{col}" stroke-width="2.2" stroke-dasharray="5 3" stroke-linecap="round"/>')
        for (xm, txt, col) in titres_boites:
            o.append(f'<text x="{xm}" y="{min(sysTop - 27, ext[0] - 12)}" text-anchor="middle" font-family="{FONT}" font-size="11" font-weight="700" fill="{col}">{txt}</text>')
        for (t, txt, col) in self.top_texts:
            x = left + t * unit + unit * min(self.bar, 4) / 2 - 6 if self.bar >= 4 else left + t * unit + unit * 0.5
            o.append(f'<text x="{x}" y="{min(sysTop - 26, ext[0] - 10)}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" fill="{col}">{txt}</text>')
        maxrow = -1
        for lab in self.labels:
            t, txt, row = lab[0], lab[1], lab[2]
            col = lab[3] if len(lab) > 3 else BLUE
            maxrow = max(maxrow, row)
            ctr = lab[4] if len(lab) > 4 else True
            x = left + t * unit + (unit * min(self.bar, 4) / 2 - 6 if ctr else unit * 0.5)
            ybase = max(sysBot + 34, ext[1] + 24) + row * 30
            if '/' in txt and row == 1 and txt.count('/') == 1 and not txt.startswith('I'):
                up, dn = txt.split('/')
                o.append(f'<text x="{x}" y="{ybase - 8}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" fill="{col}">{up}</text>')
                o.append(f'<text x="{x}" y="{ybase + 6}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" fill="{col}">{dn}</text>')
            else:
                import re as _re
                roman = bool(_re.match(r'^[IVX°]+$', txt))
                fam = FONT
                o.append(f'<text x="{x}" y="{ybase}" text-anchor="middle" font-family="{fam}" font-size="{14 if roman else 13}" font-weight="700" fill="{col}">{txt}</text>')
        if self.rows:
            for r, name in enumerate(self.rows):
                o.append(f'<text x="{x0 + 2}" y="{max(sysBot + 34, ext[1] + 24) + r * 30}" font-family="{FONT}" font-size="10" fill="{MUTED}">{name}</text>')
        Ht = max(sysBot, ext[1] - 12) + (self.bottom if self.bottom is not None else (46 + 30 * max(0, maxrow)))
        shift = max(0, 40 - ext[0]) if self.top_texts else max(0, 12 - ext[0])
        if shift:
            o = [f'<g transform="translate(0 {shift})">'] + o + ['</g>']
            Ht += shift
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Ht}" viewBox="0 0 {W} {Ht}"><rect width="100%" height="100%" fill="white"/>{"".join(o)}</svg>'

    def musique(self):
        """Contenu sonore de la figure : une liste de voix [(midi | None, durée en temps)]."""
        voix = []
        for v in self.voices:
            ev = []
            for e in v['events']:
                n, d = e[0], e[1]
                hide = len(e) > 2 and e[2].get('hide')
                ev.append((None if (n is None or hide) else midi(N(n)), d))
            voix.append(ev)
        cordes = any(st['clef'] == 'alto' for st in self.staves)
        return {'voix': voix, 'genre': 'quatuor' if cordes else 'choeur'}

    def save(self, path_png):
        SONS[os.path.basename(path_png)[:-4]] = self.musique()
        svgp = path_png[:-4] + '.svg'
        open(svgp, 'w').write(self.svg())
        subprocess.run(['rsvg-convert', '-z', '2', '-o', path_png, svgp], check=True)
        os.remove(svgp)


def satb(chords, dur=4, colors=None, **kw):
    """chords : liste de (S, A, T, B) ; None = silence. colors : {(voix, idx): couleur}."""
    colors = colors or {}
    voices = []
    for vi, (staff, stem) in enumerate([(0, 'up'), (0, 'down'), (1, 'up'), (1, 'down')]):
        evs = []
        for ci, ch in enumerate(chords):
            d = ch[4] if len(ch) > 4 else dur
            opts = {}
            if (vi, ci) in colors:
                opts['color'] = colors[(vi, ci)]
            evs.append((ch[vi], d, opts))
        voices.append({'staff': staff, 'stem': stem, 'events': evs})
    kw.setdefault('brace', (0, 1))
    kw.setdefault('gap', 104)
    return Figure([{'clef': 'treble'}, {'clef': 'bass'}], voices, **kw)
