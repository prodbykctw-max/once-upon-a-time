// ─── drawMansionBG + 9 stage helpers + drawBoss ───────────────────────────────
// Canvas 2D (FX context). Globals: FX, W, H, GS {camX, tick, ai}
// Helpers assumed present: shade, softGlow, wash, granulate, castShadow,
//   volume, rimLight, lerpC, paintWing

// ── seeded hash ──────────────────────────────────────────────────────────────
function _h(a, b = 0) {
  return ((a * 1664525 + b * 1013904223 + 22695477) & 0x7fffffff) / 0x7fffffff;
}

// ── drawMansionBG ─────────────────────────────────────────────────────────────
function drawMansionBG(st) {
  var pc = hexS(st.pc), ac = hexS(st.ac);
  const cam = GS.camX, floorY = H * 0.82;

  // base wall gradient
  const bg = FX.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0,   shade(pc, 0.18));
  bg.addColorStop(0.6, shade(pc, 0.10));
  bg.addColorStop(1,   shade(pc, 0.05));
  FX.fillStyle = bg;
  FX.fillRect(0, 0, W, H);

  // dispatch to stage
  const fns = [
    drawBG_Library, drawBG_Egyptian, drawBG_Samurai, drawBG_Royal,
    drawBG_Museum,  drawBG_Tech,     drawBG_Armory,  drawBG_ArtGallery,
    drawBG_Vault,
  ];
  (fns[GS.ai] || fns[0])(pc, ac, cam, floorY);

  // vignette
  const vig = FX.createRadialGradient(W * 0.5, H * 0.5, H * 0.22, W * 0.5, H * 0.5, W * 0.72);
  vig.addColorStop(0,   'rgba(0,0,0,0)');
  vig.addColorStop(0.7, 'rgba(0,0,0,0.18)');
  vig.addColorStop(1,   'rgba(0,0,0,0.72)');
  FX.fillStyle = vig;
  FX.fillRect(0, 0, W, H);

  // floating dust motes (14)
  const T = GS.tick;
  for (let i = 0; i < 14; i++) {
    const mx = (_h(i, 1) * W + T * (0.18 + _h(i, 3) * 0.28)) % W;
    const my = (_h(i, 2) * H - T * (0.24 + _h(i, 5) * 0.18) + H) % H;
    const mr = 1.2 + _h(i, 6) * 2.2;
    FX.beginPath();
    FX.arc(mx, my, mr, 0, Math.PI * 2);
    FX.fillStyle = `rgba(255,245,210,${(0.06 + _h(i, 7) * 0.10).toFixed(3)})`;
    FX.fill();
  }
}

// ── Stage 0 — Grand Library ───────────────────────────────────────────────────
function drawBG_Library(pc, ac, cam, floorY) {
  const far = cam * 0.15, mid = cam * 0.35;

  // --- far layer: vaulted ceiling ribs + deep receding bookcases ---
  FX.save(); FX.translate(-far, 0);
  for (let x = 0; x < W + 800; x += 320) {
    // vertical pilaster
    FX.fillStyle = shade(pc, 0.22);
    FX.fillRect(x, 0, 18, floorY);
    // gothic arch cutout
    FX.fillStyle = shade(pc, 0.14);
    const ax = x + 160, ar = 145;
    FX.beginPath();
    FX.moveTo(ax - ar, floorY);
    FX.lineTo(ax - ar, floorY * 0.42);
    FX.quadraticCurveTo(ax - ar, floorY * 0.08, ax, floorY * 0.04);
    FX.quadraticCurveTo(ax + ar, floorY * 0.08, ax + ar, floorY * 0.42);
    FX.lineTo(ax + ar, floorY);
    FX.closePath(); FX.fill();
    // vault rib tracery
    FX.strokeStyle = shade(ac, 0.55); FX.lineWidth = 1.2; FX.globalAlpha = 0.12;
    FX.beginPath(); FX.moveTo(x + 18, 0); FX.lineTo(ax, floorY * 0.14); FX.stroke();
    FX.beginPath(); FX.moveTo(x + 302, 0); FX.lineTo(ax, floorY * 0.14); FX.stroke();
    FX.globalAlpha = 1;
  }
  // distant bookshelves (far layer)
  for (let x = 18; x < W + 780; x += 302) {
    FX.fillStyle = shade(pc, 0.19);
    FX.fillRect(x, H * 0.06, 284, floorY - H * 0.06);
    // shelf rails
    for (let sy = 0; sy < 5; sy++) {
      const sy_y = H * 0.06 + sy * (floorY - H * 0.06) / 5;
      FX.fillStyle = shade(pc, 0.30);
      FX.fillRect(x, sy_y, 284, 5);
      // book spines
      for (let bx = x + 3; bx < x + 281; bx += 11) {
        const bh = (floorY - H * 0.06) / 5 * (0.38 + _h(bx, sy) * 0.52);
        const hv = _h(bx * 3, sy * 7);
        FX.fillStyle = hv < 0.28 ? shade(ac, 0.75)
                     : hv < 0.55 ? shade(ac, 0.45)
                     : hv < 0.76 ? shade(pc, 0.62)
                     : shade(pc, 0.38);
        FX.globalAlpha = 0.68;
        FX.fillRect(bx, sy_y + 5 - bh, 9, bh);
        FX.globalAlpha = 1;
      }
    }
  }
  FX.restore();

  // --- mid layer: ornate frames + chandelier glow ---
  FX.save(); FX.translate(-mid, 0);
  // framed oil paintings
  for (let x = 80; x < W + 600; x += 380) {
    const pw = 130 + _h(x, 2) * 60, ph = 90 + _h(x, 3) * 50;
    const py = H * 0.14;
    FX.strokeStyle = shade(ac, 0.82); FX.lineWidth = 7;
    FX.strokeRect(x, py, pw, ph);
    FX.strokeStyle = shade(ac, 0.55); FX.lineWidth = 3;
    FX.strokeRect(x + 5, py + 5, pw - 10, ph - 10);
    // painted canvas gradient
    const cg = FX.createLinearGradient(x + 7, py + 7, x + pw - 7, py + ph - 7);
    cg.addColorStop(0, shade(pc, 0.35));
    cg.addColorStop(1, shade(pc, 0.55));
    FX.fillStyle = cg; FX.fillRect(x + 7, py + 7, pw - 14, ph - 14);
    // subtle painted scene highlight
    FX.fillStyle = shade(ac, 0.28); FX.globalAlpha = 0.22;
    FX.beginPath(); FX.ellipse(x + pw * 0.5, py + ph * 0.5, pw * 0.24, ph * 0.2, 0, 0, Math.PI * 2); FX.fill();
    FX.globalAlpha = 1;
  }
  // chandelier glow flicker
  const flicker = 0.82 + Math.sin(GS.tick * 0.13) * 0.12 + Math.sin(GS.tick * 0.37) * 0.06;
  for (let x = 200; x < W + 600; x += 460) {
    softGlow(x - mid, H * 0.05, 120 * flicker, ac, 0.13 * flicker);
    softGlow(x - mid, H * 0.05, 48,  '255,245,192', 0.28 * flicker);
    // chandelier body
    FX.fillStyle = shade(ac, 0.72); FX.fillRect(x - 2, 0, 4, 24);
    FX.beginPath(); FX.ellipse(x, 24, 14, 8, 0, 0, Math.PI * 2);
    FX.fillStyle = shade(ac, 0.85); FX.fill();
    for (let ci = 0; ci < 7; ci++) {
      const ca = (ci / 7) * Math.PI * 2 - Math.PI / 2;
      const ex = x + Math.cos(ca) * 82, ey = 34 + Math.sin(ca) * 18;
      FX.strokeStyle = shade(ac, 0.65); FX.lineWidth = 1.5;
      FX.beginPath(); FX.moveTo(x, 30); FX.lineTo(ex, ey); FX.stroke();
      FX.fillStyle = `rgba(255,245,192,${(0.55 * flicker).toFixed(2)})`;
      FX.fillRect(ex - 2, ey - 14, 5, 14);
      FX.beginPath(); FX.arc(ex, ey - 15, 5, 0, Math.PI * 2);
      FX.fillStyle = shade(ac, 0.50); FX.fill();
    }
  }
  FX.restore();

  // --- chair rail wainscoting band ---
  FX.fillStyle = shade(pc, 0.28);
  FX.fillRect(0, floorY - H * 0.32, W, 8);
  FX.fillStyle = shade(pc, 0.35);
  FX.fillRect(0, floorY - H * 0.32 + 8, W, H * 0.10);
  FX.fillStyle = shade(pc, 0.22);
  FX.fillRect(0, floorY - H * 0.32 - 4, W, 4);

  // --- floor: parquet diagonal hatch + warm reflection ---
  FX.save(); FX.translate(-cam * 0.55, 0);
  const fp = FX.createLinearGradient(0, floorY, 0, H);
  fp.addColorStop(0, shade(pc, 0.38));
  fp.addColorStop(1, shade(pc, 0.20));
  FX.fillStyle = fp; FX.fillRect(0, floorY, W + 800, H - floorY);
  FX.strokeStyle = shade(pc, 0.48); FX.lineWidth = 1; FX.globalAlpha = 0.28;
  for (let d = -H; d < W + 800 + H; d += 28) {
    FX.beginPath(); FX.moveTo(d, floorY); FX.lineTo(d + H * 0.18, H); FX.stroke();
  }
  FX.globalAlpha = 0.14;
  for (let d = -H; d < W + 800 + H; d += 28) {
    FX.beginPath(); FX.moveTo(d + H * 0.18, floorY); FX.lineTo(d, H); FX.stroke();
  }
  FX.globalAlpha = 1;
  // warm light reflections
  for (let x = 200; x < W + 800; x += 460) {
    const rg = FX.createRadialGradient(x, floorY + 20, 5, x, floorY + 20, 90);
    rg.addColorStop(0, `rgba(255,225,140,${(0.14 * flicker).toFixed(3)})`);
    rg.addColorStop(1, 'rgba(255,225,140,0)');
    FX.fillStyle = rg; FX.beginPath(); FX.ellipse(x, floorY + 20, 90, 30, 0, 0, Math.PI * 2); FX.fill();
  }
  FX.restore();
}

