/**
 * BackgroundBuilder — hand-painted architectural parallax backgrounds.
 *
 * Lyric theme: "Once Upon A Time" — a fairy tale of love remembered, grieved,
 * and locked away. Each stage is a room inside that memory-mansion, progressing
 * from warm nostalgia (Library) through stages of heartbreak to the sealed vault.
 *
 * Six scroll-factor layers per stage (0.05 → 0.72) painted entirely with
 * Phaser Graphics. Key visual techniques:
 *   · Proper Gothic pointed arches via fillPoints() polygon approximation
 *   · Vertical gradient washes with warm/cool temperature shifts
 *   · Deterministic pseudo-random (LCG hash — stable across reloads)
 *   · Layered semi-transparent "wash-over-wash" for painted depth
 *   · Atmospheric light shafts with floating dust motes
 *   · Stage-specific lyric-inspired motifs (torn pages, petals, shards, etc.)
 */
import Phaser from 'phaser';

export class BackgroundBuilder {
  constructor(scene, W, H, stageIndex) {
    this.scene  = scene;
    this.W      = W;
    this.H      = H;
    this.idx    = stageIndex;
    const lv    = scene.level;
    this.prim   = Phaser.Display.Color.HexStringToColor(lv.primaryColor).color;
    this.acc    = Phaser.Display.Color.HexStringToColor(lv.accentColor).color;
    this.VW     = scene.scale.width || 1280;
  }

  build() {
    const stages = [
      () => this._grandLibrary(),
      () => this._egyptianHall(),
      () => this._samuraiGallery(),
      () => this._royalChambers(),
      () => this._museumWing(),
      () => this._techManor(),
      () => this._armoryCorridor(),
      () => this._artGallery(),
      () => this._treasureVault(),
    ];
    (stages[this.idx] || stages[0])();
    this._vignette();
  }

  // ─── core helpers ──────────────────────────────────────────────────────────

  _gfx(sf, depth) {
    return this.scene.add.graphics().setScrollFactor(sf).setDepth(depth);
  }

  // Minimum draw width for a layer so it never shows a raw edge.
  _lw(sf) { return Math.ceil(this.VW + (this.W - this.VW) * sf) + 128; }

  // Vertical gradient: `steps` thin horizontal bands blended top→bottom.
  _gradV(g, x, y, w, h, cA, cB, steps = 20) {
    const sh = h / steps;
    for (let i = 0; i < steps; i++) {
      const t  = i / Math.max(steps - 1, 1);
      const ci = Phaser.Display.Color.Interpolate.ColorWithColor(
        Phaser.Display.Color.IntegerToColor(cA),
        Phaser.Display.Color.IntegerToColor(cB),
        100, Math.round(t * 100),
      );
      g.fillStyle(Phaser.Display.Color.GetColor(ci.r, ci.g, ci.b), 1);
      g.fillRect(x, y + sh * i, w, sh + 1);
    }
  }

  // Noisy gradient: same as _gradV but each band gets a tiny luminance jitter
  // for a "painted canvas" feel rather than a smooth airbrush.
  _gradVPainted(g, x, y, w, h, cA, cB, steps = 22) {
    const sh = h / steps;
    for (let i = 0; i < steps; i++) {
      const t  = i / Math.max(steps - 1, 1);
      const ci = Phaser.Display.Color.Interpolate.ColorWithColor(
        Phaser.Display.Color.IntegerToColor(cA),
        Phaser.Display.Color.IntegerToColor(cB),
        100, Math.round(t * 100),
      );
      // Tiny jitter: ±6 on each channel
      const jit = (this._h(i, x) - 0.5) * 12;
      const r = Math.max(0, Math.min(255, ci.r + jit));
      const gv = Math.max(0, Math.min(255, ci.g + jit));
      const b  = Math.max(0, Math.min(255, ci.b + jit));
      g.fillStyle(Phaser.Display.Color.GetColor(r, gv, b), 1);
      g.fillRect(x, y + sh * i, w, sh + 1);
    }
  }

  // Deterministic LCG pseudo-random in [0, 1)
  _h(a, b = 0) {
    return ((a * 1664525 + b * 1013904223 + 22695477) & 0x7fffffff) / 0x7fffffff;
  }

  // Linear-interpolate two packed int colours by fraction t ∈ [0,1]
  _lerp(cA, cB, t) {
    const a = Phaser.Display.Color.IntegerToColor(cA);
    const b = Phaser.Display.Color.IntegerToColor(cB);
    return Phaser.Display.Color.GetColor(
      Math.round(a.r + (b.r - a.r) * t),
      Math.round(a.g + (b.g - a.g) * t),
      Math.round(a.b + (b.b - a.b) * t),
    );
  }
  _darken(c, f)  { return this._lerp(c, 0x000000, f); }
  _lighten(c, f) { return this._lerp(c, 0xffffff, f); }

  // Generate arc points (helper for arch shapes)
  _arcPts(cx, cy, r, a0, a1, steps = 14) {
    const pts = [];
    for (let i = 0; i <= steps; i++) {
      const a = a0 + (a1 - a0) * (i / steps);
      pts.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
    }
    return pts;
  }

  // Gothic pointed arch fill (opening, i.e. the dark interior shape).
  // cx/baseY = bottom-centre; w = total span; h = total height to apex.
  _gothicArch(g, cx, baseY, w, h, col, alpha = 1) {
    const hw     = w / 2;
    const spring = baseY - h * 0.42;   // where the arcs start curving
    const r      = hw * 1.05;

    const pts = [
      { x: cx - hw, y: baseY },
      { x: cx - hw, y: spring },
      ...this._arcPts(cx - hw + r, spring, r, Math.PI, Math.PI * 1.5, 14),
      ...this._arcPts(cx + hw - r, spring, r, Math.PI * 1.5, Math.PI * 2, 14),
      { x: cx + hw, y: spring },
      { x: cx + hw, y: baseY },
    ];
    g.fillStyle(col, alpha);
    g.fillPoints(pts, true);
  }

  // Roman semicircular arch fill
  _roundArch(g, cx, baseY, w, h, col, alpha = 1) {
    const hw = w / 2;
    const pts = [
      { x: cx - hw, y: baseY },
      { x: cx - hw, y: baseY - h * 0.5 },
      ...this._arcPts(cx, baseY - h * 0.5, hw, Math.PI, 0, 16),
      { x: cx + hw, y: baseY - h * 0.5 },
      { x: cx + hw, y: baseY },
    ];
    g.fillStyle(col, alpha);
    g.fillPoints(pts, true);
  }

  // Faceted gem / diamond shape using fillPoints (replaces the missing fillDiamond)
  _gem(g, cx, cy, rx, ry, col, alpha = 1) {
    // Main body
    g.fillStyle(col, alpha);
    g.fillPoints([
      { x: cx,         y: cy - ry     },
      { x: cx + rx,    y: cy          },
      { x: cx + rx * 0.7, y: cy + ry * 0.8 },
      { x: cx,         y: cy + ry     },
      { x: cx - rx * 0.7, y: cy + ry * 0.8 },
      { x: cx - rx,    y: cy          },
    ], true);
    // Top-left bright facet
    g.fillStyle(0xffffff, alpha * 0.30);
    g.fillPoints([
      { x: cx,         y: cy - ry     },
      { x: cx + rx * 0.5, y: cy - ry * 0.2 },
      { x: cx + rx * 0.3, y: cy + ry * 0.3 },
      { x: cx - rx * 0.2, y: cy - ry * 0.1 },
    ], true);
    // Glow halo
    g.fillStyle(col, alpha * 0.10);
    g.fillCircle(cx, cy, Math.max(rx, ry) * 2.2);
  }

  // Stone wall: filled rect + mortar grid + irregular surface patches.
  // skipFaceVar=true omits the per-block variation pass (use for far/distant layers).
  _stoneWall(g, x, y, w, h, stoneCol, mortarCol, bh = 48, bw = 120, alpha = 1, skipFaceVar = false) {
    g.fillStyle(stoneCol, alpha);
    g.fillRect(x, y, w, h);
    // Mortar lines
    g.fillStyle(mortarCol, alpha * 0.55);
    for (let row = 0; row * bh < h + bh; row++) {
      g.fillRect(x, y + row * bh, w, 3);
      const off = (row % 2) * (bw / 2);
      for (let col2 = 0; col2 * bw < w + bw; col2++) {
        g.fillRect(x + col2 * bw + off - bw / 2, y + row * bh, 3, bh);
      }
    }
    if (skipFaceVar) return;
    // Face variation (lighter patches — hand-painting, near layers only)
    for (let px = x; px < x + w; px += bw) {
      for (let py = y; py < y + h; py += bh) {
        const row = Math.round((py - y) / bh);
        const ox  = (row % 2) * (bw / 2);
        if (this._h(px + ox, py) > 0.58) {
          g.fillStyle(0xffffff, alpha * 0.045);
          g.fillRect(px + ox + 5, py + 5, bw - 10, bh - 8);
        }
        if (this._h(px + ox + 1, py + 1) > 0.80) {
          g.fillStyle(0x000000, alpha * 0.06);
          g.fillRect(px + ox + 3, py + 3, bw - 6, bh - 6);
        }
      }
    }
  }

