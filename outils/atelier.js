// Atelier : exercices d'harmonie à remplir directement sur la portée.
// Dépend de HV (verif.js), de GLYPH (symboles musicaux) et de lireMusique / jouerNotes (lecteur).
const Atelier = (() => {
  const SP = 10, H = 5, BOTTOM = {treble: 30, bass: 18};
  const INK = '#111', MUTED = '#666', FONT = 'Verdana, Geneva, DejaVu Sans, sans-serif';
  const COUL = ['#c0392b', '#c96a00', '#1e7b34', '#1f4e8c'];
  const NOMV = ['Soprano', 'Alto', 'Ténor', 'Basse'];
  const STAFF = [0, 0, 1, 1];
  const SHARP_ORDER = [3, 0, 4, 1, 5, 2, 6], FLAT_ORDER = [6, 2, 5, 1, 4, 0, 3];
  const SHARP_POS = [38, 35, 39, 36, 33, 37, 34], FLAT_POS = [34, 37, 33, 36, 32, 35, 31];
  const CLEF_SHIFT = {treble: 0, bass: -14};
  const MAJ = {Do: 0, Sol: 1, 'Ré': 2, La: 3, Mi: 4, Si: 5, Fa: -1, Sib: -2, Mib: -3, Lab: -4};
  const LETTRE = ['C', 'D', 'E', 'F', 'G', 'A', 'B'];
  const mod = (a, b) => ((a % b) + b) % b;
  const N = HV.N, dpos = HV.dpos, midi = HV.midi;

  function keyAlts(k) {
    const d = {};
    if (k > 0) SHARP_ORDER.slice(0, k).forEach(s => d[s] = 1);
    if (k < 0) FLAT_ORDER.slice(0, -k).forEach(s => d[s] = -1);
    return d;
  }
  function glyph(name, x, y, size, color) {
    const g = GLYPH[name], k = size / g.upm;
    return `<path d="${g.d}" transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(${k.toFixed(5)} ${(-k).toFixed(5)})" fill="${color || INK}"/>`;
  }
  function nomAccord(ch) {
    const tr = HV.triad(ch);
    if (!tr) {
      const A = HV.info4(ch); if (!A) return '?';
      const r = ch.map(N).find(n => n.s === A.r);
      const suf = A.nn !== null ? '9' : ({dom: '7', M7: 'maj7', m7: 'm7', 'ø': 'm7♭5', o7: '°7'}[A.q] || '7');
      return LETTRE[r.s] + (r.a === 1 ? '♯' : r.a === -1 ? '♭' : '') + suf;
    }
    const r = ch.map(N).find(n => n.s === tr[0]);
    const q = HV.qualite(ch);
    return LETTRE[r.s] + (r.a === 1 ? '♯' : r.a === -1 ? '♭' : '') + ({m: 'm', d: '°', A: '+'}[q] || '');
  }

  // ------------------------------------------------------------------ gravure
  function graver(E) {
    const ex = E.ex, unit = ex.rythme ? 40 : 24, nks = Math.abs(ex.armure), avecMesure = ex.rythme || ex.durees.some(d => d < 4);
    const left = 70 + nks * 11 + (avecMesure ? 22 : 0), x0 = 16;
    const t = []; let acc = 0; ex.durees.forEach(d => { t.push(acc); acc += d; });
    const beats = acc, endX = left + beats * unit + 4, W = endX + 14;
    const top0 = 56, gap = 104, ys = [top0, top0 + gap], sysTop = ys[0], sysBot = ys[1] + 4 * SP;
    const clefs = ['treble', 'bass'];
    const o = [], fond = [];
    const xCol = i => left + t[i] * unit + (ex.durees[i] >= 4 ? unit * 2 - 6 : unit * 0.5);
    // colonnes vérifiées
    if (E.resultat) {
      ex.durees.forEach((d, i) => {
        const xa = left + t[i] * unit - 4, xb = left + (t[i] + d) * unit - 8;
        const mauvais = E.resultat.mauvais.has(i), lien = E.resultat.liens.has(i);
        const col = mauvais ? '#c0392b' : lien ? '#c96a00' : '#1e7b34';
        const rempli = ex.voix.every(v => E.notes[i][v]) || (etapeCourante(E) && etapeCourante(E).type === 'degres');
        if (!mauvais && !lien && !rempli) return;
        fond.push(`<rect x="${xa}" y="${sysTop - 16}" width="${xb - xa}" height="${sysBot - sysTop + 32}" rx="6" fill="${col}" fill-opacity="${mauvais || lien ? 0.12 : 0.06}"/>`);
      });
    }
    ys.forEach((top, k) => {
      for (let l = 0; l < 5; l++) o.push(`<line x1="${x0}" y1="${top + l * SP}" x2="${endX}" y2="${top + l * SP}" stroke="${INK}"/>`);
      o.push(k === 0 ? glyph('treble', x0 + 4, top + 31, 40) : glyph('bass', x0 + 6, top + 32.5, 34));
      let kx = x0 + 42;
      const pos = ex.armure > 0 ? SHARP_POS : FLAT_POS;
      for (let j = 0; j < nks; j++) {
        const p = pos[j] + CLEF_SHIFT[clefs[k]], y = top + 4 * SP - (p - BOTTOM[clefs[k]]) * H;
        o.push(glyph(ex.armure > 0 ? 'sharp' : 'flat', kx, y + (ex.armure > 0 ? 5 : 3), 15)); kx += 11;
      }
      if (avecMesure) [[2, ex.mesure || 4], [4, 4]].forEach(([dy, chiffre]) => o.push(`<text x="${kx + 8}" y="${top + dy * SP - 1}" text-anchor="middle" font-family="${FONT}" font-weight="700" font-size="21" fill="${INK}">${chiffre}</text>`));
    });
    o.push(`<line x1="${x0}" y1="${sysTop}" x2="${x0}" y2="${sysBot}" stroke="${INK}" stroke-width="1.3"/>`);
    // accolade
    { const x = x0 - 12, y1 = sysTop - 1, y2 = sysBot + 1, h = y2 - y1, m = (y1 + y2) / 2, w = 9;
      o.push(`<path d="M${x + w} ${y1} C${x} ${y1 + h * .08} ${x + w * .95} ${m - h * .12} ${x} ${m} C${x + w * .95} ${m + h * .12} ${x} ${y2 - h * .08} ${x + w} ${y2} C${x + 3} ${y2 - h * .1} ${x + w * .95 + 3.5} ${m + h * .1} ${x + 3.2} ${m} C${x + w * .95 + 3.5} ${m - h * .1} ${x + 3} ${y1 + h * .1} ${x + w} ${y1} Z" fill="${INK}"/>`); }
    const MES = ex.mesure || 4, ANA = ex.anacrouse || 0;
    for (let b = ANA || MES; b <= beats + 1e-9; b += MES) {
      const x = left + b * unit - 6;
      if (Math.abs(b - beats) < 1e-9) o.push(`<line x1="${x - 4}" y1="${sysTop}" x2="${x - 4}" y2="${sysBot}" stroke="${INK}"/><line x1="${x}" y1="${sysTop}" x2="${x}" y2="${sysBot}" stroke="${INK}" stroke-width="3.5"/>`);
      else o.push(`<line x1="${x}" y1="${sysTop}" x2="${x}" y2="${sysBot}" stroke="${INK}"/>`);
    }
    // notes : chaque accord peut contenir, par voix, une noire (ou plus) ou deux croches
    const kA = keyAlts(ex.armure), accState = {};
    let ext = [sysTop, sysBot];
    const tetes = {};
    const items = [];
    E.notes.forEach((ch, i) => {
      const d = ex.durees[i], xs = left + t[i] * unit;
      [0, 1, 2, 3].forEach(v => {
        if (!ch[v]) return;
        const x2 = ex.rythme ? E.extra[i][v] : null;
        if (x2 && x2.b) {
          items.push({i, v, h: 0, n: ch[v], d: d / 2, x: xs + unit * 0.27, t: t[i]});
          items.push({i, v, h: 1, n: x2.b, d: d / 2, x: xs + unit * 0.73, t: t[i] + d / 2});
        } else items.push({i, v, h: 0, n: ch[v], d, x: xCol(i), t: t[i]});
      });
    });
    // secondes et unissons sur une même portée
    items.forEach(a => { a.dx = 0; a.partage = false; });
    items.forEach(a => items.forEach(b => {
      if (a === b || STAFF[a.v] !== STAFF[b.v] || Math.abs(a.x - b.x) > 1 || a.v >= b.v) return;
      const da = dpos(N(a.n)) - dpos(N(b.n));
      if (da === 1) a.dx = 13;
      else if (da === 0) { if (a.d >= 4 || N(a.n).a !== N(b.n).a || (a.d >= 2) !== (b.d >= 2)) a.dx = 15; else b.partage = true; }
    }));
    const croches = [];
    items.sort((a, b) => a.t - b.t || a.v - b.v).forEach(it => {
      const {i, v, h, d} = it, n = N(it.n), st = STAFF[v], top = ys[st], clef = clefs[st], p = dpos(n), bot = BOTTOM[clef];
      const y = top + 4 * SP - (p - bot) * H, x = it.x + it.dx;
      const col = ex.voix.includes(v) ? COUL[v] : INK;
      it.y = y; it.xx = x; it.col = col;
      tetes[i + ',' + v + ',' + h] = [x, y];
      ext = [Math.min(ext[0], y - 8), Math.max(ext[1], y + 8)];
      for (let q = bot - 2; q >= p; q -= 2) { const yy = top + 4 * SP - (q - bot) * H; o.push(`<line x1="${x - 11}" y1="${yy}" x2="${x + 11}" y2="${yy}" stroke="${INK}"/>`); }
      for (let q = bot + 10; q <= p; q += 2) { const yy = top + 4 * SP - (q - bot) * H; o.push(`<line x1="${x - 11}" y1="${yy}" x2="${x + 11}" y2="${yy}" stroke="${INK}"/>`); }
      const key = st + ',' + Math.floor((it.t - ANA) / MES) + ',' + n.s + ',' + n.o;
      const prev = key in accState ? accState[key] : (kA[n.s] || 0);
      if (n.a !== prev) {
        o.push(glyph(n.a === 1 ? 'sharp' : n.a === -1 ? 'flat' : 'natural', x - 19 - (it.dx === 0 && items.some(b => b !== it && STAFF[b.v] === st && Math.abs(b.x - it.x) < 1 && b.dx > 0) ? 0 : 0), y + (n.a === -1 ? 3 : 5), 15, col));
        accState[key] = n.a;
      }
      const plein = ex.rythme ? d < 2 : false;
      if (!it.partage) {
        if (d >= 4) o.push(`<ellipse cx="${x}" cy="${y}" rx="7" ry="4.6" fill="none" stroke="${col}" stroke-width="2.6" transform="rotate(-15 ${x} ${y})"/>`);
        else if (plein) o.push(`<ellipse cx="${x}" cy="${y}" rx="6" ry="4.2" fill="${col}" transform="rotate(-25 ${x} ${y})"/>`);
        else o.push(`<ellipse cx="${x}" cy="${y}" rx="6" ry="4.2" fill="none" stroke="${col}" stroke-width="1.8" transform="rotate(-25 ${x} ${y})"/>`);
      }
      const up = v === 0 || v === 2, hx = it.partage ? x - 0 : x;
      if (d < 1) croches.push({i, v, h, x: hx, y, up, col});
      else if (d < 4) {
        if (up) { o.push(`<line x1="${hx + 5.6}" y1="${y}" x2="${hx + 5.6}" y2="${y - 32}" stroke="${col}" stroke-width="1.3"/>`); ext[0] = Math.min(ext[0], y - 32); }
        else { o.push(`<line x1="${hx - 5.6}" y1="${y}" x2="${hx - 5.6}" y2="${y + 32}" stroke="${col}" stroke-width="1.3"/>`); ext[1] = Math.max(ext[1], y + 32); }
      }
      if (E.sel && E.sel[0] === i && E.sel[1] === v && (E.sel[2] || 0) === h)
        o.push(`<circle cx="${x}" cy="${y}" r="11" fill="none" stroke="${col}" stroke-width="1.5" stroke-dasharray="3 2"/>`);
      const role = E.roles && E.roles[i + ',' + v + ',' + h];
      if (role && role !== 'R') {
        const txt = {p: 'p', b: 'b', r: 'r', app: 'app', e: 'é', ant: 'ant', '?': '?'}[role];
        o.push(`<text x="${x + 8}" y="${up ? y - 7 : y + 15}" font-family="${FONT}" font-size="10" font-style="italic" font-weight="700" fill="${role === '?' ? '#c0392b' : '#1e7b34'}">${txt}</text>`);
      }
    });
    // ligatures des croches (par temps et par voix)
    const groupes = {};
    croches.forEach(c => { (groupes[c.i + ',' + c.v] = groupes[c.i + ',' + c.v] || []).push(c); });
    Object.values(groupes).forEach(g => {
      g.sort((a, b) => a.h - b.h);
      const up = g[0].up, by = up ? Math.min(...g.map(c => c.y)) - 30 : Math.max(...g.map(c => c.y)) + 30;
      const xs2 = g.map(c => c.x + (up ? 5.6 : -5.6));
      g.forEach((c, k) => o.push(`<line x1="${xs2[k]}" y1="${c.y}" x2="${xs2[k]}" y2="${by}" stroke="${c.col}" stroke-width="1.3"/>`));
      if (g.length > 1) o.push(`<line x1="${xs2[0]}" y1="${by}" x2="${xs2[g.length - 1]}" y2="${by}" stroke="${g[0].col}" stroke-width="4.5"/>`);
      else o.push(`<path d="M${xs2[0]} ${by} q 3 ${up ? 8 : -8} 9 ${up ? 12 : -12}" fill="none" stroke="${g[0].col}" stroke-width="1.6"/>`);
      ext = [Math.min(ext[0], by), Math.max(ext[1], by)];
    });
    // liaisons (retards)
    if (ex.rythme) E.notes.forEach((ch, i) => [0, 1, 2, 3].forEach(v => {
      if (!i || !E.extra[i][v].lie) return;
      const pr = E.extra[i - 1][v].b ? tetes[(i - 1) + ',' + v + ',1'] : tetes[(i - 1) + ',' + v + ',0'], cu = tetes[i + ',' + v + ',0'];
      if (!pr || !cu) return;
      const dy = (v === 0 || v === 2) ? 8 : -8;
      o.push(`<path d="M${pr[0] + 6} ${pr[1] + dy} Q${(pr[0] + cu[0]) / 2} ${pr[1] + dy * 2.4} ${cu[0] - 6} ${cu[1] + dy}" fill="none" stroke="${ex.voix.includes(v) ? COUL[v] : INK}" stroke-width="1.6"/>`);
    }));
    // note fantôme (survol)
    if (E.fantome) {
      const [i, v, nn, fh] = E.fantome, n = N(nn), st = STAFF[v], top = ys[st], bot = BOTTOM[clefs[st]];
      const y = top + 4 * SP - (dpos(n) - bot) * H;
      const x = ex.rythme && E.extra[i][v].b ? left + t[i] * unit + unit * (fh ? 0.73 : 0.27) : xCol(i);
      o.push(`<ellipse cx="${x}" cy="${y}" rx="7" ry="4.6" fill="none" stroke="${COUL[v]}" stroke-width="2" opacity=".45" transform="rotate(-15 ${x} ${y})"/>`);
      for (let q = bot - 2; q >= dpos(n); q -= 2) { const yy = top + 4 * SP - (q - bot) * H; o.push(`<line x1="${x - 11}" y1="${yy}" x2="${x + 11}" y2="${yy}" stroke="${COUL[v]}" opacity=".45"/>`); }
      for (let q = bot + 10; q <= dpos(n); q += 2) { const yy = top + 4 * SP - (q - bot) * H; o.push(`<line x1="${x - 11}" y1="${yy}" x2="${x + 11}" y2="${yy}" stroke="${COUL[v]}" opacity=".45"/>`); }
    }
    // numéros d'accords, degrés, chiffrage
    const lab = [];
    if (!ex.sansNumeros) ex.durees.forEach((d, i) => lab.push(`<text x="${xCol(i)}" y="${Math.min(sysTop - 24, ext[0] - 10)}" text-anchor="middle" font-family="${FONT}" font-size="10" fill="${MUTED}">${i + 1}</text>`));
    const base = Math.max(sysBot + 34, ext[1] + 24);
    let rangs = 0;
    const etape = etapeCourante(E);
    const degres = ex.guide && !(ex.degres && !ex.guide.some(g => g.type === 'degres')) ? ex.durees.map((d, i) => etape && etape.type === 'degres' && !E.fini ? '@' : (E.degres[i] !== null && E.degres[i] !== undefined ? libDeg(ex, E.degres[i]) : '?')) : ex.degres;
    const chiffres = ex.chiffres || (ex.guide ? E.notes.map((c, i) => chiffreVivant(E, i)) : null);
    [[degres, 0], [chiffres, 1]].forEach(([vals, r]) => {
      if (!vals) return;
      const y = base + rangs * 30; rangs++;
      vals.forEach((txt, i) => {
        if (!txt) return;
        const x = xCol(i);
        if (txt === '@') {   // menu pour choisir le degré
          const opts = (ex.menu ? ex.menu.map(m => m[0]) : DEGN.slice(0, 6)).map((d, k) => `<option value="${k}">${d}</option>`).join('');
          const lw = ex.menu ? Math.max(48, Math.min(unit * (ex.durees[i] >= 4 ? 4 : ex.durees[i]) - 4, 66)) : 48;
          lab.push(`<foreignObject x="${x - lw / 2}" y="${y - 19}" width="${lw}" height="26"><select xmlns="http://www.w3.org/1999/xhtml" data-deg="${i}" style="width:${lw}px;height:24px;font:700 13px Verdana,sans-serif;color:#1f4e8c;border:1.5px solid #1f4e8c;border-radius:6px;background:#fff;padding:0"><option value="">?</option>${opts}</select></foreignObject>`);
        } else if (/^\d\/\d$/.test(txt)) {
          const [a, b] = txt.split('/');
          lab.push(`<text x="${x}" y="${y - 8}" text-anchor="middle" font-family="${FONT}" font-size="12" font-weight="700" fill="#1f4e8c">${a}</text><text x="${x}" y="${y + 6}" text-anchor="middle" font-family="${FONT}" font-size="12" font-weight="700" fill="#1f4e8c">${b}</text>`);
        } else lab.push(`<text x="${x}" y="${y}" text-anchor="middle" font-family="${FONT}" font-size="${r === 0 ? 14 : 13}" font-weight="700" fill="${txt === '?' ? '#aaa' : '#1f4e8c'}">${txt}</text>`);
      });
    });
    const haut = Math.max(0, 40 - Math.min(sysTop - 24, ext[0] - 10));
    const Ht = Math.max(sysBot, ext[1] - 12) + 46 + 30 * Math.max(0, rangs - 1) + haut;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 ${-haut} ${W} ${Ht}" width="${Math.round(W * 1.35)}" style="height:auto;touch-action:manipulation;display:block"><rect x="0" y="${-haut}" width="${W}" height="${Ht}" fill="white"/>${fond.join('')}${o.join('')}${lab.join('')}</svg>`;
    E.geo = {left, unit, t, ys, xCol, clefs, W, Ht, haut};
    return svg;
  }

  // ------------------------------------------------------------------ interaction
  function point(E, ev) {
    const svg = E.portee.querySelector('svg'), r = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal;
    const x = (ev.clientX - r.left) * vb.width / r.width + vb.x, y = (ev.clientY - r.top) * vb.height / r.height + vb.y;
    const g = E.geo, ex = E.ex;
    const beat = (x - g.left + 6) / g.unit;
    let i = -1;
    ex.durees.forEach((d, k) => { if (beat >= g.t[k] && beat < g.t[k] + d) i = k; });
    if (i < 0) return null;
    if (!editables(E).length) return null;
    // clic sur une note existante d'une voix modifiable : on la sélectionne
    for (const v of editables(E)) {
      const n = E.notes[i][v]; if (!n || v === E.voix) continue;
      const st = STAFF[v], top = g.ys[st], yy = top + 4 * SP - (dpos(N(n)) - BOTTOM[g.clefs[st]]) * H;
      if (Math.abs(yy - y) <= 4 && Math.abs(g.xCol(i) - x) <= 18) return {i, v, sur: true};
    }
    const v = E.voix, st = STAFF[v], top = g.ys[st];
    const p = Math.round((top + 4 * SP - y) / H) + BOTTOM[g.clefs[st]];
    const [lo, hi] = HV.TESS[HV.VOIX[v]].map(x => dpos(N(x)));
    if (p < lo - 4 || p > hi + 4) return null;
    const s = mod(p, 7), o = Math.floor(p / 7), a = keyAlts(ex.armure)[s] || 0;
    const h = ex.rythme && E.extra[i][v].b && beat >= g.t[i] + ex.durees[i] / 2 ? 1 : 0;
    return {i, v, h, n: HV.FR[s] + (a === 1 ? '#' : a === -1 ? 'b' : '') + o};
  }
  // note écrite (première ou deuxième croche)
  function lireN(E, i, v, h) { return h ? (E.extra[i][v] && E.extra[i][v].b) : E.notes[i][v]; }
  function ecrireN(E, i, v, h, n) {
    if (h) E.extra[i][v].b = n;
    else {
      E.notes[i][v] = n;
      if (E.ex.rythme && i + 1 < E.notes.length && E.extra[i + 1][v].lie && !E.extra[i][v].b) E.notes[i + 1][v] = n;
      if (E.ex.rythme && !n) E.extra[i][v].b = null;
    }
    if (E.ex.rythme && h && i + 1 < E.notes.length && E.extra[i + 1][v].lie) E.notes[i + 1][v] = n;
  }
  function dessiner(E) {
    E.portee.innerHTML = graver(E);
    const ed = editables(E);
    E.boutonsVoix.forEach(b => { const v = +b.dataset.v; b.hidden = !ed.includes(v); b.classList.toggle('on', v === E.voix); });
    E.outils.hidden = !ed.length;
    E.portee.querySelectorAll('select[data-deg]').forEach(sel => {
      const i = +sel.dataset.deg;
      if (E.degres[i] !== null && E.degres[i] !== undefined) sel.value = E.degres[i];
      sel.onchange = () => { E.degres[i] = sel.value === '' ? null : +sel.value; analyser(E); dessiner(E); };
    });
    sauver(E);
  }
  function entendreAccord(E, i) {
    if (typeof jouerNotes === 'function')
      jouerNotes(E.notes[i].filter(Boolean).map(n => ({m: midi(N(n)), t: 0, d: 2})));
  }
  function poser(E, i, v, n, h) {
    h = h || 0;
    ecrireN(E, i, v, h, n); E.sel = [i, v, h];
    if (E.ex.corriger) { E.resultat = null; E.fb.className = 'fb'; E.fb.innerHTML = ''; }
    else analyser(E);
    dessiner(E); entendreAccord(E, i);
  }
  function alterer(E, a) {
    if (!E.sel) return;
    const [i, v, h] = E.sel, s = lireN(E, i, v, h); if (!s || !editables(E).includes(v)) return;
    const n = N(s); n.a = a; poser(E, i, v, HV.texte(n), h);
  }
  function deplacer(E, pas) {
    if (!E.sel) return;
    const [i, v, h] = E.sel, s = lireN(E, i, v, h); if (!s || !editables(E).includes(v)) return;
    const p = dpos(N(s)) + pas, sd = mod(p, 7), a = keyAlts(E.ex.armure)[sd] || 0;
    poser(E, i, v, HV.FR[sd] + (a === 1 ? '#' : a === -1 ? 'b' : '') + Math.floor(p / 7), h);
  }
  // deux croches / une noire
  function couperTemps(E) {
    if (!E.sel || !E.ex.rythme) return;
    const [i, v] = E.sel, x = E.extra[i][v];
    if (!editables(E).includes(v) || !E.notes[i][v]) return;
    if (x.b) { x.b = null; E.sel = [i, v, 0]; } else { x.b = E.notes[i][v]; E.sel = [i, v, 1]; }
    if (!E.ex.corriger) analyser(E); dessiner(E);
  }
  // lier la première note du temps à la note précédente (préparation d'un retard)
  function lier(E) {
    if (!E.sel || !E.ex.rythme) return;
    const [i, v] = E.sel;
    if (!i || !editables(E).includes(v)) return;
    const x = E.extra[i][v];
    x.lie = !x.lie;
    if (x.lie) {
      const pr = lireN(E, i - 1, v, E.extra[i - 1][v].b ? 1 : 0);
      if (pr) { E.notes[i][v] = pr; if (!x.b) { x.b = null; } }
    }
    E.sel = [i, v, 0];
    if (!E.ex.corriger) analyser(E); dessiner(E);
  }

  // ------------------------------------------------------------------ degrés et accords attendus
  const DEGN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'];
  const GRAMMAIRE = {0: [1, 3, 4, 5], 1: [4, 0], 3: [0, 1, 4], 4: [0, 5], 5: [1, 3, 4], 2: [3, 5]};
  function mode(ex) { return MAJ[ex.tonique] === ex.armure ? 'majeur' : 'mineur'; }
  function noteDegre(ex, k) {
    const s = (HV.FR.indexOf(ex.tonique) + k) % 7;
    let a = keyAlts(ex.armure)[s] || 0;
    if (mode(ex) === 'mineur' && k % 7 === 6) a += 1;
    return {s, a};
  }
  const pcN = n => mod(HV.SEMI[n.s] + n.a, 12);
  const txtN = n => HV.FR[n.s] + (n.a === 1 ? '♯' : n.a === -1 ? '♭' : '');
  function accordDegre(ex, d) { return [noteDegre(ex, d), noteDegre(ex, d + 2), noteDegre(ex, d + 4)]; }
  const notesDe = names => names.map(x => N(x + '4'));
  function libDeg(ex, d) { return ex.menu ? ex.menu[d][0] : DEGN[d]; }
  function accordChoisi(ex, d) { return ex.menu ? notesDe(ex.menu[d][1]) : accordDegre(ex, d); }
  function nomDegre(ex, d) { if (ex.menu) return nomAccord(ex.menu[d][1].map(x => x + '4')) + ' (' + ex.menu[d][0] + ')'; return nomAccord(accordDegre(ex, d).map(n => HV.FR[n.s] + (n.a === 1 ? '#' : n.a === -1 ? 'b' : '') + '4')) + ' (' + DEGN[d] + ')'; }
  function degreDe(ex, ch) {   // degré d'un accord écrit (solution)
    const tr = HV.triad(ch), r = ch.map(N).find(n => n.s === tr[0]);
    return mod(r.s - HV.FR.indexOf(ex.tonique), 7);
  }
  function attendu(E, i) {     // [fondamentale, tierce, quinte (, septième, neuvième)] attendues pour l'accord i, ou null
    const ex = E.ex;
    const etapeDeg = ex.guide && ex.guide.some(g => g.type === 'degres');
    if (ex.accords && !etapeDeg) return notesDe(ex.accords[i]);
    if (ex.guide && !etapeDeg && !ex.chant) return accordDegre(ex, degreDe(ex, ex.solution[i]));
    if (ex.harmonie && !ex.guide) return accordChoisi(ex, ex.harmonie[i]);
    if (ex.guide) return E.degres[i] === null || E.degres[i] === undefined ? null : accordChoisi(ex, E.degres[i]);
    if (ex.chant) return null;
    return accordDegre(ex, degreDe(ex, ex.solution[i]));
  }
  function chiffreVivant(E, i) {
    const a = attendu(E, i), b = E.notes[i][3];
    if (!a || !b) return '';
    const p = HV.pc(N(b));
    if (a.length >= 4) {
      const iv = [1, 2, 3].map(k => mod(pcN(a[k]) - pcN(a[0]), 12)).join(',');
      const q = iv === '4,7,10' ? 'dom' : iv === '3,6,9' ? 'o7' : '';
      if (a.length === 5) return p === pcN(a[0]) ? '9+' : '';
      return p === pcN(a[0]) ? (q === 'dom' ? '7+' : q === 'o7' ? '7°' : '7') : p === pcN(a[1]) ? '6/5'
        : p === pcN(a[2]) ? (q === 'dom' ? '+6' : '4/3') : p === pcN(a[3]) ? (q === 'dom' ? '+4' : '2') : '';
    }
    return p === pcN(a[0]) ? '5' : p === pcN(a[1]) ? '6' : p === pcN(a[2]) ? '6/4' : '';
  }

  // ------------------------------------------------------------------ correction au fil de l'écriture
  function etapeCourante(E) { return E.ex.guide ? E.ex.guide[E.etape] : null; }
  function editables(E) {
    const et = etapeCourante(E);
    if (E.fini) return [];
    if (!et) return E.ex.voix;
    return et.type === 'voix' ? et.voix : [];
  }
  function tierceVoulue(E) {
    const ex = E.ex, ton = HV.pc(N(ex.tonique + '4')), vi = mode(ex) === 'majeur' ? 9 : 8;
    const racine = i => { const a = attendu(E, i); if (a) return mod(pcN(a[0]) - ton, 12); const ch = E.notes[i]; if (!ch.every(Boolean)) return null; const tr = HV.triad(ch); if (!tr) return null; return mod(HV.pc(ch.map(N).find(x => x.s === tr[0])) - ton, 12); };
    const t = new Set(ex.tierce);
    E.notes.forEach((ch, i) => {
      if (racine(i) === vi && ((i > 0 && racine(i - 1) === 7) || (i < E.notes.length - 1 && racine(i + 1) === 7))) t.add(i);
    });
    return [...t];
  }
  function fautesDegres(E) {
    const ex = E.ex, errs = [], conseils = [];
    const n = E.notes.length;
    E.degres.forEach((d, i) => {
      if (d === null || d === undefined) return;
      const m = `accord ${i + 1}`;
      if (!ex.chant) {
        const juste = ex.menu ? ex.harmonie[i] : degreDe(ex, ex.solution[i]);
        if (d !== juste && ex.menu) {
          const c = ex.chiffres[i];
          const ind = {'7+': 'avec 7+, la basse est la fondamentale d\'un accord de 7e de dominante', '7': 'avec 7, la basse est la fondamentale d\'un accord de 7e',
            '6/5': 'avec 6/5, la basse est la tierce : la fondamentale est une 3ce plus bas', '+6': 'avec +6, la basse est la quinte : la fondamentale est une 4te au-dessus',
            '4/3': 'avec 4/3, la basse est la quinte : la fondamentale est une 4te au-dessus', '+4': 'avec +4, la basse est la 7e : la fondamentale est une 2de au-dessus',
            '2': 'avec 2, la basse est la 7e : la fondamentale est une 2de au-dessus', '7°': 'avec 7°, c\'est une 7e diminuée, sur la sensible', '9+': 'avec 9+, c\'est une 9e de dominante',
            '6': 'avec 6, la fondamentale est une 3ce sous la basse', '6/4': 'avec 6/4, la fondamentale est une 4te au-dessus de la basse'}[c] || 'regarde la basse, le chiffrage et les altérations';
          errs.push({i, msg: `${m} : ce n'est pas le bon accord (${ind})`});
          return;
        }
        if (d !== juste) {
          const c = ex.chiffres[i];
          const indice = c === '6' ? 'avec 6, la fondamentale est une 3ce sous la basse' : c === '6/4' ? 'avec 6/4, la fondamentale est une 4te au-dessus de la basse' : 'avec 5 (ou ♯), la fondamentale est la basse elle-même';
          errs.push({i, msg: `${m} : ce n'est pas le bon degré (${indice})`});
        }
        return;
      }
      const s = N(ex.sopReel ? ex.sopReel[i] : E.notes[i][0]), notes = accordChoisi(ex, d);
      if (!notes.some(x => pcN(x) === HV.pc(s))) errs.push({i, msg: `${m} : le ${HV.nom(s)} du soprano n'est pas dans l'accord de ${nomDegre(ex, d)}`});
    });
    if (ex.chant && ex.menu) {
      const L = E.degres.map(d => d === null || d === undefined ? null : ex.menu[d][0]);
      const fin = ex.finLabel || 'I';
      if (L[n - 1] !== null && L[n - 1] !== fin) errs.push({i: n - 1, msg: `accord ${n} : cette phrase se termine sur ${fin}`});
      if (fin === 'I' && L[n - 1] === 'I' && L[n - 2] !== null && !/^(V(7|9)?|IVm?)$/.test(L[n - 2])) errs.push({i: n - 2, msg: `accord ${n - 1} : pour finir, il faut V (ou V7) avant le I final, ou IV pour une cadence plagale`});
    } else if (ex.chant) {
      const D = E.degres;
      const fin = ex.fin === undefined ? 0 : ex.fin;
      if (D[n - 1] !== null && D[n - 1] !== undefined && D[n - 1] !== fin) errs.push({i: n - 1, msg: fin === 0 ? `accord ${n} : une phrase se termine sur I` : `accord ${n} : cette phrase se termine par une demi-cadence, sur ${DEGN[fin]}`});
      if (fin === 0 && D[n - 2] !== null && D[n - 2] !== undefined && D[n - 2] !== 4 && D[n - 1] === 0) errs.push({i: n - 2, msg: `accord ${n - 1} : pour une cadence parfaite, il faut V avant le I final`});
      if (D[0] !== null && D[0] !== undefined && D[0] !== 0) conseils.push({i: 0, msg: 'accord 1 : on commence en général sur I'});
      for (let i = 0; i < n - 1; i++) {
        const a = D[i], b = D[i + 1];
        if (a === null || b === null || a === undefined || b === undefined) continue;
        if (a === b) conseils.push({i: i + 0.5, msg: `accords ${i + 1}-${i + 2} : deux fois le même accord ; possible si tu changes d'état (par exemple I puis I6)`});
        else if (GRAMMAIRE[a] && !GRAMMAIRE[a].includes(b)) conseils.push({i: i + 0.5, msg: `accords ${i + 1}-${i + 2} : l'enchaînement ${DEGN[a]}-${DEGN[b]} sonne faible (retour en arrière)`});
      }
    }
    return {errs, conseils};
  }
  function fautesNotes(E) {
    const ex = E.ex, errs = HV.verifierPartiel(E.notes, ex.tons || ex.tonique, tierceVoulue(E), ex.libres, ex.pedales);
    const conseils = [];
    // chaque note doit appartenir à l'accord attendu
    E.notes.forEach((ch, i) => {
      const a = attendu(E, i); if (!a) return;
      const pcs = a.map(pcN);
      ch.forEach((x, v) => {
        if (!x || !ex.voix.includes(v)) return;
        const n = N(x);
        if (!pcs.includes(HV.pc(n))) errs.push({i, msg: `accord ${i + 1} : ${HV.nom(n)} n'appartient pas à l'accord de ${nomAccord(a.map(q => HV.FR[q.s] + (q.a === 1 ? '#' : q.a === -1 ? 'b' : '') + '4'))} (${a.map(txtN).join('-')})`});
      });
      // dans un chant donné, la basse est la fondamentale ou la tierce ; à la cadence, la fondamentale
      const b = ch[3];
      if (ex.chant && b && ex.voix.includes(3) && pcs.includes(HV.pc(N(b)))) {
        const n = E.notes.length;
        const lb = k => E.degres[k] === null || E.degres[k] === undefined ? null : libDeg(ex, E.degres[k]);
        const cadence64 = lb(i) === 'I' && /^V7?$/.test(lb(i + 1) || '') && (!E.notes[i + 1][3] || E.notes[i + 1][3] === b);
        if (a.length === 3 && HV.pc(N(b)) === pcs[2] && !cadence64) errs.push({i, msg: `accord ${i + 1} : la quinte à la basse donne une quarte et sixte, possible seulement en cadence (I6/4 juste avant V, sur la même basse) ; sinon mets la fondamentale (${txtN(a[0])}) ou la tierce (${txtN(a[1])})`});
        else if (i >= n - 2 && HV.pc(N(b)) !== pcs[0] && /^V7?$/.test(lb(n - 2) || '') && lb(n - 1) === 'I') errs.push({i, msg: `accord ${i + 1} : pour la cadence parfaite, mets la fondamentale (${txtN(a[0])}) à la basse`});
      }
    });
    // conseils de mélodie pour la voix qu'on est en train d'écrire
    const ed = editables(E);
    for (let i = 0; i < E.notes.length - 1; i++) ed.forEach(v => {
      const a = E.notes[i][v], b = E.notes[i + 1][v];
      if (!a || !b || v === 3) return;
      const d = Math.abs(dpos(N(b)) - dpos(N(a)));
      if (d >= 3 && d <= 5) conseils.push({i: i + 0.5, msg: `accords ${i + 1}-${i + 2} : saut de ${['', '', '', '4te', '5te', '6te'][d]} ${['au soprano', "à l'alto", 'au ténor'][v]} ; les voix chantent mieux par degrés conjoints`});
    });
    return {errs, conseils};
  }
  // ------------------------------------------------------------------ choral : notes étrangères
  const NOMROLE = {p: 'note de passage', b: 'broderie', r: 'retard', app: 'appoggiature', e: 'échappée', ant: 'anticipation'};
  function itemsVoix(E, v) {
    const ex = E.ex, out = [];
    let t = 0;
    E.notes.forEach((c, i) => {
      const d = ex.durees[i], x = E.extra[i][v];
      if (c[v]) {
        if (x.b) { out.push({i, h: 0, t, d: d / 2, n: c[v], lie: x.lie}); out.push({i, h: 1, t: t + d / 2, d: d / 2, n: x.b, lie: false}); }
        else out.push({i, h: 0, t, d, n: c[v], lie: x.lie});
      }
      t += d;
    });
    return out;
  }
  function rolesChoral(E) {
    const roles = {}, parVoix = [];
    for (let v = 0; v < 4; v++) {
      const it = itemsVoix(E, v);
      parVoix.push(it);
      it.forEach((a, k) => {
        const harm = attendu(E, a.i), n = N(a.n);
        if (!harm || harm.map(pcN).includes(HV.pc(n))) { roles[a.i + ',' + v + ',' + a.h] = 'R'; return; }
        const prev = k > 0 && Math.abs(it[k - 1].t + it[k - 1].d - a.t) < 1e-9 ? it[k - 1] : null;
        const nxt = k < it.length - 1 && Math.abs(a.t + a.d - it[k + 1].t) < 1e-9 ? it[k + 1] : null;
        const accent = a.h === 0;
        const dp = prev ? dpos(n) - dpos(N(prev.n)) : null, dn = nxt ? dpos(N(nxt.n)) - dpos(n) : null;
        let nxtReel = false;
        if (nxt) { const hn = attendu(E, nxt.i); nxtReel = !hn || hn.map(pcN).includes(HV.pc(N(nxt.n))); }
        let role = '?';
        if (accent && prev && (a.lie || midi(N(prev.n)) === midi(n)) && dn !== null && Math.abs(dn) === 1 && nxtReel) role = 'r';
        else if (!accent && nxt && midi(N(nxt.n)) === midi(n)) role = 'ant';
        else if (dp !== null && dn !== null && Math.abs(dp) === 1 && Math.abs(dn) === 1 && dp === dn) role = 'p';
        else if (dp !== null && dn !== null && Math.abs(dp) === 1 && dn === -dp) role = 'b';
        else if (accent && dn !== null && Math.abs(dn) === 1 && nxtReel) role = 'app';
        else if (!accent && dp !== null && Math.abs(dp) === 1 && dn !== null && Math.abs(dn) >= 2 && (dn > 0) !== (dp > 0) && nxtReel) role = 'e';
        roles[a.i + ',' + v + ',' + a.h] = role;
      });
    }
    return {roles, parVoix};
  }
  function fautesChoral(E) {
    const ex = E.ex, errs = [], conseils = [];
    const {roles, parVoix} = rolesChoral(E);
    E.roles = roles;
    // notes étrangères mal traitées
    Object.entries(roles).forEach(([k, r]) => {
      if (r !== '?') return;
      const [i, v, h] = k.split(',').map(Number), n = N(lireN(E, i, v, h)), a = attendu(E, i);
      errs.push({i, msg: `accord ${i + 1} : ${HV.nom(n)} (${HV.VOIX[v]}) n'est pas dans l'accord ${a ? 'de ' + nomAccord(a.map(q => HV.FR[q.s] + (q.a === 1 ? '#' : q.a === -1 ? 'b' : '') + '4')) : ''} et ce n'est pas une note étrangère bien traitée (passage, broderie, retard…)`});
    });
    // notes réelles : règles habituelles
    const sq = E.notes.map((c, i) => [0, 1, 2, 3].map(v => {
      const a = c[v], b = E.extra[i][v].b;
      if (!a) return null;
      if (roles[i + ',' + v + ',0'] === 'R' || !b) return a;
      return roles[i + ',' + v + ',1'] === 'R' ? b : a;
    }));
    HV.verifierPartiel(sq, ex.tons || ex.tonique, tierceVoulue(E), ex.libres, ex.pedales).forEach(e => errs.push(e));
    // quintes et octaves créées par les notes étrangères (entre attaques successives)
    const attaques = [...new Set(parVoix.flat().map(a => +a.t.toFixed(4)))].sort((a, b) => a - b);
    const son = (v, tt) => { const a = parVoix[v].find(a => a.t - 1e-9 <= tt && tt < a.t + a.d - 1e-9); return a ? a.n : null; };
    const celluleDe = tt => { let acc = 0, idx = 0; ex.durees.forEach((d, k) => { if (tt >= acc - 1e-9) idx = k; acc += d; }); return idx; };
    for (let k = 0; k < attaques.length - 1; k++) {
      const a = attaques[k], b = attaques[k + 1];
      if (Number.isInteger(a) && Number.isInteger(b)) continue;
      for (let u = 0; u < 4; u++) for (let l = u + 1; l < 4; l++) {
        const A = [son(u, a), son(l, a)], B = [son(u, b), son(l, b)];
        if (A.includes(null) || B.includes(null) || (A[0] === B[0] && A[1] === B[1])) continue;
        const p5 = (lo, hi) => { const d = dpos(N(hi)) - dpos(N(lo)), st = midi(N(hi)) - midi(N(lo)); return d > 0 && d % 7 === 4 && mod(st, 12) === 7; };
        const p8 = (lo, hi) => { const d = dpos(N(hi)) - dpos(N(lo)), st = midi(N(hi)) - midi(N(lo)); return mod(d, 7) === 0 && mod(st, 12) === 0; };
        const meme = (midi(N(B[0])) - midi(N(A[0]))) * (midi(N(B[1])) - midi(N(A[1]))) > 0;
        if (meme && ((p5(A[1], A[0]) && p5(B[1], B[0])) || (p8(A[1], A[0]) && p8(B[1], B[0]))))
          errs.push({i: celluleDe(b), msg: `accord ${celluleDe(b) + 1} : ${p5(A[1], A[0]) ? '5tes' : '8ves'} consécutives ${HV.VOIX[u]}/${HV.VOIX[l]}, à cause d'une note étrangère`});
      }
    }
    // chant donné : rôle de la basse (sur les notes réelles)
    if (ex.chant) sq.forEach((ch, i) => {
      const a = attendu(E, i), b = ch[3];
      if (!a || !b || !ex.voix.includes(3)) return;
      const pcs = a.map(pcN), n = E.notes.length, p = HV.pc(N(b));
      const cadence64 = E.degres[i] === 0 && E.degres[i + 1] === 4 && (!sq[i + 1] || !sq[i + 1][3] || sq[i + 1][3] === b);
      if (p === pcs[2] && !cadence64) errs.push({i, msg: `accord ${i + 1} : la quinte à la basse donne une quarte et sixte, possible seulement en cadence ; mets la fondamentale (${txtN(a[0])}) ou la tierce (${txtN(a[1])})`});
      else if (i >= n - 2 && p !== pcs[0] && E.degres[n - 2] === 4) errs.push({i, msg: `accord ${i + 1} : pour la cadence parfaite, mets la fondamentale (${txtN(a[0])}) à la basse`});
    });
    // objectif de l'exercice (nombre de notes étrangères à ajouter)
    const et = etapeCourante(E);
    const obj = (et && et.objectif) || (!ex.guide && ex.objectif);
    if (obj && etapeComplete(E)) {
      const compte = {};
      Object.entries(roles).forEach(([k, r]) => { const v = +k.split(',')[1]; if (ex.voix.includes(v) && r !== 'R' && r !== '?') compte[r] = (compte[r] || 0) + 1; });
      const total = Object.values(compte).reduce((a, b) => a + b, 0);
      Object.entries(obj).forEach(([r, nb]) => {
        const a = r === 'total' ? total : (compte[r] || 0);
        const PL = {p: ['note de passage', 'notes de passage'], b: ['broderie', 'broderies'], r: ['retard', 'retards'], app: ['appoggiature', 'appoggiatures'],
                    e: ['échappée', 'échappées'], ant: ['anticipation', 'anticipations'], total: ['note étrangère', 'notes étrangères']};
        if (a < nb) errs.push({i: null, msg: `il manque encore ${nb - a} ${PL[r][nb - a > 1 ? 1 : 0]} (objectif : ${nb})`});
      });
    }
    return {errs, conseils};
  }
  function etapeComplete(E) {
    const et = etapeCourante(E);
    if (et && et.type === 'degres') return E.degres.every(d => d !== null && d !== undefined);
    const vs = et ? et.voix : E.ex.voix;
    return E.notes.every(ch => vs.every(v => ch[v]));
  }
  function analyser(E) {
    const et = etapeCourante(E);
    E.roles = null;
    const r = et && et.type === 'degres' ? fautesDegres(E) : (E.ex.rythme ? fautesChoral(E) : fautesNotes(E));
    if (E.ex.isoles) { r.errs = r.errs.filter(e => Number.isInteger(e.i)); r.conseils = r.conseils.filter(e => Number.isInteger(e.i)); }
    const mauvais = new Set(), liens = new Set();
    r.errs.forEach(e => { if (e.i === null || e.i === undefined) return; if (Number.isInteger(e.i)) mauvais.add(e.i); else { liens.add(e.i - 0.5); liens.add(e.i + 0.5); } });
    E.resultat = {mauvais, liens};
    const txt = e => e.msg.replace(/^(accords? [\d-]+) : /, (m, p) => `<b>${p[0].toUpperCase() + p.slice(1)}</b> · `).replace(/^il manque/, 'Il manque');
    const liste = (l, cls) => l.slice().sort((a, b) => (a.i ?? 99) - (b.i ?? 99)).map(e => `<li class="${cls}">${txt(e)}</li>`).join('');
    const complet = etapeComplete(E);
    let html, cls;
    if (r.errs.length) {
      cls = 'fb bad';
      html = `<h4>${r.errs.length} correction${r.errs.length > 1 ? 's' : ''}</h4><ul>${liste(r.errs, 'err')}${liste(r.conseils, 'cons')}</ul>`;
    } else if (!complet) {
      cls = 'fb info';
      html = `<h4>Rien à corriger pour l'instant</h4>Continue.${r.conseils.length ? '<ul>' + liste(r.conseils, 'cons') + '</ul>' : ''}`;
    } else {
      cls = 'fb good';
      const derniere = !E.ex.guide || E.etape === E.ex.guide.length - 1;
      html = derniere ? `<h4>Bravo, aucune faute !</h4>Écoute ta réalisation, puis compare-la avec le corrigé : il y a souvent plusieurs bonnes solutions.`
        : `<h4>Étape réussie !</h4><button class="act prim suivante">Étape suivante →</button>`;
      if (r.conseils.length) html += '<ul>' + liste(r.conseils, 'cons') + '</ul>';
      if (!derniere) E.resultat = null;
      if (derniere && typeof window !== 'undefined' && typeof window.atelierReussi === 'function') window.atelierReussi(E.id);
    }
    E.fb.className = cls; E.fb.innerHTML = html;
    const b = E.fb.querySelector('.suivante');
    if (b) b.onclick = () => { E.etape++; E.sel = null; E.resultat = null; majEtape(E); };
  }
  function majEtape(E) {
    const et = etapeCourante(E);
    if (E.titre) {
      E.titre.innerHTML = et ? `<b>Étape ${E.etape + 1}/${E.ex.guide.length} · ${et.titre}</b><br>${et.consigne}` : '';
      E.titre.hidden = !et;
    }
    const ed = editables(E);
    if (ed.length && !ed.includes(E.voix)) E.voix = ed[0];
    E.fb.className = 'fb'; E.fb.innerHTML = '';
    if (!E.ex.corriger && (E.notes.some((c, i) => c.some((x, v) => x && !E.notesDepart[i][v])) || E.degres.some(d => d !== null && d !== undefined))) analyser(E);
    dessiner(E);
  }
  // vérification à la demande (chasse aux fautes)
  function verifier(E) {
    const vides = E.notes.map((c, i) => c.some(x => !x) ? i + 1 : 0).filter(Boolean);
    if (vides.length) { E.fb.className = 'fb bad'; E.fb.innerHTML = `<h4>Il manque des notes</h4>Complète ${vides.length > 1 ? 'les accords' : "l'accord"} ${vides.join(', ')}.`; return; }
    analyser(E); dessiner(E);
  }

  // ------------------------------------------------------------------ mise en place
  function sauver(E) { try { localStorage.setItem('harmonie-' + E.id, JSON.stringify({notes: E.notes, degres: E.degres, etape: E.etape, extra: E.extra})); } catch (e) {} }
  function charger(E) {
    try { const s = JSON.parse(localStorage.getItem('harmonie-' + E.id)); if (s && Array.isArray(s.notes) && s.notes.length === E.notes.length) return s; } catch (e) {}
    return null;
  }
  function copieX(X) { return X.map(c => c.map(x => ({b: x ? x.b : null, lie: !!(x && x.lie)}))); }
  // la réalisation, voix par voix, en événements (note, durée, lié à la suivante)
  function evenements(E, v) {
    const out = [];
    E.notes.forEach((c, i) => {
      const d = E.ex.durees[i], x = E.ex.rythme ? E.extra[i][v] : null;
      const parts = x && x.b ? [[c[v], d / 2], [x.b, d / 2]] : [[c[v], d]];
      parts.forEach(([n, dd], k) => {
        const lie = k === 0 && x && x.lie && out.length && out[out.length - 1].n === n;
        if (lie) out[out.length - 1].d += dd;
        else out.push({n, d: dd});
      });
    });
    return out;
  }
  function monter(el, id, ex) {
    const E = {id, ex, el, voix: ex.voix[0], sel: null, resultat: null, fantome: null, etape: 0, fini: false};
    E.notesDepart = ex.donne.map(c => c.slice());
    E.notes = ex.donne.map(c => c.slice());
    E.degres = ex.donne.map(() => null);
    E.extra = ex.rythme ? copieX(ex.donneX) : null;
    const s = charger(E);
    if (s) { E.notes = s.notes; E.degres = s.degres || E.degres; E.etape = Math.min(s.etape || 0, ex.guide ? ex.guide.length - 1 : 0); if (ex.rythme && s.extra) E.extra = s.extra; }
    const consigne = ex.corriger ? 'Clique sur une note pour la choisir, puis déplace-la (▲ ▼) ou clique ailleurs dans la colonne pour la remplacer. Puis clique sur « Vérifier ».'
      : 'Choisis une voix, puis clique sur la portée pour poser ses notes. Les corrections apparaissent au fur et à mesure.';
    el.innerHTML = `
      <p class="titre" hidden></p>
      <div class="barre outils">
        <span class="lbl">Voix :</span>
        ${[0, 1, 2, 3].map(v => `<button class="voix" data-v="${v}" style="--c:${COUL[v]}" hidden>${NOMV[v]}</button>`).join('')}
        <span class="sep"></span>
        <button class="petit" data-a="1" title="Dièse">♯</button><button class="petit" data-a="0" title="Bécarre">♮</button><button class="petit" data-a="-1" title="Bémol">♭</button>
        <button class="petit" data-m="1" title="Monter (flèche haut)">▲</button><button class="petit" data-m="-1" title="Descendre (flèche bas)">▼</button>
        <button class="petit" data-x="1" title="Effacer la note (Suppr)">✕</button>
        ${ex.rythme ? '<span class="sep"></span><button class="petit large" data-c="1" title="Deux croches à la place de la noire (touche C)">♪♪ croches</button><button class="petit large" data-l="1" title="Lier à la note précédente, pour un retard (touche L)">⁀ lier</button>' : ''}
      </div>
      <div class="portee" tabindex="0" aria-label="Portée de l'exercice : clique pour poser une note"></div>
      <p class="aide">${ex.guide ? '' : consigne + ' '}Deux clics sur la même note pour l'altérer. Au clavier : ▲ ▼ pour déplacer, ◀ ▶ pour changer d'accord, 1 à 4 pour la voix.</p>
      <div class="barre">
        <button class="act" data-do="ecouter">▶ Écouter</button>
        ${ex.corriger ? '<button class="act prim" data-do="verifier">✔ Vérifier</button>' : ''}
        <button class="act" data-do="solution">${ex.guide ? 'Solution de cette étape' : 'Voir une solution'}</button>
        <button class="act" data-do="effacer">↺ Recommencer</button>
      </div>
      <div class="fb" aria-live="polite"></div>`;
    E.portee = el.querySelector('.portee'); E.fb = el.querySelector('.fb'); E.titre = el.querySelector('.titre');
    E.outils = el.querySelector('.outils');
    E.boutonsVoix = [...el.querySelectorAll('.voix')];
    E.boutonsVoix.forEach(b => b.onclick = () => { E.voix = +b.dataset.v; dessiner(E); });
    el.querySelectorAll('[data-a]').forEach(b => b.onclick = () => alterer(E, +b.dataset.a));
    el.querySelectorAll('[data-m]').forEach(b => b.onclick = () => deplacer(E, +b.dataset.m));
    if (ex.rythme) { el.querySelector('[data-c]').onclick = () => couperTemps(E); el.querySelector('[data-l]').onclick = () => lier(E); }
    el.querySelector('[data-x]').onclick = () => {
      if (E.sel && editables(E).includes(E.sel[1])) {
        const [i, v, h] = E.sel;
        if (h) E.extra[i][v].b = null; else { E.notes[i][v] = null; if (ex.rythme) E.extra[i][v] = {b: null, lie: false}; }
        E.sel = [i, v, 0];
        if (!ex.corriger) analyser(E); dessiner(E);
      }
    };
    const bv = el.querySelector('[data-do="verifier"]'); if (bv) bv.onclick = () => verifier(E);
    el.querySelector('[data-do="ecouter"]').onclick = ev => {
      const voix = [0, 1, 2, 3].map(v => evenements(E, v).map(e => [e.n ? midi(N(e.n)) : null, e.d]));
      if (typeof lireMusique === 'function') lireMusique({voix, genre: 'choeur'}, ev.currentTarget);
    };
    el.querySelector('[data-do="solution"]').onclick = () => {
      const et = etapeCourante(E);
      if (et) {
        if (et.type === 'degres') E.degres = ex.harmonie ? ex.harmonie.slice() : ex.solution.map(c => degreDe(ex, c));
        else E.notes.forEach((c, i) => et.voix.forEach(v => { c[v] = ex.solution[i][v]; if (ex.rythme) E.extra[i][v] = Object.assign({}, ex.solutionX[i][v]); }));
        if (et.type === 'voix' && ex.chant) E.degres = ex.harmonie ? ex.harmonie.slice() : ex.solution.map(c => degreDe(ex, c));
        analyser(E); dessiner(E);
        return;
      }
      E.notes = ex.solution.map(c => c.slice()); if (ex.rythme) E.extra = copieX(ex.solutionX); E.sel = null; analyser(E); dessiner(E);
      E.fb.className = 'fb info';
      E.fb.innerHTML = `<h4>Une solution possible</h4>C'est celle du corrigé. Il en existe d'autres : clique sur « Recommencer » et essaie la tienne !`;
    };
    el.querySelector('[data-do="effacer"]').onclick = () => {
      E.notes = E.notesDepart.map(c => c.slice()); E.degres = E.degres.map(() => null); E.etape = 0;
      if (ex.rythme) E.extra = copieX(ex.donneX);
      E.resultat = null; E.sel = null; majEtape(E);
    };
    E.portee.addEventListener('click', ev => {
      if (ev.target.closest('select')) return;
      const pt = point(E, ev); if (!pt) return;
      if (pt.sur) { E.voix = pt.v; E.sel = [pt.i, pt.v]; dessiner(E); entendreAccord(E, pt.i); return; }
      const cur = lireN(E, pt.i, pt.v, pt.h);
      if (cur) {
        const a = N(cur), b = N(pt.n);
        if (a.s === b.s && a.o === b.o) {
          const choisie = E.sel && E.sel[0] === pt.i && E.sel[1] === pt.v && (E.sel[2] || 0) === pt.h;
          if (!choisie) { E.sel = [pt.i, pt.v, pt.h]; dessiner(E); entendreAccord(E, pt.i); return; }   // 1er clic : on choisit la note
          const cyc = [0, 1, -1]; a.a = cyc[(cyc.indexOf(a.a) + 1) % 3]; poser(E, pt.i, pt.v, HV.texte(a), pt.h); return;
        }
      }
      if (ex.rythme && !pt.h && E.extra[pt.i][pt.v].lie) E.extra[pt.i][pt.v].lie = false;
      poser(E, pt.i, pt.v, pt.n, pt.h);
    });
    E.portee.addEventListener('mousemove', ev => {
      if (ev.target.closest('select')) return;
      const pt = point(E, ev);
      const f = pt && !pt.sur ? [pt.i, pt.v, pt.n, pt.h || 0] : null;
      if (JSON.stringify(f) !== JSON.stringify(E.fantome)) { E.fantome = f; dessiner(E); }
    });
    E.portee.addEventListener('mouseleave', () => { if (E.fantome) { E.fantome = null; dessiner(E); } });
    E.portee.addEventListener('keydown', ev => {
      if (ev.target.closest('select')) return;
      const k = ev.key, ed = editables(E);
      if (k === 'ArrowUp' || k === 'ArrowDown') { deplacer(E, k === 'ArrowUp' ? 1 : -1); ev.preventDefault(); }
      else if (k === 'ArrowLeft' || k === 'ArrowRight') {
        const i = E.sel ? E.sel[0] : 0, j = Math.max(0, Math.min(E.notes.length - 1, i + (k === 'ArrowRight' ? 1 : -1)));
        E.sel = [j, E.voix]; dessiner(E); ev.preventDefault();
      } else if ('1234'.includes(k) && ed.includes(+k - 1)) { E.voix = +k - 1; if (E.sel) E.sel[1] = E.voix; dessiner(E); }
      else if (k === 'Delete' || k === 'Backspace') { el.querySelector('[data-x]').click(); ev.preventDefault(); }
      else if (ex.rythme && (k === 'c' || k === 'C')) couperTemps(E);
      else if (ex.rythme && (k === 'l' || k === 'L')) lier(E);
    });
    majEtape(E);
    return E;
  }
  // image seule (sans interaction), pour les entraînements de l'appli
  function image(ex, notes, mauvais) {
    const E = {ex, notes, degres: notes.map(() => null), extra: null, sel: null, fantome: null, etape: 0, voix: 0,
      resultat: mauvais ? {mauvais: new Set(mauvais), liens: new Set()} : null};
    return graver(E);
  }
  return {monter, image};
})();