// ── Stage 1 — Egyptian Hall ───────────────────────────────────────────────────
function drawBG_Egyptian(pc, ac, cam, floorY) {
  const far = cam * 0.15, mid = cam * 0.35;

  // --- far: sandstone block wall ---
  FX.save(); FX.translate(-far, 0);
  const sw = 155, sh = 56;
  FX.fillStyle = shade(pc, 0.28);
  FX.fillRect(0, 0, W + 600, floorY);
  FX.strokeStyle = shade(pc, 0.18); FX.lineWidth = 3;
  for (let row = 0; row * sh < floorY + sh; row++) {
    FX.beginPath(); FX.moveTo(0, row * sh); FX.lineTo(W + 600, row * sh); FX.stroke();
    const off = (row % 2) * (sw / 2);
    for (let col = 0; col * sw < W + 600 + sw; col++) {
      FX.beginPath(); FX.moveTo(col * sw + off, row * sh); FX.lineTo(col * sw + off, (row + 1) * sh); FX.stroke();
    }
  }
  // hieroglyph band
  FX.globalAlpha = 0.22;
  for (let x = 12; x < W + 580; x += 32) {
    const gy = H * 0.38, hv = _h(x, 1);
    FX.strokeStyle = shade(ac, 0.80); FX.lineWidth = 1.5;
    if (hv < 0.2) { // eye of ra
      FX.beginPath(); FX.ellipse(x + 10, gy + 8, 8, 5, 0, 0, Math.PI * 2); FX.stroke();
      FX.beginPath(); FX.arc(x + 10, gy + 8, 3, 0, Math.PI * 2); FX.fillStyle = shade(ac, 0.80); FX.fill();
    } else if (hv < 0.45) { // djed pillar
      FX.beginPath(); FX.moveTo(x + 10, gy + 2); FX.lineTo(x + 10, gy + 18);
      for (let dj = 0; dj < 4; dj++) { FX.moveTo(x + 4, gy + 5 + dj * 3); FX.lineTo(x + 16, gy + 5 + dj * 3); }
      FX.stroke();
    } else if (hv < 0.72) { // scarab oval
      FX.beginPath(); FX.ellipse(x + 10, gy + 8, 7, 9, 0, 0, Math.PI * 2); FX.stroke();
      FX.beginPath(); FX.moveTo(x + 10, gy); FX.lineTo(x + 10, gy - 4); FX.stroke();
    } else { // ankh
      FX.beginPath(); FX.arc(x + 10, gy + 5, 4, 0, Math.PI * 2); FX.stroke();
      FX.beginPath(); FX.moveTo(x + 10, gy + 9); FX.lineTo(x + 10, gy + 18);
      FX.moveTo(x + 5,  gy + 12); FX.lineTo(x + 15, gy + 12); FX.stroke();
    }
  }
  FX.globalAlpha = 1;
  FX.restore();

  // --- mid: lotus columns ---
  FX.save(); FX.translate(-mid, 0);
  for (let x = 60; x < W + 600; x += 310) {
    // column shaft
    const cg = FX.createLinearGradient(x, 0, x + 52, 0);
    cg.addColorStop(0,   shade(pc, 0.38));
    cg.addColorStop(0.5, shade(pc, 0.55));
    cg.addColorStop(1,   shade(pc, 0.30));
    FX.fillStyle = cg; FX.fillRect(x, H * 0.05, 52, floorY - H * 0.05);
    // horizontal drum rings
    FX.fillStyle = shade(ac, 0.22); FX.globalAlpha = 0.25;
    for (let gy = H * 0.10; gy < floorY; gy += 60) FX.fillRect(x, gy, 52, 7);
    FX.globalAlpha = 1;
    // lotus cap: fan of petals
    FX.fillStyle = shade(ac, 0.72); FX.globalAlpha = 0.78;
    for (let pi = -3; pi <= 3; pi++) {
      const pa = -Math.PI * 0.5 + pi * 0.24;
      FX.beginPath();
      FX.moveTo(x + 26, H * 0.05);
      FX.quadraticCurveTo(x + 26 + Math.cos(pa - 0.14) * 44, H * 0.05 - 32,
                          x + 26 + Math.cos(pa) * 56, H * 0.05 - 42);
      FX.quadraticCurveTo(x + 26 + Math.cos(pa + 0.14) * 44, H * 0.05 - 32,
                          x + 26, H * 0.05);
      FX.fill();
    }
    FX.globalAlpha = 1;
    // base plinth
    FX.fillStyle = shade(pc, 0.46);
    FX.fillRect(x - 8, floorY - 10, 68, 10);
    // torch sconce
    FX.fillStyle = shade(pc, 0.35);
    FX.fillRect(x + 54, H * 0.30, 18, 4); FX.fillRect(x + 54 + 18, H * 0.28, 5, 9);
    const flk = 0.8 + Math.sin(GS.tick * 0.17 + x) * 0.12 + Math.sin(GS.tick * 0.41 + x) * 0.08;
    softGlow(x - mid + 54 + 23, H * 0.27, 44 * flk, '255,140,30', 0.32 * flk);
    FX.fillStyle = `rgba(255,160,40,${(0.72 * flk).toFixed(2)})`;
    FX.beginPath(); FX.ellipse(x + 54 + 23, H * 0.26, 4, 8 * flk, 0, 0, Math.PI * 2); FX.fill();
  }
  FX.restore();

  // --- floor: sandy with cartouche ovals ---
  FX.save(); FX.translate(-cam * 0.55, 0);
  const flg = FX.createLinearGradient(0, floorY, 0, H);
  flg.addColorStop(0, shade(pc, 0.42));
  flg.addColorStop(1, shade(pc, 0.22));
  FX.fillStyle = flg; FX.fillRect(0, floorY, W + 800, H - floorY);
  granulate(W * 0.5, floorY + (H - floorY) * 0.5, W * 0.5 + 400, (H - floorY) * 0.5 + 4,
            pc.replace('rgb(','').replace(')',''), 80, 99);
  // cartouche oval patterns
  FX.strokeStyle = shade(ac, 0.58); FX.lineWidth = 1.5; FX.globalAlpha = 0.18;
  for (let cx = 100; cx < W + 800; cx += 180) {
    FX.beginPath(); FX.ellipse(cx, floorY + 22, 38, 12, 0, 0, Math.PI * 2); FX.stroke();
    FX.beginPath(); FX.moveTo(cx - 22, floorY + 12); FX.lineTo(cx + 22, floorY + 12); FX.stroke();
  }
  FX.globalAlpha = 1;
  FX.restore();
}