  // Bookshelves inside a rectangle; `seed` drives per-book variation.
  // `stride` skips books for distant/cheap layers (stride=1 = every book, stride=2 = every other)
  _books(g, x, y, w, h, nShelves, seed = 0, stride = 1) {
    const shH = h / nShelves;
    const step = 12 * stride;
    for (let s = 0; s < nShelves; s++) {
      const ty = y + s * shH;
      // Shelf board
      g.fillStyle(this._darken(this.prim, 0.25), 0.88);
      g.fillRect(x, ty + shH - 5, w, 6);
      // Books on this shelf
      for (let bx = x + 3; bx < x + w - 3; bx += step) {
        const bh2   = shH * 0.38 + this._h(bx, seed + s) * shH * 0.50;
        const shade = this._h(bx * 3, seed + s * 7);
        const bc    = shade < 0.28 ? this.acc
                    : shade < 0.52 ? this._lerp(this.acc, this.prim, 0.5)
                    : shade < 0.76 ? this.prim
                    : this._darken(this.prim, 0.40);
        g.fillStyle(bc, 0.72);
        g.fillRect(bx, ty + shH - 5 - bh2, 10, bh2);
        g.fillStyle(0xffffff, 0.055);
        g.fillRect(bx + 1, ty + shH - 5 - bh2 + 4, 2, bh2 - 8);
        if (this._h(bx * 7, seed + s) > 0.62) {
          g.fillStyle(this.acc, 0.20);
          g.fillRect(bx + 2, ty + shH - 5 - bh2 * 0.55, 7, 2);
        }
      }
    }
  }

  // Ornate classical column (fluted shaft, capital, base)
  _ornateCol(g, cx, y, colH, r, dark, light, alpha = 1) {
    const nF = 8;
    for (let i = 0; i < nF; i++) {
      g.fillStyle(i % 2 === 0 ? dark : this._lerp(dark, light, 0.42), alpha * 0.93);
      g.fillRect(cx - r + (r * 2 / nF) * i, y, r * 2 / nF + 1, colH);
    }
    // Capital
    g.fillStyle(light, alpha);
    g.fillRect(cx - r * 1.7, y - 12, r * 3.4, 12);
    g.fillRect(cx - r * 1.3, y - 22, r * 2.6, 10);
    g.fillRect(cx - r * 2.0, y - 30, r * 4.0, 8);
    // Base
    g.fillStyle(light, alpha * 0.88);
    g.fillRect(cx - r * 1.3, y + colH,      r * 2.6, 10);
    g.fillRect(cx - r * 1.7, y + colH + 10, r * 3.4, 10);
    g.fillRect(cx - r * 2.0, y + colH + 20, r * 4.0, 7);
  }

  // Egyptian lotus column
  _lotusCol(g, cx, y, colH, r, stone, gold, alpha = 1) {
    g.fillStyle(stone, alpha * 0.90);
    g.fillRect(cx - r, y, r * 2, colH);
    // Hieroglyph bands
    g.fillStyle(gold, alpha * 0.17);
    for (let gy = y + 22; gy < y + colH; gy += 58) {
      g.fillRect(cx - r, gy, r * 2, 9);
    }
    // Lotus capital petals
    g.fillStyle(gold, alpha * 0.82);
    g.fillRect(cx - r * 1.6, y - 9, r * 3.2, 9);
    for (let i = -2; i <= 2; i++) {
      g.fillStyle(this._lerp(gold, 0xffffff, 0.18), alpha * 0.55);
      g.fillTriangle(cx + i * r * 0.55, y - 9, cx + (i - 0.5) * r * 0.55, y - 30, cx + (i + 0.5) * r * 0.55, y - 30);
    }
    // Base
    g.fillStyle(stone, alpha * 0.80);
    g.fillRect(cx - r * 1.4, y + colH, r * 2.8, 10);
    g.fillRect(cx - r * 1.7, y + colH + 10, r * 3.4, 9);
  }

  // Wall sconce lamp
  _lamp(g, cx, cy, poleCol, glowCol) {
    g.fillStyle(poleCol, 0.88);
    g.fillRect(cx, cy, 3, 50);
    g.fillRect(cx - 24, cy + 14, 24, 3);
    g.fillStyle(poleCol, 0.95);
    g.fillRect(cx - 32, cy + 5, 18, 22);
    g.fillTriangle(cx - 32, cy + 27, cx - 14, cy + 27, cx - 23, cy + 40);
    g.fillStyle(glowCol, 0.22);
    g.fillCircle(cx - 23, cy + 15, 30);
    g.fillStyle(glowCol, 0.40);
    g.fillCircle(cx - 23, cy + 15, 11);
    g.fillStyle(glowCol, 0.055);
    g.fillEllipse(cx - 23, cy + 85, 110, 35);
  }

  // Chandelier
  _chandelier(g, cx, ty, col, glowCol, arms = 6, radius = 90) {
    g.fillStyle(col, 0.72);
    g.fillRect(cx - 2, ty, 4, 32);
    g.fillStyle(col, 0.90);
    g.fillEllipse(cx, ty + 32, 32, 20);
    for (let i = 0; i < arms; i++) {
      const angle = (i / arms) * Math.PI * 2 - Math.PI / 2;
      const ex = cx + Math.cos(angle) * radius;
      const ey = ty + 42 + Math.sin(angle) * radius * 0.22;
      g.lineStyle(2, col, 0.68);
      g.lineBetween(cx, ty + 40, ex, ey);
      g.fillStyle(0xfff5c0, 0.62);
      g.fillRect(ex - 3, ey - 16, 6, 16);
      g.fillStyle(glowCol, 0.48);
      g.fillCircle(ex, ey - 18, 6);
      g.fillStyle(glowCol, 0.13);
      g.fillCircle(ex, ey - 14, 22);
    }
    g.fillStyle(glowCol, 0.055);
    g.fillCircle(cx, ty + 42, radius * 2.2);
  }

  // Torn page / floating memory (lyric motif: "stupid dreams and memories")
  _tornPage(g, cx, cy, size, col, alpha = 1) {
    const s = size;
    g.fillStyle(col, alpha * 0.55);
    // Slightly irregular rectangle
    g.fillPoints([
      { x: cx - s,       y: cy - s * 1.4 },
      { x: cx + s * 0.9, y: cy - s * 1.3 },
      { x: cx + s,       y: cy + s * 1.2 },
      { x: cx - s * 0.85, y: cy + s * 1.4 },
    ], true);
    // Ruled lines (text on the page)
    g.fillStyle(col, alpha * 0.18);
    for (let ly = cy - s + 5; ly < cy + s; ly += 10) {
      const lineW = (s * 1.6) * (0.5 + this._h(cx, ly) * 0.5);
      g.fillRect(cx - s * 0.8, ly, lineW, 2);
    }
    // Torn bottom edge
    g.fillStyle(col, alpha * 0.30);
    for (let tx = cx - s * 0.85; tx < cx + s; tx += 7) {
      g.fillTriangle(tx, cy + s * 1.4, tx + 7, cy + s * 1.4, tx + 3, cy + s * 1.4 + this._h(tx, cy) * 12);
    }
  }

  // 4-point star sparkle
  _star(g, cx, cy, r, col, alpha = 1) {
    g.fillStyle(col, alpha);
    g.fillPoints([
      { x: cx,     y: cy - r },
      { x: cx + r * 0.2, y: cy - r * 0.2 },
      { x: cx + r, y: cy },
      { x: cx + r * 0.2, y: cy + r * 0.2 },
      { x: cx,     y: cy + r },
      { x: cx - r * 0.2, y: cy + r * 0.2 },
      { x: cx - r, y: cy },
      { x: cx - r * 0.2, y: cy - r * 0.2 },
    ], true);
  }

  // Neon bar (Tech Manor)
  _neonBar(g, x, y, w, h, col, alpha = 1) {
    g.fillStyle(col, alpha);
    g.fillRect(x, y, w, h);
    g.fillStyle(col, alpha * 0.18);
    g.fillRect(x - 4, y - 4, w + 8, h + 8);
    g.fillStyle(col, alpha * 0.07);
    g.fillRect(x - 10, y - 10, w + 20, h + 20);
  }

  // Screen-space vignette + global darkening
  _vignette() {
    const { scene } = this;
    const sw = scene.scale.width, sh = scene.scale.height;
    const v  = scene.add.graphics().setScrollFactor(0).setDepth(-1);
    v.fillStyle(0x000000, 0.46);
    v.fillRect(0, 0,        sw, 74);
    v.fillRect(0, sh - 74,  sw, 74);
    for (let i = 0; i < 7; i++) {
      v.fillStyle(0x000000, 0.26 * (1 - i / 7));
      v.fillRect(0,                  74, (i + 1) * 18, sh - 148);
      v.fillRect(sw - (i + 1) * 18, 74, (i + 1) * 18, sh - 148);
    }
    scene.add.rectangle(0, 0, this.W, this.H, 0x000000, 0.36)
      .setOrigin(0).setScrollFactor(0).setDepth(-2);
  }

  // ─── Stage 0 — The Grand Library ──────────────────────────────────────────
  // "Stupid dreams and memories, the only things you left with me"
  // Amber warmth, dark mahogany, floating torn pages in dusty light shafts
  _grandLibrary() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#0e0600');

    // A: ember-warm deep void (sf 0.05)
    { const sf = 0.05, lw = this._lw(sf), g = this._gfx(sf, -16);
      this._gradVPainted(g, 0, 0, lw, H, 0x0e0500, 0x241000, 22);
      for (let x = 500; x < lw; x += 900) {
        g.fillStyle(0x8b4513, 0.08); g.fillCircle(x, H * 0.70, 260);
      }
    }

    // B: distant vaulted hall — gothic arches + dark receding shelves (sf 0.15)
    { const sf = 0.15, lw = this._lw(sf), g = this._gfx(sf, -15);
      this._gradVPainted(g, 0, 0, lw, H * 0.24, 0x120700, 0x1f0d00, 10);
      // Arch spans
      for (let x = 0; x < lw; x += 400) {
        // Pier
        g.fillStyle(0x1a0a00, 0.96); g.fillRect(x, 0, 26, H * 0.84);
        // Dark arch opening
        this._gothicArch(g, x + 213, H * 0.84, 348, H * 0.82, 0x120700, 0.92);
        // Keystone glow
        g.fillStyle(0xd4af37, 0.08); g.fillCircle(x + 213, H * 0.03, 22);
      }
      // Far bookshelf wall (stride=3 for performance — distant, barely visible)
      for (let x = 28; x < lw; x += 220) {
        g.fillStyle(0x180900, 0.88); g.fillRect(x, H * 0.09, 194, H * 0.73);
        this._books(g, x + 4, H * 0.09, 186, H * 0.73, 4, x, 3);
      }
      this._gradVPainted(g, 0, H * 0.82, lw, H * 0.18, 0x180900, 0x0e0500, 8);
    }

