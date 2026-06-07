/**
 * BackgroundBuilder — hand-painted architectural parallax backgrounds.
 *
 * Five scroll-factor layers per stage give an illusion of real depth.
 * Everything is drawn with Phaser Graphics so no extra image assets are needed.
 * Techniques used for the "painted" feel:
 *   · Multiple overlapping semi-transparent shapes (wash-over-wash)
 *   · Vertical gradient fills (atmospheric perspective)
 *   · Deterministic pseudo-random variation (no Math.random → stable reloads)
 *   · Architectural light / shadow cues (ambient occlusion hints)
 *   · Stage-specific warm / cool color grading
 */
import Phaser from 'phaser';

export class BackgroundBuilder {
  constructor(scene, W, H, stageIndex) {
    this.scene = scene;
    this.W = W;       // world width (6400)
    this.H = H;       // world height (720)
    this.idx = stageIndex;

    const lv = scene.level;
    this.prim = Phaser.Display.Color.HexStringToColor(lv.primaryColor).color;
    this.acc  = Phaser.Display.Color.HexStringToColor(lv.accentColor).color;
    this.primC = Phaser.Display.Color.HexStringToColor(lv.primaryColor);
    this.accC  = Phaser.Display.Color.HexStringToColor(lv.accentColor);

    // Logical viewport width (used to compute per-layer draw widths)
    this.VW = scene.scale.width || 1280;
  }