// ── Stage 2 — Samurai Gallery ─────────────────────────────────────────────────
function drawBG_Samurai(pc, ac, cam, floorY) {
  const far = cam * 0.15, mid = cam * 0.35;

  // --- far: warm wood panel walls ---
  FX.save(); FX.translate(-far, 0);
  FX.fillStyle = shade(pc, 0.30);
  FX.fillRect(0, 0, W + 600, floorY);
  // horizontal rail lines
  const rails = [0.10, 0.25, 0.55, 0.68];
  for (const ry of rails) {
    FX.fillStyle = shade(pc, 0.42); FX.fillRect(0, H * ry, W + 600, 6);
  }
  // vertical panel dividers
  FX.strokeStyle = shade(pc, 0.22); FX.lineWidth = 2;
  for (let x = 0; x < W + 600; x += 110) {
    FX.beginPath(); FX.moveTo(x, 0); FX.lineTo(x, floorY); FX.stroke();
  }
  // shoji screen pattern (upper wall)
  FX.fillStyle = 'rgba(255,245,220,0.06)';
  for (let x = 0; x < W + 600; x += 36)
    for (let y = H * 0.01; y < H * 0.24; y += 28) FX.fillRect(x + 2, y + 2, 32, 24);
  FX.strokeStyle = shade(pc, 0.45); FX.lineWidth = 1; FX.globalAlpha = 0.35;
  for (let x = 0; x < W + 600; x += 36) {
    FX.beginPath(); FX.moveTo(x, H * 0.01); FX.lineTo(x, H * 0.24); FX.stroke();
  }
  for (let y = H * 0.01; y < H * 0.24; y += 28) {
    FX.beginPath(); FX.moveTo(0, y); FX.lineTo(W + 600, y); FX.stroke();
  }
  FX.globalAlpha = 1;
  // enso circles
  for (let x = 160; x < W + 600; x += 440) {
    FX.strokeStyle = shade(ac, 0.62); FX.lineWidth = 4; FX.globalAlpha = 0.22;
    FX.beginPath(); FX.arc(x, H * 0.42, 44, 0.3, Math.PI * 1.88); FX.stroke();
    FX.globalAlpha = 1;
  }
  FX.restore();

  // --- mid: katana mounts + floor transition ---
  FX.save(); FX.translate(-mid, 0);
  for (let x = 80; x < W + 600; x += 380) {
    // lacquered stand
    FX.fillStyle = shade(pc, 0.46);
    FX.fillRect(x, H * 0.34, 190, 5); FX.fillRect(x, H * 0.46, 190, 5);
    // sword lines (diagonal)
    for (let ki = 0; ki < 3; ki++) {
      const sx = x + 25 + ki * 55, sa = -0.42 + ki * 0.04;
      FX.save(); FX.translate(sx, H * 0.30);
      FX.rotate(sa);
      FX.strokeStyle = 'rgba(210,210,220,0.70)'; FX.lineWidth = 2.2;
      FX.beginPath(); FX.moveTo(0, -82); FX.lineTo(0, 40); FX.stroke();
      // guard circle
      FX.strokeStyle = shade(ac, 0.72); FX.lineWidth = 3.5;
      FX.beginPath(); FX.arc(0, 0, 7, 0, Math.PI * 2); FX.stroke();
      FX.restore();
    }
  }
  // torch sconce glow
  for (let x = 200; x < W + 600; x += 480) {
    const flk = 0.8 + Math.sin(GS.tick * 0.19 + x) * 0.14;
    softGlow(x - mid, H * 0.28, 55 * flk, '255,130,20', 0.28 * flk);
    FX.fillStyle = `rgba(255,150,30,${(0.68 * flk).toFixed(2)})`;
    FX.beginPath(); FX.ellipse(x, H * 0.26, 5, 10 * flk, 0, 0, Math.PI * 2); FX.fill();
  }
  FX.restore();

  // --- floor: stone/wood planks ---
  FX.save(); FX.translate(-cam * 0.55, 0);
  FX.fillStyle = shade(pc, 0.34);
  FX.fillRect(0, floorY, W + 800, H - floorY);
  FX.strokeStyle = shade(pc, 0.24); FX.lineWidth = 2; FX.globalAlpha = 0.35;
  for (let x = 0; x < W + 800; x += 95) {
    FX.beginPath(); FX.moveTo(x, floorY); FX.lineTo(x, H); FX.stroke();
  }
  FX.globalAlpha = 1;
  FX.restore();
}

// ── Stage 3 — Royal Chambers ──────────────────────────────────────────────────
function drawBG_Royal(pc, ac, cam, floorY) {
  const far = cam * 0.15, mid = cam * 0.35;

  // --- far: deep velvet walls with vertical wave texture ---
  FX.save(); FX.translate(-far, 0);
  const vg = FX.createLinearGradient(0, 0, 0, floorY);
  vg.addColorStop(0, shade(pc, 0.22));
  vg.addColorStop(1, shade(pc, 0.14));
  FX.fillStyle = vg; FX.fillRect(0, 0, W + 600, floorY);
  // pseudo-velvet wave curves
  FX.strokeStyle = shade(pc, 0.32); FX.lineWidth = 1; FX.globalAlpha = 0.38;
  for (let x = 0; x < W + 600; x += 18) {
    FX.beginPath(); FX.moveTo(x, 0);
    for (let y = 0; y < floorY; y += 30) {
      const wv = Math.sin(y * 0.08 + x * 0.05) * 4;
      FX.lineTo(x + wv, y);
    }
    FX.stroke();
  }
  FX.globalAlpha = 1;
  // baroque wall molding
  const moldY = H * 0.12;
  for (let i = 0; i < 4; i++) {
    FX.strokeStyle = shade(ac, 0.60 + i * 0.06); FX.lineWidth = 3 - i * 0.5;
    FX.globalAlpha = 0.18 + i * 0.06;
    FX.strokeRect(i * 6, moldY + i * 5, W + 600 - i * 12, floorY - moldY - i * 10);
  }
  FX.globalAlpha = 1;
  // tall Gothic window cutouts
  for (let x = 280; x < W + 600; x += 560) {
    // night sky inside
    const wg = FX.createLinearGradient(x - 55, 0, x + 55, 0);
    wg.addColorStop(0, 'rgba(10,0,24,0.90)');
    wg.addColorStop(1, 'rgba(18,0,36,0.90)');
    FX.fillStyle = wg;
    // pointed arch fill
    FX.beginPath();
    FX.moveTo(x - 52, floorY * 0.88);
    FX.lineTo(x - 52, floorY * 0.42);
    FX.quadraticCurveTo(x - 52, H * 0.04, x, H * 0.02);
    FX.quadraticCurveTo(x + 52, H * 0.04, x + 52, floorY * 0.42);
    FX.lineTo(x + 52, floorY * 0.88);
    FX.closePath(); FX.fill();
    // stars inside window
    for (let si = 0; si < 16; si++) {
      const sx = x - 45 + _h(si, x) * 90;
      const sy = H * 0.05 + _h(si + 1, x) * floorY * 0.75;
      FX.fillStyle = `rgba(255,255,200,${(0.28 + _h(si, x + 1) * 0.32).toFixed(2)})`;
      FX.beginPath(); FX.arc(sx, sy, 0.8 + _h(si * 2, x) * 1.6, 0, Math.PI * 2); FX.fill();
    }
    // frame
    FX.strokeStyle = shade(ac, 0.82); FX.lineWidth = 4;
    FX.beginPath();
    FX.moveTo(x - 52, floorY * 0.88);
    FX.lineTo(x - 52, floorY * 0.42);
    FX.quadraticCurveTo(x - 52, H * 0.04, x, H * 0.02);
    FX.quadraticCurveTo(x + 52, H * 0.04, x + 52, floorY * 0.42);
    FX.lineTo(x + 52, floorY * 0.88);
    FX.stroke();
  }
  FX.restore();

  // --- mid: grand chandelier ---
  FX.save(); FX.translate(-mid, 0);
  for (let x = 270; x < W + 600; x += 540) {
    const flk = 0.88 + Math.sin(GS.tick * 0.11) * 0.08 + Math.sin(GS.tick * 0.31) * 0.04;
    softGlow(x - mid, H * 0.08, 160 * flk, ac, 0.10 * flk);
    softGlow(x - mid, H * 0.08, 55,  '255,245,192', 0.22 * flk);
    // central orb
    FX.beginPath(); FX.arc(x, H * 0.06, 20, 0, Math.PI * 2);
    FX.fillStyle = shade(ac, 0.85); FX.fill();
    // arms
    for (let ci = 0; ci < 8; ci++) {
      const ca = (ci / 8) * Math.PI * 2 - Math.PI / 2;
      const ex = x + Math.cos(ca) * 105, ey = H * 0.08 + Math.sin(ca) * 22;
      FX.strokeStyle = shade(ac, 0.70); FX.lineWidth = 2;
      FX.beginPath(); FX.moveTo(x, H * 0.08); FX.lineTo(ex, ey); FX.stroke();
      // crystal drops
      FX.fillStyle = shade(ac, 0.55); FX.globalAlpha = 0.80 * flk;
      FX.beginPath(); FX.moveTo(ex, ey); FX.lineTo(ex - 4, ey + 14); FX.lineTo(ex + 4, ey + 14); FX.closePath(); FX.fill();
      FX.globalAlpha = 1;
      softGlow(ex - mid, ey - 6, 18 * flk, '255,245,192', 0.22 * flk);
    }
  }
  FX.restore();

  // --- floor: marble with vein lines ---
  FX.save(); FX.translate(-cam * 0.55, 0);
  const mg = FX.createLinearGradient(0, floorY, 0, H);
  mg.addColorStop(0, shade(pc, 0.48));
  mg.addColorStop(0.5, shade(pc, 0.55));
  mg.addColorStop(1, shade(pc, 0.36));
  FX.fillStyle = mg; FX.fillRect(0, floorY, W + 800, H - floorY);
  // diagonal vein lines
  FX.strokeStyle = shade(ac, 0.52); FX.lineWidth = 1; FX.globalAlpha = 0.12;
  for (let d = 0; d < W + 800 + H; d += 44) {
    FX.beginPath(); FX.moveTo(d, floorY); FX.lineTo(d - H * 0.22, H); FX.stroke();
    FX.beginPath(); FX.moveTo(d, H); FX.lineTo(d + H * 0.18, floorY); FX.stroke();
  }
  FX.globalAlpha = 1;
  FX.restore();
}