    // C: vault rib tracery + mid bookshelves (sf 0.32)
    { const sf = 0.32, lw = this._lw(sf), g = this._gfx(sf, -14);
      // Ribbed vault ceiling
      for (let x = 0; x < lw; x += 280) {
        g.lineStyle(3, 0xd4af37, 0.13);
        g.lineBetween(x, 0, x + 140, H * 0.17);
        g.lineBetween(x + 280, 0, x + 140, H * 0.17);
        g.fillStyle(0xd4af37, 0.09); g.fillCircle(x + 140, H * 0.04, 11);
      }
      // Shelf units
      for (let x = 0; x < lw; x += 264) {
        g.fillStyle(0x3b1a05, 0.94);
        g.fillRect(x, H * 0.07, 7, H * 0.74);
        g.fillRect(x + 257, H * 0.07, 7, H * 0.74);
        g.fillRect(x, H * 0.07, 264, 7);
        g.fillStyle(0x2a0f00, 0.92); g.fillRect(x + 7, H * 0.08, 250, H * 0.73);
        this._books(g, x + 10, H * 0.10, 244, H * 0.70, 5, x * 3, 2);
      }
      // Parquet floor
      g.fillStyle(0x1c0b00, 0.97); g.fillRect(0, H * 0.82, lw, H * 0.18);
      for (let x = 0; x < lw; x += 95) { g.fillStyle(0x2e1200, 0.34); g.fillRect(x, H * 0.82, 2, H * 0.18); }
      for (let y = H * 0.84; y < H; y += 40) { g.fillStyle(0x2e1200, 0.17); g.fillRect(0, y, lw, 2); }
      // Floor reflection sheen
      g.fillStyle(0xd4af37, 0.025); g.fillRect(0, H * 0.82, lw, 5);
    }

    // D: ornate pillars + balcony rail + reading lamps (sf 0.56)
    { const sf = 0.56, lw = this._lw(sf), g = this._gfx(sf, -13);
      for (let x = 260; x < lw; x += 528) {
        this._ornateCol(g, x, H * 0.05, H * 0.77, 22, 0x2a0f00, 0x5a2e08, 0.96);
        g.fillStyle(0xd4af37, 0.06); g.fillCircle(x, H * 0.06, 60);
      }
      // Balcony rail ~52%
      g.fillStyle(0x3b1a05, 0.92); g.fillRect(0, H * 0.52, lw, 10);
      for (let x = 20; x < lw; x += 47) {
        g.fillStyle(0x5a2e08, 0.80); g.fillRect(x, H * 0.52 + 10, 7, 68);
        g.fillStyle(this.acc, 0.14); g.fillCircle(x + 3, H * 0.52 + 44, 4);
      }
      g.fillStyle(0x3b1a05, 0.88); g.fillRect(0, H * 0.52 + 78, lw, 10);
      // Lamps
      for (let x = 110; x < lw; x += 528) this._lamp(g, x, H * 0.22, 0x5a2e08, 0xfff5c0);
      for (let x = 370; x < lw; x += 528) this._lamp(g, x, H * 0.60, 0x5a2e08, 0xfff5c0);
    }

    // E: floating torn pages — "memories you left with me" (sf 0.25)
    { const sf = 0.25, lw = this._lw(sf), g = this._gfx(sf, -12);
      for (let i = 0; i < 22; i++) {
        const px = this._h(i, 1) * lw;
        const py = H * 0.08 + this._h(i, 2) * H * 0.72;
        const sz = 8 + this._h(i, 3) * 16;
        this._tornPage(g, px, py, sz, 0xf5e8d0, this._h(i, 4) * 0.22 + 0.06);
      }
    }

