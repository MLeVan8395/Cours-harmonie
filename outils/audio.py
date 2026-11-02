"""Fabrique les fichiers audio (MP3) et MIDI de chaque exemple.

Usage : python3 outils/audio.py CHEMIN/VERS/FluidR3_GM

Les sons viennent de la banque General MIDI FluidR3_GM, dans la version
« une note = un fichier » de https://github.com/gleitz/midi-js-soundfonts
(dossiers choir_aahs-mp3, violin-mp3, viola-mp3, cello-mp3…).
La musique de chaque figure est lue dans cours/audio/sons-*.json,
écrits par build_partie*.py.
"""
import glob, json, os, struct, subprocess, sys
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(ICI, '..', 'cours', 'audio')
SR = 44100
TEMPO = 90           # noires par minute
NOMS = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
# instrument General MIDI de chaque voix : (dossier de la banque, programme MIDI, volume)
INSTR = {
    'choeur': [('choir_aahs', 52, 1.0), ('choir_aahs', 52, 0.8), ('choir_aahs', 52, 0.8), ('choir_aahs', 52, 0.9)],
    'quatuor': [('violin', 40, 1.0), ('violin', 40, 0.8), ('viola', 41, 0.85), ('cello', 42, 0.95)],
}
_cache = {}


def echantillon(banque, inst, m):
    cle = (inst, m)
    if cle not in _cache:
        f = os.path.join(banque, f'{inst}-mp3', f'{NOMS[m % 12]}{m // 12 - 1}.mp3')
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                             capture_output=True, check=True).stdout
        _cache[cle] = np.frombuffer(raw, dtype=np.float32).copy()
    return _cache[cle]


def rendre(musique, banque):
    sec = 60 / TEMPO
    instr = INSTR[musique['genre']]
    total = max(sum(d for _, d in v) for v in musique['voix']) * sec + 1.5
    out = np.zeros(int(total * SR) + SR)
    for i, voix in enumerate(musique['voix']):
        inst, _, vol = instr[min(i, len(instr) - 1)] if len(musique['voix']) > 1 else instr[0]
        t = 0.0
        for m, d in voix:
            if m is not None:
                s = echantillon(banque, inst, m)
                n = min(len(s), int((d * sec + 0.12) * SR))
                seg = s[:n].copy()
                fade = min(n, int(0.12 * SR))
                seg[n - fade:] *= np.linspace(1, 0, fade)
                a = int(t * SR)
                out[a:a + n] += seg * vol
            t += d * sec
    out = out[:int(total * SR)]
    out /= max(1e-6, np.abs(out).max()) / 0.85
    return out.astype(np.float32)


def ecrire_mp3(signal, chemin):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                    '-codec:a', 'libmp3lame', '-b:a', '64k', chemin], input=signal.tobytes(), check=True)


def ecrire_midi(musique, chemin):
    """Fichier MIDI de format 1 : une piste par voix, avec son instrument General MIDI."""
    tpq = 480
    def vlq(n):
        b = [n & 0x7F]
        n >>= 7
        while n:
            b.insert(0, (n & 0x7F) | 0x80)
            n >>= 7
        return bytes(b)
    pistes = []
    tempo = int(60_000_000 / TEMPO)
    pistes.append(b'\x00\xff\x51\x03' + tempo.to_bytes(3, 'big') + b'\x00\xff\x2f\x00')
    instr = INSTR[musique['genre']]
    for i, voix in enumerate(musique['voix']):
        _, prog, vol = instr[min(i, len(instr) - 1)]
        ch = i % 16
        ev = bytearray(b'\x00' + bytes([0xC0 | ch, prog]))
        attente = 0
        for m, d in voix:
            ticks = int(d * tpq)
            if m is None:
                attente += ticks
                continue
            ev += vlq(attente) + bytes([0x90 | ch, m, int(80 * vol)])
            ev += vlq(ticks) + bytes([0x80 | ch, m, 0])
            attente = 0
        ev += b'\x00\xff\x2f\x00'
        pistes.append(bytes(ev))
    with open(chemin, 'wb') as f:
        f.write(b'MThd' + struct.pack('>IHHH', 6, 1, len(pistes), tpq))
        for p in pistes:
            f.write(b'MTrk' + struct.pack('>I', len(p)) + p)


if __name__ == '__main__':
    banque = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/sf/gm/FluidR3_GM')
    n = 0
    for dossier in (AUD, os.path.join(ICI, '..', 'cahier', 'audio')):
        for fj in sorted(glob.glob(os.path.join(dossier, 'sons-*.json'))):
            for nom, mus in json.load(open(fj)).items():
                ecrire_mp3(rendre(mus, banque), os.path.join(dossier, nom + '.mp3'))
                ecrire_midi(mus, os.path.join(dossier, nom + '.mid'))
                n += 1
    print(f'{n} exemples rendus en MP3 et MIDI')