// ── Stage 4 — Museum Wing ─────────────────────────────────────────────────────
function drawBG_Museum(pc, ac, cam, floorY) {
  const far = cam * 0.15, mid = cam * 0.35;

  // --- far: off-white stone walls with panel joints ---
  FX.save(); FX.translate(-far, 0);
  FX.fillStyle = shade(pc, 0.36);
  FX.fillRect(0, 0, W + 600, floorY);
  FX.strokeStyle = shade(pc, 0.26); FX.lineWidth = 2; FX.globalAlpha = 0.28;
  for (let x = 0; x < W + 600; x += 260) {
    FX.beginPath(); FX.moveTo(x, 0); FX.lineTo(x, floorY); FX.stroke();
  }
  for (let y = 0; y < floorY; y += 180) {
    FX.beginPath(); FX.moveTo(0, y); FX.lineTo(W + 600, y); FX.stroke();
  }
  FX.globalAlpha = 1;
  FX.restore();

  // --- mid: glass display cases + exhibition plinths ---
  FX.save(); FX.translate(-mid, 0);
  for (let x = 55; x < W + 600; x += 340) {
    // display case
    FX.strokeStyle = 'rgba(180,220,230,0.60)'; FX.lineWidth = 2;
    FX.strokeRect(x, H * 0.26, 170, H * 0.46);
    FX.fillStyle = 'rgba(180,220,230,0.05)'; FX.fillRect(x + 2, H * 0.28, 166, H * 0.44);
    // artifact inside
    const av = _h(x, 9);
    FX.fillStyle = shade(ac, 0.62); FX.globalAlpha = 0.55;
    if (av < 0.33) { // urn
      FX.beginPath(); FX.ellipse(x + 85, H * 0.59, 22, 32, 0, 0, Math.PI * 2); FX.fill();
      FX.beginPath(); FX.ellipse(x + 85, H * 0.46, 14, 9, 0, 0, Math.PI * 2); FX.fill();
      FX.fillRect(x + 82, H * 0.36, 6, 10);
    } else if (av < 0.66) { // mask
      FX.beginPath(); FX.ellipse(x + 85, H * 0.50, 20, 26, 0, 0, Math.PI * 2); FX.fill();
      FX.fillStyle = shade(pc, 0.24); FX.globalAlpha = 0.68;
      FX.beginPath(); FX.ellipse(x + 77, H * 0.47, 5, 4, -0.2, 0, Math.PI * 2); FX.fill();
      FX.beginPath(); FX.ellipse(x + 93, H * 0.47, 5, 4, 0.2, 0, Math.PI * 2); FX.fill();
    } else { // vase
      FX.beginPath(); FX.ellipse(x + 85, H * 0.56, 16, 22, 0, 0, Math.PI * 2); FX.fill();
      FX.beginPath(); FX.ellipse(x + 85, H * 0.40, 11, 7, 0, 0, Math.PI * 2); FX.fill();
    }
    FX.globalAlpha = 1;
    // plinth
    FX.fillStyle = shade(pc, 0.44);
    FX.fillRect(x + 20, H * 0.72, 130, 18); FX.fillRect(x + 12, H * 0.70, 146, 10);
    // track lighting cone
    FX.fillStyle = 'rgba(255,255,230,0.06)';
    FX.beginPath(); FX.moveTo(x + 85, 0); FX.lineTo(x + 55, H * 0.30); FX.lineTo(x + 115, H * 0.30); FX.closePath(); FX.fill();
    softGlow(x - mid + 85, H * 0.32, 36, '255,255,230', 0.22);
  }
  FX.restore();

  // --- floor: polished marble grid ---
  FX.save(); FX.translate(-cam * 0.55, 0);
  const flg = FX.createLinearGradient(0, floorY, 0, H);
  flg.addColorStop(0, shade(pc, 0.52));
  flg.addColorStop(1, shade(pc, 0.35));
  FX.fillStyle = flg; FX.fillRect(0, floorY, W + 800, H - floorY);
  FX.strokeStyle = shade(pc, 0.30); FX.lineWidth = 1.5; FX.globalAlpha = 0.32;
  for (let x = 0; x < W + 800; x += 110) {
    FX.beginPath(); FX.moveTo(x, floorY); FX.lineTo(x, H); FX.stroke();
  }
  for (let y = floorY; y < H; y += 80) {
    FX.beginPath(); FX.moveTo(0, y); FX.lineTo(W + 800, y); FX.stroke();
  }
  FX.globalAlpha = 1;
  FX.restore();
}

// ── Stage 5 — Tech Manor ──────────────────────────────────────────────────────
function drawBG_Tech(pc, ac, cam, floorY) {
  const far = cam * 0.15, mid = cam * 0.35;

  // --- far: very dark walls + neon circuit traces ---
  FX.save(); FX.translate(-far, 0);
  FX.fillStyle = shade(pc, 0.14);
  FX.fillRect(0, 0, W + 600, floorY);
  // circuit trace network
  FX.strokeStyle = shade(ac, 0.80); FX.lineWidth = 1.5; FX.globalAlpha = 0.28;
  for (let x = 0; x < W + 600; x += 120) {
    const y0 = H * 0.10 + _h(x, 0) * H * 0.50;
    FX.beginPath(); FX.moveTo(x, y0); FX.lineTo(x + 80, y0);
    // branch
    FX.moveTo(x + 40, y0); FX.lineTo(x + 40, y0 - 22 - _h(x, 1) * 30);
    FX.moveTo(x + 40, y0); FX.lineTo(x + 40, y0 + 18 + _h(x, 2) * 28);
    FX.stroke();
    // node dot
    FX.beginPath(); FX.arc(x + 40, y0, 3, 0, Math.PI * 2);
    FX.fillStyle = shade(ac, 0.90); FX.fill();
  }
  FX.globalAlpha = 1;
  // server-rack silhouettes
  for (let x = 20; x < W + 600; x += 480) {
    FX.fillStyle = shade(pc, 0.20);
    FX.fillRect(x, H * 0.08, 90, floorY - H * 0.08);
    FX.fillStyle = shade(pc, 0.26);
    FX.fillRect(x + 4, H * 0.10, 82, floorY - H * 0.12);
    // indicator LEDs
    for (let ly = H * 0.12; ly < floorY - 10; ly += 22) {
      const ledv = _h(x + ly, 5);
      FX.fillStyle = ledv < 0.33 ? 'rgba(68,255,100,0.68)'
                   : ledv < 0.55 ? shade(ac, 0.90)
                   : 'rgba(255,80,60,0.55)';
      FX.fillRect(x + 9, ly + 8, 5, 5);
    }
  }
  FX.restore();

  // --- mid: holographic panel displays ---
  FX.save(); FX.translate(-mid, 0);
  for (let x = 150; x < W + 600; x += 420) {
    // panel border
    FX.strokeStyle = shade(ac, 0.82); FX.lineWidth = 1.5;
    FX.strokeRect(x, H * 0.18, 195, H * 0.46);
    FX.fillStyle = `rgba(0,20,50,0.35)`;
    FX.fillRect(x + 1, H * 0.19, 193, H * 0.44);
    // scanlines
    FX.globalAlpha = 0.07;
    for (let sy = H * 0.19; sy < H * 0.63; sy += 5) {
      FX.fillStyle = shade(ac, 0.60); FX.fillRect(x + 1, sy, 193, 2);
    }
    FX.globalAlpha = 1;
    // data bars
    FX.fillStyle = shade(ac, 0.70); FX.globalAlpha = 0.30;
    for (let bi = 0; bi < 9; bi++) {
      const bw = 20 + _h(bi, x) * 120;
      FX.fillRect(x + 8, H * 0.22 + bi * 28, bw, 14);
    }
    FX.globalAlpha = 1;
    // ambient panel glow
    softGlow(x - mid + 97, H * 0.41, 80, ac, 0.08);
  }
  // hexagonal grid floor
  const hx = (r) => r * Math.sqrt(3), hy = (r) => r;
  const hr = 28;
  for (let col = 0; col < Math.ceil((W + 600) / (hx(hr) * 2)) + 2; col++) {
    for (let row = 0; row < 4; row++) {
      const cx2 = col * hx(hr) * 2 + (row % 2) * hx(hr);
      const cy2 = floorY + 4 + row * hy(hr) * 1.5;
      const lit = _h(col * 17 + row * 5, 3) > 0.62;
      FX.beginPath();
      for (let vi = 0; vi < 6; vi++) {
        const va = (Math.PI / 6) + vi * (Math.PI / 3);
        const vx = cx2 + hr * Math.cos(va), vy2 = cy2 + hr * Math.sin(va);
        vi === 0 ? FX.moveTo(vx, vy2) : FX.lineTo(vx, vy2);
      }
      FX.closePath();
      FX.fillStyle = lit ? shade(ac, 0.28) : shade(pc, 0.18);
      FX.globalAlpha = lit ? 0.35 : 0.18;
      FX.fill();
      FX.strokeStyle = shade(ac, 0.55); FX.lineWidth = 1; FX.globalAlpha = 0.25;
      FX.stroke();
      FX.globalAlpha = 1;
    }
  }
  FX.restore();

  // dark floor base
  FX.save(); FX.translate(-cam * 0.55, 0);
  FX.fillStyle = shade(pc, 0.16);
  FX.fillRect(0, floorY, W + 800, 6);
  softGlow(W * 0.5, floorY, W * 0.5, ac, 0.06);
  FX.restore();
}