  // ────────────────────────────────────────────────────────
  //  Public entry
  // ────────────────────────────────────────────────────────

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
    this._universalVignette();
  }

  // ────────────────────────────────────────────────────────
  //  Low-level helpers
  // ────────────────────────────────────────────────────────

  /** Create a Graphics object with scroll-factor and depth pre-set. */
  _gfx(sf, depth) {
    return this.scene.add.graphics().setScrollFactor(sf).setDepth(depth);
  }

  /**
   * Minimum draw width so the layer always fills the viewport as the
   * camera travels from x=0 to x=(W-VW).
   * renderX = objectX − cameraX × sf  →  need objectX=0, so width ≥ VW + (W−VW)×sf
   */
  _lw(sf) {
    return Math.ceil(this.VW + (this.W - this.VW) * sf) + 64; // +64 safety margin
  }

  /** Vertical gradient: fills a rect with `steps` horizontal bands. */
  _gradV(g, x, y, w, h, colA, colB, steps = 18) {
    const sh = h / steps;
    for (let i = 0; i < steps; i++) {
      const t = i / Math.max(steps - 1, 1);
      const c = Phaser.Display.Color.Interpolate.ColorWithColor(
        Phaser.Display.Color.IntegerToColor(colA),
        Phaser.Display.Color.IntegerToColor(colB),
        100, Math.round(t * 100),
      );
      g.fillStyle(Phaser.Display.Color.GetColor(c.r, c.g, c.b), 1);
      g.fillRect(x, y + sh * i, w, sh + 1);
    }
  }

  /** Deterministic pseudo-random in [0,1) — no Math.random, stable across reloads. */
  _h(a, b = 0) {
    return ((a * 1664525 + b * 1013904223 + 22695477) & 0x7fffffff) / 0x7fffffff;
  }

  /** Interpolate two integer colors by fraction t ∈ [0,1]. */
  _lerp(colA, colB, t) {
    const a = Phaser.Display.Color.IntegerToColor(colA);
    const b = Phaser.Display.Color.IntegerToColor(colB);
    return Phaser.Display.Color.GetColor(
      Math.round(a.r + (b.r - a.r) * t),
      Math.round(a.g + (b.g - a.g) * t),
      Math.round(a.b + (b.b - a.b) * t),
    );
  }

  /** Darken an integer color by fraction. */
  _darken(col, f) { return this._lerp(col, 0x000000, f); }
  /** Lighten an integer color by fraction. */
  _lighten(col, f) { return this._lerp(col, 0xffffff, f); }

  // ────────────────────────────────────────────────────────
  //  Architectural elements
  // ────────────────────────────────────────────────────────

  /**
   * Bookshelves: draws `nShelves` shelf rows inside a frame rect.
   * seed controls per-shelf variation.
   */
  _booksInRect(g, x, y, w, h, nShelves, seed = 0) {
    const shelfH = h / nShelves;
    for (let s = 0; s < nShelves; s++) {
      const ty = y + s * shelfH;
      // shelf board
      g.fillStyle(this._darken(this.prim, 0.2), 0.85);
      g.fillRect(x, ty + shelfH - 5, w, 5);
      // books
      for (let bx = x + 3; bx < x + w - 3; bx += 12) {
        const bh = shelfH * 0.4 + this._h(bx, seed + s) * shelfH * 0.48;
        const shade = this._h(bx * 3, seed + s * 7);
        let bc = shade < 0.3  ? this.acc
               : shade < 0.55 ? this._lerp(this.acc, this.prim, 0.5)
               : shade < 0.78 ? this.prim
                              : this._darken(this.prim, 0.35);
        g.fillStyle(bc, 0.70);
        g.fillRect(bx, ty + shelfH - 5 - bh, 10, bh);
        // spine highlight wash
        g.fillStyle(0xffffff, 0.06);
        g.fillRect(bx + 1, ty + shelfH - 5 - bh + 3, 2, bh - 6);
        // occasional gold title strip
        if (this._h(bx * 7, seed + s) > 0.65) {
          g.fillStyle(this.acc, 0.22);
          g.fillRect(bx + 2, ty + shelfH - 5 - bh * 0.55, 7, 2);
        }
      }
    }
  }

  /** Ornate classical column: fluted shaft + capital + base. */
  _ornateCol(g, cx, y, colH, r, dark, light, alpha = 1) {
    const nFlutes = 7;
    for (let i = 0; i < nFlutes; i++) {
      const c = i % 2 === 0 ? dark : this._lerp(dark, light, 0.45);
      g.fillStyle(c, alpha * 0.92);
      g.fillRect(cx - r + (r * 2 / nFlutes) * i, y, r * 2 / nFlutes + 1, colH);
    }
    // Capital
    g.fillStyle(light, alpha);
    g.fillRect(cx - r * 1.6, y - 10, r * 3.2, 10);
    g.fillRect(cx - r * 1.2, y - 18, r * 2.4, 8);
    g.fillRect(cx - r * 1.85, y - 24, r * 3.7, 6);
    // Base
    g.fillStyle(light, alpha * 0.9);
    g.fillRect(cx - r * 1.2, y + colH,      r * 2.4, 8);
    g.fillRect(cx - r * 1.6, y + colH + 8,  r * 3.2, 8);
    g.fillRect(cx - r * 1.85,y + colH + 16, r * 3.7, 6);
  }

  /** Egyptian pillar with lotus capital. */
  _lotusCol(g, cx, y, colH, r, stone, gold, alpha = 1) {
    // Shaft with slight entasis (taper)
    g.fillStyle(stone, alpha * 0.9);
    g.fillRect(cx - r, y, r * 2, colH);
    // Hieroglyph bands
    g.fillStyle(gold, alpha * 0.18);
    for (let gy = y + 20; gy < y + colH; gy += 55) {
      g.fillRect(cx - r, gy, r * 2, 8);
    }
    // Lotus capital
    g.fillStyle(gold, alpha * 0.85);
    g.fillRect(cx - r * 1.5, y - 8, r * 3, 8);
    // Lotus petals (fan shapes using triangles)
    for (let i = -2; i <= 2; i++) {
      g.fillStyle(this._lerp(gold, 0xffffff, 0.2), alpha * 0.55);
      g.fillTriangle(
        cx + i * r * 0.6, y - 8,
        cx + (i - 0.5) * r * 0.6, y - 28,
        cx + (i + 0.5) * r * 0.6, y - 28,
      );
    }
    // Base
    g.fillStyle(stone, alpha * 0.8);
    g.fillRect(cx - r * 1.3, y + colH, r * 2.6, 10);
    g.fillRect(cx - r * 1.6, y + colH + 10, r * 3.2, 8);
  }

  /** Stone-block wall: fill + mortar grid. */
  _stoneWall(g, x, y, w, h, stoneCol, mortarCol, bh = 44, bw = 110, alpha = 1) {
    g.fillStyle(stoneCol, alpha);
    g.fillRect(x, y, w, h);
    g.fillStyle(mortarCol, alpha * 0.55);
    for (let row = 0; row * bh < h; row++) {
      g.fillRect(x, y + row * bh, w, 3);            // horizontal mortar
      const offset = row % 2 === 0 ? 0 : bw / 2;
      for (let col = 0; col * bw < w + bw; col++) {
        const mx = x + col * bw + offset - bw / 2;
        g.fillRect(mx, y + row * bh, 3, bh);        // vertical mortar
      }
    }
    // Subtle stone face variation: random lighter patches
    for (let rx = x; rx < x + w; rx += bw) {
      for (let ry = y; ry < y + h; ry += bh) {
        const row = Math.round((ry - y) / bh);
        const offset = row % 2 === 0 ? 0 : bw / 2;
        const bx = rx + offset;
        if (this._h(bx, ry) > 0.6) {
          g.fillStyle(0xffffff, alpha * 0.04);
          g.fillRect(bx + 4, ry + 4, bw - 8, bh - 8);
        }
      }
    }
  }

  /** Arched window with glow. */
  _archWindow(g, cx, cy, w, h, frameCol, glowCol, alpha = 1) {
    // Outer frame
    g.fillStyle(this._darken(frameCol, 0.3), alpha);
    g.fillRect(cx - w / 2 - 6, cy - h / 2 - 6, w + 12, h + 12);
    // Glass
    g.fillStyle(glowCol, alpha * 0.28);
    g.fillRect(cx - w / 2, cy - h / 2, w, h);
    // Window panes
    g.fillStyle(this._darken(frameCol, 0.2), alpha * 0.7);
    g.fillRect(cx - 3, cy - h / 2, 6, h);
    g.fillRect(cx - w / 2, cy - 3, w, 6);
    // Arch top
    g.fillStyle(glowCol, alpha * 0.22);
    g.fillCircle(cx, cy - h / 2, w / 2);
    // Exterior glow haze
    g.fillStyle(glowCol, alpha * 0.07);
    g.fillCircle(cx, cy - h * 0.1, w * 1.8);
    // Bright center reflection
    g.fillStyle(0xffffff, alpha * 0.06);
    g.fillRect(cx - w * 0.3, cy - h / 2 + 5, w * 0.1, h - 10);
  }

  /** Oil lamp / sconce on a wall. */
  _wallLamp(g, cx, cy, poleCol, glowCol) {
    // Bracket
    g.fillStyle(poleCol, 0.9);
    g.fillRect(cx, cy, 3, 50);          // wall plate
    g.fillRect(cx - 22, cy + 12, 22, 3); // arm
    // Housing
    g.fillStyle(poleCol, 0.95);
    g.fillRect(cx - 30, cy + 4, 18, 20);
    g.fillTriangle(cx - 30, cy + 24, cx - 12, cy + 24, cx - 21, cy + 36);
    // Glow
    g.fillStyle(glowCol, 0.20);
    g.fillCircle(cx - 21, cy + 14, 28);
    g.fillStyle(glowCol, 0.35);
    g.fillCircle(cx - 21, cy + 14, 10);
    // Warm floor pool
    g.fillStyle(glowCol, 0.06);
    g.fillEllipse(cx - 21, cy + 80, 90, 30);
  }

  /** Chandelier hanging from ceiling. */
  _chandelier(g, cx, ty, col, glowCol, arms = 5, radius = 80) {
    // Chain
    g.fillStyle(col, 0.7);
    g.fillRect(cx - 2, ty, 4, 30);
    // Central body
    g.fillStyle(col, 0.9);
    g.fillEllipse(cx, ty + 30, 30, 18);
    // Arms
    for (let i = 0; i < arms; i++) {
      const angle = (i / arms) * Math.PI * 2 - Math.PI / 2;
      const ex = cx + Math.cos(angle) * radius;
      const ey = ty + 40 + Math.sin(angle) * radius * 0.25;
      g.lineStyle(2, col, 0.7);
      g.lineBetween(cx, ty + 38, ex, ey);
      // Candle
      g.fillStyle(0xfff5c0, 0.6);
      g.fillRect(ex - 3, ey - 14, 6, 14);
      // Flame glow
      g.fillStyle(glowCol, 0.45);
      g.fillCircle(ex, ey - 16, 6);
      g.fillStyle(glowCol, 0.15);
      g.fillCircle(ex, ey - 14, 18);
    }
    // Central diffuse glow
    g.fillStyle(glowCol, 0.06);
    g.fillCircle(cx, ty + 40, radius * 2);
  }

  /** Neon-style glow bar (for Tech Manor). */
  _neonBar(g, x, y, w, h, col, alpha = 1) {
    // Core
    g.fillStyle(col, alpha);
    g.fillRect(x, y, w, h);
    // Glow halos
    g.fillStyle(col, alpha * 0.18);
    g.fillRect(x - 4, y - 4, w + 8, h + 8);
    g.fillStyle(col, alpha * 0.08);
    g.fillRect(x - 10, y - 10, w + 20, h + 20);
  }

  /** Universal screen-space vignette (darkens edges + a slight dark overlay). */
  _universalVignette() {
    const { scene } = this;
    const sw = scene.scale.width;
    const sh = scene.scale.height;
    const v = scene.add.graphics().setScrollFactor(0).setDepth(-1);
    // Top + bottom bars
    v.fillStyle(0x000000, 0.45);
    v.fillRect(0, 0, sw, 72);
    v.fillRect(0, sh - 72, sw, 72);
    // Soft side gradients (5 thin strips each side)
    for (let i = 0; i < 6; i++) {
      const a = 0.28 * (1 - i / 6);
      v.fillStyle(0x000000, a);
      v.fillRect(0, 72, (i + 1) * 18, sh - 144);
      v.fillRect(sw - (i + 1) * 18, 72, (i + 1) * 18, sh - 144);
    }
    // Global darkening wash
    const dark = scene.add.rectangle(0, 0, this.W, this.H, 0x000000, 0.38)
      .setOrigin(0).setScrollFactor(0).setDepth(-2);
  }

  // ────────────────────────────────────────────────────────
  //  Stage backgrounds
  // ────────────────────────────────────────────────────────

  // ── 0  The Grand Library ─────────────────────────────────
  _grandLibrary() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#0d0500');

    // Layer A — deep void with ember glow (sf 0.06)
    {
      const sf = 0.06, lw = this._lw(sf);
      const g = this._gfx(sf, -14);
      this._gradV(g, 0, 0, lw, H, 0x0d0400, 0x231000, 20);
      // Glow pools from deep behind the stacks
      for (let x = 400; x < lw; x += 700) {
        g.fillStyle(0x8b4513, 0.09);
        g.fillCircle(x, H * 0.72, 220);
      }
    }

    // Layer B — distant gothic arched hall + dark shelves (sf 0.16)
    {
      const sf = 0.16, lw = this._lw(sf);
      const g = this._gfx(sf, -13);
      this._gradV(g, 0, 0, lw, H * 0.22, 0x110600, 0x1e0a00, 8);
      // Ceiling coffers + arches
      for (let x = 0; x < lw; x += 380) {
        // Arch pier
        g.fillStyle(0x1c0900, 0.95);
        g.fillRect(x, 0, 22, H * 0.82);
        // Span fill
        g.fillStyle(0x150700, 0.90);
        g.fillRect(x + 22, H * 0.02, 336, H * 0.18);
        // Pointed apex glow
        g.fillStyle(0xd4af37, 0.07);
        g.fillCircle(x + 190 + 22, H * 0.03, 20);
      }
      // Receding bookshelves (very dark, far away)
      for (let x = 25; x < lw; x += 210) {
        g.fillStyle(0x190800, 0.88);
        g.fillRect(x, H * 0.10, 188, H * 0.71);
        this._booksInRect(g, x, H * 0.10, 188, H * 0.71, 4, x);
      }
      // Far floor
      this._gradV(g, 0, H * 0.80, lw, H * 0.20, 0x190800, 0x0d0500, 6);
    }

    // Layer C — mid hall: detailed mahogany shelves (sf 0.34)
    {
      const sf = 0.34, lw = this._lw(sf);
      const g = this._gfx(sf, -12);
      // Vault ribs (golden tracery lines across ceiling)
      for (let x = 0; x < lw; x += 270) {
        g.lineStyle(2, 0xd4af37, 0.15);
        g.lineBetween(x, 0, x + 135, H * 0.16);
        g.lineBetween(x + 270, 0, x + 135, H * 0.16);
        g.fillStyle(0xd4af37, 0.10);
        g.fillCircle(x + 135, H * 0.03, 10);
      }
      // Shelf units
      for (let x = 0; x < lw; x += 260) {
        // Frame
        g.fillStyle(0x3b1a05, 0.93);
        g.fillRect(x, H * 0.07, 6, H * 0.74);
        g.fillRect(x + 254, H * 0.07, 6, H * 0.74);
        g.fillRect(x, H * 0.07, 260, 6);
        // Case back
        g.fillStyle(0x2a0f00, 0.90);
        g.fillRect(x + 6, H * 0.07, 248, H * 0.74);
        // Books
        this._booksInRect(g, x + 8, H * 0.09, 244, H * 0.71, 5, x * 3);
      }
      // Polished parquet floor
      g.fillStyle(0x1c0b00, 0.97);
      g.fillRect(0, H * 0.82, lw, H * 0.18);
      for (let x = 0; x < lw; x += 90) {
        g.fillStyle(0x2e1200, 0.35);
        g.fillRect(x, H * 0.82, 2, H * 0.18);
      }
      for (let y = H * 0.84; y < H; y += 38) {
        g.fillStyle(0x2e1200, 0.18);
        g.fillRect(0, y, lw, 2);
      }
      // Floor reflection sheen
      g.fillStyle(0xd4af37, 0.03);
      g.fillRect(0, H * 0.83, lw, 4);
    }

    // Layer D — near: ornate pillars + reading lamps + balcony (sf 0.57)
    {
      const sf = 0.57, lw = this._lw(sf);
      const g = this._gfx(sf, -11);
      // Ornate pillars
      for (let x = 250; x < lw; x += 520) {
        this._ornateCol(g, x, H * 0.05, H * 0.77, 20, 0x2a0f00, 0x5a2e08, 0.96);
        // Ambient glow around pillar
        g.fillStyle(0xd4af37, 0.05);
        g.fillCircle(x, H * 0.06, 55);
      }
      // Upper balcony rail at 52% height
      g.fillStyle(0x3b1a05, 0.90);
      g.fillRect(0, H * 0.52, lw, 9);
      for (let x = 18; x < lw; x += 46) {
        g.fillStyle(0x5a2e08, 0.80);
        g.fillRect(x, H * 0.52 + 9, 7, 64);
        g.fillStyle(this.acc, 0.14);
        g.fillCircle(x + 3, H * 0.52 + 40, 4);
      }
      g.fillStyle(0x3b1a05, 0.85);
      g.fillRect(0, H * 0.52 + 73, lw, 9);
      // Reading lamps on balcony
      for (let x = 100; x < lw; x += 520) {
        this._wallLamp(g, x, H * 0.22, 0x5a2e08, 0xfff5c0);
      }
      // Ground-floor wall sconces
      for (let x = 340; x < lw; x += 520) {
        this._wallLamp(g, x, H * 0.60, 0x5a2e08, 0xfff5c0);
      }
    }

    // Layer E — light shafts from skylights (sf 0.20)
    {
      const sf = 0.20, lw = this._lw(sf);
      const g = this._gfx(sf, -10);
      for (let x = 190; x < lw; x += 380) {
        // Wide diffuse shaft
        g.fillStyle(0xd4af37, 0.035);
        g.fillTriangle(x - 45, 0, x + 45, 0, x + 80, H * 0.70);
        // Bright core shaft
        g.fillStyle(0xfff5c0, 0.025);
        g.fillTriangle(x - 12, 0, x + 12, 0, x + 22, H * 0.60);
        // Mote particle band
        for (let my = 40; my < H * 0.65; my += 28) {
          g.fillStyle(0xfff5c0, 0.03);
          g.fillCircle(x + (my / H) * 30, my, 4);
        }
      }
    }
  }

  // ── 1  Egyptian Hall ──────────────────────────────────────
  _egyptianHall() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#150b00');

    // Layer A — warm sandstone sky (sf 0.06)
    {
      const sf = 0.06, lw = this._lw(sf);
      const g = this._gfx(sf, -14);
      this._gradV(g, 0, 0, lw, H, 0x0f0800, 0x2b1800, 20);
    }

    // Layer B — distant pyramid interior / colonnade (sf 0.16)
    {
      const sf = 0.16, lw = this._lw(sf);
      const g = this._gfx(sf, -13);
      // Far ceiling
      this._gradV(g, 0, 0, lw, H * 0.18, 0x110900, 0x1f1000, 8);
      // Distant columns
      for (let x = 0; x < lw; x += 340) {
        g.fillStyle(0x2a1800, 0.85);
        g.fillRect(x + 130, 0, 80, H * 0.80);
        // Hieroglyph bands
        g.fillStyle(this.acc, 0.10);
        for (let gy = 30; gy < H * 0.80; gy += 60) g.fillRect(x + 130, gy, 80, 7);
      }
      // Distant wall
      this._stoneWall(g, 0, H * 0.05, lw, H * 0.76, 0x1f1100, 0x0d0700, 55, 140, 0.85);
      // Distant floor
      this._gradV(g, 0, H * 0.80, lw, H * 0.20, 0x2a1600, 0x110a00, 6);
    }

    // Layer C — mid colonnade (sf 0.34)
    {
      const sf = 0.34, lw = this._lw(sf);
      const g = this._gfx(sf, -12);
      // Ceiling: painted ceiling panels
      this._gradV(g, 0, 0, lw, H * 0.14, 0x1a0f00, 0x2b1800, 6);
      for (let x = 0; x < lw; x += 420) {
        g.fillStyle(this.acc, 0.08);
        g.fillRect(x, 0, 420, H * 0.02);
      }
      // Main columns
      for (let x = 0; x < lw; x += 360) {
        this._lotusCol(g, x + 30, H * 0.05, H * 0.76, 32, 0x3d2300, this.acc, 0.90);
        this._lotusCol(g, x + 330, H * 0.05, H * 0.76, 32, 0x3d2300, this.acc, 0.90);
      }
      // Wall hieroglyphs between columns
      for (let x = 60; x < lw; x += 360) {
        g.fillStyle(this.acc, 0.12);
        for (let gy = H * 0.08; gy < H * 0.72; gy += 50) {
          // Rows of rectangular glyphs
          for (let gx = x; gx < x + 260; gx += 24) {
            if (this._h(gx, gy) > 0.45) {
              g.fillRect(gx, gy, 18, 14);
            }
          }
        }
        // Horizontal divider bands
        g.fillStyle(this.acc, 0.18);
        g.fillRect(x, H * 0.08, 260, 5);
        g.fillRect(x, H * 0.72, 260, 5);
      }
      // Sand floor
      this._gradV(g, 0, H * 0.80, lw, H * 0.20, 0x3d2300, 0x1a0f00, 8);
      // Tile pattern on floor
      for (let x = 0; x < lw; x += 120) {
        g.fillStyle(0x2a1600, 0.4);
        g.fillRect(x, H * 0.80, 3, H * 0.20);
      }
    }

    // Layer D — near: large statues + torches (sf 0.57)
    {
      const sf = 0.57, lw = this._lw(sf);
      const g = this._gfx(sf, -11);
      // Canopic jar / statue silhouettes
      for (let x = 180; x < lw; x += 560) {
        // Seated statue body
        g.fillStyle(0x2a1600, 0.92);
        g.fillRect(x - 30, H * 0.30, 60, H * 0.50);  // torso
        g.fillRect(x - 45, H * 0.54, 90, H * 0.26);  // legs/seat
        g.fillCircle(x, H * 0.28, 30);               // head
        // Headdress (nemes)
        g.fillStyle(this.acc, 0.20);
        g.fillTriangle(x, H * 0.18, x - 22, H * 0.28, x + 22, H * 0.28);
        // Crook
        g.fillStyle(this.acc, 0.25);
        g.fillRect(x + 10, H * 0.35, 5, 40);
      }
      // Wall torches
      for (let x = 100; x < lw; x += 560) {
        this._wallLamp(g, x, H * 0.30, 0x4a2800, 0xffaa44);
      }
      for (let x = 380; x < lw; x += 560) {
        this._wallLamp(g, x, H * 0.55, 0x4a2800, 0xffaa44);
      }
      // Foreground sandy floor shadow
      g.fillStyle(0x0d0700, 0.85);
      g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // Layer E — golden light shafts from above (sf 0.20)
    {
      const sf = 0.20, lw = this._lw(sf);
      const g = this._gfx(sf, -10);
      for (let x = 210; x < lw; x += 360) {
        g.fillStyle(0xd4af37, 0.05);
        g.fillTriangle(x - 30, 0, x + 30, 0, x + 55, H * 0.80);
        g.fillStyle(0xffd700, 0.03);
        g.fillTriangle(x - 8, 0, x + 8, 0, x + 15, H * 0.75);
        // Motes
        for (let my = 20; my < H * 0.75; my += 32) {
          g.fillStyle(0xffd700, 0.04);
          g.fillCircle(x + my * 0.06, my, 3);
        }
      }
    }
  }

  // ── 2  Samurai Gallery ───────────────────────────────────
  _samuraiGallery() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#0d0000');

    // Layer A — deep crimson night void (sf 0.06)
    {
      const sf = 0.06, lw = this._lw(sf);
      const g = this._gfx(sf, -14);
      this._gradV(g, 0, 0, lw, H, 0x0a0000, 0x1a0500, 20);
      // Moon glow pools
      for (let x = 600; x < lw; x += 1200) {
        g.fillStyle(0xfff5e0, 0.06);
        g.fillCircle(x, H * 0.12, 120);
      }
    }

    // Layer B — distant shoji screen wall (sf 0.16)
    {
      const sf = 0.16, lw = this._lw(sf);
      const g = this._gfx(sf, -13);
      // Dark wood frame behind everything
      g.fillStyle(0x1a0800, 0.90);
      g.fillRect(0, 0, lw, H * 0.85);
      // Shoji rice-paper panels (backlit, very faint)
      for (let x = 0; x < lw; x += 220) {
        for (let panel = 0; panel < 3; panel++) {
          const px = x + panel * 70;
          g.fillStyle(0x2a1800, 0.80);
          g.fillRect(px, H * 0.07, 65, H * 0.72);
          // Rice paper translucency
          g.fillStyle(0xfff5e0, 0.04);
          g.fillRect(px + 3, H * 0.09, 59, H * 0.68);
          // Grid lines
          g.fillStyle(0x1a0800, 0.50);
          for (let sy = H * 0.12; sy < H * 0.72; sy += 32) g.fillRect(px, sy, 65, 2);
          for (let sx = px + 20; sx < px + 65; sx += 20) g.fillRect(sx, H * 0.07, 2, H * 0.72);
        }
      }
      // Cherry blossom silhouette (far)
      for (let x = 200; x < lw; x += 800) {
        // Branch
        g.fillStyle(0x1c0a00, 0.70);
        g.fillRect(x, H * 0.05, 4, H * 0.32);
        g.fillRect(x - 60, H * 0.18, 64, 3);
        g.fillRect(x + 4, H * 0.24, 55, 3);
        // Blossoms (tiny circles)
        for (let i = 0; i < 12; i++) {
          const bx = x - 70 + this._h(i, x) * 130;
          const by = H * 0.06 + this._h(i, x + 1) * H * 0.26;
          g.fillStyle(0x8b0000, 0.28);
          g.fillCircle(bx, by, 5 + this._h(i * 3, x) * 6);
        }
      }
      this._gradV(g, 0, H * 0.82, lw, H * 0.18, 0x1a0800, 0x0d0400, 6);
    }

    // Layer C — mid dojo hall: weapon racks + columns (sf 0.34)
    {
      const sf = 0.34, lw = this._lw(sf);
      const g = this._gfx(sf, -12);
      // Coffered wooden ceiling
      this._gradV(g, 0, 0, lw, H * 0.15, 0x1a0800, 0x2e1200, 6);
      for (let x = 0; x < lw; x += 160) {
        g.fillStyle(0x3b1a05, 0.6);
        g.fillRect(x, 0, 6, H * 0.15);
      }
      for (let y = H * 0.04; y < H * 0.15; y += 35) {
        g.fillStyle(0x3b1a05, 0.4);
        g.fillRect(0, y, lw, 4);
      }
      // Lacquered wooden pillars
      for (let x = 60; x < lw; x += 480) {
        this._ornateCol(g, x, H * 0.07, H * 0.74, 16, 0x3b0000, 0x7a0000, 0.92);
      }
      // Katana racks on wall
      for (let x = 120; x < lw; x += 480) {
        // Rack bar
        g.fillStyle(0x3b1a05, 0.8);
        g.fillRect(x, H * 0.24, 200, 6);
        g.fillRect(x, H * 0.38, 200, 6);
        // Katanas (diagonal lines)
        for (let k = 0; k < 5; k++) {
          const kx = x + 20 + k * 38;
          // Handle
          g.fillStyle(0x5a2e08, 0.9);
          g.fillRect(kx, H * 0.25, 6, 24);
          // Guard (tsuba)
          g.fillStyle(this.acc, 0.60);
          g.fillRect(kx - 4, H * 0.25 + 24, 14, 4);
          // Blade
          g.fillStyle(0xc0c0c0, 0.55);
          g.fillRect(kx + 1, H * 0.30, 3, 50);
          // Blade highlight
          g.fillStyle(0xffffff, 0.20);
          g.fillRect(kx + 2, H * 0.30, 1, 45);
        }
      }
      // Paper lanterns hanging
      for (let x = 200; x < lw; x += 480) {
        // String
        g.fillStyle(0x3b1a05, 0.6);
        g.fillRect(x + 100 - 2, 0, 3, H * 0.22);
        // Lantern body
        g.fillStyle(0xd4af37, 0.05);
        g.fillEllipse(x + 100, H * 0.22 + 30, 44, 60);
        g.fillStyle(0x8b0000, 0.65);
        g.fillEllipse(x + 100, H * 0.22 + 30, 38, 54);
        // Glow
        g.fillStyle(0xff9900, 0.15);
        g.fillCircle(x + 100, H * 0.22 + 30, 40);
        // Stripes
        for (let ly = H * 0.22 + 6; ly < H * 0.22 + 54; ly += 10) {
          g.fillStyle(0xd4af37, 0.25);
          g.fillRect(x + 100 - 19, ly, 38, 3);
        }
      }
      // Dark tatami/stone floor
      g.fillStyle(0x1e0c00, 0.95);
      g.fillRect(0, H * 0.82, lw, H * 0.18);
      for (let x = 0; x < lw; x += 130) {
        g.fillStyle(0x2e1200, 0.25);
        g.fillRect(x, H * 0.82, 2, H * 0.18);
      }
    }

    // Layer D — near: armor stands + falling blossoms (sf 0.57)
    {
      const sf = 0.57, lw = this._lw(sf);
      const g = this._gfx(sf, -11);
      // Armor stands every ~600px
      for (let x = 220; x < lw; x += 600) {
        // Stand pole
        g.fillStyle(0x3b1a05, 0.85);
        g.fillRect(x - 3, H * 0.38, 6, H * 0.44);
        g.fillRect(x - 25, H * 0.80, 50, 8);
        // Chest plate
        g.fillStyle(0x8b0000, 0.70);
        g.fillRect(x - 22, H * 0.28, 44, 52);
        // Shoulder guards
        g.fillStyle(0x8b0000, 0.60);
        g.fillRect(x - 38, H * 0.30, 20, 30);
        g.fillRect(x + 18, H * 0.30, 20, 30);
        // Helmet
        g.fillStyle(0x5a0000, 0.80);
        g.fillEllipse(x, H * 0.24, 42, 36);
        // Menpo (face mask) glint
        g.fillStyle(0xc0c0c0, 0.20);
        g.fillRect(x - 14, H * 0.30, 28, 18);
        // Mon (family crest) on chest
        g.fillStyle(this.acc, 0.22);
        g.fillCircle(x, H * 0.35, 10);
      }
      // Scattered cherry blossom petals
      for (let i = 0; i < 30; i++) {
        const px = this._h(i, 3) * lw;
        const py = this._h(i, 4) * H * 0.90;
        g.fillStyle(0xd4607a, 0.25);
        g.fillEllipse(px, py, 10, 7);
      }
      g.fillStyle(0x0d0500, 0.88);
      g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // Layer E — moonlight shafts through shoji (sf 0.22)
    {
      const sf = 0.22, lw = this._lw(sf);
      const g = this._gfx(sf, -10);
      for (let x = 240; x < lw; x += 480) {
        g.fillStyle(0xfff5e0, 0.035);
        g.fillTriangle(x - 25, 0, x + 25, 0, x + 40, H * 0.75);
        g.fillStyle(0xfff5e0, 0.02);
        g.fillTriangle(x - 60, 0, x + 60, 0, x + 90, H * 0.85);
      }
    }
  }

  // ── 3  Royal Chambers ────────────────────────────────────
  _royalChambers() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#0a0015');

    // Layer A — deep velvet void (sf 0.06)
    {
      const sf = 0.06, lw = this._lw(sf);
      const g = this._gfx(sf, -14);
      this._gradV(g, 0, 0, lw, H, 0x080010, 0x150028, 20);
    }

    // Layer B — distant ornate wallpaper hall (sf 0.16)
    {
      const sf = 0.16, lw = this._lw(sf);
      const g = this._gfx(sf, -13);
      this._gradV(g, 0, 0, lw, H, 0x0e0020, 0x1a0038, 18);
      // Damask wallpaper pattern (small repeating motif)
      for (let x = 0; x < lw; x += 60) {
        for (let y = 30; y < H * 0.78; y += 70) {
          g.fillStyle(this.acc, 0.06);
          g.fillEllipse(x + 30, y + 35, 24, 40);
          g.fillStyle(this.prim, 0.04);
          g.fillCircle(x + 30, y + 35, 8);
          g.fillCircle(x + 30, y + 10, 6);
          g.fillCircle(x + 30, y + 60, 6);
        }
      }
      // Chair rail molding
      g.fillStyle(this.acc, 0.22);
      g.fillRect(0, H * 0.54, lw, 5);
      g.fillRect(0, H * 0.56, lw, 3);
      // Wainscoting below rail
      g.fillStyle(this.prim, 0.25);
      g.fillRect(0, H * 0.56, lw, H * 0.24);
      // Paneling lines
      for (let x = 0; x < lw; x += 180) {
        g.fillStyle(this.acc, 0.10);
        g.fillRect(x + 15, H * 0.58, 150, H * 0.20);
        g.fillStyle(this.acc, 0.05);
        g.fillRect(x + 18, H * 0.585, 144, H * 0.19);
      }
    }

    // Layer C — mid hall: chandeliers + tapestries (sf 0.34)
    {
      const sf = 0.34, lw = this._lw(sf);
      const g = this._gfx(sf, -12);
      // Gilded cornice at ceiling
      g.fillStyle(this.acc, 0.20);
      g.fillRect(0, H * 0.06, lw, 10);
      // Egg-and-dart detail
      for (let x = 0; x < lw; x += 24) {
        g.fillStyle(this.acc, 0.12);
        g.fillEllipse(x + 12, H * 0.06 + 5, 16, 10);
      }
      // Ceiling panels (coffered)
      for (let x = 0; x < lw; x += 300) {
        g.fillStyle(this.prim, 0.18);
        g.fillRect(x + 20, H * 0.02, 260, H * 0.05);
        g.fillStyle(this.acc, 0.08);
        g.fillRect(x + 25, H * 0.025, 250, H * 0.04);
      }
      // Chandeliers
      for (let x = 200; x < lw; x += 600) {
        this._chandelier(g, x, H * 0.06, this.acc, 0xfff5c0, 6, 90);
      }
      // Floor-to-ceiling tapestries
      for (let x = 100; x < lw; x += 600) {
        // Tapestry background
        g.fillStyle(this.prim, 0.80);
        g.fillRect(x - 55, H * 0.09, 110, H * 0.60);
        // Border
        g.fillStyle(this.acc, 0.35);
        g.fillRect(x - 55, H * 0.09, 110, 5);
        g.fillRect(x - 55, H * 0.09 + H * 0.60 - 5, 110, 5);
        g.fillRect(x - 55, H * 0.09, 5, H * 0.60);
        g.fillRect(x + 50, H * 0.09, 5, H * 0.60);
        // Heraldic design
        g.fillStyle(this.acc, 0.25);
        g.fillCircle(x, H * 0.28, 25);
        g.fillTriangle(x - 20, H * 0.38, x + 20, H * 0.38, x, H * 0.55);
        // Decorative scrollwork
        g.fillStyle(this.acc, 0.14);
        for (let ty = H * 0.45; ty < H * 0.65; ty += 20) {
          g.fillRect(x - 35, ty, 70, 3);
        }
      }
      // Mirror frames
      for (let x = 380; x < lw; x += 600) {
        g.fillStyle(this.acc, 0.45);
        g.fillEllipse(x, H * 0.30, 100, 130);
        g.fillStyle(0x0e0020, 0.65);
        g.fillEllipse(x, H * 0.30, 88, 118);
        // Reflection sheen
        g.fillStyle(0xffffff, 0.06);
        g.fillRect(x - 28, H * 0.18, 12, 80);
      }
      // Persian rug on floor
      g.fillStyle(this.prim, 0.55);
      g.fillRect(0, H * 0.82, lw, H * 0.18);
      // Rug border
      g.fillStyle(this.acc, 0.18);
      g.fillRect(0, H * 0.82, lw, 5);
      // Rug pattern
      for (let x = 40; x < lw; x += 80) {
        g.fillStyle(this.acc, 0.10);
        g.fillCircle(x, H * 0.88, 14);
      }
    }

    // Layer D — near: ornate pillars + candelabras (sf 0.57)
    {
      const sf = 0.57, lw = this._lw(sf);
      const g = this._gfx(sf, -11);
      for (let x = 200; x < lw; x += 540) {
        this._ornateCol(g, x, H * 0.06, H * 0.76, 18, 0x1a0038, 0x4b0082, 0.95);
        g.fillStyle(this.acc, 0.07);
        g.fillCircle(x, H * 0.07, 50);
      }
      // Tall candelabras
      for (let x = 380; x < lw; x += 540) {
        // Stand
        g.fillStyle(this.acc, 0.55);
        g.fillRect(x - 3, H * 0.42, 6, H * 0.40);
        g.fillRect(x - 16, H * 0.82, 32, 6);
        // Top plate
        g.fillRect(x - 18, H * 0.43, 36, 6);
        // 3 candles
        for (let ci = -1; ci <= 1; ci++) {
          const cx2 = x + ci * 14;
          g.fillStyle(0xfff5e0, 0.65);
          g.fillRect(cx2 - 3, H * 0.30, 6, H * 0.13);
          g.fillStyle(0xffaa00, 0.50);
          g.fillCircle(cx2, H * 0.29, 5);
          g.fillStyle(0xffcc00, 0.15);
          g.fillCircle(cx2, H * 0.29, 18);
        }
      }
      g.fillStyle(0x0a0015, 0.88);
      g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // Layer E — candlelight warm glow shafts (sf 0.20)
    {
      const sf = 0.20, lw = this._lw(sf);
      const g = this._gfx(sf, -10);
      for (let x = 200; x < lw; x += 600) {
        g.fillStyle(0x9370db, 0.04);
        g.fillTriangle(x - 40, 0, x + 40, 0, x + 65, H * 0.72);
        g.fillStyle(0xd4af37, 0.025);
        g.fillTriangle(x - 12, 0, x + 12, 0, x + 20, H * 0.65);
      }
    }
  }

  // ── 4  Museum Wing ───────────────────────────────────────
  _museumWing() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#0c1414');

    // Layer A — cool diffuse museum light (sf 0.06)
    {
      const sf = 0.06, lw = this._lw(sf);
      const g = this._gfx(sf, -14);
      this._gradV(g, 0, 0, lw, H, 0x0c1414, 0x1a2a2a, 20);
    }

    // Layer B — distant vaulted gallery (sf 0.16)
    {
      const sf = 0.16, lw = this._lw(sf);
      const g = this._gfx(sf, -13);
      this._stoneWall(g, 0, H * 0.06, lw, H * 0.76, 0x1e2e2e, 0x0c1414, 50, 130, 0.88);
      // Skylight ceiling
      this._gradV(g, 0, 0, lw, H * 0.06, 0x2a3838, 0x3a4848, 4);
      for (let x = 180; x < lw; x += 360) {
        // Skylight pane
        g.fillStyle(0x88ccdd, 0.08);
        g.fillRect(x - 60, 0, 120, H * 0.05);
        g.fillStyle(0x2a3838, 0.6);
        g.fillRect(x - 60, H * 0.025, 120, 3);
        g.fillRect(x, 0, 3, H * 0.05);
      }
      this._gradV(g, 0, H * 0.80, lw, H * 0.20, 0x2a3838, 0x0c1414, 6);
    }

    // Layer C — mid: display cases + pillars (sf 0.34)
    {
      const sf = 0.34, lw = this._lw(sf);
      const g = this._gfx(sf, -12);
      // Coffered ceiling with steel beams
      g.fillStyle(0x223030, 0.9);
      g.fillRect(0, 0, lw, H * 0.12);
      for (let x = 0; x < lw; x += 240) {
        g.fillStyle(0x334040, 0.7);
        g.fillRect(x, 0, 8, H * 0.12);
        g.fillStyle(0x88ccdd, 0.04);
        g.fillRect(x + 8, 0, 232, H * 0.12);
      }
      for (let y = 0; y < H * 0.12; y += 40) {
        g.fillStyle(0x334040, 0.5);
        g.fillRect(0, y, lw, 5);
      }
      // Display cases (glass vitrines)
      for (let x = 60; x < lw; x += 360) {
        // Case frame (steel/brass)
        g.fillStyle(0x4a5a5a, 0.9);
        g.fillRect(x, H * 0.38, 200, 5);
        g.fillRect(x, H * 0.62, 200, 5);
        g.fillRect(x, H * 0.38, 5, H * 0.24);
        g.fillRect(x + 195, H * 0.38, 5, H * 0.24);
        // Glass pane
        g.fillStyle(0x88ccdd, 0.06);
        g.fillRect(x + 5, H * 0.40, 190, H * 0.22);
        // Artifact inside (generic shape)
        g.fillStyle(this.acc, 0.30);
        g.fillRect(x + 70, H * 0.44, 60, 40);
        g.fillEllipse(x + 100, H * 0.44, 40, 30);
        // Spotlight on case
        g.fillStyle(0xffffff, 0.03);
        g.fillTriangle(x + 100, H * 0.12, x + 80, H * 0.40, x + 120, H * 0.40);
      }
      // Classical pillars
      for (let x = 220; x < lw; x += 360) {
        this._ornateCol(g, x, H * 0.10, H * 0.72, 15, 0x2a3838, 0x4a5a5a, 0.90);
      }
      // Marble floor with reflection
      this._gradV(g, 0, H * 0.82, lw, H * 0.18, 0x2a3838, 0x1a2828, 6);
      // Tile grid
      for (let x = 0; x < lw; x += 100) {
        g.fillStyle(0x334040, 0.30);
        g.fillRect(x, H * 0.82, 2, H * 0.18);
      }
      for (let y = H * 0.82; y < H; y += 45) {
        g.fillStyle(0x334040, 0.18);
        g.fillRect(0, y, lw, 2);
      }
    }

    // Layer D — near: information plaques + specimen mounts (sf 0.57)
    {
      const sf = 0.57, lw = this._lw(sf);
      const g = this._gfx(sf, -11);
      for (let x = 100; x < lw; x += 480) {
        // Mounted artifact panel
        g.fillStyle(0x334040, 0.85);
        g.fillRect(x, H * 0.28, 180, 200);
        g.fillStyle(this.acc, 0.28);
        g.fillRect(x + 15, H * 0.30, 150, 4);
        g.fillStyle(0x4a5a5a, 0.55);
        for (let ty = H * 0.34; ty < H * 0.48; ty += 12) {
          g.fillRect(x + 15, ty, 150 * (0.4 + this._h(x, ty) * 0.6), 6);
        }
        // Plaque
        g.fillStyle(this.acc, 0.35);
        g.fillRect(x + 30, H * 0.50, 120, 30);
        g.fillStyle(0x223030, 0.75);
        for (let ty = H * 0.52; ty < H * 0.52 + 22; ty += 7) {
          g.fillRect(x + 38, ty, 90 * (0.5 + this._h(x * 2, ty) * 0.5), 4);
        }
      }
      g.fillStyle(0x0c1414, 0.88);
      g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // Layer E — cool museum spotlights (sf 0.20)
    {
      const sf = 0.20, lw = this._lw(sf);
      const g = this._gfx(sf, -10);
      for (let x = 200; x < lw; x += 360) {
        g.fillStyle(0x88ccdd, 0.04);
        g.fillTriangle(x - 18, 0, x + 18, 0, x + 30, H * 0.55);
        g.fillStyle(0xffffff, 0.018);
        g.fillTriangle(x - 5, 0, x + 5, 0, x + 8, H * 0.50);
      }
    }
  }

  // ── 5  Tech Manor ────────────────────────────────────────
  _techManor() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#050510');

    // Layer A — deep blue-black void + data-stream glow (sf 0.06)
    {
      const sf = 0.06, lw = this._lw(sf);
      const g = this._gfx(sf, -14);
      this._gradV(g, 0, 0, lw, H, 0x030310, 0x0d0d28, 20);
      // Faint data-stream columns
      for (let x = 0; x < lw; x += 40) {
        for (let y = 0; y < H; y += 30) {
          if (this._h(x, y) > 0.85) {
            g.fillStyle(0x4a90e2, 0.08);
            g.fillRect(x, y, 12, 18);
          }
        }
      }
    }

    // Layer B — server room / ancient stone walls hybrid (sf 0.16)
    {
      const sf = 0.16, lw = this._lw(sf);
      const g = this._gfx(sf, -13);
      // Stone wall base (castle meets tech)
      this._stoneWall(g, 0, H * 0.08, lw, H * 0.73, 0x0d0d1e, 0x06060f, 50, 120, 0.90);
      // Server rack overlaid on stone
      for (let x = 0; x < lw; x += 320) {
        g.fillStyle(0x1a1a38, 0.85);
        g.fillRect(x + 30, H * 0.10, 120, H * 0.68);
        // Rack units
        for (let ry = H * 0.12; ry < H * 0.76; ry += 22) {
          g.fillStyle(0x222244, 0.9);
          g.fillRect(x + 33, ry, 114, 18);
          // Status LEDs
          g.fillStyle(this.acc, 0.55);
          g.fillCircle(x + 40, ry + 9, 3);
          g.fillStyle(0x44ff44, 0.40);
          g.fillCircle(x + 50, ry + 9, 3);
          // Drive bays
          g.fillStyle(0x334, 0.5);
          for (let bx = x + 60; bx < x + 140; bx += 14) {
            g.fillStyle(0x333355, 0.6);
            g.fillRect(bx, ry + 3, 10, 12);
          }
        }
      }
      // Glowing floor strip
      this._neonBar(g, 0, H * 0.80, lw, 3, this.acc, 0.35);
      this._gradV(g, 0, H * 0.80, lw, H * 0.20, 0x0d0d24, 0x050510, 6);
    }

    // Layer C — holographic displays + neon pillars (sf 0.34)
    {
      const sf = 0.34, lw = this._lw(sf);
      const g = this._gfx(sf, -12);
      // Ceiling grid
      g.fillStyle(0x1a1a38, 0.85);
      g.fillRect(0, 0, lw, H * 0.10);
      for (let x = 0; x < lw; x += 80) {
        g.fillStyle(this.acc, 0.08);
        g.fillRect(x, 0, 2, H * 0.10);
      }
      for (let y = 0; y < H * 0.10; y += 25) {
        g.fillStyle(this.acc, 0.06);
        g.fillRect(0, y, lw, 2);
      }
      // Holographic display panels
      for (let x = 50; x < lw; x += 480) {
        // Panel frame (glowing edge)
        this._neonBar(g, x, H * 0.14, 220, 3, this.acc, 0.60);
        this._neonBar(g, x, H * 0.14 + H * 0.52, 220, 3, this.acc, 0.60);
        this._neonBar(g, x, H * 0.14, 3, H * 0.52, this.acc, 0.60);
        this._neonBar(g, x + 217, H * 0.14, 3, H * 0.52, this.acc, 0.60);
        // Holographic content
        g.fillStyle(this.acc, 0.04);
        g.fillRect(x + 3, H * 0.14 + 3, 214, H * 0.52 - 6);
        // Scan lines
        for (let sy = H * 0.17; sy < H * 0.65; sy += 8) {
          g.fillStyle(this.acc, 0.06);
          g.fillRect(x + 5, sy, 210, 3);
        }
        // Data graph shape
        for (let gx = x + 10; gx < x + 210; gx += 20) {
          const ht = 40 + this._h(gx, x) * 100;
          g.fillStyle(this.acc, 0.18);
          g.fillRect(gx, H * 0.60 - ht, 14, ht);
        }
      }
      // Neon accent pillars
      for (let x = 280; x < lw; x += 480) {
        this._neonBar(g, x - 6, H * 0.10, 12, H * 0.72, this.acc, 0.12);
        g.fillStyle(0x1a1a38, 0.9);
        g.fillRect(x - 5, H * 0.10, 10, H * 0.72);
        this._neonBar(g, x - 1, H * 0.10, 2, H * 0.72, this.acc, 0.55);
      }
      // Metallic floor with reflection
      g.fillStyle(0x111126, 0.95);
      g.fillRect(0, H * 0.82, lw, H * 0.18);
      for (let x = 0; x < lw; x += 80) {
        g.fillStyle(this.acc, 0.05);
        g.fillRect(x, H * 0.82, 2, H * 0.18);
      }
      // Floor reflection of neon
      for (let x = 50; x < lw; x += 480) {
        g.fillStyle(this.acc, 0.04);
        g.fillRect(x, H * 0.82, 220, H * 0.18);
      }
    }

    // Layer D — near: circuit-board archways + floating UI widgets (sf 0.57)
    {
      const sf = 0.57, lw = this._lw(sf);
      const g = this._gfx(sf, -11);
      // Archways with circuit board motifs
      for (let x = 0; x < lw; x += 560) {
        g.fillStyle(0x0d0d1e, 0.92);
        g.fillRect(x, 0, 24, H * 0.84);
        // PCB traces
        g.fillStyle(this.acc, 0.20);
        for (let ty = 20; ty < H * 0.84; ty += 55) {
          g.fillRect(x + 6, ty, 12, 3);
          g.fillRect(x + 6, ty + 3, 3, 20);
          g.fillCircle(x + 12, ty + 23, 4);
        }
      }
      g.fillStyle(0x050510, 0.90);
      g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // Layer E — neon light shafts (sf 0.20)
    {
      const sf = 0.20, lw = this._lw(sf);
      const g = this._gfx(sf, -10);
      for (let x = 130; x < lw; x += 480) {
        g.fillStyle(this.acc, 0.04);
        g.fillTriangle(x - 20, 0, x + 20, 0, x + 35, H * 0.70);
        g.fillStyle(this.acc, 0.025);
        g.fillTriangle(x - 45, 0, x + 45, 0, x + 65, H * 0.80);
      }
    }
  }

  // ── 6  Armory Corridor ───────────────────────────────────
  _armoryCorridor() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#0a0d10');

    // Layer A — cold stone void (sf 0.06)
    {
      const sf = 0.06, lw = this._lw(sf);
      const g = this._gfx(sf, -14);
      this._gradV(g, 0, 0, lw, H, 0x080c10, 0x141e24, 20);
    }

    // Layer B — far stone corridor (sf 0.16)
    {
      const sf = 0.16, lw = this._lw(sf);
      const g = this._gfx(sf, -13);
      this._stoneWall(g, 0, H * 0.04, lw, H * 0.78, 0x1a2228, 0x0e1418, 56, 144, 0.90);
      // Arrow-slit windows
      for (let x = 150; x < lw; x += 360) {
        g.fillStyle(0x0e1418, 0.9);
        g.fillRect(x - 10, H * 0.10, 20, H * 0.28);
        g.fillRect(x - 5, H * 0.10 - 20, 10, 20);
        // Faint exterior glow
        g.fillStyle(0x88aacc, 0.06);
        g.fillRect(x - 8, H * 0.12, 16, H * 0.24);
      }
      this._gradV(g, 0, H * 0.80, lw, H * 0.20, 0x1a2228, 0x0a0d10, 6);
    }

    // Layer C — mid armory: weapon racks + banners (sf 0.34)
    {
      const sf = 0.34, lw = this._lw(sf);
      const g = this._gfx(sf, -12);
      // Curved stone vault ceiling
      this._gradV(g, 0, 0, lw, H * 0.15, 0x141e24, 0x1e2c34, 6);
      for (let x = 0; x < lw; x += 240) {
        g.fillStyle(0x1a2630, 0.6);
        g.fillRect(x, 0, 6, H * 0.15);
      }
      // Weapon racks (swords, spears, shields)
      for (let x = 30; x < lw; x += 440) {
        // Rack beam
        g.fillStyle(0x2e3840, 0.9);
        g.fillRect(x, H * 0.15, 280, 8);
        // Swords hanging
        for (let k = 0; k < 6; k++) {
          const kx = x + 22 + k * 44;
          // Sword hilt
          g.fillStyle(this.acc, 0.55);
          g.fillRect(kx - 8, H * 0.16, 16, 5);
          g.fillStyle(0x4a5a6a, 0.70);
          g.fillRect(kx - 2, H * 0.21, 4, H * 0.36);
          // Blade glint
          g.fillStyle(0xc0c0c0, 0.55);
          g.fillRect(kx - 1, H * 0.22, 2, H * 0.34);
          g.fillStyle(0xffffff, 0.14);
          g.fillRect(kx, H * 0.22, 1, H * 0.30);
        }
        // Shields mounted on wall
        for (let k = 0; k < 4; k++) {
          const sx = x + 300 + k * 65;
          // Shield body
          g.fillStyle(0x2e3840, 0.9);
          g.fillRect(sx - 22, H * 0.20, 44, 52);
          g.fillTriangle(sx - 22, H * 0.20 + 52, sx + 22, H * 0.20 + 52, sx, H * 0.20 + 70);
          // Shield emblem
          g.fillStyle(this.acc, 0.35);
          g.fillCircle(sx, H * 0.20 + 26, 12);
          g.fillStyle(this.acc, 0.20);
          g.fillRect(sx - 14, H * 0.20 + 22, 28, 4);
          g.fillRect(sx - 2, H * 0.20 + 14, 4, 20);
          // Boss stud
          g.fillStyle(this.acc, 0.55);
          g.fillCircle(sx, H * 0.20 + 26, 5);
        }
      }
      // Battle banners
      for (let x = 180; x < lw; x += 440) {
        // Pole
        g.fillStyle(0x4a5a6a, 0.8);
        g.fillRect(x + 220 - 3, H * 0.03, 6, H * 0.55);
        // Banner cloth
        g.fillStyle(0x8b0000, 0.65);
        g.fillRect(x + 220, H * 0.04, 70, H * 0.42);
        // Banner edge serration
        for (let by = H * 0.04; by < H * 0.04 + H * 0.42; by += 20) {
          g.fillStyle(this.acc, 0.20);
          g.fillRect(x + 220, by, 70, 4);
        }
        // Emblem
        g.fillStyle(this.acc, 0.45);
        g.fillCircle(x + 220 + 35, H * 0.18, 20);
        g.fillStyle(0x8b0000, 0.7);
        g.fillCircle(x + 220 + 35, H * 0.18, 12);
        g.fillStyle(this.acc, 0.40);
        g.fillRect(x + 220 + 33, H * 0.12, 4, 24);
        g.fillRect(x + 220 + 27, H * 0.17, 16, 4);
      }
      // Stone floor
      this._stoneWall(g, 0, H * 0.82, lw, H * 0.18, 0x1e2a30, 0x0e1418, 30, 90, 0.92);
    }

    // Layer D — near: iron torch brackets + portcullis shadows (sf 0.57)
    {
      const sf = 0.57, lw = this._lw(sf);
      const g = this._gfx(sf, -11);
      // Iron torch brackets
      for (let x = 100; x < lw; x += 480) {
        this._wallLamp(g, x, H * 0.25, 0x2e3840, 0xff7722);
      }
      for (let x = 360; x < lw; x += 480) {
        this._wallLamp(g, x, H * 0.55, 0x2e3840, 0xff7722);
      }
      // Portcullis shadow bars
      for (let x = 0; x < lw; x += 560) {
        g.fillStyle(0x0a0d10, 0.25);
        g.fillRect(x, 0, 10, H * 0.82);
      }
      g.fillStyle(0x0a0d10, 0.88);
      g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // Layer E — torch fire glow shafts (sf 0.20)
    {
      const sf = 0.20, lw = this._lw(sf);
      const g = this._gfx(sf, -10);
      for (let x = 140; x < lw; x += 480) {
        g.fillStyle(0xff7722, 0.04);
        g.fillTriangle(x - 22, H * 0.28, x + 22, H * 0.28, x + 35, H * 0.82);
        g.fillStyle(0xff9944, 0.025);
        g.fillTriangle(x - 40, H * 0.28, x + 40, H * 0.28, x + 55, H * 0.92);
      }
    }
  }

  // ── 7  Art Gallery ───────────────────────────────────────
  _artGallery() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#120008');

    // Layer A — deep maroon void (sf 0.06)
    {
      const sf = 0.06, lw = this._lw(sf);
      const g = this._gfx(sf, -14);
      this._gradV(g, 0, 0, lw, H, 0x0e0006, 0x200010, 20);
    }

    // Layer B — distant long gallery with paintings (sf 0.16)
    {
      const sf = 0.16, lw = this._lw(sf);
      const g = this._gfx(sf, -13);
      // Wall
      this._gradV(g, 0, H * 0.05, lw, H * 0.78, 0x1c0010, 0x280018, 10);
      // Picture rail molding
      g.fillStyle(this.acc, 0.18);
      g.fillRect(0, H * 0.10, lw, 6);
      // Far paintings (simplified rectangles)
      for (let x = 30; x < lw; x += 260) {
        const pw = 100 + this._h(x, 0) * 80;
        const ph = 80 + this._h(x, 1) * 70;
        // Frame
        g.fillStyle(this.acc, 0.35);
        g.fillRect(x, H * 0.14, pw + 10, ph + 10);
        // Canvas
        const baseHue = this._h(x, 2);
        const cc = baseHue < 0.33 ? 0x8b3020 : baseHue < 0.66 ? 0x1e4a6a : 0x3a5a2a;
        g.fillStyle(cc, 0.55);
        g.fillRect(x + 5, H * 0.14 + 5, pw, ph);
        // Highlight
        g.fillStyle(0xffffff, 0.04);
        g.fillRect(x + 7, H * 0.14 + 7, pw * 0.4, ph);
      }
      this._gradV(g, 0, H * 0.80, lw, H * 0.20, 0x1c0010, 0x0e0006, 6);
    }

    // Layer C — mid gallery: large masterwork paintings + pedestals (sf 0.34)
    {
      const sf = 0.34, lw = this._lw(sf);
      const g = this._gfx(sf, -12);
      // Coffered ceiling with rosettes
      this._gradV(g, 0, 0, lw, H * 0.12, 0x1c0012, 0x2e001e, 6);
      for (let x = 60; x < lw; x += 180) {
        g.fillStyle(this.acc, 0.10);
        g.fillCircle(x, H * 0.06, 15);
        g.lineStyle(1, this.acc, 0.08);
        g.lineBetween(x, H * 0.0, x, H * 0.12);
        g.lineBetween(x - 90, H * 0.06, x + 90, H * 0.06);
      }
      // Large ornate-framed paintings
      for (let x = 0; x < lw; x += 460) {
        const pw = 200, ph = 140;
        const px = x + 30, py = H * 0.14;
        // Elaborate gold frame (4 layers of molding)
        g.fillStyle(this._lighten(this.acc, 0.3), 0.65);
        g.fillRect(px - 16, py - 16, pw + 32, ph + 32);
        g.fillStyle(this.acc, 0.80);
        g.fillRect(px - 10, py - 10, pw + 20, ph + 20);
        g.fillStyle(this._darken(this.acc, 0.3), 0.70);
        g.fillRect(px - 5, py - 5, pw + 10, ph + 10);
        // Frame corner rosettes
        for (const [fx, fy] of [[px - 10, py - 10],[px + pw + 10, py - 10],[px - 10, py + ph + 10],[px + pw + 10, py + ph + 10]]) {
          g.fillStyle(this._lighten(this.acc, 0.5), 0.80);
          g.fillCircle(fx, fy, 8);
        }
        // Canvas (color-field painting)
        const palette = [0x8b2020, 0x4a2060, 0x1e4060, 0x3a6020, 0x8b5020];
        const mainCol = palette[Math.floor(this._h(x, 5) * palette.length)];
        g.fillStyle(mainCol, 0.70);
        g.fillRect(px, py, pw, ph);
        // Painted subject (abstract shape)
        g.fillStyle(this._lighten(mainCol, 0.3), 0.35);
        g.fillEllipse(px + pw * 0.5, py + ph * 0.45, pw * 0.55, ph * 0.60);
        // Light glare on varnish
        g.fillStyle(0xffffff, 0.05);
        g.fillRect(px + 8, py + 8, pw * 0.25, ph - 16);
        // Spotlight cone
        g.fillStyle(0xfff5c0, 0.04);
        g.fillTriangle(px + pw / 2 - 15, 0, px + pw / 2 + 15, 0, px + pw / 2 + 30, py);
      }
      // Marble pedestals with sculptures
      for (let x = 280; x < lw; x += 460) {
        // Pedestal
        g.fillStyle(0x3a2028, 0.85);
        g.fillRect(x - 28, H * 0.54, 56, H * 0.28);
        g.fillRect(x - 35, H * 0.78, 70, 8);
        g.fillRect(x - 35, H * 0.52, 70, 8);
        // Abstract sculpture
        g.fillStyle(0xc0a0a8, 0.60);
        g.fillEllipse(x, H * 0.46, 44, 55);
        g.fillCircle(x, H * 0.36, 18);
        // Highlight
        g.fillStyle(0xffffff, 0.08);
        g.fillRect(x - 14, H * 0.35, 6, 60);
      }
      // Parquet with herringbone hint
      g.fillStyle(0x200010, 0.95);
      g.fillRect(0, H * 0.82, lw, H * 0.18);
      for (let x = 0; x < lw; x += 60) {
        g.fillStyle(0x380020, 0.25);
        g.fillRect(x, H * 0.82, 2, H * 0.18);
      }
      for (let y = H * 0.84; y < H; y += 28) {
        g.fillStyle(0x380020, 0.14);
        g.fillRect(0, y, lw, 2);
      }
    }

    // Layer D — near: ornate columns + track lighting (sf 0.57)
    {
      const sf = 0.57, lw = this._lw(sf);
      const g = this._gfx(sf, -11);
      for (let x = 200; x < lw; x += 540) {
        this._ornateCol(g, x, H * 0.06, H * 0.76, 18, 0x200010, 0x800020, 0.95);
        g.fillStyle(this.acc, 0.06);
        g.fillCircle(x, H * 0.07, 50);
      }
      // Gallery track lighting bar
      g.fillStyle(0x2e1a18, 0.80);
      g.fillRect(0, H * 0.06, lw, 8);
      // Track lights
      for (let x = 80; x < lw; x += 200) {
        g.fillStyle(0x3a2020, 0.9);
        g.fillEllipse(x, H * 0.07, 20, 14);
        g.fillStyle(0xfff5c0, 0.25);
        g.fillCircle(x, H * 0.08, 5);
        g.fillStyle(0xfff5c0, 0.06);
        g.fillTriangle(x - 18, H * 0.09, x + 18, H * 0.09, x + 25, H * 0.50);
      }
      g.fillStyle(0x0e0006, 0.88);
      g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // Layer E — gallery spotlights (sf 0.20)
    {
      const sf = 0.20, lw = this._lw(sf);
      const g = this._gfx(sf, -10);
      for (let x = 130; x < lw; x += 460) {
        g.fillStyle(0xfff5c0, 0.04);
        g.fillTriangle(x - 20, H * 0.07, x + 20, H * 0.07, x + 32, H * 0.55);
        g.fillStyle(0xfff5c0, 0.022);
        g.fillTriangle(x - 45, H * 0.07, x + 45, H * 0.07, x + 60, H * 0.65);
      }
    }
  }

  // ── 8  Treasure Vault ────────────────────────────────────
  _treasureVault() {
    const { scene, W, H } = this;
    scene.cameras.main.setBackgroundColor('#050510');

    // Layer A — deep dark near-black with golden underglow (sf 0.06)
    {
      const sf = 0.06, lw = this._lw(sf);
      const g = this._gfx(sf, -14);
      this._gradV(g, 0, 0, lw, H, 0x050510, 0x0f0f20, 20);
      // Distant gold glow pools
      for (let x = 400; x < lw; x += 800) {
        g.fillStyle(0xffd700, 0.07);
        g.fillCircle(x, H * 0.75, 250);
      }
    }

    // Layer B — far vault interior: stacked chests + archways (sf 0.16)
    {
      const sf = 0.16, lw = this._lw(sf);
      const g = this._gfx(sf, -13);
      this._stoneWall(g, 0, H * 0.05, lw, H * 0.76, 0x0f0f1e, 0x070710, 60, 150, 0.88);
      // Distant stacked treasure chests
      for (let x = 0; x < lw; x += 300) {
        for (let row = 0; row < 3; row++) {
          const cy = H * 0.65 - row * 52;
          g.fillStyle(0x2a1e00, 0.80);
          g.fillRect(x + 40, cy, 90, 44);
          // Chest lid
          g.fillStyle(0x3d2c00, 0.75);
          g.fillRect(x + 40, cy, 90, 12);
          // Gold bands
          g.fillStyle(this.acc, 0.25);
          g.fillRect(x + 40, cy + 6, 90, 4);
          g.fillRect(x + 80, cy, 6, 44);
          // Keyhole
          g.fillStyle(0xffd700, 0.35);
          g.fillCircle(x + 84, cy + 22, 4);
        }
      }
      this._gradV(g, 0, H * 0.80, lw, H * 0.20, 0x1a1600, 0x050510, 6);
    }

    // Layer C — mid vault: gem-encrusted walls + coin piles (sf 0.34)
    {
      const sf = 0.34, lw = this._lw(sf);
      const g = this._gfx(sf, -12);
      // Ceiling vault ribs
      this._gradV(g, 0, 0, lw, H * 0.13, 0x0f0f1e, 0x1a1a30, 6);
      for (let x = 0; x < lw; x += 220) {
        g.fillStyle(0x1a1a30, 0.65);
        g.fillRect(x, 0, 5, H * 0.13);
        g.fillStyle(this.acc, 0.08);
        g.fillCircle(x + 110, H * 0.03, 10);
      }
      // Gem-studded wall panel sections
      for (let x = 0; x < lw; x += 500) {
        // Dark wall section
        g.fillStyle(0x0d0d20, 0.90);
        g.fillRect(x, H * 0.12, 400, H * 0.60);
        // Scattered gems
        const gemCols = [0xff4444, 0x44ff88, 0x4488ff, 0xffd700, 0xff88ff];
        for (let i = 0; i < 18; i++) {
          const gx = x + 15 + this._h(i, x) * 370;
          const gy = H * 0.15 + this._h(i + 1, x) * H * 0.54;
          const gc = gemCols[Math.floor(this._h(i * 3, x) * gemCols.length)];
          const gr = 4 + this._h(i, x + 1) * 8;
          // Gem body
          g.fillStyle(gc, 0.55);
          g.fillDiamond(gx, gy, gr * 0.8, gr);
          // Gem facet highlight
          g.fillStyle(0xffffff, 0.25);
          g.fillDiamond(gx - gr * 0.15, gy - gr * 0.2, gr * 0.25, gr * 0.35);
          // Glow halo
          g.fillStyle(gc, 0.08);
          g.fillCircle(gx, gy, gr * 2.5);
        }
      }
      // Gold coin piles on floor
      for (let x = 80; x < lw; x += 240) {
        const pileH = 20 + this._h(x, 7) * 40;
        const pileW = 60 + this._h(x, 8) * 80;
        // Pile base ellipse
        g.fillStyle(this.acc, 0.28);
        g.fillEllipse(x + pileW / 2, H * 0.80, pileW, pileH * 0.6);
        // Individual coin glints
        for (let ci = 0; ci < 8; ci++) {
          const cx2 = x + 8 + this._h(ci, x) * (pileW - 16);
          const cy = H * 0.75 - this._h(ci + 1, x) * pileH * 0.7;
          g.fillStyle(this.acc, 0.50);
          g.fillEllipse(cx2, cy, 14, 8);
          g.fillStyle(0xffffff, 0.15);
          g.fillEllipse(cx2 - 2, cy - 1, 6, 3);
        }
      }
      // Vault door sections on walls
      for (let x = 350; x < lw; x += 500) {
        // Door frame
        g.fillStyle(0x2a2a40, 0.90);
        g.fillRect(x, H * 0.18, 110, H * 0.60);
        g.fillStyle(0x3a3a50, 0.70);
        g.fillRect(x + 4, H * 0.20, 102, H * 0.56);
        // Locking mechanism
        g.fillStyle(this.acc, 0.45);
        for (let ly = H * 0.25; ly < H * 0.70; ly += 50) {
          g.fillCircle(x + 20, ly, 10);
          g.fillCircle(x + 90, ly, 10);
        }
        // Handle
        g.fillStyle(this.acc, 0.60);
        g.fillCircle(x + 55, H * 0.48, 16);
        g.fillStyle(0x0f0f1e, 0.7);
        g.fillCircle(x + 55, H * 0.48, 8);
      }
      // Floor (dark stone with gold sheen)
      this._gradV(g, 0, H * 0.82, lw, H * 0.18, 0x1a1600, 0x050510, 6);
      for (let x = 0; x < lw; x += 100) {
        g.fillStyle(this.acc, 0.05);
        g.fillRect(x, H * 0.82, 2, H * 0.18);
      }
    }

    // Layer D — near: candelabras + gem-glint particles (sf 0.57)
    {
      const sf = 0.57, lw = this._lw(sf);
      const g = this._gfx(sf, -11);
      for (let x = 160; x < lw; x += 560) {
        // Candelabra
        g.fillStyle(this.acc, 0.55);
        g.fillRect(x - 3, H * 0.40, 6, H * 0.42);
        g.fillRect(x - 18, H * 0.82, 36, 7);
        g.fillRect(x - 22, H * 0.40, 44, 7);
        // 3 candle branches
        for (let ci = -1; ci <= 1; ci++) {
          const cx2 = x + ci * 18;
          g.fillStyle(0xfff5e0, 0.70);
          g.fillRect(cx2 - 3, H * 0.26, 6, H * 0.14);
          g.fillStyle(0xffcc00, 0.55);
          g.fillCircle(cx2, H * 0.25, 6);
          g.fillStyle(0xffcc00, 0.14);
          g.fillCircle(cx2, H * 0.25, 20);
        }
      }
      // Floating gem sparkle particles
      for (let i = 0; i < 40; i++) {
        const px = this._h(i, 9) * lw;
        const py = H * 0.10 + this._h(i, 10) * H * 0.72;
        const gemCols2 = [0xff6666, 0x66ff99, 0x6699ff, 0xffd700, 0xff99ff];
        g.fillStyle(gemCols2[i % gemCols2.length], 0.30);
        g.fillCircle(px, py, 3);
        g.fillStyle(0xffffff, 0.18);
        g.fillCircle(px, py, 1);
      }
      g.fillStyle(0x050510, 0.88);
      g.fillRect(0, H * 0.83, lw, H * 0.17);
    }

    // Layer E — golden light rays from coin piles (sf 0.20)
    {
      const sf = 0.20, lw = this._lw(sf);
      const g = this._gfx(sf, -10);
      for (let x = 200; x < lw; x += 500) {
        g.fillStyle(0xffd700, 0.05);
        g.fillTriangle(x - 35, H * 0.80, x + 35, H * 0.80, x - 20, 0);
        g.fillTriangle(x - 10, H * 0.80, x + 10, H * 0.80, x + 5, 0);
        g.fillStyle(0xffd700, 0.025);
        g.fillTriangle(x - 60, H * 0.82, x + 60, H * 0.82, x - 40, 0);
      }
    }
  }
}
