"""Lecture d'un fichier MusicXML compressé (.mxl) : pour chaque partie, la liste des notes (début, durée, note, mesure).
Gère les accords, les voix multiples (backup/forward) ; ignore les petites notes."""
import zipfile, sys, xml.etree.ElementTree as ET
FR = {'C': 'Do', 'D': 'Ré', 'E': 'Mi', 'F': 'Fa', 'G': 'Sol', 'A': 'La', 'B': 'Si'}


def lire(f):
    z = zipfile.ZipFile(f)
    nom = [n for n in z.namelist() if n.endswith('.xml') and 'META' not in n][0]
    root = ET.fromstring(z.read(nom))
    parts = []
    for p in root.findall('part'):
        div, t, key, temps = 1, 0.0, None, None
        notes, mesures = [], []
        for m in p.findall('measure'):
            debut = t
            mesures.append((m.get('number'), t))
            dern = t
            for el in m:
                if el.tag == 'attributes':
                    if el.find('divisions') is not None:
                        div = int(el.findtext('divisions'))
                    if el.find('key/fifths') is not None:
                        key = int(el.findtext('key/fifths'))
                    if el.find('time/beats') is not None:
                        temps = (int(el.findtext('time/beats')), int(el.findtext('time/beat-type')))
                elif el.tag == 'backup':
                    t -= int(el.findtext('duration')) / div
                elif el.tag == 'forward':
                    t += int(el.findtext('duration')) / div
                elif el.tag == 'note':
                    if el.find('grace') is not None or el.find('duration') is None:
                        continue
                    d = int(el.findtext('duration')) / div
                    ch = el.find('chord') is not None
                    t0 = dern if ch else t
                    if el.find('rest') is None:
                        st = el.findtext('pitch/step'); al = int(float(el.findtext('pitch/alter') or 0)); o = el.findtext('pitch/octave')
                        n = FR[st] + {1: '#', -1: 'b', 0: '', 2: '##', -2: 'bb'}[al] + o
                        tie = any(x.get('type') == 'stop' for x in el.findall('tie'))
                        notes.append({'t': t0, 'd': d, 'n': n, 'lie': tie, 'm': m.get('number'), 'v': el.findtext('voice') or '1'})
                    if not ch:
                        dern = t
                        t += d
        parts.append({'key': key, 'temps': temps, 'notes': notes, 'mesures': mesures})
    return parts


if __name__ == '__main__':
    P = lire(sys.argv[1]); nb = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    print([p['key'] for p in P], P[0]['temps'])
    for p in P:
        print(' | '.join(f"{x['t']:.2f}:{x['n']}/{x['d']:.2f}{'~' if x['lie'] else ''}" for x in p['notes'] if int(''.join(c for c in x['m'] if c.isdigit()) or 0) <= nb))