// ── Stage 6 — Armory Corridor ─────────────────────────────────────────────────
function drawBG_Armory(pc, ac, cam, floorY) {
  const far = cam * 0.15, mid = cam * 0.35;

  // --- far: rough stone block walls ---
  FX.save(); FX.translate(-far, 0);
  const bw = 148, bh = 62;
  FX.fillStyle = shade(pc, 0.26);
  FX.fillRect(0, 0, W + 600, floorY);
  FX.strokeStyle = shade(pc, 0.18); FX.lineWidth = 3; FX.globalAlpha = 0.45;
  for (let row = 0; row * bh < floorY + bh; row++) {
    FX.beginPath(); FX.moveTo(0, row * bh); FX.lineTo(W + 600, row * bh); FX.stroke();
    const off = (row % 2) * (bw / 2);
    for (let col = 0; col * bw < W + 600 + bw; col++) {
      FX.beginPath(); FX.moveTo(col * bw + off, row * bh); FX.lineTo(col * bw + off, (row + 1) * bh); FX.stroke();
    }
  }
  FX.globalAlpha = 1;
  // Gothic stone arches
  for (let x = 250; x < W + 600; x += 500) {
    FX.strokeStyle = shade(ac, 0.50); FX.lineWidth = 5; FX.globalAlpha = 0.28;
    FX.beginPath();
    FX.moveTo(x - 88, floorY);
    FX.lineTo(x - 88, floorY * 0.45);
    FX.quadraticCurveTo(x - 88, H * 0.05, x, H * 0.02);
    FX.quadraticCurveTo(x + 88, H * 0.05, x + 88, floorY * 0.45);
    FX.lineTo(x + 88, floorY);
    FX.stroke();
    FX.globalAlpha = 1;
  }
  FX.restore();

  // --- mid: iron weapon bracket mounts ---
  FX.save(); FX.translate(-mid, 0);
  for (let x = 120; x < W + 600; x += 350) {
    // bracket mount base
    FX.fillStyle = shade(pc, 0.40);
    FX.fillRect(x - 4, H * 0.28, 8, 18); FX.fillRect(x - 26, H * 0.34, 52, 6);
    // crossed swords (two rotated thin rects)
    for (let si = 0; si < 2; si++) {
      const angle = (si === 0 ? -0.38 : 0.38);
      FX.save(); FX.translate(x, H * 0.46); FX.rotate(angle);
      FX.fillStyle = 'rgba(192,192,200,0.55)'; FX.fillRect(-2, -58, 4, 116);
      // guard
      FX.strokeStyle = shade(ac, 0.65); FX.lineWidth = 3;
      FX.beginPath(); FX.moveTo(-12, 0); FX.lineTo(12, 0); FX.stroke();
      FX.restore();
    }
    // torch sconce
    FX.fillStyle = shade(pc, 0.42); FX.fillRect(x + 60, H * 0.30, 22, 5);
    const flk = 0.80 + Math.sin(GS.tick * 0.21 + x) * 0.14 + Math.sin(GS.tick * 0.47 + x) * 0.06;
    softGlow(x - mid + 82, H * 0.28, 52 * flk, '255,130,20', 0.30 * flk);
    FX.fillStyle = `rgba(255,155,35,${(0.72 * flk).toFixed(2)})`;
    FX.beginPath(); FX.ellipse(x + 82, H * 0.26, 5, 10 * flk, 0, 0, Math.PI * 2); FX.fill();
  }
  FX.restore();

  // --- floor: worn flagstone tiles ---
  FX.save(); FX.translate(-cam * 0.55, 0);
  FX.fillStyle = shade(pc, 0.30);
  FX.fillRect(0, floorY, W + 800, H - floorY);
  FX.strokeStyle = shade(pc, 0.20); FX.lineWidth = 3; FX.globalAlpha = 0.40;
  const tw = 120, th = (H - floorY);
  for (let col = 0; col * tw < W + 800; col++) {
    FX.beginPath(); FX.moveTo(col * tw, floorY); FX.lineTo(col * tw, H); FX.stroke();
  }
  FX.beginPath(); FX.moveTo(0, floorY + th * 0.5); FX.lineTo(W + 800, floorY + th * 0.5); FX.stroke();
  // irregular grout blobs
  FX.globalAlpha = 0.15;
  for (let i = 0; i < 32; i++) {
    FX.beginPath(); FX.arc(_h(i, 90) * (W + 800), floorY + 5 + _h(i, 91) * (H - floorY - 10), 4 + _h(i, 92) * 8, 0, Math.PI * 2);
    FX.fillStyle = shade(pc, 0.18); FX.fill();
  }
  FX.globalAlpha = 1;
  FX.restore();
}

// ── Stage 7 — Art Gallery ─────────────────────────────────────────────────────
function drawBG_ArtGallery(pc, ac, cam, floorY) {
  const far = cam * 0.15, mid = cam * 0.35;

  // --- far: deep crimson/burgundy walls with dado rail ---
  FX.save(); FX.translate(-far, 0);
  const wg = FX.createLinearGradient(0, 0, 0, floorY);
  wg.addColorStop(0, shade(pc, 0.20));
  wg.addColorStop(1, shade(pc, 0.14));
  FX.fillStyle = wg; FX.fillRect(0, 0, W + 600, floorY);
  // dado rail
  FX.fillStyle = shade(ac, 0.78); FX.globalAlpha = 0.55;
  FX.fillRect(0, H * 0.62, W + 600, 7);
  FX.fillRect(0, H * 0.65, W + 600, 3);
  FX.globalAlpha = 1;
  // wainscot below dado
  const dag = FX.createLinearGradient(0, H * 0.65, 0, floorY);
  dag.addColorStop(0, shade(pc, 0.24));
  dag.addColorStop(1, shade(pc, 0.18));
  FX.fillStyle = dag; FX.fillRect(0, H * 0.65, W + 600, floorY - H * 0.65);
  // ceiling coffers
  for (let x = 0; x < W + 600; x += 140) {
    for (let ci = 0; ci < 2; ci++) {
      FX.strokeStyle = shade(ac, 0.50); FX.lineWidth = 2; FX.globalAlpha = 0.18;
      FX.strokeRect(x + 4 + ci * 4, H * 0.01 + ci * 4, 132 - ci * 8, H * 0.07 - ci * 8);
      // central rosette
      FX.beginPath(); FX.arc(x + 70, H * 0.045, 4 - ci * 1.5, 0, Math.PI * 2);
      FX.fillStyle = shade(ac, 0.65); FX.fill();
      FX.globalAlpha = 1;
    }
  }
  FX.restore();

  // --- mid: large ornate gold-frame paintings ---
  FX.save(); FX.translate(-mid, 0);
  for (let x = 42; x < W + 600; x += 430) {
    const pw = 210, ph = 150, py = H * 0.13;
    // outer frame
    FX.strokeStyle = shade(ac, 0.90); FX.lineWidth = 8;
    FX.strokeRect(x, py, pw, ph);
    // inner frame
    FX.strokeStyle = shade(ac, 0.70); FX.lineWidth = 4;
    FX.strokeRect(x + 10, py + 10, pw - 20, ph - 20);
    // corner flourish arcs
    FX.strokeStyle = shade(ac, 0.65); FX.lineWidth = 2; FX.globalAlpha = 0.65;
    for (const [fcx, fcy, fa] of [
      [x + 14, py + 14, 0], [x + pw - 14, py + 14, Math.PI * 0.5],
      [x + 14, py + ph - 14, -Math.PI * 0.5], [x + pw - 14, py + ph - 14, Math.PI],
    ]) {
      FX.beginPath(); FX.arc(fcx, fcy, 14, fa, fa + Math.PI * 0.5); FX.stroke();
    }
    FX.globalAlpha = 1;
    // painted canvas scene
    const palette2 = [0x4a1520, 0x1a3048, 0x2c4a18, 0x483820, 0x301848, 0x482418];
    const mc = palette2[Math.floor(_h(x, 11) * palette2.length)];
    const cg2 = FX.createLinearGradient(x + 14, py + 14, x + pw - 14, py + ph - 14);
    cg2.addColorStop(0, `rgb(${(mc>>16)&255},${(mc>>8)&255},${mc&255})`);
    cg2.addColorStop(1, shade(pc, 0.28));
    FX.fillStyle = cg2; FX.fillRect(x + 14, py + 14, pw - 28, ph - 28);
    // soft landscape horizon suggestion
    FX.fillStyle = shade(ac, 0.30); FX.globalAlpha = 0.25;
    FX.beginPath(); FX.ellipse(x + 14 + (pw - 28) * 0.5, py + 14 + (ph - 28) * 0.55, (pw - 28) * 0.42, (ph - 28) * 0.28, 0, 0, Math.PI * 2); FX.fill();
    FX.globalAlpha = 1;
    // spotlight cone from ceiling
    FX.fillStyle = 'rgba(255,245,200,0.07)';
    FX.beginPath(); FX.moveTo(x + pw * 0.5, 0);
    FX.lineTo(x + pw * 0.5 - 30, py); FX.lineTo(x + pw * 0.5 + 30, py); FX.closePath(); FX.fill();
    softGlow(x - mid + pw * 0.5, py + ph * 0.5, 60, '255,245,200', 0.10);
  }
  FX.restore();

  // --- floor: rich dark hardwood planks ---
  FX.save(); FX.translate(-cam * 0.55, 0);
  const hg = FX.createLinearGradient(0, floorY, 0, H);
  hg.addColorStop(0, shade(pc, 0.32));
  hg.addColorStop(1, shade(pc, 0.18));
  FX.fillStyle = hg; FX.fillRect(0, floorY, W + 800, H - floorY);
  FX.strokeStyle = shade(pc, 0.22); FX.lineWidth = 1.8; FX.globalAlpha = 0.38;
  for (let x = 0; x < W + 800; x += 88) {
    FX.beginPath(); FX.moveTo(x, floorY); FX.lineTo(x, H); FX.stroke();
  }
  FX.globalAlpha = 1;
  // knot circles
  for (let i = 0; i < 24; i++) {
    const kx = _h(i, 100) * (W + 800);
    const ky = floorY + 5 + _h(i, 101) * (H - floorY - 10);
    FX.strokeStyle = shade(pc, 0.22); FX.lineWidth = 1.5; FX.globalAlpha = 0.22;
    FX.beginPath(); FX.ellipse(kx, ky, 5 + _h(i, 102) * 8, 4 + _h(i, 103) * 5, 0, 0, Math.PI * 2); FX.stroke();
    FX.globalAlpha = 1;
  }
  FX.restore();
}