    // F: golden light shafts through skylight (sf 0.18)
    { const sf = 0.18, lw = this._lw(sf), g = this._gfx(sf, -11);
      for (let x = 200; x < lw; x += 400) {
        g.fillStyle(0xd4af37, 0.042);
        g.fillTriangle(x - 50, 0, x + 50, 0, x + 85, H * 0.72);
        g.fillStyle(0xfff5c0, 0.028);
        g.fillTriangle(x - 14, 0, x + 14, 0, x + 22, H * 0.62);
        // Dust motes in shaft
        for (let my = 30; my < H * 0.65; my += 34) {
          g.fillStyle(0xfff5c0, 0.038);
          g.fillCircle(x + my * 0.07, my, 3 + this._h(x, my) * 3);
        }
      }
    }
  }

  // ─── Stage 1 — Egyptian Hall ────────────────────────────────────────────────
  // "On bended knee I begged and plead that you would stay"
  // Monumental gold columns, hieroglyphs of a plea, burning torchlight
  _egyptianHall() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#140b00');

    // A: warm sand-heat void (sf 0.05)
    { const sf = 0.05, lw = this._lw(sf), g = this._gfx(sf, -16);
      this._gradVPainted(g, 0, 0, lw, H, 0x100800, 0x2c1900, 22);
    }

    // B: distant hypostyle colonnade (sf 0.15)
    { const sf = 0.15, lw = this._lw(sf), g = this._gfx(sf, -15);
      this._gradVPainted(g, 0, 0, lw, H * 0.18, 0x140c00, 0x221200, 9);
      // Wall surface
      g.fillStyle(0x1f1200, 0.88); g.fillRect(0, H * 0.04, lw, H * 0.77);
      // Hieroglyph strip bands
      g.fillStyle(this.acc, 0.08);
      for (let y = H * 0.06; y < H * 0.78; y += 62) g.fillRect(0, y, lw, 9);
      // Far columns
      for (let x = 0; x < lw; x += 320) {
        g.fillStyle(0x2e1c00, 0.86); g.fillRect(x + 110, 0, 100, H * 0.80);
        g.fillStyle(this.acc, 0.09);
        for (let gy = 30; gy < H * 0.78; gy += 62) g.fillRect(x + 110, gy, 100, 9);
        // Hieroglyph carved rows
        for (let gx = x + 116; gx < x + 204; gx += 22) {
          for (let gy = H * 0.09; gy < H * 0.72; gy += 52) {
            if (this._h(gx, gy) > 0.44) { g.fillStyle(this.acc, 0.11); g.fillRect(gx, gy, 16, 14); }
          }
        }
      }
      this._gradVPainted(g, 0, H * 0.80, lw, H * 0.20, 0x2a1600, 0x100800, 7);
    }

    // C: mid colonnade — lotus columns + cartouche wall (sf 0.33)
    { const sf = 0.33, lw = this._lw(sf), g = this._gfx(sf, -14);
      this._gradVPainted(g, 0, 0, lw, H * 0.15, 0x1c1000, 0x2e1800, 8);
      for (let x = 0; x < lw; x += 380) {
        this._lotusCol(g, x + 40, H * 0.05, H * 0.76, 34, 0x3d2300, this.acc, 0.92);
        this._lotusCol(g, x + 340, H * 0.05, H * 0.76, 34, 0x3d2300, this.acc, 0.92);
      }
      // Wall cartouches between columns
      for (let x = 78; x < lw; x += 380) {
        g.fillStyle(this.acc, 0.13);
        for (let gy = H * 0.08; gy < H * 0.72; gy += 55) {
          for (let gx = x; gx < x + 240; gx += 26) {
            if (this._h(gx, gy) > 0.40) g.fillRect(gx, gy, 20, 15);
          }
        }
        g.fillStyle(this.acc, 0.20); g.fillRect(x, H * 0.07, 240, 6);
        g.fillStyle(this.acc, 0.20); g.fillRect(x, H * 0.73, 240, 6);
      }
      this._gradVPainted(g, 0, H * 0.80, lw, H * 0.20, 0x3d2300, 0x1a1000, 8);
      for (let x = 0; x < lw; x += 130) { g.fillStyle(0x2a1600, 0.38); g.fillRect(x, H * 0.80, 3, H * 0.20); }
    }

    // D: near — pharaoh statues + wall torches (sf 0.57)
    { const sf = 0.57, lw = this._lw(sf), g = this._gfx(sf, -13);
      for (let x = 190; x < lw; x += 580) {
        g.fillStyle(0x2a1800, 0.93);
        g.fillRect(x - 32, H * 0.30, 64, H * 0.50);
        g.fillRect(x - 48, H * 0.54, 96, H * 0.26);
        g.fillCircle(x, H * 0.28, 32);
        g.fillStyle(this.acc, 0.22);
        g.fillTriangle(x, H * 0.17, x - 24, H * 0.28, x + 24, H * 0.28);
        g.fillStyle(this.acc, 0.28);
        g.fillRect(x + 11, H * 0.34, 6, 44);
      }
      for (let x = 100; x < lw; x += 580) this._lamp(g, x, H * 0.28, 0x4a2800, 0xffaa44);
      for (let x = 400; x < lw; x += 580) this._lamp(g, x, H * 0.56, 0x4a2800, 0xffaa44);
      g.fillStyle(0x0e0800, 0.88); g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // E: 4-point star sparks from torch embers (sf 0.20)
    { const sf = 0.20, lw = this._lw(sf), g = this._gfx(sf, -12);
      for (let i = 0; i < 18; i++) {
        const sx = this._h(i, 5) * lw;
        const sy = H * 0.20 + this._h(i, 6) * H * 0.50;
        this._star(g, sx, sy, 3 + this._h(i, 7) * 5, 0xffcc44, this._h(i, 8) * 0.20 + 0.05);
      }
    }

    // F: hot golden light shafts from high windows (sf 0.18)
    { const sf = 0.18, lw = this._lw(sf), g = this._gfx(sf, -11);
      for (let x = 200; x < lw; x += 380) {
        g.fillStyle(0xd4af37, 0.052);
        g.fillTriangle(x - 32, 0, x + 32, 0, x + 58, H * 0.82);
        g.fillStyle(0xffd700, 0.030);
        g.fillTriangle(x - 8, 0, x + 8, 0, x + 16, H * 0.76);
        for (let my = 22; my < H * 0.76; my += 35) {
          g.fillStyle(0xffd700, 0.042);
          g.fillCircle(x + my * 0.07, my, 3 + this._h(x, my) * 2);
        }
      }
    }
  }

  // ─── Stage 2 — Samurai Gallery ─────────────────────────────────────────────
  // "I was blind but now I see the truth"
  // Cold blade-clarity, shoji light, cherry blossoms = beautiful but fleeting
  _samuraiGallery() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#0d0000');

    // A: deep crimson void with moon (sf 0.05)
    { const sf = 0.05, lw = this._lw(sf), g = this._gfx(sf, -16);
      this._gradVPainted(g, 0, 0, lw, H, 0x0a0000, 0x1c0600, 22);
      for (let x = 700; x < lw; x += 1400) {
        g.fillStyle(0xfff5e0, 0.07); g.fillCircle(x, H * 0.11, 130);
        g.fillStyle(0xfff5e0, 0.10); g.fillCircle(x, H * 0.11, 55);
      }
    }

    // B: distant shoji screen wall (sf 0.15)
    { const sf = 0.15, lw = this._lw(sf), g = this._gfx(sf, -15);
      g.fillStyle(0x1a0800, 0.92); g.fillRect(0, 0, lw, H * 0.86);
      for (let x = 0; x < lw; x += 230) {
        for (let p = 0; p < 3; p++) {
          const px = x + p * 74;
          g.fillStyle(0x2c1600, 0.82); g.fillRect(px, H * 0.07, 70, H * 0.73);
          g.fillStyle(0xfff5e0, 0.045); g.fillRect(px + 3, H * 0.09, 64, H * 0.69);
          g.fillStyle(0x1a0800, 0.52);
          for (let sy = H * 0.12; sy < H * 0.73; sy += 34) g.fillRect(px, sy, 70, 2);
          for (let sxs = px + 22; sxs < px + 70; sxs += 22) g.fillRect(sxs, H * 0.07, 2, H * 0.73);
        }
      }
      this._gradVPainted(g, 0, H * 0.82, lw, H * 0.18, 0x1c0a00, 0x0d0400, 7);
    }

    // C: mid dojo — lacquered pillars + katana racks + lanterns (sf 0.33)
    { const sf = 0.33, lw = this._lw(sf), g = this._gfx(sf, -14);
      this._gradVPainted(g, 0, 0, lw, H * 0.16, 0x1a0800, 0x2e1200, 8);
      for (let x = 0; x < lw; x += 170) { g.fillStyle(0x3b1a05, 0.58); g.fillRect(x, 0, 6, H * 0.16); }
      // Pillars
      for (let x = 70; x < lw; x += 500) this._ornateCol(g, x, H * 0.07, H * 0.74, 17, 0x3b0000, 0x7a0000, 0.92);
      // Katana racks
      for (let x = 130; x < lw; x += 500) {
        g.fillStyle(0x3b1a05, 0.82); g.fillRect(x, H * 0.22, 220, 6); g.fillRect(x, H * 0.37, 220, 6);
        for (let k = 0; k < 5; k++) {
          const kx = x + 22 + k * 40;
          g.fillStyle(0x5a2e08, 0.92); g.fillRect(kx, H * 0.23, 6, 24);
          g.fillStyle(this.acc, 0.62); g.fillRect(kx - 5, H * 0.23 + 24, 16, 5);
          g.fillStyle(0xd8d8d8, 0.58); g.fillRect(kx + 1, H * 0.29, 3, 54);
          g.fillStyle(0xffffff, 0.22); g.fillRect(kx + 2, H * 0.30, 1, 48);
        }
      }
      // Paper lanterns
      for (let x = 210; x < lw; x += 500) {
        g.fillStyle(0x3b1a05, 0.60); g.fillRect(x + 110 - 2, 0, 3, H * 0.23);
        g.fillStyle(0x8b0000, 0.68); g.fillEllipse(x + 110, H * 0.23 + 32, 40, 58);
        g.fillStyle(0xff9900, 0.16); g.fillCircle(x + 110, H * 0.23 + 32, 44);
        for (let ly = H * 0.23 + 7; ly < H * 0.23 + 55; ly += 11) { g.fillStyle(0xd4af37, 0.24); g.fillRect(x + 110 - 20, ly, 40, 3); }
      }
      // Cherry blossom branch silhouette
      for (let x = 300; x < lw; x += 1000) {
        g.fillStyle(0x1c0a00, 0.72);
        g.fillRect(x, H * 0.04, 5, H * 0.35); g.fillRect(x - 70, H * 0.18, 75, 4); g.fillRect(x + 5, H * 0.26, 62, 4);
        for (let bi = 0; bi < 14; bi++) {
          g.fillStyle(0x8b0000, 0.28);
          g.fillCircle(x - 75 + this._h(bi, x) * 150, H * 0.06 + this._h(bi, x + 1) * H * 0.28, 5 + this._h(bi * 3, x) * 7);
        }
      }
      g.fillStyle(0x1e0c00, 0.96); g.fillRect(0, H * 0.82, lw, H * 0.18);
      for (let x = 0; x < lw; x += 140) { g.fillStyle(0x2e1200, 0.25); g.fillRect(x, H * 0.82, 2, H * 0.18); }
    }

    // D: near — armour stands + falling petals (sf 0.57)
    { const sf = 0.57, lw = this._lw(sf), g = this._gfx(sf, -13);
      for (let x = 230; x < lw; x += 620) {
        g.fillStyle(0x3b1a05, 0.86); g.fillRect(x - 3, H * 0.38, 6, H * 0.44); g.fillRect(x - 26, H * 0.80, 52, 9);
        g.fillStyle(0x8b0000, 0.72); g.fillRect(x - 24, H * 0.27, 48, 55);
        g.fillStyle(0x8b0000, 0.62); g.fillRect(x - 40, H * 0.28, 20, 32); g.fillRect(x + 20, H * 0.28, 20, 32);
        g.fillStyle(0x5a0000, 0.82); g.fillEllipse(x, H * 0.23, 44, 38);
        g.fillStyle(0xc0c0c0, 0.22); g.fillRect(x - 15, H * 0.29, 30, 20);
        g.fillStyle(this.acc, 0.24); g.fillCircle(x, H * 0.34, 11);
      }
      // Falling blossom petals
      for (let i = 0; i < 35; i++) {
        const px = this._h(i, 10) * lw, py = H * 0.05 + this._h(i, 11) * H * 0.88;
        g.fillStyle(0xd4607a, 0.28); g.fillEllipse(px, py, 11, 8);
      }
      g.fillStyle(0x0d0500, 0.90); g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // E: moonlight + blossom sparkles (sf 0.20)
    { const sf = 0.20, lw = this._lw(sf), g = this._gfx(sf, -12);
      for (let x = 250; x < lw; x += 500) {
        g.fillStyle(0xfff5e0, 0.036); g.fillTriangle(x - 28, 0, x + 28, 0, x + 44, H * 0.77);
      }
      for (let i = 0; i < 20; i++) {
        this._star(g, this._h(i, 12) * lw, H * 0.05 + this._h(i, 13) * H * 0.50, 2 + this._h(i, 14) * 4, 0xffd4a0, 0.12 + this._h(i, 15) * 0.10);
      }
    }

    // F: deep floor + side shadows (sf 0.72)
    { const sf = 0.72, lw = this._lw(sf), g = this._gfx(sf, -11);
      g.fillStyle(0x0d0500, 0.92); g.fillRect(0, H * 0.82, lw, H * 0.18);
    }
  }

  // ─── Stage 3 — Royal Chambers ──────────────────────────────────────────────
  // "At a time in life you were all that I wanted"
  // Peak of the fairy tale — the most opulent, warmest, most beautiful room
  _royalChambers() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#0a0015');

    // A: deep velvet void with star-dust (sf 0.05)
    { const sf = 0.05, lw = this._lw(sf), g = this._gfx(sf, -16);
      this._gradVPainted(g, 0, 0, lw, H, 0x080012, 0x18002e, 22);
      for (let i = 0; i < 40; i++) {
        this._star(g, this._h(i, 20) * lw, this._h(i, 21) * H * 0.55, 1 + this._h(i, 22) * 3, 0xd4af37, 0.07 + this._h(i, 23) * 0.09);
      }
    }

    // B: damask wallpaper + distant arched hall (sf 0.15)
    { const sf = 0.15, lw = this._lw(sf), g = this._gfx(sf, -15);
      this._gradVPainted(g, 0, 0, lw, H, 0x0e0020, 0x1c003c, 20);
      for (let x = 0; x < lw; x += 62) {
        for (let y = 32; y < H * 0.78; y += 72) {
          g.fillStyle(this.acc, 0.055); g.fillEllipse(x + 31, y + 36, 26, 44);
          g.fillStyle(this.prim, 0.04); g.fillCircle(x + 31, y + 36, 9);
          g.fillCircle(x + 31, y + 12, 6); g.fillCircle(x + 31, y + 62, 6);
        }
      }
      // Chair rail
      g.fillStyle(this.acc, 0.24); g.fillRect(0, H * 0.54, lw, 6); g.fillRect(0, H * 0.57, lw, 3);
      g.fillStyle(this.prim, 0.22); g.fillRect(0, H * 0.57, lw, H * 0.24);
      for (let x = 0; x < lw; x += 190) {
        g.fillStyle(this.acc, 0.11); g.fillRect(x + 16, H * 0.585, 158, H * 0.205);
        g.fillStyle(this.acc, 0.05); g.fillRect(x + 20, H * 0.592, 150, H * 0.192);
      }
    }

    // C: chandeliers + tapestries + mirrors (sf 0.33)
    { const sf = 0.33, lw = this._lw(sf), g = this._gfx(sf, -14);
      // Gilded cornice
      g.fillStyle(this.acc, 0.22); g.fillRect(0, H * 0.06, lw, 11);
      for (let x = 0; x < lw; x += 26) { g.fillStyle(this.acc, 0.12); g.fillEllipse(x + 13, H * 0.06 + 5, 18, 11); }
      // Ceiling coffers
      for (let x = 0; x < lw; x += 310) {
        g.fillStyle(this.prim, 0.18); g.fillRect(x + 22, H * 0.02, 266, H * 0.05);
        g.fillStyle(this.acc, 0.08); g.fillRect(x + 27, H * 0.025, 256, H * 0.04);
      }
      // Chandeliers
      for (let x = 210; x < lw; x += 620) this._chandelier(g, x, H * 0.06, this.acc, 0xfff5c0, 7, 96);
      // Tapestries
      for (let x = 110; x < lw; x += 620) {
        g.fillStyle(this.prim, 0.82); g.fillRect(x - 60, H * 0.09, 120, H * 0.62);
        g.fillStyle(this.acc, 0.38); g.fillRect(x - 60, H * 0.09, 120, 6); g.fillRect(x - 60, H * 0.09 + H * 0.62 - 6, 120, 6);
        g.fillRect(x - 60, H * 0.09, 6, H * 0.62); g.fillRect(x + 54, H * 0.09, 6, H * 0.62);
        g.fillStyle(this.acc, 0.28); g.fillCircle(x, H * 0.29, 26);
        g.fillTriangle(x - 22, H * 0.38, x + 22, H * 0.38, x, H * 0.56);
        for (let ty = H * 0.46; ty < H * 0.65; ty += 22) { g.fillStyle(this.acc, 0.15); g.fillRect(x - 38, ty, 76, 3); }
      }
      // Ornate mirrors
      for (let x = 400; x < lw; x += 620) {
        g.fillStyle(this.acc, 0.48); g.fillEllipse(x, H * 0.30, 108, 138);
        g.fillStyle(0x0a0018, 0.68); g.fillEllipse(x, H * 0.30, 92, 122);
        g.fillStyle(0xffffff, 0.055); g.fillRect(x - 30, H * 0.18, 13, 84);
      }
      // Persian rug
      g.fillStyle(this.prim, 0.58); g.fillRect(0, H * 0.82, lw, H * 0.18);
      g.fillStyle(this.acc, 0.20); g.fillRect(0, H * 0.82, lw, 6);
      for (let x = 44; x < lw; x += 85) { g.fillStyle(this.acc, 0.11); g.fillCircle(x, H * 0.89, 15); }
    }

    // D: pillars + candelabras (sf 0.57)
    { const sf = 0.57, lw = this._lw(sf), g = this._gfx(sf, -13);
      for (let x = 210; x < lw; x += 560) {
        this._ornateCol(g, x, H * 0.06, H * 0.76, 19, 0x1a0038, 0x4b0082, 0.96);
        g.fillStyle(this.acc, 0.07); g.fillCircle(x, H * 0.07, 55);
      }
      for (let x = 390; x < lw; x += 560) {
        g.fillStyle(this.acc, 0.58); g.fillRect(x - 3, H * 0.42, 6, H * 0.40); g.fillRect(x - 18, H * 0.82, 36, 7); g.fillRect(x - 20, H * 0.42, 40, 7);
        for (let ci = -1; ci <= 1; ci++) {
          const cxi = x + ci * 15;
          g.fillStyle(0xfff5e0, 0.68); g.fillRect(cxi - 3, H * 0.29, 6, H * 0.13);
          g.fillStyle(0xffaa00, 0.52); g.fillCircle(cxi, H * 0.28, 6);
          g.fillStyle(0xffcc00, 0.14); g.fillCircle(cxi, H * 0.28, 22);
        }
      }
      g.fillStyle(0x0a0015, 0.90); g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // E: fairy-tale star sparkles scattered in air (sf 0.22)
    { const sf = 0.22, lw = this._lw(sf), g = this._gfx(sf, -12);
      for (let i = 0; i < 30; i++) {
        const r = 2 + this._h(i, 30) * 6;
        this._star(g, this._h(i, 31) * lw, H * 0.04 + this._h(i, 32) * H * 0.75, r, 0xffd700, 0.06 + this._h(i, 33) * 0.10);
      }
    }

    // F: candlelight warm shafts (sf 0.18)
    { const sf = 0.18, lw = this._lw(sf), g = this._gfx(sf, -11);
      for (let x = 210; x < lw; x += 620) {
        g.fillStyle(0x9370db, 0.04); g.fillTriangle(x - 45, 0, x + 45, 0, x + 70, H * 0.74);
        g.fillStyle(0xd4af37, 0.025); g.fillTriangle(x - 12, 0, x + 12, 0, x + 22, H * 0.66);
      }
    }
  }

  // ─── Stage 4 — Museum Wing ──────────────────────────────────────────────────
  // "Craving for your touch and your love in the morning"
  // Cold preservation of warm memories — everything beautiful but behind glass
  _museumWing() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#0c1414');

    // A: cool diffuse grey-teal void (sf 0.05)
    { const sf = 0.05, lw = this._lw(sf), g = this._gfx(sf, -16);
      this._gradVPainted(g, 0, 0, lw, H, 0x0c1414, 0x1c2e2e, 22);
    }

    // B: distant vaulted gallery + skylights (sf 0.15)
    { const sf = 0.15, lw = this._lw(sf), g = this._gfx(sf, -15);
      this._stoneWall(g, 0, H * 0.06, lw, H * 0.76, 0x1e2e2e, 0x0c1414, 52, 136, 0.90, true);
      this._gradVPainted(g, 0, 0, lw, H * 0.06, 0x2c3c3c, 0x3c4c4c, 4);
      for (let x = 190; x < lw; x += 380) {
        g.fillStyle(0x88ccdd, 0.09); g.fillRect(x - 65, 0, 130, H * 0.06);
        g.fillStyle(0x2c3c3c, 0.62); g.fillRect(x - 65, H * 0.027, 130, 3); g.fillRect(x, 0, 3, H * 0.06);
      }
      this._gradVPainted(g, 0, H * 0.80, lw, H * 0.20, 0x2c3c3c, 0x0c1414, 7);
    }

    // C: display cases + pillars + marble floor (sf 0.33)
    { const sf = 0.33, lw = this._lw(sf), g = this._gfx(sf, -14);
      g.fillStyle(0x243030, 0.92); g.fillRect(0, 0, lw, H * 0.13);
      for (let x = 0; x < lw; x += 250) {
        g.fillStyle(0x344040, 0.72); g.fillRect(x, 0, 8, H * 0.13);
        g.fillStyle(0x88ccdd, 0.04); g.fillRect(x + 8, 0, 242, H * 0.13);
      }
      for (let y = 0; y < H * 0.13; y += 42) { g.fillStyle(0x344040, 0.52); g.fillRect(0, y, lw, 5); }
      // Vitrines (display cases)
      for (let x = 65; x < lw; x += 380) {
        g.fillStyle(0x4a5c5c, 0.92); g.fillRect(x, H * 0.37, 210, 6); g.fillRect(x, H * 0.63, 210, 6);
        g.fillRect(x, H * 0.37, 6, H * 0.26); g.fillRect(x + 204, H * 0.37, 6, H * 0.26);
        g.fillStyle(0x88ccdd, 0.065); g.fillRect(x + 6, H * 0.39, 198, H * 0.24);
        // Artifact inside
        g.fillStyle(this.acc, 0.32); g.fillRect(x + 72, H * 0.43, 66, 44); g.fillEllipse(x + 105, H * 0.43, 44, 32);
        // Spotlight down
        g.fillStyle(0xffffff, 0.032); g.fillTriangle(x + 105, H * 0.13, x + 85, H * 0.39, x + 125, H * 0.39);
        // Reflection in floor
        g.fillStyle(this.acc, 0.06); g.fillRect(x + 72, H * 0.82, 66, 28);
      }
      // Pillars
      for (let x = 235; x < lw; x += 380) this._ornateCol(g, x, H * 0.11, H * 0.71, 16, 0x2c3c3c, 0x4c5c5c, 0.92);
      // Marble floor
      this._gradVPainted(g, 0, H * 0.82, lw, H * 0.18, 0x2c3c3c, 0x1c2c2c, 7);
      for (let x = 0; x < lw; x += 105) { g.fillStyle(0x344040, 0.32); g.fillRect(x, H * 0.82, 2, H * 0.18); }
      for (let y = H * 0.82; y < H; y += 48) { g.fillStyle(0x344040, 0.18); g.fillRect(0, y, lw, 2); }
    }

    // D: plaques + specimen mounts + archway frames (sf 0.57)
    { const sf = 0.57, lw = this._lw(sf), g = this._gfx(sf, -13);
      for (let x = 110; x < lw; x += 490) {
        this._roundArch(g, x + 90, H * 0.82, 180, H * 0.70, 0x243030, 0.88);
        g.fillStyle(0x344040, 0.88); g.fillRect(x, H * 0.27, 190, 210);
        g.fillStyle(this.acc, 0.30); g.fillRect(x + 16, H * 0.29, 158, 5);
        for (let ty = H * 0.34; ty < H * 0.49; ty += 13) {
          g.fillStyle(0x4a5c5c, 0.58); g.fillRect(x + 16, ty, 158 * (0.4 + this._h(x, ty) * 0.6), 7);
        }
        g.fillStyle(this.acc, 0.38); g.fillRect(x + 32, H * 0.505, 126, 32);
      }
      g.fillStyle(0x0c1414, 0.90); g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // E: cool museum skylight shafts (sf 0.18)
    { const sf = 0.18, lw = this._lw(sf), g = this._gfx(sf, -12);
      for (let x = 205; x < lw; x += 380) {
        g.fillStyle(0x88ccdd, 0.042); g.fillTriangle(x - 20, 0, x + 20, 0, x + 34, H * 0.57);
        g.fillStyle(0xffffff, 0.018); g.fillTriangle(x - 5, 0, x + 5, 0, x + 9, H * 0.52);
        for (let my = 18; my < H * 0.52; my += 36) { g.fillStyle(0x88ccdd, 0.036); g.fillCircle(x + my * 0.04, my, 4 + this._h(x, my) * 2); }
      }
    }

    // F: faint warm glow from artifacts (sf 0.05)
    { const sf = 0.05, lw = this._lw(sf), g = this._gfx(sf, -11);
      for (let x = 240; x < lw; x += 760) { g.fillStyle(this.acc, 0.055); g.fillCircle(x, H * 0.50, 160); }
    }
  }

  // ─── Stage 5 — Tech Manor ───────────────────────────────────────────────────
  // "And it felt so right, never saw it coming"
  // Reality fracturing — ancient castle fused with glitching digital world
  _techManor() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#050510');

    // A: deep blue-black data void (sf 0.05)
    { const sf = 0.05, lw = this._lw(sf), g = this._gfx(sf, -16);
      this._gradVPainted(g, 0, 0, lw, H, 0x030310, 0x0f0f28, 22);
      // Distant data-stream glyphs
      for (let x = 0; x < lw; x += 44) {
        for (let y = 0; y < H; y += 32) {
          if (this._h(x, y) > 0.86) { g.fillStyle(this.acc, 0.07); g.fillRect(x, y, 14, 20); }
        }
      }
    }

    // B: stone castle walls with server racks overlaid (sf 0.15)
    { const sf = 0.15, lw = this._lw(sf), g = this._gfx(sf, -15);
      this._stoneWall(g, 0, H * 0.08, lw, H * 0.74, 0x0d0d1e, 0x06060e, 52, 125, 0.92, true);
      for (let x = 0; x < lw; x += 330) {
        g.fillStyle(0x1a1a3a, 0.88); g.fillRect(x + 32, H * 0.10, 126, H * 0.68);
        for (let ry = H * 0.12; ry < H * 0.76; ry += 48) {
          g.fillStyle(0x222246, 0.92); g.fillRect(x + 35, ry, 120, 20);
          g.fillStyle(this.acc, 0.58); g.fillCircle(x + 43, ry + 10, 3);
          g.fillStyle(0x44ff88, 0.42); g.fillCircle(x + 53, ry + 10, 3);
          for (let bx = x + 64; bx < x + 148; bx += 15) { g.fillStyle(0x333357, 0.62); g.fillRect(bx, ry + 4, 11, 12); }
        }
      }
      this._neonBar(g, 0, H * 0.80, lw, 3, this.acc, 0.38);
      this._gradVPainted(g, 0, H * 0.80, lw, H * 0.20, 0x0f0f26, 0x050510, 7);
    }

    // C: holographic panels + neon pillars + circuit ceiling (sf 0.33)
    { const sf = 0.33, lw = this._lw(sf), g = this._gfx(sf, -14);
      // Ceiling grid
      g.fillStyle(0x1a1a3a, 0.88); g.fillRect(0, 0, lw, H * 0.11);
      for (let x = 0; x < lw; x += 85) { g.fillStyle(this.acc, 0.085); g.fillRect(x, 0, 2, H * 0.11); }
      for (let y = 0; y < H * 0.11; y += 27) { g.fillStyle(this.acc, 0.065); g.fillRect(0, y, lw, 2); }
      // Holographic display panels
      for (let x = 55; x < lw; x += 490) {
        this._neonBar(g, x, H * 0.13, 230, 3, this.acc, 0.62);
        this._neonBar(g, x, H * 0.13 + H * 0.53, 230, 3, this.acc, 0.62);
        this._neonBar(g, x, H * 0.13, 3, H * 0.53, this.acc, 0.62);
        this._neonBar(g, x + 227, H * 0.13, 3, H * 0.53, this.acc, 0.62);
        g.fillStyle(this.acc, 0.042); g.fillRect(x + 3, H * 0.13 + 3, 224, H * 0.53 - 6);
        for (let sy = H * 0.16; sy < H * 0.64; sy += 9) { g.fillStyle(this.acc, 0.062); g.fillRect(x + 5, sy, 220, 4); }
        for (let bx = x + 10; bx < x + 220; bx += 22) {
          const ht = 42 + this._h(bx, x) * 108;
          g.fillStyle(this.acc, 0.20); g.fillRect(bx, H * 0.62 - ht, 16, ht);
        }
      }
      // Neon pillars
      for (let x = 290; x < lw; x += 490) {
        this._neonBar(g, x - 7, H * 0.11, 14, H * 0.71, this.acc, 0.11);
        g.fillStyle(0x1a1a3a, 0.92); g.fillRect(x - 5, H * 0.11, 10, H * 0.71);
        this._neonBar(g, x - 1, H * 0.11, 2, H * 0.71, this.acc, 0.58);
      }
      // Metallic floor
      g.fillStyle(0x111128, 0.96); g.fillRect(0, H * 0.82, lw, H * 0.18);
      for (let x = 0; x < lw; x += 85) { g.fillStyle(this.acc, 0.052); g.fillRect(x, H * 0.82, 2, H * 0.18); }
      for (let x = 55; x < lw; x += 490) { g.fillStyle(this.acc, 0.04); g.fillRect(x, H * 0.82, 230, H * 0.18); }
    }

    // D: circuit-board archways + near panels (sf 0.57)
    { const sf = 0.57, lw = this._lw(sf), g = this._gfx(sf, -13);
      for (let x = 0; x < lw; x += 580) {
        g.fillStyle(0x0d0d1e, 0.93); g.fillRect(x, 0, 26, H * 0.84);
        g.fillStyle(this.acc, 0.22);
        for (let ty = 22; ty < H * 0.84; ty += 58) {
          g.fillRect(x + 7, ty, 12, 3); g.fillRect(x + 7, ty + 3, 3, 22); g.fillCircle(x + 13, ty + 25, 5);
        }
      }
      g.fillStyle(0x050510, 0.92); g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // E: glitch fragments — "never saw it coming" (sf 0.22)
    { const sf = 0.22, lw = this._lw(sf), g = this._gfx(sf, -12);
      for (let i = 0; i < 20; i++) {
        const gx = this._h(i, 40) * lw, gy = H * 0.05 + this._h(i, 41) * H * 0.80;
        const gw = 8 + this._h(i, 42) * 80, gh = 2 + this._h(i, 43) * 8;
        g.fillStyle(this.acc, 0.08 + this._h(i, 44) * 0.10); g.fillRect(gx, gy, gw, gh);
      }
    }

    // F: neon light shafts (sf 0.18)
    { const sf = 0.18, lw = this._lw(sf), g = this._gfx(sf, -11);
      for (let x = 135; x < lw; x += 490) {
        g.fillStyle(this.acc, 0.042); g.fillTriangle(x - 22, 0, x + 22, 0, x + 38, H * 0.72);
        g.fillStyle(this.acc, 0.022); g.fillTriangle(x - 50, 0, x + 50, 0, x + 72, H * 0.84);
      }
    }
  }

  // ─── Stage 6 — Armory Corridor ─────────────────────────────────────────────
  // "Guess the fairy tale only lasted a moment"
  // The battle is over — cold stone, fallen banners, the aftermath of heartbreak
  _armoryCorridor() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#0a0d10');

    // A: cold stone void (sf 0.05)
    { const sf = 0.05, lw = this._lw(sf), g = this._gfx(sf, -16);
      this._gradVPainted(g, 0, 0, lw, H, 0x080c10, 0x141e26, 22);
    }

    // B: far stone corridor with arrow-slits (sf 0.15)
    { const sf = 0.15, lw = this._lw(sf), g = this._gfx(sf, -15);
      this._stoneWall(g, 0, H * 0.04, lw, H * 0.78, 0x1c2430, 0x0e1418, 58, 148, 0.92, true);
      for (let x = 160; x < lw; x += 375) {
        g.fillStyle(0x0e1418, 0.92); g.fillRect(x - 12, H * 0.10, 24, H * 0.30);
        g.fillStyle(0x88aacc, 0.065); g.fillRect(x - 9, H * 0.12, 18, H * 0.26);
      }
      // Distant vault ceiling
      this._gradVPainted(g, 0, 0, lw, H * 0.04, 0x141e26, 0x1e2c38, 4);
      this._gradVPainted(g, 0, H * 0.80, lw, H * 0.20, 0x1c2430, 0x0a0d10, 7);
    }

    // C: weapon racks + banners + vaulted ceiling (sf 0.33)
    { const sf = 0.33, lw = this._lw(sf), g = this._gfx(sf, -14);
      this._gradVPainted(g, 0, 0, lw, H * 0.16, 0x141e26, 0x1e2c38, 7);
      for (let x = 0; x < lw; x += 250) { g.fillStyle(0x1c2c38, 0.62); g.fillRect(x, 0, 6, H * 0.16); }
      // Weapon racks
      for (let x = 32; x < lw; x += 460) {
        g.fillStyle(0x2e3a42, 0.92); g.fillRect(x, H * 0.14, 295, 9);
        for (let k = 0; k < 6; k++) {
          const kx = x + 24 + k * 46;
          g.fillStyle(this.acc, 0.58); g.fillRect(kx - 9, H * 0.15, 18, 5);
          g.fillStyle(0x4a5c6c, 0.72); g.fillRect(kx - 2, H * 0.20, 4, H * 0.37);
          g.fillStyle(0xc8c8c8, 0.58); g.fillRect(kx - 1, H * 0.21, 2, H * 0.35);
          g.fillStyle(0xffffff, 0.16); g.fillRect(kx, H * 0.21, 1, H * 0.31);
        }
        // Shields
        for (let k = 0; k < 4; k++) {
          const sx = x + 310 + k * 68;
          g.fillStyle(0x2e3a42, 0.92);
          g.fillPoints([
            { x: sx - 24, y: H * 0.19 }, { x: sx + 24, y: H * 0.19 },
            { x: sx + 24, y: H * 0.19 + 56 }, { x: sx, y: H * 0.19 + 76 },
            { x: sx - 24, y: H * 0.19 + 56 },
          ], true);
          g.fillStyle(this.acc, 0.38); g.fillCircle(sx, H * 0.19 + 28, 13);
          g.fillStyle(this.acc, 0.22); g.fillRect(sx - 16, H * 0.19 + 24, 32, 4); g.fillRect(sx - 2, H * 0.19 + 14, 4, 22);
          g.fillStyle(this.acc, 0.58); g.fillCircle(sx, H * 0.19 + 28, 5);
        }
      }
      // Battle banners (some slightly torn — "fairy tale ended")
      for (let x = 190; x < lw; x += 460) {
        g.fillStyle(0x4a5c6c, 0.82); g.fillRect(x + 230 - 4, H * 0.02, 7, H * 0.57);
        g.fillStyle(0x8b0000, 0.68); g.fillRect(x + 230, H * 0.03, 75, H * 0.44);
        for (let by = H * 0.03; by < H * 0.03 + H * 0.44; by += 22) { g.fillStyle(this.acc, 0.22); g.fillRect(x + 230, by, 75, 4); }
        g.fillStyle(this.acc, 0.48); g.fillCircle(x + 230 + 37, H * 0.17, 22);
        g.fillStyle(0x8b0000, 0.72); g.fillCircle(x + 230 + 37, H * 0.17, 13);
        g.fillStyle(this.acc, 0.44); g.fillRect(x + 230 + 35, H * 0.11, 4, 26); g.fillRect(x + 230 + 27, H * 0.17, 20, 4);
        // Torn lower edge
        for (let tx = x + 230; tx < x + 305; tx += 8) {
          const tear = this._h(tx, x) * 18;
          g.fillStyle(0x0a0d10, 0.7); g.fillTriangle(tx, H * 0.03 + H * 0.44 - tear, tx + 8, H * 0.03 + H * 0.44 - tear, tx + 4, H * 0.03 + H * 0.44 + 4);
        }
      }
      this._stoneWall(g, 0, H * 0.82, lw, H * 0.18, 0x1e2a32, 0x0e1418, 32, 95, 0.94);
    }

    // D: iron torches + portcullis shadow bars (sf 0.57)
    { const sf = 0.57, lw = this._lw(sf), g = this._gfx(sf, -13);
      for (let x = 105; x < lw; x += 490) this._lamp(g, x, H * 0.24, 0x2e3a42, 0xff7722);
      for (let x = 370; x < lw; x += 490) this._lamp(g, x, H * 0.55, 0x2e3a42, 0xff7722);
      for (let x = 0; x < lw; x += 580) { g.fillStyle(0x0a0d10, 0.27); g.fillRect(x, 0, 11, H * 0.84); }
      g.fillStyle(0x0a0d10, 0.90); g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // E: torch ember sparks floating up (sf 0.22)
    { const sf = 0.22, lw = this._lw(sf), g = this._gfx(sf, -12);
      for (let i = 0; i < 22; i++) {
        const ex = this._h(i, 50) * lw, ey = H * 0.15 + this._h(i, 51) * H * 0.65;
        this._star(g, ex, ey, 2 + this._h(i, 52) * 4, 0xff7722, 0.06 + this._h(i, 53) * 0.10);
      }
    }

    // F: torch fire shafts (sf 0.18)
    { const sf = 0.18, lw = this._lw(sf), g = this._gfx(sf, -11);
      for (let x = 148; x < lw; x += 490) {
        g.fillStyle(0xff7722, 0.042); g.fillTriangle(x - 24, H * 0.28, x + 24, H * 0.28, x + 38, H * 0.84);
        g.fillStyle(0xff9944, 0.022); g.fillTriangle(x - 44, H * 0.28, x + 44, H * 0.28, x + 58, H * 0.96);
      }
    }
  }

  // ─── Stage 7 — Art Gallery ──────────────────────────────────────────────────
  // "Everything all I've had, now it's gone"
  // Beautiful things behind glass, unreachable — paintings of what was
  _artGallery() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#120008');

    // A: deep maroon void (sf 0.05)
    { const sf = 0.05, lw = this._lw(sf), g = this._gfx(sf, -16);
      this._gradVPainted(g, 0, 0, lw, H, 0x0e0006, 0x220012, 22);
    }

    // B: distant long gallery with hung paintings (sf 0.15)
    { const sf = 0.15, lw = this._lw(sf), g = this._gfx(sf, -15);
      this._gradVPainted(g, 0, H * 0.05, lw, H * 0.78, 0x1e0012, 0x2c0018, 12);
      g.fillStyle(this.acc, 0.20); g.fillRect(0, H * 0.10, lw, 7); // picture rail
      for (let x = 32; x < lw; x += 270) {
        const pw = 105 + this._h(x, 0) * 85, ph = 84 + this._h(x, 1) * 72;
        g.fillStyle(this.acc, 0.38); g.fillRect(x, H * 0.13, pw + 12, ph + 12);
        const cc = this._h(x, 2) < 0.33 ? 0x8b2020 : this._h(x, 2) < 0.66 ? 0x1e4060 : 0x2c5a1a;
        g.fillStyle(cc, 0.58); g.fillRect(x + 6, H * 0.13 + 6, pw, ph);
        g.fillStyle(0xffffff, 0.038); g.fillRect(x + 8, H * 0.135, pw * 0.38, ph);
      }
      this._gradVPainted(g, 0, H * 0.80, lw, H * 0.20, 0x1e0012, 0x0e0006, 7);
    }

    // C: large masterwork paintings + pedestals + coffered ceiling (sf 0.33)
    { const sf = 0.33, lw = this._lw(sf), g = this._gfx(sf, -14);
      this._gradVPainted(g, 0, 0, lw, H * 0.12, 0x1e0012, 0x300018, 7);
      for (let x = 65; x < lw; x += 185) {
        g.fillStyle(this.acc, 0.11); g.fillCircle(x, H * 0.06, 16);
        g.lineStyle(1, this.acc, 0.075); g.lineBetween(x, 0, x, H * 0.12); g.lineBetween(x - 92, H * 0.06, x + 92, H * 0.06);
      }
      for (let x = 0; x < lw; x += 475) {
        const pw = 210, ph = 148, px = x + 32, py = H * 0.13;
        // 4-layer ornate gold frame
        g.fillStyle(this._lighten(this.acc, 0.28), 0.68); g.fillRect(px - 18, py - 18, pw + 36, ph + 36);
        g.fillStyle(this.acc, 0.82);                       g.fillRect(px - 12, py - 12, pw + 24, ph + 24);
        g.fillStyle(this._darken(this.acc, 0.28), 0.72);   g.fillRect(px - 6,  py - 6,  pw + 12, ph + 12);
        // Corner rosettes
        for (const [fx, fy] of [[px - 12, py - 12],[px + pw + 12, py - 12],[px - 12, py + ph + 12],[px + pw + 12, py + ph + 12]]) {
          g.fillStyle(this._lighten(this.acc, 0.50), 0.82); g.fillCircle(fx, fy, 9);
        }
        // Canvas
        const palette = [0x8b2020, 0x4a2060, 0x1e4060, 0x3a6020, 0x8b5020, 0x602040];
        const mainC = palette[Math.floor(this._h(x, 5) * palette.length)];
        g.fillStyle(mainC, 0.72); g.fillRect(px, py, pw, ph);
        g.fillStyle(this._lighten(mainC, 0.28), 0.36); g.fillEllipse(px + pw * 0.5, py + ph * 0.44, pw * 0.58, ph * 0.62);
        // Varnish glare
        g.fillStyle(0xffffff, 0.048); g.fillRect(px + 7, py + 7, pw * 0.24, ph - 14);
        // Spotlight
        g.fillStyle(0xfff5c0, 0.038); g.fillTriangle(px + pw / 2 - 16, 0, px + pw / 2 + 16, 0, px + pw / 2 + 32, py);
      }
      // Marble pedestals
      for (let x = 295; x < lw; x += 475) {
        g.fillStyle(0x3a2028, 0.88); g.fillRect(x - 30, H * 0.54, 60, H * 0.28);
        g.fillStyle(0x4a3038, 0.72); g.fillRect(x - 37, H * 0.78, 74, 9); g.fillRect(x - 37, H * 0.52, 74, 9);
        g.fillStyle(0xc0a0a8, 0.62); g.fillEllipse(x, H * 0.45, 46, 58); g.fillCircle(x, H * 0.35, 20);
        g.fillStyle(0xffffff, 0.08); g.fillRect(x - 16, H * 0.34, 7, 64);
      }
      // Herringbone parquet
      g.fillStyle(0x220012, 0.96); g.fillRect(0, H * 0.82, lw, H * 0.18);
      for (let x = 0; x < lw; x += 62) { g.fillStyle(0x3a0020, 0.27); g.fillRect(x, H * 0.82, 2, H * 0.18); }
      for (let y = H * 0.84; y < H; y += 30) { g.fillStyle(0x3a0020, 0.14); g.fillRect(0, y, lw, 2); }
    }

    // D: ornate columns + track lighting + near archways (sf 0.57)
    { const sf = 0.57, lw = this._lw(sf), g = this._gfx(sf, -13);
      for (let x = 210; x < lw; x += 560) {
        this._ornateCol(g, x, H * 0.06, H * 0.76, 19, 0x220012, 0x800020, 0.96);
        g.fillStyle(this.acc, 0.065); g.fillCircle(x, H * 0.07, 55);
      }
      g.fillStyle(0x2e1a18, 0.82); g.fillRect(0, H * 0.06, lw, 9);
      for (let x = 85; x < lw; x += 210) {
        g.fillStyle(0x3a2020, 0.92); g.fillEllipse(x, H * 0.075, 22, 15);
        g.fillStyle(0xfff5c0, 0.28); g.fillCircle(x, H * 0.085, 6);
        g.fillStyle(0xfff5c0, 0.062); g.fillTriangle(x - 20, H * 0.095, x + 20, H * 0.095, x + 28, H * 0.52);
      }
      g.fillStyle(0x0e0006, 0.90); g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // E: gallery spotlights (sf 0.18)
    { const sf = 0.18, lw = this._lw(sf), g = this._gfx(sf, -12);
      for (let x = 137; x < lw; x += 475) {
        g.fillStyle(0xfff5c0, 0.044); g.fillTriangle(x - 22, H * 0.07, x + 22, H * 0.07, x + 36, H * 0.57);
        g.fillStyle(0xfff5c0, 0.022); g.fillTriangle(x - 50, H * 0.07, x + 50, H * 0.07, x + 66, H * 0.68);
        for (let my = H * 0.10; my < H * 0.52; my += 38) { g.fillStyle(0xfff5c0, 0.026); g.fillCircle(x + (my - H * 0.10) * 0.05, my, 3 + this._h(x, my) * 2); }
      }
    }

    // F: floating star sparks — "everything I've had" (sf 0.22)
    { const sf = 0.22, lw = this._lw(sf), g = this._gfx(sf, -11);
      for (let i = 0; i < 25; i++) {
        const r = 1 + this._h(i, 60) * 5;
        this._star(g, this._h(i, 61) * lw, H * 0.05 + this._h(i, 62) * H * 0.80, r, 0xffd700, 0.04 + this._h(i, 63) * 0.07);
      }
    }
  }

  // ─── Stage 8 — Treasure Vault ───────────────────────────────────────────────
  // "Once Upon A…" — the ellipsis, the locked-away love, the sealed ending
  // Darkness, guarded gold, gems that used to sparkle freely, now imprisoned
  _treasureVault() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#05050f');

    // A: near-black void with deep golden underglow (sf 0.05)
    { const sf = 0.05, lw = this._lw(sf), g = this._gfx(sf, -16);
      this._gradVPainted(g, 0, 0, lw, H, 0x050510, 0x101022, 22);
      for (let x = 500; x < lw; x += 1000) {
        g.fillStyle(0xffd700, 0.08); g.fillCircle(x, H * 0.76, 280);
        g.fillStyle(0xffd700, 0.04); g.fillCircle(x, H * 0.76, 420);
      }
    }

    // B: stacked treasure chests + stone vault (sf 0.15)
    { const sf = 0.15, lw = this._lw(sf), g = this._gfx(sf, -15);
      this._stoneWall(g, 0, H * 0.05, lw, H * 0.77, 0x0f0f1e, 0x070710, 62, 155, 0.90, true);
      for (let x = 0; x < lw; x += 310) {
        for (let row = 0; row < 3; row++) {
          const cy = H * 0.65 - row * 54;
          g.fillStyle(0x2c2000, 0.82); g.fillRect(x + 42, cy, 94, 46);
          g.fillStyle(0x3e2e00, 0.78); g.fillRect(x + 42, cy, 94, 13);
          g.fillStyle(this.acc, 0.27); g.fillRect(x + 42, cy + 7, 94, 5); g.fillRect(x + 84, cy, 6, 46);
          g.fillStyle(0xffd700, 0.38); g.fillCircle(x + 88, cy + 23, 5);
        }
      }
      this._gradVPainted(g, 0, H * 0.80, lw, H * 0.20, 0x1c1800, 0x050510, 7);
    }

    // C: gem walls + coin piles + vault doors (sf 0.33)
    { const sf = 0.33, lw = this._lw(sf), g = this._gfx(sf, -14);
      this._gradVPainted(g, 0, 0, lw, H * 0.14, 0x0f0f1e, 0x1e1e34, 7);
      for (let x = 0; x < lw; x += 225) { g.fillStyle(0x1e1e34, 0.68); g.fillRect(x, 0, 5, H * 0.14); g.fillStyle(this.acc, 0.08); g.fillCircle(x + 112, H * 0.03, 11); }
      // Gem-studded wall panels
      const gemCols = [0xff4444, 0x44ff88, 0x4488ff, 0xffd700, 0xff88ff, 0x44ffff];
      for (let x = 0; x < lw; x += 510) {
        g.fillStyle(0x0d0d20, 0.92); g.fillRect(x, H * 0.12, 410, H * 0.62);
        for (let i = 0; i < 22; i++) {
          const gx = x + 16 + this._h(i, x) * 378;
          const gy = H * 0.15 + this._h(i + 1, x) * H * 0.56;
          const gc = gemCols[Math.floor(this._h(i * 3, x) * gemCols.length)];
          const gr = 5 + this._h(i, x + 1) * 10;
          this._gem(g, gx, gy, gr, gr * 1.35, gc, 0.58);
        }
      }
      // Gold coin piles
      for (let x = 85; x < lw; x += 245) {
        const pH = 22 + this._h(x, 7) * 44, pW = 65 + this._h(x, 8) * 85;
        g.fillStyle(this.acc, 0.30); g.fillEllipse(x + pW / 2, H * 0.80, pW, pH * 0.62);
        for (let ci = 0; ci < 9; ci++) {
          const cx2 = x + 9 + this._h(ci, x) * (pW - 18);
          const cy  = H * 0.75 - this._h(ci + 1, x) * pH * 0.72;
          g.fillStyle(this.acc, 0.52); g.fillEllipse(cx2, cy, 15, 9);
          g.fillStyle(0xffffff, 0.16); g.fillEllipse(cx2 - 2, cy - 1, 6, 3);
        }
      }
      // Vault door sections
      for (let x = 360; x < lw; x += 510) {
        g.fillStyle(0x2a2a42, 0.92); g.fillRect(x, H * 0.17, 115, H * 0.62);
        g.fillStyle(0x3a3a52, 0.72); g.fillRect(x + 5, H * 0.19, 105, H * 0.58);
        g.fillStyle(this.acc, 0.48);
        for (let ly = H * 0.24; ly < H * 0.72; ly += 52) {
          g.fillCircle(x + 21, ly, 11); g.fillCircle(x + 94, ly, 11);
        }
        g.fillCircle(x + 57, H * 0.48, 18);
        g.fillStyle(0x0f0f1e, 0.72); g.fillCircle(x + 57, H * 0.48, 9);
      }
      // Floor with gold sheen
      this._gradVPainted(g, 0, H * 0.82, lw, H * 0.18, 0x1c1800, 0x050510, 7);
      for (let x = 0; x < lw; x += 105) { g.fillStyle(this.acc, 0.052); g.fillRect(x, H * 0.82, 2, H * 0.18); }
    }

    // D: candelabras + floating gem sparkles (sf 0.57)
    { const sf = 0.57, lw = this._lw(sf), g = this._gfx(sf, -13);
      for (let x = 165; x < lw; x += 575) {
        g.fillStyle(this.acc, 0.58); g.fillRect(x - 3, H * 0.40, 6, H * 0.42); g.fillRect(x - 19, H * 0.82, 38, 8); g.fillRect(x - 23, H * 0.40, 46, 8);
        for (let ci = -1; ci <= 1; ci++) {
          const cxi = x + ci * 19;
          g.fillStyle(0xfff5e0, 0.72); g.fillRect(cxi - 3, H * 0.27, 6, H * 0.13);
          g.fillStyle(0xffcc00, 0.56); g.fillCircle(cxi, H * 0.26, 7);
          g.fillStyle(0xffcc00, 0.14); g.fillCircle(cxi, H * 0.26, 24);
        }
      }
      // Sparkle particles — "Jeweled Paradise"
      const gemColsD = [0xff4444, 0x44ff88, 0x4488ff, 0xffd700, 0xff88ff, 0x44ffff];
      for (let i = 0; i < 48; i++) {
        const px = this._h(i, 70) * lw, py = H * 0.08 + this._h(i, 71) * H * 0.76;
        const gc = gemColsD[i % 6];
        this._star(g, px, py, 1 + this._h(i, 72) * 5, gc, 0.12 + this._h(i, 73) * 0.18);
      }
      g.fillStyle(0x05050f, 0.90); g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // E: upward gold light from coin piles (sf 0.20)
    { const sf = 0.20, lw = this._lw(sf), g = this._gfx(sf, -12);
      for (let x = 205; x < lw; x += 510) {
        g.fillStyle(0xffd700, 0.052); g.fillTriangle(x - 38, H * 0.82, x + 38, H * 0.82, x - 22, 0);
        g.fillStyle(0xffd700, 0.030); g.fillTriangle(x - 10, H * 0.82, x + 10, H * 0.82, x + 5, 0);
        g.fillStyle(0xffd700, 0.018); g.fillTriangle(x - 65, H * 0.84, x + 65, H * 0.84, x - 42, 0);
      }
    }

    // F: "Once Upon A…" — final sparkle constellation overhead (sf 0.06)
    { const sf = 0.06, lw = this._lw(sf), g = this._gfx(sf, -11);
      for (let i = 0; i < 55; i++) {
        const r = 1 + this._h(i, 80) * 4;
        this._star(g, this._h(i, 81) * lw, H * 0.02 + this._h(i, 82) * H * 0.48, r, 0xffd700, 0.05 + this._h(i, 83) * 0.10);
      }
    }
  }
}
