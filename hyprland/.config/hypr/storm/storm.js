/* IonVeil — Signal Storm
   Self-contained canvas effect: streaking cyan rain + branching lightning.
   Usage: IonVeilStorm(canvasEl, configOverrides?) → { strike, start, stop, destroy, config } */

function IonVeilStorm(canvas, userConfig) {
  const ctx = canvas.getContext('2d');

  const CONFIG = Object.assign({
    rainColor:    '110,231,255',
    boltColor:    '110,231,255',
    boltColorAlt: '255,107,214',
    boltCore:     '230,250,255',
    flashColor:   '120,210,255',
    slant: 0.16,
    rainDensity:  13,
    rainMinLen:   14, rainMaxLen: 66,
    rainMinSpeed: 240, rainMaxSpeed: 700,
    rainMinAlpha: 0.05, rainMaxAlpha: 0.23,
    rainMinWidth: 0.6, rainMaxWidth: 1.6,
    boltAltChance:    0.18,
    boltMinGap:       1.8, boltMaxGap: 5.4,
    doubleStrike:     0.35,
    boltLifeSpeed:    3.4,
    boltSegMin:       16, boltSegMax: 24,
    boltJitter:       78,
    boltBranches:     [2, 4],
    flashStrength:    0.18,
    maxDpr: 2,
  }, userConfig || {});

  const C = CONFIG;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const rnd = (a, b) => a + Math.random() * (b - a);

  let w = 0, h = 0, drops = [], bolts = [], flash = 0, last = 0, nextBolt = 1.2, raf = null, running = false;

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, C.maxDpr);
    w = window.innerWidth; h = window.innerHeight;
    canvas.width = w * dpr; canvas.height = h * dpr;
    canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    initDrops();
  }

  function mkDrop(seeded) {
    return {
      x: Math.random() * (w + 120) - 60,
      y: seeded ? Math.random() * h : -20 - Math.random() * h,
      len: rnd(C.rainMinLen, C.rainMaxLen),
      spd: rnd(C.rainMinSpeed, C.rainMaxSpeed),
      a:   rnd(C.rainMinAlpha, C.rainMaxAlpha),
      lw:  rnd(C.rainMinWidth, C.rainMaxWidth),
    };
  }
  function initDrops() {
    const n = Math.round(w / C.rainDensity);
    drops = [];
    for (let i = 0; i < n; i++) drops.push(mkDrop(true));
  }

  function spawnBolt() {
    const pink = Math.random() < C.boltAltChance;
    const col = pink ? C.boltColorAlt : C.boltColor;
    const startX = w * (0.18 + Math.random() * 0.64);
    const segs = Math.floor(rnd(C.boltSegMin, C.boltSegMax));
    const stepY = (h + 30) / segs;
    const pts = [{ x: startX, y: -12 }];
    let x = startX, y = -12;
    for (let i = 0; i < segs; i++) {
      x += (Math.random() - 0.5) * C.boltJitter + stepY * C.slant;
      y += stepY;
      pts.push({ x, y });
    }
    const branches = [];
    const nb = Math.floor(rnd(C.boltBranches[0], C.boltBranches[1] + 1));
    for (let b = 0; b < nb; b++) {
      const idx = 2 + Math.floor(Math.random() * (pts.length - 5));
      let bx = pts[idx].x, by = pts[idx].y;
      const bp = [{ x: bx, y: by }];
      const bs = 3 + Math.floor(Math.random() * 4);
      for (let i = 0; i < bs; i++) {
        bx += (Math.random() - 0.4) * 64 * (Math.random() < 0.5 ? -1 : 1);
        by += stepY * (0.5 + Math.random());
        bp.push({ x: bx, y: by });
      }
      branches.push(bp);
    }
    bolts.push({ pts, branches, col, life: 1 });
    flash = Math.max(flash, pink ? C.flashStrength * 0.55 : C.flashStrength);
  }

  function strokePath(pts, col, alpha, lw) {
    ctx.beginPath();
    ctx.moveTo(pts[0].x, pts[0].y);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i].x, pts[i].y);
    ctx.strokeStyle = 'rgba(' + col + ',' + alpha + ')';
    ctx.lineWidth = lw; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.stroke();
  }

  function frame(t) {
    const dt = Math.min(0.05, (t - last) / 1000 || 0);
    last = t;
    ctx.clearRect(0, 0, w, h);

    for (const d of drops) {
      d.y += d.spd * dt;
      d.x += d.spd * C.slant * dt;
      if (d.y - d.len > h) Object.assign(d, mkDrop(false));
      const dx = d.len * C.slant;
      const g = ctx.createLinearGradient(d.x, d.y - d.len, d.x + dx, d.y);
      g.addColorStop(0, 'rgba(' + C.rainColor + ',0)');
      g.addColorStop(1, 'rgba(' + C.rainColor + ',' + d.a + ')');
      ctx.strokeStyle = g; ctx.lineWidth = d.lw; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(d.x, d.y - d.len); ctx.lineTo(d.x + dx, d.y); ctx.stroke();
    }

    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    for (const bl of bolts) {
      const a = bl.life;
      strokePath(bl.pts, bl.col, 0.10 * a, 7);
      strokePath(bl.pts, bl.col, 0.22 * a, 3.2);
      strokePath(bl.pts, C.boltCore, 0.85 * a, 1.3);
      for (const br of bl.branches) {
        strokePath(br, bl.col, 0.18 * a, 2.2);
        strokePath(br, C.boltCore, 0.6 * a, 1);
      }
      bl.life -= dt * C.boltLifeSpeed;
    }
    ctx.restore();
    bolts = bolts.filter(b => b.life > 0);

    if (flash > 0.002) {
      ctx.fillStyle = 'rgba(' + C.flashColor + ',' + (flash * 0.5) + ')';
      ctx.fillRect(0, 0, w, h);
      flash *= 0.82;
    }

    nextBolt -= dt;
    if (nextBolt <= 0) {
      spawnBolt();
      if (Math.random() < C.doubleStrike) setTimeout(spawnBolt, 90 + Math.random() * 120);
      nextBolt = rnd(C.boltMinGap, C.boltMaxGap);
    }

    if (running) raf = requestAnimationFrame(frame);
  }

  function renderStatic() {
    ctx.clearRect(0, 0, w, h);
    for (let i = 0; i < 40; i++) {
      const d = mkDrop(true); const dx = d.len * C.slant;
      ctx.strokeStyle = 'rgba(' + C.rainColor + ',' + d.a + ')';
      ctx.lineWidth = d.lw;
      ctx.beginPath(); ctx.moveTo(d.x, d.y - d.len); ctx.lineTo(d.x + dx, d.y); ctx.stroke();
    }
  }

  function start() {
    if (running) return;
    running = true; last = 0;
    raf = requestAnimationFrame(frame);
  }
  function stop() {
    running = false;
    if (raf) cancelAnimationFrame(raf);
    raf = null;
  }
  function destroy() { stop(); window.removeEventListener('resize', resize); }

  resize();
  window.addEventListener('resize', resize);
  if (reduce) { renderStatic(); } else { start(); }

  return { strike: spawnBolt, start, stop, destroy, config: C };
}

if (typeof module !== 'undefined' && module.exports) module.exports = IonVeilStorm;
if (typeof window !== 'undefined') window.IonVeilStorm = IonVeilStorm;