// ── Stage 8 — Treasure Vault ──────────────────────────────────────────────────
function drawBG_Vault(pc, ac, cam, floorY) {
  const far = cam * 0.15, mid = cam * 0.35;
  const gemPalette = ['255,60,60', '60,230,110', '60,130,255', '255,215,0', '255,120,255', '60,240,240'];

  // --- far: dark iron/stone vault walls with riveted panels ---
  FX.save(); FX.translate(-far, 0);
  FX.fillStyle = shade(pc, 0.20);
  FX.fillRect(0, 0, W + 600, floorY);
  // riveted panels
  for (let x = 0; x < W + 600; x += 195) {
    FX.strokeStyle = shade(pc, 0.34); FX.lineWidth = 2; FX.globalAlpha = 0.38;
    FX.strokeRect(x + 8, H * 0.04, 179, floorY - H * 0.06);
    // rivets
    FX.fillStyle = shade(pc, 0.42); FX.globalAlpha = 0.50;
    for (const [rx, ry] of [[x + 12, H * 0.06], [x + 183, H * 0.06], [x + 12, floorY - 12], [x + 183, floorY - 12]]) {
      FX.beginPath(); FX.arc(rx, ry, 4, 0, Math.PI * 2); FX.fill();
    }
    FX.globalAlpha = 1;
  }
  // gem clusters in walls
  for (let i = 0; i < 28; i++) {
    const gx = _h(i, 110) * (W + 600);
    const gy = H * 0.05 + _h(i, 111) * (floorY - H * 0.10);
    const gc = gemPalette[i % 6];
    const gr = 4 + _h(i, 112) * 9;
    // diamond shape
    FX.fillStyle = `rgba(${gc},0.62)`;
    FX.beginPath();
    FX.moveTo(gx, gy - gr); FX.lineTo(gx + gr * 0.65, gy); FX.lineTo(gx, gy + gr); FX.lineTo(gx - gr * 0.65, gy); FX.closePath(); FX.fill();
    // inner highlight
    FX.fillStyle = `rgba(255,255,255,0.28)`;
    FX.beginPath();
    FX.moveTo(gx, gy - gr); FX.lineTo(gx + gr * 0.32, gy - gr * 0.2); FX.lineTo(gx, gy + gr * 0.3); FX.lineTo(gx - gr * 0.22, gy - gr * 0.18); FX.closePath(); FX.fill();
    // outer glow
    softGlow(gx - far, gy, gr * 1.8, gc, 0.15);
  }
  FX.restore();

  // --- mid: treasure chests + gold coin piles + ornate iron door arches ---
  FX.save(); FX.translate(-mid, 0);
  // door arch frames
  for (let x = 290; x < W + 600; x += 580) {
    FX.strokeStyle = shade(ac, 0.62); FX.lineWidth = 5;
    FX.beginPath();
    FX.moveTo(x - 68, floorY);
    FX.lineTo(x - 68, floorY * 0.45);
    FX.quadraticCurveTo(x - 68, H * 0.08, x, H * 0.05);
    FX.quadraticCurveTo(x + 68, H * 0.08, x + 68, floorY * 0.45);
    FX.lineTo(x + 68, floorY);
    FX.stroke();
    // rivet dots on frame
    FX.fillStyle = shade(ac, 0.72); FX.globalAlpha = 0.50;
    for (let ry = floorY * 0.48; ry < floorY; ry += 38) {
      FX.beginPath(); FX.arc(x - 68, ry, 4, 0, Math.PI * 2); FX.fill();
      FX.beginPath(); FX.arc(x + 68, ry, 4, 0, Math.PI * 2); FX.fill();
    }
    FX.globalAlpha = 1;
  }
  // gold coin piles at wall base
  for (let x = 60; x < W + 600; x += 220) {
    const ph = 18 + _h(x, 7) * 28;
    for (let ci = 0; ci < 10; ci++) {
      const cog = FX.createRadialGradient(
        x + 8 + _h(ci, x) * 100, floorY - ph + _h(ci + 1, x) * ph,
        1,
        x + 8 + _h(ci, x) * 100, floorY - ph + _h(ci + 1, x) * ph,
        9
      );
      cog.addColorStop(0, 'rgba(255,235,80,0.90)');
      cog.addColorStop(1, 'rgba(180,130,10,0.55)');
      FX.fillStyle = cog;
      FX.beginPath(); FX.ellipse(x + 8 + _h(ci, x) * 100, floorY - 4 - _h(ci + 1, x) * ph, 9, 5.5, 0, 0, Math.PI * 2); FX.fill();
    }
  }
  // treasure chests
  for (let x = 130; x < W + 600; x += 520) {
    // body
    FX.fillStyle = shade(pc, 0.36); FX.fillRect(x, floorY - 48, 88, 38);
    // iron straps
    FX.strokeStyle = shade(pc, 0.24); FX.lineWidth = 4;
    FX.strokeRect(x, floorY - 48, 88, 38);
    FX.beginPath(); FX.moveTo(x + 26, floorY - 48); FX.lineTo(x + 26, floorY - 10); FX.stroke();
    FX.beginPath(); FX.moveTo(x + 62, floorY - 48); FX.lineTo(x + 62, floorY - 10); FX.stroke();
    // arc lid
    FX.fillStyle = shade(pc, 0.44);
    FX.beginPath(); FX.ellipse(x + 44, floorY - 48, 44, 16, 0, Math.PI, 0); FX.fill();
    FX.strokeStyle = shade(ac, 0.70); FX.lineWidth = 3;
    FX.beginPath(); FX.ellipse(x + 44, floorY - 48, 44, 16, 0, Math.PI, 0); FX.stroke();
    // lock
    FX.fillStyle = shade(ac, 0.80); FX.beginPath(); FX.arc(x + 44, floorY - 28, 7, 0, Math.PI * 2); FX.fill();
    softGlow(x - mid + 44, floorY - 28, 22, ac, 0.18);
  }
  FX.restore();

  // --- floor: dark jeweled ground + scattered gem glints ---
  FX.save(); FX.translate(-cam * 0.55, 0);
  FX.fillStyle = shade(pc, 0.22);
  FX.fillRect(0, floorY, W + 800, H - floorY);
  // gem glints (seeded star shapes)
  for (let i = 0; i < 55; i++) {
    const gx = _h(i, 120) * (W + 800);
    const gy = floorY + 4 + _h(i, 121) * (H - floorY - 8);
    const gc = gemPalette[i % 6];
    const gr2 = 1.5 + _h(i, 122) * 4;
    FX.fillStyle = `rgba(${gc},${(0.45 + _h(i, 123) * 0.35).toFixed(2)})`;
    // 4-point star
    FX.beginPath();
    FX.moveTo(gx, gy - gr2); FX.lineTo(gx + gr2 * 0.25, gy - gr2 * 0.25);
    FX.lineTo(gx + gr2, gy); FX.lineTo(gx + gr2 * 0.25, gy + gr2 * 0.25);
    FX.lineTo(gx, gy + gr2); FX.lineTo(gx - gr2 * 0.25, gy + gr2 * 0.25);
    FX.lineTo(gx - gr2, gy); FX.lineTo(gx - gr2 * 0.25, gy - gr2 * 0.25);
    FX.closePath(); FX.fill();
  }
  FX.restore();
}

