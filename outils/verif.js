// Vérificateur des règles d'écriture à 4 voix : traduction fidèle de verif.py
// (mêmes règles, mêmes messages). Notes au format « Do4 », « Sib3 », « Fa#3 ».
const HV = (() => {
  const FR = ['Do', 'Ré', 'Mi', 'Fa', 'Sol', 'La', 'Si'];
  const SEMI = [0, 2, 4, 5, 7, 9, 11];
  const VOIX = ['soprano', 'alto', 'ténor', 'basse'];
  const TESS = {soprano: ['Do4', 'Sol5'], alto: ['Sol3', 'Ré5'], 'ténor': ['Do3', 'Sol4'], basse: ['Fa2', 'Do4']};

  function N(s) {
    const m = /^(Do|Ré|Mi|Fa|Sol|La|Si)(#|b)?(\d)$/.exec(s);
    if (!m) throw new Error('note ' + s);
    return {s: FR.indexOf(m[1]), a: m[2] === '#' ? 1 : m[2] === 'b' ? -1 : 0, o: +m[3]};
  }
  const dpos = n => n.o * 7 + n.s;
  const midi = n => 12 * (n.o + 1) + SEMI[n.s] + n.a;
  const pc = n => (((SEMI[n.s] + n.a) % 12) + 12) % 12;
  const nom = n => FR[n.s] + (n.a === 1 ? '♯' : n.a === -1 ? '♭' : '');
  const texte = n => FR[n.s] + (n.a === 1 ? '#' : n.a === -1 ? 'b' : '') + n.o;
  const mod = (a, b) => ((a % b) + b) % b;
  function isP5(lo, hi) { const d = dpos(hi) - dpos(lo), st = midi(hi) - midi(lo); return d > 0 && d % 7 === 4 && mod(st, 12) === 7; }
  function isP8(lo, hi) { const d = dpos(hi) - dpos(lo), st = midi(hi) - midi(lo); return mod(d, 7) === 0 && mod(st, 12) === 0; }

  function triad(ch) {
    const steps = [...new Set(ch.map(x => N(x).s))].sort((a, b) => a - b);
    for (const r of steps) {
      const t = (r + 2) % 7, f = (r + 4) % 7;
      if (steps.every(s => s === r || s === t || s === f)) return [r, t, f];
    }
    return null;
  }
  function etat(ch) {
    const tr = triad(ch); if (!tr) return null;
    const b = N(ch[3]).s;
    return b === tr[0] ? '5' : b === tr[1] ? '6' : '64';
  }
  function qualite(ch) {
    const tr = triad(ch);
    const notes = {}; ch.forEach(x => { const n = N(x); notes[n.s] = n; });
    const [r, t, f] = tr.map(s => notes[s]);
    if (!t) return null;
    const t3 = mod(pc(t) - pc(r), 12);
    if (!f) return t3 === 4 ? 'M' : 'm';
    const t5 = mod(pc(f) - pc(r), 12);
    return ({'4,7': 'M', '3,7': 'm', '3,6': 'd', '4,8': 'A'})[t3 + ',' + t5] || '?';
  }

  // renvoie une liste de {i: indice d'accord (ou de l'enchaînement), msg}
  function verifier(chords, tonic, allowThird) {
    allowThird = new Set(allowThird || []);
    const errs = [];
    const P = chords.map(ch => ch.map(N));
    const sens = mod(pc(N(tonic + '4')) + 11, 12);
    const add = (i, msg) => errs.push({i, msg});
    P.forEach((ch, i) => {
      const m = `accord ${i + 1}`;
      ch.forEach((n, v) => {
        const [lo, hi] = TESS[VOIX[v]].map(N);
        if (midi(n) < midi(lo) || midi(n) > midi(hi)) add(i, `${m} : ${VOIX[v]} hors tessiture (${nom(n)})`);
      });
      for (let v = 0; v < 3; v++) if (midi(ch[v]) < midi(ch[v + 1])) add(i, `${m} : croisement ${VOIX[v]}/${VOIX[v + 1]}`);
      if (dpos(ch[0]) - dpos(ch[1]) > 7) add(i, `${m} : écart soprano-alto supérieur à l'octave`);
      if (dpos(ch[1]) - dpos(ch[2]) > 7) add(i, `${m} : écart alto-ténor supérieur à l'octave`);
      if (dpos(ch[2]) - dpos(ch[3]) > 11) add(i, `${m} : écart ténor-basse supérieur à la douzième`);
      const tr = triad(chords[i]);
      if (!tr) add(i, `${m} : pas un accord parfait`);
      else {
        const [r, t, f] = tr, steps = ch.map(n => n.s), cnt = x => steps.filter(s => s === x).length;
        const e = etat(chords[i]), q = qualite(chords[i]);
        if (!steps.includes(t)) add(i, `${m} : tierce absente`);
        if (e === '5') {
          if (cnt(t) > 1 && !allowThird.has(i)) add(i, `${m} : tierce doublée`);
          if (cnt(r) < 2 && !allowThird.has(i) && !(cnt(f) >= 2 && q === 'd')) add(i, `${m} : fondamentale non doublée à l'état fondamental`);
          if (cnt(r) > 3) add(i, `${m} : fondamentale quadruplée`);
        } else if (e === '6') {
          if (!steps.includes(f) || !steps.includes(r)) add(i, `${m} : accord de sixte incomplet`);
          if (cnt(t) > 1 && q === 'M') add(i, `${m} : basse doublée dans un accord de sixte majeur`);
        } else if (e === '64') {
          if (cnt(f) < 2) add(i, `${m} : basse non doublée dans un accord de quarte et sixte`);
          if (!steps.includes(r)) add(i, `${m} : accord de quarte et sixte incomplet`);
        }
        if (q === 'A') add(i, `${m} : accord augmenté`);
      }
      if (ch.filter(n => pc(n) === sens).length > 1) add(i, `${m} : sensible doublée`);
    });
    for (let i = 0; i < P.length - 1; i++) {
      const a = P[i], b = P[i + 1], m = `accords ${i + 1}-${i + 2}`;
      for (let u = 0; u < 4; u++) for (let l = u + 1; l < 4; l++) {
        if (midi(a[u]) === midi(b[u]) && midi(a[l]) === midi(b[l])) continue;
        for (const [test, nm0] of [[isP5, '5tes'], [isP8, '8ves']]) {
          if (test(a[l], a[u]) && test(b[l], b[u])) {
            const same = (midi(b[u]) - midi(a[u])) * (midi(b[l]) - midi(a[l])) > 0;
            let nm = nm0;
            if (midi(a[u]) === midi(a[l]) && midi(b[u]) === midi(b[l])) nm = 'unissons';
            add(i + 0.5, `${m} : ${nm} ${same ? 'consécutives' : 'par mouvement contraire'} ${VOIX[u]}/${VOIX[l]}`);
          }
        }
      }
      const du = midi(b[0]) - midi(a[0]), dl = midi(b[3]) - midi(a[3]);
      if (du * dl > 0) for (const [test, nm] of [[isP5, '5te'], [isP8, '8ve']])
        if (test(b[3], b[0]) && !test(a[3], a[0]) && Math.abs(dpos(b[0]) - dpos(a[0])) > 1)
          add(i + 0.5, `${m} : ${nm} directe soprano/basse (soprano par saut)`);
      for (let v = 0; v < 3; v++)
        if (midi(b[v]) < midi(a[v + 1]) || midi(b[v + 1]) > midi(a[v])) add(i + 0.5, `${m} : chevauchement ${VOIX[v]}/${VOIX[v + 1]}`);
      for (const v of [0, 3])
        if (pc(a[v]) === sens && pc(b[v]) !== (sens + 1) % 12 && pc(b[v]) !== sens) add(i + 0.5, `${m} : sensible (${VOIX[v]}) non résolue sur la tonique`);
      for (let v = 0; v < 4; v++) {
        const d = dpos(b[v]) - dpos(a[v]), st = midi(b[v]) - midi(a[v]), ad = Math.abs(d), ast = Math.abs(st);
        if (ad === 1 && ast === 3) add(i + 0.5, `${m} : seconde augmentée (${VOIX[v]})`);
        if (ad === 3 && ast === 6) add(i + 0.5, `${m} : quarte augmentée (${VOIX[v]})`);
        if (ad === 6) add(i + 0.5, `${m} : saut de septième (${VOIX[v]})`);
        if (ad > 7) add(i + 0.5, `${m} : saut de plus d'une octave (${VOIX[v]})`);
        if (v < 3 && ad > 4 && !(ad === 7 && ast === 12) && !(ad === 5 && st > 0)) add(i + 0.5, `${m} : saut trop grand (${VOIX[v]})`);
      }
    }
    return errs;
  }

  // Même vérification, mais sur une réalisation en cours : les notes absentes valent null.
  // Les règles d'un accord ne s'appliquent qu'aux notes déjà écrites ; doublures et état
  // seulement quand l'accord est complet. Sur une réalisation complète, même résultat que verifier().
  function verifierPartiel(chords, tonic, allowThird) {
    const complet = ch => ch.every(Boolean);
    const errs = [];
    const add = (i, msg) => errs.push({i, msg});
    const sens = mod(pc(N(tonic + '4')) + 11, 12);
    chords.forEach((ch, i) => {
      if (complet(ch)) { verifier([ch], tonic, allowThird && new Set(allowThird).has(i) ? [0] : []).forEach(e => add(i, e.msg.replace('accord 1 :', `accord ${i + 1} :`))); return; }
      const m = `accord ${i + 1}`, P = ch.map(x => x ? N(x) : null);
      P.forEach((n, v) => {
        if (!n) return;
        const [lo, hi] = TESS[VOIX[v]].map(N);
        if (midi(n) < midi(lo) || midi(n) > midi(hi)) add(i, `${m} : ${VOIX[v]} hors tessiture (${nom(n)})`);
      });
      const pres = [0, 1, 2, 3].filter(v => P[v]);
      for (let k = 0; k < pres.length - 1; k++) { const u = pres[k], l = pres[k + 1]; if (midi(P[u]) < midi(P[l])) add(i, `${m} : croisement ${VOIX[u]}/${VOIX[l]}`); }
      if (P[0] && P[1] && dpos(P[0]) - dpos(P[1]) > 7) add(i, `${m} : écart soprano-alto supérieur à l'octave`);
      if (P[1] && P[2] && dpos(P[1]) - dpos(P[2]) > 7) add(i, `${m} : écart alto-ténor supérieur à l'octave`);
      if (P[2] && P[3] && dpos(P[2]) - dpos(P[3]) > 11) add(i, `${m} : écart ténor-basse supérieur à la douzième`);
      if (P.filter(n => n && pc(n) === sens).length > 1) add(i, `${m} : sensible doublée`);
    });
    for (let i = 0; i < chords.length - 1; i++) {
      const a = chords[i].map(x => x ? N(x) : null), b = chords[i + 1].map(x => x ? N(x) : null), m = `accords ${i + 1}-${i + 2}`;
      const ok = v => a[v] && b[v];
      for (let u = 0; u < 4; u++) for (let l = u + 1; l < 4; l++) {
        if (!ok(u) || !ok(l)) continue;
        if (midi(a[u]) === midi(b[u]) && midi(a[l]) === midi(b[l])) continue;
        for (const [test, nm0] of [[isP5, '5tes'], [isP8, '8ves']]) {
          if (test(a[l], a[u]) && test(b[l], b[u])) {
            const same = (midi(b[u]) - midi(a[u])) * (midi(b[l]) - midi(a[l])) > 0;
            let nm = nm0;
            if (midi(a[u]) === midi(a[l]) && midi(b[u]) === midi(b[l])) nm = 'unissons';
            add(i + 0.5, `${m} : ${nm} ${same ? 'consécutives' : 'par mouvement contraire'} ${VOIX[u]}/${VOIX[l]}`);
          }
        }
      }
      if (ok(0) && ok(3)) {
        const du = midi(b[0]) - midi(a[0]), dl = midi(b[3]) - midi(a[3]);
        if (du * dl > 0) for (const [test, nm] of [[isP5, '5te'], [isP8, '8ve']])
          if (test(b[3], b[0]) && !test(a[3], a[0]) && Math.abs(dpos(b[0]) - dpos(a[0])) > 1)
            add(i + 0.5, `${m} : ${nm} directe soprano/basse (soprano par saut)`);
      }
      for (let v = 0; v < 3; v++) {
        if (b[v] && a[v + 1] && midi(b[v]) < midi(a[v + 1])) add(i + 0.5, `${m} : chevauchement ${VOIX[v]}/${VOIX[v + 1]}`);
        else if (b[v + 1] && a[v] && midi(b[v + 1]) > midi(a[v])) add(i + 0.5, `${m} : chevauchement ${VOIX[v]}/${VOIX[v + 1]}`);
      }
      for (const v of [0, 3])
        if (ok(v) && pc(a[v]) === sens && pc(b[v]) !== (sens + 1) % 12 && pc(b[v]) !== sens) add(i + 0.5, `${m} : sensible (${VOIX[v]}) non résolue sur la tonique`);
      for (let v = 0; v < 4; v++) {
        if (!ok(v)) continue;
        const d = dpos(b[v]) - dpos(a[v]), st = midi(b[v]) - midi(a[v]), ad = Math.abs(d), ast = Math.abs(st);
        if (ad === 1 && ast === 3) add(i + 0.5, `${m} : seconde augmentée (${VOIX[v]})`);
        if (ad === 3 && ast === 6) add(i + 0.5, `${m} : quarte augmentée (${VOIX[v]})`);
        if (ad === 6) add(i + 0.5, `${m} : saut de septième (${VOIX[v]})`);
        if (ad > 7) add(i + 0.5, `${m} : saut de plus d'une octave (${VOIX[v]})`);
        if (v < 3 && ad > 4 && !(ad === 7 && ast === 12) && !(ad === 5 && st > 0)) add(i + 0.5, `${m} : saut trop grand (${VOIX[v]})`);
      }
    }
    return errs;
  }
  return {N, dpos, midi, pc, nom, texte, triad, etat, qualite, verifier, verifierPartiel, FR, SEMI, TESS, VOIX};
})();
if (typeof module !== 'undefined') module.exports = HV;
