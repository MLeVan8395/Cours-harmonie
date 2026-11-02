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

  // accords de 7e (et de 9e)
  function tetrade(ch) {
    const steps = new Set(ch.filter(Boolean).map(x => N(x).s));
    for (const r of [...steps].sort((a, b) => a - b)) {
      const t = (r + 2) % 7, f = (r + 4) % 7, s = (r + 6) % 7, nn = (r + 1) % 7;
      if (steps.has(t) && steps.has(s) && [...steps].every(x => [r, t, f, s, nn].includes(x))) return [r, t, f, s, steps.has(nn) ? nn : null];
    }
    return null;
  }
  function sixteAug(ch) {
    const L = ch.filter(Boolean).map(N);
    for (const a of L) for (const b of L) {
      if (mod(b.s - a.s, 7) === 5 && mod(pc(b) - pc(a), 12) === 10) {
        const pa = pc(a);
        const rest = [...new Set(L.map(n => mod(pc(n) - pa, 12)))].filter(x => x !== 0 && x !== 10).sort((x, y) => x - y).join(',');
        const t = {'4': 'it', '4,6': 'fr', '4,7': 'al'}[rest];
        if (t) return {type: t, b6: pa, s4: pc(b)};
      }
    }
    return null;
  }
  const vue = (ch, ped) => ped ? [ch[0], ch[1], ch[2], ch[2]] : ch.slice(0, 4);
  function info4(ch) {
    const te = tetrade(ch);
    if (!te || triad(ch) || sixteAug(ch)) return null;
    const [r, t, f, s, nn] = te;
    const notes = {}; ch.forEach(x => { const n = N(x); notes[n.s] = n; });
    const pr = pc(notes[r]), t3 = mod(pc(notes[t]) - pr, 12), t7 = mod(pc(notes[s]) - pr, 12);
    const t5 = notes[f] ? mod(pc(notes[f]) - pr, 12) : null;
    let q = '?';
    if (t3 === 4 && t7 === 10 && (t5 === 7 || t5 === null)) q = 'dom';
    else if (t3 === 4 && t7 === 11 && (t5 === 7 || t5 === null)) q = 'M7';
    else if (t3 === 3 && t7 === 10 && (t5 === 7 || t5 === null)) q = 'm7';
    else if (t3 === 3 && t7 === 10 && t5 === 6) q = 'ø';
    else if (t3 === 3 && t7 === 9 && (t5 === 6 || t5 === null)) q = 'o7';
    const b = N(ch[3]).s;
    let e = b === r ? '7' : b === t ? '65' : b === f ? '43' : b === s ? '2' : '9b';
    if (nn !== null && b === r) e = '9';
    return {r, t, f, s, nn, q, etat: e, pr};
  }
  const sensibleDe = tonic => mod(pc(N(tonic + '4')) + 11, 12);
  function familleDominante(A, sens) {
    if (!A) return null;
    if (A.q === 'dom') return (A.pr + 4) % 12;
    if (A.q === 'o7' || (A.q === 'ø' && A.pr === sens)) return A.pr;
    return null;
  }
  function racine(ch) {
    if (sixteAug(ch)) return null;
    const tr = triad(ch);
    if (tr) return pc(ch.map(N).find(n => n.s === tr[0]));
    const A = info4(ch);
    return A ? A.pr : null;
  }
  const tonsDe = (tonic, n) => Array.isArray(tonic) ? tonic : Array(n).fill(tonic);
  // règles propres aux accords de 7e entre deux accords complets (a, b : notes N ; A, B : info4)
  function regles7(a, b, A, B, sensA, sensB, meme, m, add, i) {
    const ls = familleDominante(A, sensA);
    if (A && !meme) {
      for (let v = 0; v < 4; v++) {
        if (!a[v] || !b[v]) continue;
        if (a[v].s === A.s) {
          const d = dpos(b[v]) - dpos(a[v]);
          const monte43 = A.etat === '43' && d === 1 && a[3] && b[3] && dpos(b[3]) - dpos(a[3]) === 1;
          if (d !== -1 && !monte43) add(i + 0.5, `${m} : septième (${VOIX[v]}) non résolue (elle descend d'un degré)`);
        }
        if (A.nn !== null && a[v].s === A.nn && dpos(b[v]) - dpos(a[v]) !== -1) add(i + 0.5, `${m} : neuvième (${VOIX[v]}) non résolue (elle descend d'un degré)`);
      }
      if (ls !== null && ls !== sensA)
        for (const v of [0, 3]) if (a[v] && b[v] && pc(a[v]) === ls && pc(b[v]) !== (ls + 1) % 12) add(i + 0.5, `${m} : sensible de l'accord (${VOIX[v]}) non résolue (elle monte d'un demi-ton)`);
    }
    if (B && familleDominante(B, sensB) === null && !meme)
      for (let v = 0; v < 4; v++) if (a[v] && b[v] && b[v].s === B.s && midi(a[v]) !== midi(b[v])) add(i + 0.5, `${m} : septième (${VOIX[v]}) non préparée`);
  }
  function regles6(a, b, X, Xb, m, add, i) {
    if (!X || (Xb && Xb.b6 === X.b6)) return;
    for (let v = 0; v < 4; v++) {
      if (!a[v] || !b[v]) continue;
      if (pc(a[v]) === X.b6 && midi(b[v]) !== midi(a[v]) - 1) add(i + 0.5, `${m} : sixte augmentée (${VOIX[v]}) non résolue (cette note descend d'un demi-ton)`);
      if (pc(a[v]) === X.s4 && midi(b[v]) !== midi(a[v]) + 1) add(i + 0.5, `${m} : sixte augmentée (${VOIX[v]}) non résolue (cette note monte d'un demi-ton)`);
    }
  }
  // règles d'un accord de 4 sons complet
  function regles4(ch, A, sens, m, add, i) {
    const steps = ch.map(n => n.s), cnt = x => steps.filter(s => s === x).length;
    if (A.q === '?') add(i, `${m} : accord de septième inusité`);
    if (cnt(A.s) > 1) add(i, `${m} : septième doublée`);
    if (A.nn !== null) {
      if (A.etat !== '9') add(i, `${m} : accord de neuvième renversé (la fondamentale reste à la basse)`);
      else if (cnt(A.nn) > 1) add(i, `${m} : neuvième doublée`);
      else { const v9 = steps.indexOf(A.nn); if (dpos(ch[v9]) - dpos(ch[3]) < 8) add(i, `${m} : neuvième trop près de la fondamentale (au moins une 9e au-dessus de la basse)`); if (ch.some(n => n.s === A.t && midi(n) > midi(ch[v9]))) add(i, `${m} : neuvième sous la sensible (elle se place au-dessus de la tierce)`); }
    } else if (A.etat === '7') {
      if (!steps.includes(A.f) && cnt(A.r) < 2) add(i, `${m} : sans la quinte, il faut doubler la fondamentale`);
    } else if (!steps.includes(A.f) || !steps.includes(A.r)) add(i, `${m} : accord de septième renversé incomplet`);
    const ls = familleDominante(A, sens);
    if (ls !== null && ls !== sens && ch.filter(n => pc(n) === ls).length > 1) add(i, `${m} : sensible doublée`);
  }

  // renvoie une liste de {i: indice d'accord (ou de l'enchaînement), msg}
  function verifier(chords, tonic, allowThird, libres, pedales) {
    pedales = new Set(pedales || []);
    allowThird = new Set(allowThird || []); libres = new Set(libres || []);
    const errs = [];
    const P = chords.map(ch => ch.map(N));
    const SENS = tonsDe(tonic, chords.length).map(sensibleDe);
    const TONS = tonsDe(tonic, chords.length);
    const VUE = chords.map((ch, i) => vue(ch, pedales.has(i)));
    const INFO = VUE.map(info4), S6 = chords.map(sixteAug);
    const add = (i, msg) => errs.push({i, msg});
    P.forEach((ch, i) => {
      const m = `accord ${i + 1}`, sens = SENS[i];
      ch.forEach((n, v) => {
        const [lo, hi] = TESS[VOIX[v]].map(N);
        if (midi(n) < midi(lo) || midi(n) > midi(hi)) add(i, `${m} : ${VOIX[v]} hors tessiture (${nom(n)})`);
      });
      for (let v = 0; v < 3; v++) if (midi(ch[v]) < midi(ch[v + 1])) add(i, `${m} : croisement ${VOIX[v]}/${VOIX[v + 1]}`);
      if (dpos(ch[0]) - dpos(ch[1]) > 7) add(i, `${m} : écart soprano-alto supérieur à l'octave`);
      if (dpos(ch[1]) - dpos(ch[2]) > 7) add(i, `${m} : écart alto-ténor supérieur à l'octave`);
      if (dpos(ch[2]) - dpos(ch[3]) > 11) add(i, `${m} : écart ténor-basse supérieur à la douzième`);
      const tr = triad(VUE[i]);
      if (S6[i]) {
        const X = S6[i];
        if (ch.filter(n => pc(n) === X.b6).length > 1 || ch.filter(n => pc(n) === X.s4).length > 1) add(i, `${m} : note de la sixte augmentée doublée`);
      } else if (pedales.has(i)) {
        const hs = new Set(ch.slice(0, 3).map(n => n.s));
        if (tr) { if (hs.size < 3) add(i, `${m} : accord incomplet au-dessus de la pédale`); }
        else if (!INFO[i] || !['dom', 'o7', 'ø'].includes(INFO[i].q)) add(i, `${m} : accord non reconnu au-dessus de la pédale`);
      } else if (!tr) { if (INFO[i]) regles4(ch, INFO[i], sens, m, add, i); else add(i, `${m} : accord non reconnu (vérifie la fondamentale et la tierce)`); }
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
          const napo = racine(chords[i]) === (pc(N(TONS[i] + '4')) + 1) % 12;
          if (cnt(t) > 1 && q === 'M' && !napo) add(i, `${m} : basse doublée dans un accord de sixte majeur`);
        } else if (e === '64') {
          if (cnt(f) < 2) add(i, `${m} : basse non doublée dans un accord de quarte et sixte`);
          if (!steps.includes(r)) add(i, `${m} : accord de quarte et sixte incomplet`);
        }
        if (q === 'A') add(i, `${m} : accord augmenté`);
      }
      if (ch.filter(n => pc(n) === sens).length > 1) add(i, `${m} : sensible doublée`);
    });
    for (let i = 0; i < P.length - 1; i++) {
      const a = P[i], b = P[i + 1], m = `accords ${i + 1}-${i + 2}`, sens = SENS[i];
      const ra = racine(VUE[i]), meme = ra !== null && ra === racine(VUE[i + 1]);
      if (ra !== null && !S6[i] && !pedales.has(i) && triad(VUE[i]) && qualite(VUE[i]) === 'M' && ra === (pc(N(TONS[i] + '4')) + 1) % 12 && !meme)
        for (let v = 0; v < 4; v++) if (pc(a[v]) === ra && dpos(b[v]) >= dpos(a[v])) add(i + 0.5, `${m} : 2e degré abaissé (${VOIX[v]}) non résolu (il descend)`);
      regles6(a, b, S6[i], S6[i + 1], m, add, i);
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
        if (pc(a[v]) === sens && pc(b[v]) !== (sens + 1) % 12 && pc(b[v]) !== sens && !meme && !libres.has(i)) add(i + 0.5, `${m} : sensible (${VOIX[v]}) non résolue sur la tonique`);
      regles7(a, b, INFO[i], INFO[i + 1], sens, SENS[i + 1], meme, m, add, i);
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
  function verifierPartiel(chords, tonic, allowThird, libres, pedales) {
    pedales = new Set(pedales || []);
    libres = new Set(libres || []);
    const complet = ch => ch.every(Boolean);
    const errs = [];
    const add = (i, msg) => errs.push({i, msg});
    const TONS = tonsDe(tonic, chords.length), SENS = TONS.map(sensibleDe);
    chords.forEach((ch, i) => {
      const sens = SENS[i];
      if (complet(ch)) { verifier([ch], TONS[i], allowThird && new Set(allowThird).has(i) ? [0] : [], [], pedales.has(i) ? [0] : []).forEach(e => add(i, e.msg.replace('accord 1 :', `accord ${i + 1} :`))); return; }
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
      const ok = v => a[v] && b[v], sens = SENS[i];
      const ca = complet(chords[i]), cb = complet(chords[i + 1]);
      const va = ca ? vue(chords[i], pedales.has(i)) : null, vb = cb ? vue(chords[i + 1], pedales.has(i + 1)) : null;
      const ra = ca ? racine(va) : null, meme = ra !== null && cb && ra === racine(vb);
      if (ca) regles6(a, b, sixteAug(chords[i]), cb ? sixteAug(chords[i + 1]) : null, m, add, i);
      if (ca && !sixteAug(chords[i]) && !pedales.has(i) && triad(va) && qualite(va) === 'M' && ra === (pc(N(TONS[i] + '4')) + 1) % 12 && !meme)
        for (let v = 0; v < 4; v++) if (a[v] && b[v] && pc(a[v]) === ra && dpos(b[v]) >= dpos(a[v])) add(i + 0.5, `${m} : 2e degré abaissé (${VOIX[v]}) non résolu (il descend)`);
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
        if (ok(v) && pc(a[v]) === sens && pc(b[v]) !== (sens + 1) % 12 && pc(b[v]) !== sens && !meme && !libres.has(i)) add(i + 0.5, `${m} : sensible (${VOIX[v]}) non résolue sur la tonique`);
      regles7(a, b, ca ? info4(va) : null, cb ? info4(vb) : null, sens, SENS[i + 1], meme, m, add, i);
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
  return {N, dpos, midi, pc, nom, texte, triad, etat, qualite, tetrade, info4, sixteAug, racine, familleDominante, sensibleDe, verifier, verifierPartiel, FR, SEMI, TESS, VOIX};
})();
if (typeof module !== 'undefined') module.exports = HV;