// ─── drawBoss ─────────────────────────────────────────────────────────────────
// b = { x, y, W:70, H:96, type, enraged, slamT }
// ac = rgb string e.g. "120,40,200"
function drawBoss(b, ac) {
  const x = b.x, y = b.y, W70 = b.W || 70, H96 = b.H || 96;
  const A = GS.tick;
  const pulse = Math.sin(A * 0.09) * 0.5 + 0.5;
  const ph2 = b.enraged;
  const cx = x + W70 * 0.5, cy = y + H96 * 0.5;

  // ── shockwave ring ─────────────────────────────────────────────────────────
  if (b.slamT > 0) {
    const sr = (1 - b.slamT) * 180;
    FX.strokeStyle = `rgba(${ac},${(b.slamT * 0.8).toFixed(2)})`;
    FX.lineWidth = 4;
    FX.beginPath(); FX.arc(cx, y + H96, sr, 0, Math.PI * 2); FX.stroke();
  }

  if (b.type === 'REVENANT') {
    _drawRevenant(x, y, W70, H96, cx, cy, ac, pulse, ph2);
  } else if (b.type === 'HEARTBREAKER') {
    _drawHeartbreaker(x, y, W70, H96, cx, cy, ac, pulse, ph2);
  }
}

function _drawRevenant(x, y, W70, H96, cx, cy, ac, pulse, ph2) {
  const A = GS.tick;

  // ground shadow
  castShadow(cx, y + H96, W70 * 0.85);

  // phase 2 aura
  if (ph2) {
    FX.globalAlpha = 0.22 + pulse * 0.12;
    softGlow(cx, cy, H96 * 1.1 + pulse * 22, '160,10,20', 0.45);
    FX.globalAlpha = 1;
  }

  // --- flowing cape (behind body) ---
  const capeSwing = Math.sin(A * 0.06) * 7;
  FX.fillStyle = ph2 ? 'rgba(60,0,0,0.88)' : 'rgba(14,8,22,0.88)';
  FX.beginPath();
  FX.moveTo(cx - W70 * 0.38, y + H96 * 0.22);
  FX.bezierCurveTo(
    cx - W70 * 0.82 + capeSwing, y + H96 * 0.40,
    cx - W70 * 0.92 + capeSwing, y + H96 * 0.85,
    cx - W70 * 0.32 + capeSwing, y + H96
  );
  FX.lineTo(cx + W70 * 0.32 + capeSwing, y + H96);
  FX.bezierCurveTo(
    cx + W70 * 0.92 + capeSwing, y + H96 * 0.85,
    cx + W70 * 0.78 + capeSwing, y + H96 * 0.40,
    cx + W70 * 0.38, y + H96 * 0.22
  );
  FX.closePath(); FX.fill();

  // --- tuxedo body ---
  const jacketColor = ph2 ? 'rgba(38,4,4,0.96)' : 'rgba(22,18,30,0.96)';
  FX.fillStyle = jacketColor;
  FX.fillRect(cx - W70 * 0.36, y + H96 * 0.38, W70 * 0.72, H96 * 0.54);

  // shirt front (white)
  FX.fillStyle = 'rgba(230,225,240,0.82)';
  FX.beginPath();
  FX.moveTo(cx - W70 * 0.10, y + H96 * 0.38);
  FX.lineTo(cx - W70 * 0.04, y + H96 * 0.70);
  FX.lineTo(cx + W70 * 0.04, y + H96 * 0.70);
  FX.lineTo(cx + W70 * 0.10, y + H96 * 0.38);
  FX.closePath(); FX.fill();

  // lapels
  FX.fillStyle = jacketColor;
  FX.beginPath();
  FX.moveTo(cx - W70 * 0.36, y + H96 * 0.38);
  FX.lineTo(cx - W70 * 0.10, y + H96 * 0.38);
  FX.lineTo(cx - W70 * 0.02, y + H96 * 0.52);
  FX.lineTo(cx - W70 * 0.20, y + H96 * 0.62);
  FX.lineTo(cx - W70 * 0.36, y + H96 * 0.62);
  FX.closePath(); FX.fill();
  FX.beginPath();
  FX.moveTo(cx + W70 * 0.36, y + H96 * 0.38);
  FX.lineTo(cx + W70 * 0.10, y + H96 * 0.38);
  FX.lineTo(cx + W70 * 0.02, y + H96 * 0.52);
  FX.lineTo(cx + W70 * 0.20, y + H96 * 0.62);
  FX.lineTo(cx + W70 * 0.36, y + H96 * 0.62);
  FX.closePath(); FX.fill();

  // bow tie
  FX.fillStyle = ph2 ? 'rgba(180,20,20,0.90)' : `rgba(${ac},0.80)`;
  FX.beginPath();
  FX.moveTo(cx - W70 * 0.09, y + H96 * 0.40);
  FX.lineTo(cx - W70 * 0.01, y + H96 * 0.43);
  FX.lineTo(cx - W70 * 0.09, y + H96 * 0.46);
  FX.closePath(); FX.fill();
  FX.beginPath();
  FX.moveTo(cx + W70 * 0.09, y + H96 * 0.40);
  FX.lineTo(cx + W70 * 0.01, y + H96 * 0.43);
  FX.lineTo(cx + W70 * 0.09, y + H96 * 0.46);
  FX.closePath(); FX.fill();

  // pants
  FX.fillStyle = ph2 ? 'rgba(28,2,2,0.96)' : 'rgba(16,12,22,0.96)';
  FX.fillRect(cx - W70 * 0.34, y + H96 * 0.72, W70 * 0.68, H96 * 0.28);

  // --- head ---
  const skinColor = ph2 ? 'rgba(80,12,12,0.95)' : 'rgba(46,34,28,0.95)';
  FX.fillStyle = skinColor;
  FX.beginPath(); FX.ellipse(cx, y + H96 * 0.24, W70 * 0.25, H96 * 0.17, 0, 0, Math.PI * 2); FX.fill();

  // defined jaw
  FX.fillStyle = ph2 ? 'rgba(65,8,8,0.90)' : 'rgba(36,26,20,0.90)';
  FX.beginPath(); FX.ellipse(cx, y + H96 * 0.30, W70 * 0.22, H96 * 0.09, 0, 0, Math.PI * 2); FX.fill();

  // top hat
  FX.fillStyle = ph2 ? 'rgba(32,2,2,0.96)' : 'rgba(12,10,18,0.96)';
  FX.fillRect(cx - W70 * 0.20, y + H96 * 0.04, W70 * 0.40, H96 * 0.14);
  // brim
  FX.fillRect(cx - W70 * 0.28, y + H96 * 0.14, W70 * 0.56, H96 * 0.04);
  // gold band
  FX.fillStyle = ph2 ? 'rgba(180,20,20,0.78)' : `rgba(${ac},0.78)`;
  FX.fillRect(cx - W70 * 0.20, y + H96 * 0.15, W70 * 0.40, H96 * 0.018);

  // glowing hollow eyes
  const eyeGlow = 0.55 + pulse * 0.38;
  FX.fillStyle = `rgba(${ac},${eyeGlow.toFixed(2)})`;
  FX.beginPath(); FX.ellipse(cx - W70 * 0.10, y + H96 * 0.22, W70 * 0.055, H96 * 0.038, 0, 0, Math.PI * 2); FX.fill();
  FX.beginPath(); FX.ellipse(cx + W70 * 0.10, y + H96 * 0.22, W70 * 0.055, H96 * 0.038, 0, 0, Math.PI * 2); FX.fill();
  // inner dark void
  FX.fillStyle = 'rgba(0,0,0,0.75)';
  FX.beginPath(); FX.ellipse(cx - W70 * 0.10, y + H96 * 0.22, W70 * 0.030, H96 * 0.022, 0, 0, Math.PI * 2); FX.fill();
  FX.beginPath(); FX.ellipse(cx + W70 * 0.10, y + H96 * 0.22, W70 * 0.030, H96 * 0.022, 0, 0, Math.PI * 2); FX.fill();
  // eye glow halos
  softGlow(cx - W70 * 0.10, y + H96 * 0.22, W70 * 0.12, ac, 0.20 * eyeGlow);
  softGlow(cx + W70 * 0.10, y + H96 * 0.22, W70 * 0.12, ac, 0.20 * eyeGlow);

  // --- left hand: white glove + wilted bouquet ---
  const lhx = cx - W70 * 0.54 + Math.sin(GS.tick * 0.07) * 3;
  const lhy = y + H96 * 0.72;
  FX.fillStyle = 'rgba(220,215,230,0.85)';
  FX.beginPath(); FX.ellipse(lhx, lhy, W70 * 0.12, H96 * 0.08, 0.3, 0, Math.PI * 2); FX.fill();
  // bouquet stems (drooping)
  FX.strokeStyle = 'rgba(60,90,30,0.65)'; FX.lineWidth = 1.5;
  for (let fi = -2; fi <= 2; fi++) {
    const fx2 = lhx + fi * 5, fy2 = lhy - 8;
    FX.beginPath(); FX.moveTo(fx2, fy2);
    FX.quadraticCurveTo(fx2 + fi * 4, fy2 - 18, fx2 + fi * 8, fy2 - 28); FX.stroke();
    // drooping flower heads
    FX.fillStyle = fi % 2 === 0 ? 'rgba(160,40,80,0.65)' : 'rgba(100,30,60,0.55)';
    FX.beginPath(); FX.ellipse(fx2 + fi * 8, fy2 - 28, 4, 3, fi * 0.4, 0, Math.PI * 2); FX.fill();
  }

  // --- right hand: white glove + broken gold ring ---
  const rhx = cx + W70 * 0.54 + Math.sin(GS.tick * 0.07 + 1) * 3;
  const rhy = y + H96 * 0.72;
  FX.fillStyle = 'rgba(220,215,230,0.85)';
  FX.beginPath(); FX.ellipse(rhx, rhy, W70 * 0.12, H96 * 0.08, -0.3, 0, Math.PI * 2); FX.fill();
  // broken ring (open circle with crack)
  FX.strokeStyle = `rgba(${ac},0.82)`; FX.lineWidth = 3;
  FX.beginPath(); FX.arc(rhx, rhy - 16, 9, 0.3, Math.PI * 1.9); FX.stroke();
  FX.strokeStyle = `rgba(${ac},0.40)`; FX.lineWidth = 1.5;
  FX.beginPath(); FX.moveTo(rhx + 7, rhy - 20); FX.lineTo(rhx + 11, rhy - 16); FX.lineTo(rhx + 7, rhy - 12); FX.stroke();
}

function _drawHeartbreaker(x, y, W70, H96, cx, cy, ac, pulse, ph2) {
  const A = GS.tick;

  // draw base revenant form first
  _drawRevenant(x, y, W70, H96, cx, cy, ac, pulse, ph2);

  // --- thorn crown ---
  const thornY = y + H96 * 0.06;
  FX.strokeStyle = 'rgba(50,18,6,0.88)'; FX.lineWidth = 2.5;
  for (let ti = -4; ti <= 4; ti++) {
    const tx = cx + ti * 9, ty = thornY + Math.abs(ti) * 3;
    FX.beginPath(); FX.moveTo(tx - 4, ty + 8); FX.lineTo(tx, ty - 8); FX.lineTo(tx + 4, ty + 8); FX.stroke();
    // thorn spikes
    FX.strokeStyle = 'rgba(30,8,2,0.72)'; FX.lineWidth = 1.2;
    FX.beginPath(); FX.moveTo(tx + 2, ty); FX.lineTo(tx + 8, ty - 4); FX.stroke();
    FX.beginPath(); FX.moveTo(tx - 2, ty); FX.lineTo(tx - 8, ty - 4); FX.stroke();
    FX.strokeStyle = 'rgba(50,18,6,0.88)'; FX.lineWidth = 2.5;
  }

  // --- cracked glowing heart on chest ---
  const heartCx = cx, heartCy = y + H96 * 0.54;
  const hs = 12 + pulse * 3;
  const heartGlow = ph2 ? `rgba(200,0,20,${(0.70 + pulse * 0.25).toFixed(2)})` : `rgba(${ac},${(0.60 + pulse * 0.30).toFixed(2)})`;
  FX.fillStyle = heartGlow;
  FX.beginPath();
  FX.moveTo(heartCx, heartCy + hs * 0.38);
  FX.bezierCurveTo(heartCx - hs * 1.1, heartCy - hs * 0.6, heartCx - hs * 1.1, heartCy - hs * 1.5, heartCx, heartCy - hs * 0.65);
  FX.bezierCurveTo(heartCx + hs * 1.1, heartCy - hs * 1.5, heartCx + hs * 1.1, heartCy - hs * 0.6, heartCx, heartCy + hs * 0.38);
  FX.fill();
  softGlow(heartCx, heartCy, hs * 2.8, ph2 ? '200,0,20' : ac, 0.30 * (0.6 + pulse * 0.4));
  // fracture lines
  FX.strokeStyle = 'rgba(0,0,0,0.68)'; FX.lineWidth = 1.8;
  FX.beginPath(); FX.moveTo(heartCx, heartCy - hs * 0.65); FX.lineTo(heartCx + 3, heartCy - hs * 0.2); FX.lineTo(heartCx - 2, heartCy + hs * 0.1); FX.stroke();
  FX.beginPath(); FX.moveTo(heartCx - hs * 0.4, heartCy - hs * 0.4); FX.lineTo(heartCx - hs * 0.1, heartCy); FX.stroke();
  // crimson drips
  FX.fillStyle = 'rgba(180,0,12,0.72)';
  for (let di = 0; di < 3; di++) {
    const drx = heartCx - hs * 0.3 + di * hs * 0.3;
    const dry = heartCy + hs * 0.38 + di * 8 + Math.sin(A * 0.09 + di) * 3;
    FX.beginPath(); FX.ellipse(drx, dry, 2, 4 + di * 1.5, 0, 0, Math.PI * 2); FX.fill();
  }

  // --- torn/shredded jacket edges ---
  FX.strokeStyle = 'rgba(22,6,6,0.72)'; FX.lineWidth = 2.2;
  const shredL = cx - W70 * 0.36, shredR = cx + W70 * 0.36;
  for (let sj = 0; sj < 5; sj++) {
    const sy0 = y + H96 * 0.42 + sj * H96 * 0.09;
    const jag = 5 + _h(sj, 200) * 6;
    FX.beginPath();
    FX.moveTo(shredL, sy0);
    FX.lineTo(shredL - jag, sy0 + H96 * 0.032);
    FX.lineTo(shredL, sy0 + H96 * 0.065); FX.stroke();
    FX.beginPath();
    FX.moveTo(shredR, sy0);
    FX.lineTo(shredR + jag, sy0 + H96 * 0.032);
    FX.lineTo(shredR, sy0 + H96 * 0.065); FX.stroke();
  }

  // --- phase 2 enrage: crimson skin tint + orbiting broken hearts ---
  if (ph2) {
    // crimson overlay on face
    FX.fillStyle = 'rgba(140,10,10,0.22)';
    FX.beginPath(); FX.ellipse(cx, y + H96 * 0.24, W70 * 0.27, H96 * 0.19, 0, 0, Math.PI * 2); FX.fill();

    // orbiting broken heart fragments
    for (let oi = 0; oi < 5; oi++) {
      const oa = A * 0.045 + (oi / 5) * Math.PI * 2;
      const orb = 68 + pulse * 12;
      const ox = cx + Math.cos(oa) * orb, oy = cy + Math.sin(oa) * orb * 0.55;
      const os = 6 + _h(oi, 300) * 5;
      FX.fillStyle = `rgba(200,0,20,${(0.55 + _h(oi, 301) * 0.25).toFixed(2)})`;
      // mini broken heart
      FX.beginPath();
      FX.moveTo(ox, oy + os * 0.3);
      FX.bezierCurveTo(ox - os, oy - os * 0.5, ox - os, oy - os * 1.2, ox, oy - os * 0.5);
      FX.bezierCurveTo(ox + os, oy - os * 1.2, ox + os, oy - os * 0.5, ox, oy + os * 0.3);
      FX.fill();
      FX.strokeStyle = 'rgba(0,0,0,0.50)'; FX.lineWidth = 1;
      FX.beginPath(); FX.moveTo(ox, oy - os * 0.5); FX.lineTo(ox + 2, oy); FX.stroke();
      softGlow(ox, oy, os * 1.8, '200,0,20', 0.18);
    }
  }
}
