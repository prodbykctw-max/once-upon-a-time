/**
 * BackgroundBuilder — hand-painted architectural parallax backgrounds.
 * Uses the native HTML5 Canvas 2D API (fast native C++) baked into Phaser
 * textures, replacing the previous Phaser.Graphics approach which was too
 * slow on mobile due to JS command-buffer overhead.
 *
 * Six scroll-factor layers per stage (0.05 → 0.72). Each layer is painted
 * onto an HTMLCanvasElement then registered as a static Phaser texture.
 */
import Phaser from 'phaser';

export class BackgroundBuilder {
  constructor(scene, W, H, stageIndex) {
    this.scene = scene;
    this.W     = W;
    this.H     = H;
    this.idx   = stageIndex;
    const lv   = scene.level;
    this.prim  = Phaser.Display.Color.HexStringToColor(lv.primaryColor).color;
    this.acc   = Phaser.Display.Color.HexStringToColor(lv.accentColor).color;
    this.VW    = scene.scale.width || 1280;
    this._lineW = 1; this._lineCol = '#fff'; this._lineA = 1;
    this._keyIndex = 0;
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

  // ─── layer management ──────────────────────────────────────────────────────

  _lw(sf) { return Math.ceil(this.VW + (this.W - this.VW) * sf) + 128; }

  _beginLayer(sf, depth) {
    const lw  = this._lw(sf);
    const cvs = document.createElement('canvas');
    cvs.width = lw; cvs.height = this.H;
    const ctx = cvs.getContext('2d');
    return { ctx, lw, cvs, sf, depth };
  }

  _commit({ cvs, sf, depth }) {
    const key = `_bg_${this.idx}_${this._keyIndex++}`;
    if (this.scene.textures.exists(key)) this.scene.textures.remove(key);
    this.scene.textures.addCanvas(key, cvs);
    this.scene.add.image(0, 0, key)
      .setOrigin(0).setScrollFactor(sf).setDepth(depth);
  }

  // ─── colour helpers ────────────────────────────────────────────────────────

  _css(col, alpha = 1) {
    const r = (col >> 16) & 0xff, g = (col >> 8) & 0xff, b = col & 0xff;
    return alpha >= 1 ? `rgb(${r},${g},${b})` : `rgba(${r},${g},${b},${alpha.toFixed(3)})`;
  }

  _h(a, b = 0) {
    return ((a * 1664525 + b * 1013904223 + 22695477) & 0x7fffffff) / 0x7fffffff;
  }

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

  // ─── canvas drawing helpers ────────────────────────────────────────────────

  _gradV(ctx, x, y, w, h, cA, cB) {
    const grd = ctx.createLinearGradient(x, y, x, y + h);
    grd.addColorStop(0, this._css(cA));
    grd.addColorStop(1, this._css(cB));
    ctx.fillStyle = grd;
    ctx.fillRect(x, y, w, h);
  }

  // Painted gradient: adds mid-tone stops for depth (still one draw call)
  _gradVP(ctx, x, y, w, h, cA, cB) {
    const grd = ctx.createLinearGradient(x, y, x, y + h);
    grd.addColorStop(0,    this._css(cA));
    grd.addColorStop(0.45, this._css(this._lerp(cA, cB, 0.4)));
    grd.addColorStop(1,    this._css(cB));
    ctx.fillStyle = grd;
    ctx.fillRect(x, y, w, h);
  }

  _circle(ctx, cx, cy, r) {
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
  }

  _ellipse(ctx, cx, cy, rw, rh) {
    ctx.beginPath(); ctx.ellipse(cx, cy, rw, rh, 0, 0, Math.PI * 2); ctx.fill();
  }

  _tri(ctx, x1, y1, x2, y2, x3, y3) {
    ctx.beginPath();
    ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.lineTo(x3, y3);
    ctx.closePath(); ctx.fill();
  }

  _pts(ctx, pts) {
    if (!pts.length) return;
    ctx.beginPath(); ctx.moveTo(pts[0].x, pts[0].y);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i].x, pts[i].y);
    ctx.closePath(); ctx.fill();
  }

  _line(ctx, x1, y1, x2, y2, w, col, alpha = 1) {
    ctx.strokeStyle = this._css(col, alpha);
    ctx.lineWidth   = w;
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
  }

  // ─── architectural helpers ─────────────────────────────────────────────────

  _arcPts(cx, cy, r, a0, a1, steps = 14) {
    const pts = [];
    for (let i = 0; i <= steps; i++) {
      const a = a0 + (a1 - a0) * (i / steps);
      pts.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
    }
    return pts;
  }

  _gothicArch(ctx, cx, baseY, w, h, col, alpha = 1) {
    const hw = w / 2, spring = baseY - h * 0.42, r = hw * 1.05;
    const pts = [
      { x: cx - hw, y: baseY }, { x: cx - hw, y: spring },
      ...this._arcPts(cx - hw + r, spring, r, Math.PI, Math.PI * 1.5, 14),
      ...this._arcPts(cx + hw - r, spring, r, Math.PI * 1.5, Math.PI * 2, 14),
      { x: cx + hw, y: spring }, { x: cx + hw, y: baseY },
    ];
    ctx.fillStyle = this._css(col, alpha); this._pts(ctx, pts);
  }

  _roundArch(ctx, cx, baseY, w, h, col, alpha = 1) {
    const hw = w / 2;
    const pts = [
      { x: cx - hw, y: baseY }, { x: cx - hw, y: baseY - h * 0.5 },
      ...this._arcPts(cx, baseY - h * 0.5, hw, Math.PI, 0, 16),
      { x: cx + hw, y: baseY - h * 0.5 }, { x: cx + hw, y: baseY },
    ];
    ctx.fillStyle = this._css(col, alpha); this._pts(ctx, pts);
  }

  _gem(ctx, cx, cy, rx, ry, col, alpha = 1) {
    ctx.fillStyle = this._css(col, alpha);
    this._pts(ctx, [
      { x: cx,           y: cy - ry         },
      { x: cx + rx,      y: cy              },
      { x: cx + rx*0.7,  y: cy + ry * 0.8   },
      { x: cx,           y: cy + ry         },
      { x: cx - rx*0.7,  y: cy + ry * 0.8   },
      { x: cx - rx,      y: cy              },
    ]);
    ctx.fillStyle = `rgba(255,255,255,${(alpha * 0.28).toFixed(3)})`;
    this._pts(ctx, [
      { x: cx,           y: cy - ry         },
      { x: cx + rx*0.5,  y: cy - ry * 0.2   },
      { x: cx + rx*0.3,  y: cy + ry * 0.3   },
      { x: cx - rx*0.2,  y: cy - ry * 0.1   },
    ]);
  }

  _stoneWall(ctx, x, y, w, h, stoneCol, mortarCol, bh = 48, bw = 120, alpha = 1) {
    ctx.fillStyle = this._css(stoneCol, alpha); ctx.fillRect(x, y, w, h);
    ctx.fillStyle = this._css(mortarCol, alpha * 0.55);
    for (let row = 0; row * bh < h + bh; row++) {
      ctx.fillRect(x, y + row * bh, w, 3);
      const off = (row % 2) * (bw / 2);
      for (let col2 = 0; col2 * bw < w + bw; col2++) {
        ctx.fillRect(x + col2 * bw + off - bw / 2, y + row * bh, 3, bh);
      }
    }
  }

  _books(ctx, x, y, w, h, nShelves, seed = 0, stride = 1) {
    const shH = h / nShelves, step = 12 * stride;
    for (let s = 0; s < nShelves; s++) {
      const ty = y + s * shH;
      ctx.fillStyle = this._css(this._darken(this.prim, 0.25), 0.88);
      ctx.fillRect(x, ty + shH - 5, w, 6);
      for (let bx = x + 3; bx < x + w - 3; bx += step) {
        const bh2  = shH * 0.38 + this._h(bx, seed + s) * shH * 0.50;
        const shd  = this._h(bx * 3, seed + s * 7);
        const bc   = shd < 0.28 ? this.acc
                   : shd < 0.52 ? this._lerp(this.acc, this.prim, 0.5)
                   : shd < 0.76 ? this.prim
                   : this._darken(this.prim, 0.40);
        ctx.fillStyle = this._css(bc, 0.72);
        ctx.fillRect(bx, ty + shH - 5 - bh2, 10, bh2);
        ctx.fillStyle = 'rgba(255,255,255,0.055)';
        ctx.fillRect(bx + 1, ty + shH - 5 - bh2 + 4, 2, bh2 - 8);
      }
    }
  }

  _ornateCol(ctx, cx, y, colH, r, dark, light, alpha = 1) {
    const nF = 8;
    for (let i = 0; i < nF; i++) {
      ctx.fillStyle = this._css(i % 2 === 0 ? dark : this._lerp(dark, light, 0.42), alpha * 0.93);
      ctx.fillRect(cx - r + (r * 2 / nF) * i, y, r * 2 / nF + 1, colH);
    }
    ctx.fillStyle = this._css(light, alpha);
    ctx.fillRect(cx - r * 1.7, y - 12, r * 3.4, 12);
    ctx.fillRect(cx - r * 1.3, y - 22, r * 2.6, 10);
    ctx.fillRect(cx - r * 2.0, y - 30, r * 4.0, 8);
    ctx.fillStyle = this._css(light, alpha * 0.88);
    ctx.fillRect(cx - r * 1.3, y + colH,      r * 2.6, 10);
    ctx.fillRect(cx - r * 1.7, y + colH + 10, r * 3.4, 10);
    ctx.fillRect(cx - r * 2.0, y + colH + 20, r * 4.0, 7);
  }

  _lotusCol(ctx, cx, y, colH, r, stone, gold, alpha = 1) {
    ctx.fillStyle = this._css(stone, alpha * 0.90); ctx.fillRect(cx - r, y, r * 2, colH);
    ctx.fillStyle = this._css(gold, alpha * 0.17);
    for (let gy = y + 22; gy < y + colH; gy += 58) ctx.fillRect(cx - r, gy, r * 2, 9);
    ctx.fillStyle = this._css(gold, alpha * 0.82); ctx.fillRect(cx - r * 1.6, y - 9, r * 3.2, 9);
    ctx.fillStyle = this._css(this._lerp(gold, 0xffffff, 0.18), alpha * 0.55);
    for (let i = -2; i <= 2; i++)
      this._tri(ctx, cx + i * r * 0.55, y - 9, cx + (i - 0.5) * r * 0.55, y - 30, cx + (i + 0.5) * r * 0.55, y - 30);
    ctx.fillStyle = this._css(stone, alpha * 0.80);
    ctx.fillRect(cx - r * 1.4, y + colH, r * 2.8, 10);
    ctx.fillRect(cx - r * 1.7, y + colH + 10, r * 3.4, 9);
  }

  _lamp(ctx, cx, cy, poleCol, glowCol) {
    ctx.fillStyle = this._css(poleCol, 0.88);
    ctx.fillRect(cx, cy, 3, 50); ctx.fillRect(cx - 24, cy + 14, 24, 3);
    ctx.fillRect(cx - 32, cy + 5, 18, 22);
    this._tri(ctx, cx - 32, cy + 27, cx - 14, cy + 27, cx - 23, cy + 40);
    ctx.fillStyle = this._css(glowCol, 0.22); this._circle(ctx, cx - 23, cy + 15, 30);
    ctx.fillStyle = this._css(glowCol, 0.40); this._circle(ctx, cx - 23, cy + 15, 11);
    ctx.fillStyle = this._css(glowCol, 0.055); this._ellipse(ctx, cx - 23, cy + 85, 55, 17.5);
  }

  _chandelier(ctx, cx, ty, col, glowCol, arms = 6, radius = 90) {
    ctx.fillStyle = this._css(col, 0.72); ctx.fillRect(cx - 2, ty, 4, 32);
    ctx.fillStyle = this._css(col, 0.90); this._ellipse(ctx, cx, ty + 32, 16, 10);
    for (let i = 0; i < arms; i++) {
      const angle = (i / arms) * Math.PI * 2 - Math.PI / 2;
      const ex = cx + Math.cos(angle) * radius;
      const ey = ty + 42 + Math.sin(angle) * radius * 0.22;
      this._line(ctx, cx, ty + 40, ex, ey, 2, col, 0.68);
      ctx.fillStyle = '#fff5c0'; ctx.globalAlpha = 0.62;
      ctx.fillRect(ex - 3, ey - 16, 6, 16);
      ctx.globalAlpha = 1;
      ctx.fillStyle = this._css(glowCol, 0.48); this._circle(ctx, ex, ey - 18, 6);
      ctx.fillStyle = this._css(glowCol, 0.13); this._circle(ctx, ex, ey - 14, 22);
    }
    ctx.fillStyle = this._css(glowCol, 0.055); this._circle(ctx, cx, ty + 42, radius * 2.2);
  }

  _tornPage(ctx, cx, cy, size, col, alpha = 1) {
    const s = size;
    ctx.fillStyle = this._css(col, alpha * 0.55);
    this._pts(ctx, [
      { x: cx - s,        y: cy - s * 1.4 },
      { x: cx + s * 0.9,  y: cy - s * 1.3 },
      { x: cx + s,        y: cy + s * 1.2 },
      { x: cx - s * 0.85, y: cy + s * 1.4 },
    ]);
    ctx.fillStyle = this._css(col, alpha * 0.14);
    for (let ly = cy - s + 5; ly < cy + s; ly += 12) {
      ctx.fillRect(cx - s * 0.8, ly, s * 1.5 * (0.5 + this._h(cx, ly) * 0.5), 2);
    }
  }

  _star(ctx, cx, cy, r, col, alpha = 1) {
    ctx.fillStyle = this._css(col, alpha);
    this._pts(ctx, [
      { x: cx,           y: cy - r          },
      { x: cx + r * 0.2, y: cy - r * 0.2   },
      { x: cx + r,       y: cy             },
      { x: cx + r * 0.2, y: cy + r * 0.2   },
      { x: cx,           y: cy + r          },
      { x: cx - r * 0.2, y: cy + r * 0.2   },
      { x: cx - r,       y: cy             },
      { x: cx - r * 0.2, y: cy - r * 0.2   },
    ]);
  }

  _neonBar(ctx, x, y, w, h, col, alpha = 1) {
    ctx.fillStyle = this._css(col, alpha);      ctx.fillRect(x, y, w, h);
    ctx.fillStyle = this._css(col, alpha * 0.18); ctx.fillRect(x - 4, y - 4, w + 8, h + 8);
    ctx.fillStyle = this._css(col, alpha * 0.07); ctx.fillRect(x - 10, y - 10, w + 20, h + 20);
  }

  _vignette() {
    const { scene } = this;
    const sw = scene.scale.width, sh = scene.scale.height;
    const layer = this._beginLayer(0, -1);
    const ctx   = layer.ctx;
    layer.cvs.width = sw; layer.cvs.height = sh;
    ctx.fillStyle = 'rgba(0,0,0,0.46)';
    ctx.fillRect(0, 0, sw, 74); ctx.fillRect(0, sh - 74, sw, 74);
    for (let i = 0; i < 7; i++) {
      ctx.fillStyle = `rgba(0,0,0,${(0.26 * (1 - i / 7)).toFixed(3)})`;
      ctx.fillRect(0,              74, (i + 1) * 18, sh - 148);
      ctx.fillRect(sw-(i+1)*18,   74, (i + 1) * 18, sh - 148);
    }
    // Global dark tint over entire screen
    ctx.fillStyle = 'rgba(0,0,0,0.30)';
    ctx.fillRect(0, 0, sw, sh);
    this._commit(layer);
  }

  // ─── Stage 0 — The Grand Library ──────────────────────────────────────────
  _grandLibrary() {
    const { H } = this;
    this.scene.cameras.main.setBackgroundColor('#0e0600');

    // A: ember-warm deep void (sf 0.05)
    { const L = this._beginLayer(0.05, -16), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H, 0x0e0500, 0x241000);
      ctx.fillStyle = 'rgba(139,69,19,0.07)';
      for (let x = 500; x < lw; x += 900) this._circle(ctx, x, H * 0.70, 260);
      this._commit(L);
    }

    // B: distant vaulted hall — gothic arches + dark receding shelves (sf 0.15)
    { const L = this._beginLayer(0.15, -15), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H * 0.24, 0x120700, 0x1f0d00);
      for (let x = 0; x < lw; x += 400) {
        ctx.fillStyle = this._css(0x1a0a00, 0.96); ctx.fillRect(x, 0, 26, H * 0.84);
        this._gothicArch(ctx, x + 213, H * 0.84, 348, H * 0.82, 0x120700, 0.92);
        ctx.fillStyle = this._css(0xd4af37, 0.07); this._circle(ctx, x + 213, H * 0.03, 22);
      }
      for (let x = 28; x < lw; x += 220) {
        ctx.fillStyle = this._css(0x180900, 0.88); ctx.fillRect(x, H * 0.09, 194, H * 0.73);
        this._books(ctx, x + 4, H * 0.09, 186, H * 0.73, 4, x, 3);
      }
      this._gradVP(ctx, 0, H * 0.82, lw, H * 0.18, 0x180900, 0x0e0500);
      this._commit(L);
    }

    // C: vault rib tracery + mid bookshelves (sf 0.32)
    { const L = this._beginLayer(0.32, -14), { ctx, lw } = L;
      for (let x = 0; x < lw; x += 280) {
        this._line(ctx, x, 0, x + 140, H * 0.17, 3, 0xd4af37, 0.12);
        this._line(ctx, x + 280, 0, x + 140, H * 0.17, 3, 0xd4af37, 0.12);
        ctx.fillStyle = this._css(0xd4af37, 0.08); this._circle(ctx, x + 140, H * 0.04, 11);
      }
      for (let x = 0; x < lw; x += 264) {
        ctx.fillStyle = this._css(0x3b1a05, 0.94);
        ctx.fillRect(x, H * 0.07, 7, H * 0.74);
        ctx.fillRect(x + 257, H * 0.07, 7, H * 0.74);
        ctx.fillRect(x, H * 0.07, 264, 7);
        ctx.fillStyle = this._css(0x2a0f00, 0.92); ctx.fillRect(x + 7, H * 0.08, 250, H * 0.73);
        this._books(ctx, x + 10, H * 0.10, 244, H * 0.70, 5, x * 3, 2);
      }
      ctx.fillStyle = this._css(0x1c0b00, 0.97); ctx.fillRect(0, H * 0.82, lw, H * 0.18);
      for (let x = 0; x < lw; x += 95) { ctx.fillStyle = this._css(0x2e1200, 0.32); ctx.fillRect(x, H * 0.82, 2, H * 0.18); }
      this._commit(L);
    }

    // D: ornate pillars + balcony rail + reading lamps (sf 0.56)
    { const L = this._beginLayer(0.56, -13), { ctx, lw } = L;
      for (let x = 260; x < lw; x += 528) {
        this._ornateCol(ctx, x, H * 0.05, H * 0.77, 22, 0x2a0f00, 0x5a2e08, 0.96);
        ctx.fillStyle = this._css(0xd4af37, 0.055); this._circle(ctx, x, H * 0.06, 60);
      }
      ctx.fillStyle = this._css(0x3b1a05, 0.92); ctx.fillRect(0, H * 0.52, lw, 10);
      for (let x = 20; x < lw; x += 47) {
        ctx.fillStyle = this._css(0x5a2e08, 0.80); ctx.fillRect(x, H * 0.52 + 10, 7, 68);
        ctx.fillStyle = this._css(this.acc, 0.13); this._circle(ctx, x + 3, H * 0.52 + 44, 4);
      }
      ctx.fillStyle = this._css(0x3b1a05, 0.88); ctx.fillRect(0, H * 0.52 + 78, lw, 10);
      for (let x = 110; x < lw; x += 528) this._lamp(ctx, x, H * 0.22, 0x5a2e08, 0xfff5c0);
      for (let x = 370; x < lw; x += 528) this._lamp(ctx, x, H * 0.60, 0x5a2e08, 0xfff5c0);
      this._commit(L);
    }

    // E: floating torn pages (sf 0.25)
    { const L = this._beginLayer(0.25, -12), { ctx, lw } = L;
      for (let i = 0; i < 22; i++) {
        const px = this._h(i, 1) * lw, py = H * 0.08 + this._h(i, 2) * H * 0.72;
        this._tornPage(ctx, px, py, 8 + this._h(i, 3) * 16, 0xf5e8d0, this._h(i, 4) * 0.20 + 0.06);
      }
      this._commit(L);
    }

    // F: golden light shafts + dust motes (sf 0.18)
    { const L = this._beginLayer(0.18, -11), { ctx, lw } = L;
      for (let x = 200; x < lw; x += 400) {
        ctx.fillStyle = 'rgba(212,175,55,0.038)';
        this._tri(ctx, x - 50, 0, x + 50, 0, x + 85, H * 0.72);
        ctx.fillStyle = 'rgba(255,245,192,0.022)';
        this._tri(ctx, x - 14, 0, x + 14, 0, x + 22, H * 0.62);
        for (let my = 30; my < H * 0.65; my += 50) {
          ctx.fillStyle = `rgba(255,245,192,0.032)`;
          this._circle(ctx, x + my * 0.07, my, 3 + this._h(x, my) * 3);
        }
      }
      this._commit(L);
    }
  }

  // ─── Stage 1 — Egyptian Hall ──────────────────────────────────────────────
  _egyptianHall() {
    const { H } = this;
    this.scene.cameras.main.setBackgroundColor('#140b00');

    { const L = this._beginLayer(0.05, -16), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H, 0x100800, 0x2c1900);
      this._commit(L);
    }

    { const L = this._beginLayer(0.15, -15), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H * 0.18, 0x140c00, 0x221200);
      ctx.fillStyle = this._css(0x1f1200, 0.88); ctx.fillRect(0, H * 0.04, lw, H * 0.77);
      ctx.fillStyle = this._css(this.acc, 0.07);
      for (let y = H * 0.06; y < H * 0.78; y += 62) ctx.fillRect(0, y, lw, 9);
      for (let x = 0; x < lw; x += 320) {
        ctx.fillStyle = this._css(0x2e1c00, 0.86); ctx.fillRect(x + 110, 0, 100, H * 0.80);
        ctx.fillStyle = this._css(this.acc, 0.08);
        for (let gy = 30; gy < H * 0.78; gy += 62) ctx.fillRect(x + 110, gy, 100, 9);
      }
      this._gradVP(ctx, 0, H * 0.80, lw, H * 0.20, 0x2a1600, 0x100800);
      this._commit(L);
    }

    { const L = this._beginLayer(0.33, -14), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H * 0.15, 0x1c1000, 0x2e1800);
      for (let x = 0; x < lw; x += 380) {
        this._lotusCol(ctx, x + 40,  H * 0.05, H * 0.76, 34, 0x3d2300, this.acc, 0.92);
        this._lotusCol(ctx, x + 340, H * 0.05, H * 0.76, 34, 0x3d2300, this.acc, 0.92);
      }
      for (let x = 78; x < lw; x += 380) {
        ctx.fillStyle = this._css(this.acc, 0.12);
        for (let gy = H * 0.08; gy < H * 0.72; gy += 55)
          for (let gx = x; gx < x + 240; gx += 26)
            if (this._h(gx, gy) > 0.40) ctx.fillRect(gx, gy, 20, 15);
        ctx.fillStyle = this._css(this.acc, 0.20);
        ctx.fillRect(x, H * 0.07, 240, 6); ctx.fillRect(x, H * 0.73, 240, 6);
      }
      this._gradVP(ctx, 0, H * 0.80, lw, H * 0.20, 0x3d2300, 0x1a1000);
      this._commit(L);
    }

    { const L = this._beginLayer(0.57, -13), { ctx, lw } = L;
      for (let x = 190; x < lw; x += 580) {
        ctx.fillStyle = this._css(0x2a1800, 0.93);
        ctx.fillRect(x - 32, H * 0.30, 64, H * 0.50);
        ctx.fillRect(x - 48, H * 0.54, 96, H * 0.26);
        this._circle(ctx, x, H * 0.28, 32);
        ctx.fillStyle = this._css(this.acc, 0.22);
        this._tri(ctx, x, H * 0.17, x - 24, H * 0.28, x + 24, H * 0.28);
        ctx.fillStyle = this._css(this.acc, 0.26); ctx.fillRect(x + 11, H * 0.34, 6, 44);
      }
      for (let x = 100; x < lw; x += 580) this._lamp(ctx, x, H * 0.28, 0x4a2800, 0xffaa44);
      for (let x = 400; x < lw; x += 580) this._lamp(ctx, x, H * 0.56, 0x4a2800, 0xffaa44);
      ctx.fillStyle = this._css(0x0e0800, 0.88); ctx.fillRect(0, H * 0.83, lw, H * 0.17);
      this._commit(L);
    }

    { const L = this._beginLayer(0.20, -12), { ctx, lw } = L;
      for (let i = 0; i < 18; i++)
        this._star(ctx, this._h(i,5)*lw, H*0.20+this._h(i,6)*H*0.50, 3+this._h(i,7)*5, 0xffcc44, this._h(i,8)*0.18+0.05);
      this._commit(L);
    }

    { const L = this._beginLayer(0.18, -11), { ctx, lw } = L;
      for (let x = 200; x < lw; x += 380) {
        ctx.fillStyle = 'rgba(212,175,55,0.048)';
        this._tri(ctx, x - 32, 0, x + 32, 0, x + 58, H * 0.82);
        ctx.fillStyle = 'rgba(255,215,0,0.026)';
        this._tri(ctx, x - 8, 0, x + 8, 0, x + 16, H * 0.76);
      }
      this._commit(L);
    }
  }

  // ─── Stage 2 — Samurai Gallery ────────────────────────────────────────────
  _samuraiGallery() {
    const { H } = this;
    this.scene.cameras.main.setBackgroundColor('#0d0000');

    { const L = this._beginLayer(0.05, -16), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H, 0x0a0000, 0x1c0600);
      for (let x = 700; x < lw; x += 1400) {
        ctx.fillStyle = 'rgba(255,245,224,0.065)'; this._circle(ctx, x, H * 0.11, 130);
        ctx.fillStyle = 'rgba(255,245,224,0.10)';  this._circle(ctx, x, H * 0.11, 55);
      }
      this._commit(L);
    }

    { const L = this._beginLayer(0.15, -15), { ctx, lw } = L;
      ctx.fillStyle = this._css(0x1a0800, 0.92); ctx.fillRect(0, 0, lw, H * 0.86);
      for (let x = 0; x < lw; x += 230) {
        for (let p = 0; p < 3; p++) {
          const px = x + p * 74;
          ctx.fillStyle = this._css(0x2c1600, 0.82); ctx.fillRect(px, H * 0.07, 70, H * 0.73);
          ctx.fillStyle = 'rgba(255,245,224,0.04)'; ctx.fillRect(px + 3, H * 0.09, 64, H * 0.69);
          ctx.fillStyle = this._css(0x1a0800, 0.50);
          for (let sy = H * 0.12; sy < H * 0.73; sy += 34) ctx.fillRect(px, sy, 70, 2);
          for (let sx = px + 22; sx < px + 70; sx += 22) ctx.fillRect(sx, H * 0.07, 2, H * 0.73);
        }
      }
      this._gradVP(ctx, 0, H * 0.82, lw, H * 0.18, 0x1c0a00, 0x0d0400);
      this._commit(L);
    }

    { const L = this._beginLayer(0.33, -14), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H * 0.16, 0x1a0800, 0x2e1200);
      for (let x = 70; x < lw; x += 500) this._ornateCol(ctx, x, H * 0.07, H * 0.74, 17, 0x3b0000, 0x7a0000, 0.92);
      for (let x = 130; x < lw; x += 500) {
        ctx.fillStyle = this._css(0x3b1a05, 0.82);
        ctx.fillRect(x, H * 0.22, 220, 6); ctx.fillRect(x, H * 0.37, 220, 6);
        for (let k = 0; k < 5; k++) {
          const kx = x + 22 + k * 40;
          ctx.fillStyle = this._css(0x5a2e08, 0.92); ctx.fillRect(kx, H * 0.23, 6, 24);
          ctx.fillStyle = this._css(this.acc, 0.62); ctx.fillRect(kx - 5, H * 0.23 + 24, 16, 5);
          ctx.fillStyle = 'rgba(216,216,216,0.58)'; ctx.fillRect(kx + 1, H * 0.29, 3, 54);
        }
      }
      for (let x = 210; x < lw; x += 500) {
        ctx.fillStyle = this._css(0x3b1a05, 0.60); ctx.fillRect(x + 110 - 2, 0, 3, H * 0.23);
        ctx.fillStyle = this._css(0x8b0000, 0.68); this._ellipse(ctx, x + 110, H * 0.23 + 32, 20, 29);
        ctx.fillStyle = 'rgba(255,153,0,0.15)'; this._circle(ctx, x + 110, H * 0.23 + 32, 44);
      }
      for (let x = 300; x < lw; x += 1000) {
        ctx.fillStyle = this._css(0x1c0a00, 0.72);
        ctx.fillRect(x, H * 0.04, 5, H * 0.35);
        ctx.fillRect(x - 70, H * 0.18, 75, 4);
        ctx.fillRect(x + 5, H * 0.26, 62, 4);
        for (let bi = 0; bi < 14; bi++) {
          ctx.fillStyle = this._css(0x8b0000, 0.26);
          this._circle(ctx, x - 75 + this._h(bi, x) * 150, H * 0.06 + this._h(bi, x + 1) * H * 0.28, 5 + this._h(bi * 3, x) * 7);
        }
      }
      ctx.fillStyle = this._css(0x1e0c00, 0.96); ctx.fillRect(0, H * 0.82, lw, H * 0.18);
      this._commit(L);
    }

    { const L = this._beginLayer(0.57, -13), { ctx, lw } = L;
      for (let x = 230; x < lw; x += 620) {
        ctx.fillStyle = this._css(0x3b1a05, 0.86);
        ctx.fillRect(x - 3, H * 0.38, 6, H * 0.44); ctx.fillRect(x - 26, H * 0.80, 52, 9);
        ctx.fillStyle = this._css(0x8b0000, 0.72); ctx.fillRect(x - 24, H * 0.27, 48, 55);
        ctx.fillStyle = this._css(0x5a0000, 0.82); this._ellipse(ctx, x, H * 0.23, 22, 19);
        ctx.fillStyle = this._css(this.acc, 0.22); this._circle(ctx, x, H * 0.34, 11);
      }
      for (let i = 0; i < 35; i++) {
        ctx.fillStyle = this._css(0xd4607a, 0.26);
        this._ellipse(ctx, this._h(i,10)*lw, H*0.05+this._h(i,11)*H*0.88, 5.5, 4);
      }
      ctx.fillStyle = this._css(0x0d0500, 0.90); ctx.fillRect(0, H * 0.83, lw, H * 0.17);
      this._commit(L);
    }

    { const L = this._beginLayer(0.20, -12), { ctx, lw } = L;
      for (let x = 250; x < lw; x += 500) {
        ctx.fillStyle = 'rgba(255,245,224,0.032)';
        this._tri(ctx, x - 28, 0, x + 28, 0, x + 44, H * 0.77);
      }
      for (let i = 0; i < 20; i++)
        this._star(ctx, this._h(i,12)*lw, H*0.05+this._h(i,13)*H*0.50, 2+this._h(i,14)*4, 0xffd4a0, 0.10+this._h(i,15)*0.08);
      this._commit(L);
    }

    { const L = this._beginLayer(0.72, -11), { ctx, lw } = L;
      ctx.fillStyle = this._css(0x0d0500, 0.92); ctx.fillRect(0, H * 0.82, lw, H * 0.18);
      this._commit(L);
    }
  }

  // ─── Stage 3 — Royal Chambers ─────────────────────────────────────────────
  _royalChambers() {
    const { H } = this;
    this.scene.cameras.main.setBackgroundColor('#0a0015');

    { const L = this._beginLayer(0.05, -16), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H, 0x080012, 0x18002e);
      for (let i = 0; i < 40; i++)
        this._star(ctx, this._h(i,20)*lw, this._h(i,21)*H*0.55, 1+this._h(i,22)*3, 0xd4af37, 0.065+this._h(i,23)*0.085);
      this._commit(L);
    }

    { const L = this._beginLayer(0.15, -15), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H, 0x0e0020, 0x1c003c);
      for (let x = 0; x < lw; x += 62)
        for (let y = 32; y < H * 0.78; y += 72) {
          ctx.fillStyle = this._css(this.acc, 0.05); this._ellipse(ctx, x + 31, y + 36, 13, 22);
        }
      ctx.fillStyle = this._css(this.acc, 0.22); ctx.fillRect(0, H * 0.54, lw, 6); ctx.fillRect(0, H * 0.57, lw, 3);
      ctx.fillStyle = this._css(this.prim, 0.20); ctx.fillRect(0, H * 0.57, lw, H * 0.24);
      this._commit(L);
    }

    { const L = this._beginLayer(0.33, -14), { ctx, lw } = L;
      ctx.fillStyle = this._css(this.acc, 0.20); ctx.fillRect(0, H * 0.06, lw, 11);
      for (let x = 310; x < lw; x += 310) { ctx.fillStyle = this._css(this.prim, 0.16); ctx.fillRect(x, H * 0.02, 2, H * 0.05); }
      for (let x = 210; x < lw; x += 620) this._chandelier(ctx, x, H * 0.06, this.acc, 0xfff5c0, 7, 96);
      for (let x = 110; x < lw; x += 620) {
        ctx.fillStyle = this._css(this.prim, 0.82);
        ctx.fillRect(x - 60, H * 0.09, 120, H * 0.62);
        ctx.fillStyle = this._css(this.acc, 0.36);
        ctx.fillRect(x - 60, H * 0.09, 120, 6); ctx.fillRect(x - 60, H * 0.09 + H * 0.62 - 6, 120, 6);
        ctx.fillRect(x - 60, H * 0.09, 6, H * 0.62); ctx.fillRect(x + 54, H * 0.09, 6, H * 0.62);
        ctx.fillStyle = this._css(this.acc, 0.26); this._circle(ctx, x, H * 0.29, 26);
        ctx.fillStyle = this._css(this.acc, 0.18);
        this._tri(ctx, x - 22, H * 0.38, x + 22, H * 0.38, x, H * 0.56);
      }
      for (let x = 400; x < lw; x += 620) {
        ctx.fillStyle = this._css(this.acc, 0.46); this._ellipse(ctx, x, H * 0.30, 54, 69);
        ctx.fillStyle = this._css(0x0a0018, 0.68); this._ellipse(ctx, x, H * 0.30, 46, 61);
      }
      ctx.fillStyle = this._css(this.prim, 0.56); ctx.fillRect(0, H * 0.82, lw, H * 0.18);
      ctx.fillStyle = this._css(this.acc, 0.18); ctx.fillRect(0, H * 0.82, lw, 6);
      this._commit(L);
    }

    { const L = this._beginLayer(0.57, -13), { ctx, lw } = L;
      for (let x = 210; x < lw; x += 560) {
        this._ornateCol(ctx, x, H * 0.06, H * 0.76, 19, 0x1a0038, 0x4b0082, 0.96);
        ctx.fillStyle = this._css(this.acc, 0.065); this._circle(ctx, x, H * 0.07, 55);
      }
      for (let x = 390; x < lw; x += 560) {
        ctx.fillStyle = this._css(this.acc, 0.56);
        ctx.fillRect(x - 3, H * 0.42, 6, H * 0.40); ctx.fillRect(x - 18, H * 0.82, 36, 7); ctx.fillRect(x - 20, H * 0.42, 40, 7);
        for (let ci = -1; ci <= 1; ci++) {
          ctx.fillStyle = 'rgba(255,245,224,0.66)'; ctx.fillRect(x + ci * 15 - 3, H * 0.29, 6, H * 0.13);
          ctx.fillStyle = 'rgba(255,170,0,0.50)'; this._circle(ctx, x + ci * 15, H * 0.28, 6);
          ctx.fillStyle = 'rgba(255,204,0,0.13)'; this._circle(ctx, x + ci * 15, H * 0.28, 22);
        }
      }
      ctx.fillStyle = this._css(0x0a0015, 0.90); ctx.fillRect(0, H * 0.83, lw, H * 0.17);
      this._commit(L);
    }

    { const L = this._beginLayer(0.22, -12), { ctx, lw } = L;
      for (let i = 0; i < 30; i++)
        this._star(ctx, this._h(i,31)*lw, H*0.04+this._h(i,32)*H*0.75, 2+this._h(i,30)*6, 0xffd700, 0.055+this._h(i,33)*0.09);
      this._commit(L);
    }

    { const L = this._beginLayer(0.18, -11), { ctx, lw } = L;
      for (let x = 210; x < lw; x += 620) {
        ctx.fillStyle = 'rgba(147,112,219,0.038)'; this._tri(ctx, x-45,0, x+45,0, x+70,H*0.74);
        ctx.fillStyle = 'rgba(212,175,55,0.022)';  this._tri(ctx, x-12,0, x+12,0, x+22,H*0.66);
      }
      this._commit(L);
    }
  }

  // ─── Stage 4 — Museum Wing ────────────────────────────────────────────────
  _museumWing() {
    const { H } = this;
    this.scene.cameras.main.setBackgroundColor('#0c1414');

    { const L = this._beginLayer(0.05, -16), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H, 0x0c1414, 0x1c2e2e);
      this._commit(L);
    }

    { const L = this._beginLayer(0.15, -15), { ctx, lw } = L;
      this._stoneWall(ctx, 0, H * 0.06, lw, H * 0.76, 0x1e2e2e, 0x0c1414, 52, 136, 0.90);
      this._gradVP(ctx, 0, 0, lw, H * 0.06, 0x2c3c3c, 0x3c4c4c);
      for (let x = 190; x < lw; x += 380) {
        ctx.fillStyle = 'rgba(136,204,221,0.08)'; ctx.fillRect(x - 65, 0, 130, H * 0.06);
        ctx.fillStyle = this._css(0x2c3c3c, 0.60);
        ctx.fillRect(x - 65, H * 0.027, 130, 3); ctx.fillRect(x, 0, 3, H * 0.06);
      }
      this._gradVP(ctx, 0, H * 0.80, lw, H * 0.20, 0x2c3c3c, 0x0c1414);
      this._commit(L);
    }

    { const L = this._beginLayer(0.33, -14), { ctx, lw } = L;
      ctx.fillStyle = this._css(0x243030, 0.92); ctx.fillRect(0, 0, lw, H * 0.13);
      for (let x = 0; x < lw; x += 250) {
        ctx.fillStyle = this._css(0x344040, 0.72); ctx.fillRect(x, 0, 8, H * 0.13);
      }
      for (let x = 65; x < lw; x += 380) {
        ctx.fillStyle = this._css(0x4a5c5c, 0.92);
        ctx.fillRect(x, H * 0.37, 210, 6); ctx.fillRect(x, H * 0.63, 210, 6);
        ctx.fillRect(x, H * 0.37, 6, H * 0.26); ctx.fillRect(x + 204, H * 0.37, 6, H * 0.26);
        ctx.fillStyle = 'rgba(136,204,221,0.06)'; ctx.fillRect(x + 6, H * 0.39, 198, H * 0.24);
        ctx.fillStyle = this._css(this.acc, 0.30);
        ctx.fillRect(x + 72, H * 0.43, 66, 44); this._ellipse(ctx, x + 105, H * 0.43, 22, 16);
        ctx.fillStyle = 'rgba(255,255,255,0.028)';
        this._tri(ctx, x + 105, H * 0.13, x + 85, H * 0.39, x + 125, H * 0.39);
      }
      for (let x = 235; x < lw; x += 380) this._ornateCol(ctx, x, H * 0.11, H * 0.71, 16, 0x2c3c3c, 0x4c5c5c, 0.92);
      this._gradVP(ctx, 0, H * 0.82, lw, H * 0.18, 0x2c3c3c, 0x1c2c2c);
      this._commit(L);
    }

    { const L = this._beginLayer(0.57, -13), { ctx, lw } = L;
      for (let x = 110; x < lw; x += 490) {
        this._roundArch(ctx, x + 90, H * 0.82, 180, H * 0.70, 0x243030, 0.88);
        ctx.fillStyle = this._css(0x344040, 0.88); ctx.fillRect(x, H * 0.27, 190, 210);
        ctx.fillStyle = this._css(this.acc, 0.28); ctx.fillRect(x + 16, H * 0.29, 158, 5);
        ctx.fillStyle = this._css(this.acc, 0.36); ctx.fillRect(x + 32, H * 0.505, 126, 32);
      }
      ctx.fillStyle = this._css(0x0c1414, 0.90); ctx.fillRect(0, H * 0.83, lw, H * 0.17);
      this._commit(L);
    }

    { const L = this._beginLayer(0.18, -12), { ctx, lw } = L;
      for (let x = 205; x < lw; x += 380) {
        ctx.fillStyle = 'rgba(136,204,221,0.038)';
        this._tri(ctx, x - 20, 0, x + 20, 0, x + 34, H * 0.57);
        ctx.fillStyle = 'rgba(255,255,255,0.016)';
        this._tri(ctx, x - 5, 0, x + 5, 0, x + 9, H * 0.52);
      }
      ctx.fillStyle = this._css(this.acc, 0.05);
      for (let x = 240; x < lw; x += 760) this._circle(ctx, x, H * 0.50, 160);
      this._commit(L);
    }

    { const L = this._beginLayer(0.05, -11), { ctx, lw } = L;
      ctx.fillStyle = this._css(this.acc, 0.05);
      for (let x = 240; x < lw; x += 760) this._circle(ctx, x, H * 0.50, 160);
      this._commit(L);
    }
  }

  // ─── Stage 5 — Tech Manor ─────────────────────────────────────────────────
  _techManor() {
    const { H } = this;
    this.scene.cameras.main.setBackgroundColor('#050510');

    { const L = this._beginLayer(0.05, -16), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H, 0x030310, 0x0f0f28);
      for (let x = 0; x < lw; x += 44)
        for (let y = 0; y < H; y += 32)
          if (this._h(x, y) > 0.88) { ctx.fillStyle = this._css(this.acc, 0.06); ctx.fillRect(x, y, 14, 20); }
      this._commit(L);
    }

    { const L = this._beginLayer(0.15, -15), { ctx, lw } = L;
      this._stoneWall(ctx, 0, H * 0.08, lw, H * 0.74, 0x0d0d1e, 0x06060e, 52, 125, 0.92);
      for (let x = 0; x < lw; x += 660) {
        ctx.fillStyle = this._css(0x1a1a3a, 0.88); ctx.fillRect(x + 32, H * 0.10, 126, H * 0.68);
        for (let ry = H * 0.12; ry < H * 0.76; ry += 48) {
          ctx.fillStyle = this._css(0x222246, 0.92); ctx.fillRect(x + 35, ry, 120, 20);
          ctx.fillStyle = this._css(this.acc, 0.56); this._circle(ctx, x + 43, ry + 10, 3);
          ctx.fillStyle = 'rgba(68,255,136,0.40)';  this._circle(ctx, x + 53, ry + 10, 3);
        }
      }
      this._neonBar(ctx, 0, H * 0.80, lw, 3, this.acc, 0.36);
      this._gradVP(ctx, 0, H * 0.80, lw, H * 0.20, 0x0f0f26, 0x050510);
      this._commit(L);
    }

    { const L = this._beginLayer(0.33, -14), { ctx, lw } = L;
      ctx.fillStyle = this._css(0x1a1a3a, 0.88); ctx.fillRect(0, 0, lw, H * 0.11);
      for (let x = 0; x < lw; x += 85) { ctx.fillStyle = this._css(this.acc, 0.08); ctx.fillRect(x, 0, 2, H * 0.11); }
      for (let x = 55; x < lw; x += 490) {
        this._neonBar(ctx, x, H * 0.13, 230, 3, this.acc, 0.60);
        this._neonBar(ctx, x, H * 0.13 + H * 0.53, 230, 3, this.acc, 0.60);
        this._neonBar(ctx, x, H * 0.13, 3, H * 0.53, this.acc, 0.60);
        this._neonBar(ctx, x + 227, H * 0.13, 3, H * 0.53, this.acc, 0.60);
        ctx.fillStyle = this._css(this.acc, 0.04); ctx.fillRect(x + 3, H * 0.13 + 3, 224, H * 0.53 - 6);
        for (let sy = H * 0.16; sy < H * 0.64; sy += 9) { ctx.fillStyle = this._css(this.acc, 0.058); ctx.fillRect(x + 5, sy, 220, 4); }
        for (let bx = x + 10; bx < x + 220; bx += 22) {
          const ht = 42 + this._h(bx, x) * 108;
          ctx.fillStyle = this._css(this.acc, 0.18); ctx.fillRect(bx, H * 0.62 - ht, 16, ht);
        }
      }
      for (let x = 290; x < lw; x += 490) {
        this._neonBar(ctx, x - 7, H * 0.11, 14, H * 0.71, this.acc, 0.10);
        ctx.fillStyle = this._css(0x1a1a3a, 0.92); ctx.fillRect(x - 5, H * 0.11, 10, H * 0.71);
        this._neonBar(ctx, x - 1, H * 0.11, 2, H * 0.71, this.acc, 0.56);
      }
      ctx.fillStyle = this._css(0x111128, 0.96); ctx.fillRect(0, H * 0.82, lw, H * 0.18);
      this._commit(L);
    }

    { const L = this._beginLayer(0.57, -13), { ctx, lw } = L;
      for (let x = 0; x < lw; x += 580) {
        ctx.fillStyle = this._css(0x0d0d1e, 0.93); ctx.fillRect(x, 0, 26, H * 0.84);
        ctx.fillStyle = this._css(this.acc, 0.20);
        for (let ty = 22; ty < H * 0.84; ty += 58) {
          ctx.fillRect(x + 7, ty, 12, 3); ctx.fillRect(x + 7, ty + 3, 3, 22);
          this._circle(ctx, x + 13, ty + 25, 5);
        }
      }
      ctx.fillStyle = this._css(0x050510, 0.92); ctx.fillRect(0, H * 0.83, lw, H * 0.17);
      this._commit(L);
    }

    { const L = this._beginLayer(0.22, -12), { ctx, lw } = L;
      for (let i = 0; i < 20; i++) {
        ctx.fillStyle = this._css(this.acc, 0.07 + this._h(i,44)*0.09);
        ctx.fillRect(this._h(i,40)*lw, H*0.05+this._h(i,41)*H*0.80, 8+this._h(i,42)*80, 2+this._h(i,43)*8);
      }
      this._commit(L);
    }

    { const L = this._beginLayer(0.18, -11), { ctx, lw } = L;
      for (let x = 135; x < lw; x += 490) {
        ctx.fillStyle = this._css(this.acc, 0.038); this._tri(ctx, x-22,0, x+22,0, x+38,H*0.72);
        ctx.fillStyle = this._css(this.acc, 0.020); this._tri(ctx, x-50,0, x+50,0, x+72,H*0.84);
      }
      this._commit(L);
    }
  }

  // ─── Stage 6 — Armory Corridor ────────────────────────────────────────────
  _armoryCorridor() {
    const { H } = this;
    this.scene.cameras.main.setBackgroundColor('#0a0d10');

    { const L = this._beginLayer(0.05, -16), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H, 0x080c10, 0x141e26);
      this._commit(L);
    }

    { const L = this._beginLayer(0.15, -15), { ctx, lw } = L;
      this._stoneWall(ctx, 0, H * 0.04, lw, H * 0.78, 0x1c2430, 0x0e1418, 58, 148, 0.92);
      for (let x = 160; x < lw; x += 375) {
        ctx.fillStyle = this._css(0x0e1418, 0.92); ctx.fillRect(x - 12, H * 0.10, 24, H * 0.30);
        ctx.fillStyle = 'rgba(136,170,204,0.06)';  ctx.fillRect(x - 9,  H * 0.12, 18, H * 0.26);
      }
      this._gradVP(ctx, 0, H * 0.80, lw, H * 0.20, 0x1c2430, 0x0a0d10);
      this._commit(L);
    }

    { const L = this._beginLayer(0.33, -14), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H * 0.16, 0x141e26, 0x1e2c38);
      for (let x = 32; x < lw; x += 460) {
        ctx.fillStyle = this._css(0x2e3a42, 0.92); ctx.fillRect(x, H * 0.14, 295, 9);
        for (let k = 0; k < 6; k++) {
          const kx = x + 24 + k * 46;
          ctx.fillStyle = this._css(this.acc, 0.56); ctx.fillRect(kx - 9, H * 0.15, 18, 5);
          ctx.fillStyle = this._css(0x4a5c6c, 0.72); ctx.fillRect(kx - 2, H * 0.20, 4, H * 0.37);
          ctx.fillStyle = 'rgba(200,200,200,0.56)'; ctx.fillRect(kx - 1, H * 0.21, 2, H * 0.35);
        }
        for (let k = 0; k < 4; k++) {
          const sx = x + 310 + k * 68;
          ctx.fillStyle = this._css(0x2e3a42, 0.92);
          this._pts(ctx, [
            { x: sx - 24, y: H * 0.19 }, { x: sx + 24, y: H * 0.19 },
            { x: sx + 24, y: H * 0.19 + 56 }, { x: sx, y: H * 0.19 + 76 },
            { x: sx - 24, y: H * 0.19 + 56 },
          ]);
          ctx.fillStyle = this._css(this.acc, 0.36); this._circle(ctx, sx, H * 0.19 + 28, 13);
          ctx.fillStyle = this._css(this.acc, 0.56); this._circle(ctx, sx, H * 0.19 + 28, 5);
        }
      }
      for (let x = 190; x < lw; x += 460) {
        ctx.fillStyle = this._css(0x4a5c6c, 0.82); ctx.fillRect(x + 230 - 4, H * 0.02, 7, H * 0.57);
        ctx.fillStyle = this._css(0x8b0000, 0.68); ctx.fillRect(x + 230, H * 0.03, 75, H * 0.44);
        ctx.fillStyle = this._css(this.acc, 0.46); this._circle(ctx, x + 230 + 37, H * 0.17, 22);
        ctx.fillStyle = this._css(0x8b0000, 0.70); this._circle(ctx, x + 230 + 37, H * 0.17, 13);
        for (let tx = x + 230; tx < x + 305; tx += 8) {
          const tear = this._h(tx, x) * 18;
          ctx.fillStyle = this._css(0x0a0d10, 0.7);
          this._tri(ctx, tx, H*0.03+H*0.44-tear, tx+8, H*0.03+H*0.44-tear, tx+4, H*0.03+H*0.44+4);
        }
      }
      this._stoneWall(ctx, 0, H * 0.82, lw, H * 0.18, 0x1e2a32, 0x0e1418, 32, 95, 0.94);
      this._commit(L);
    }

    { const L = this._beginLayer(0.57, -13), { ctx, lw } = L;
      for (let x = 105; x < lw; x += 490) this._lamp(ctx, x, H * 0.24, 0x2e3a42, 0xff7722);
      for (let x = 370; x < lw; x += 490) this._lamp(ctx, x, H * 0.55, 0x2e3a42, 0xff7722);
      for (let x = 0; x < lw; x += 580) { ctx.fillStyle = this._css(0x0a0d10, 0.25); ctx.fillRect(x, 0, 11, H * 0.84); }
      ctx.fillStyle = this._css(0x0a0d10, 0.90); ctx.fillRect(0, H * 0.83, lw, H * 0.17);
      this._commit(L);
    }

    { const L = this._beginLayer(0.22, -12), { ctx, lw } = L;
      for (let i = 0; i < 22; i++)
        this._star(ctx, this._h(i,50)*lw, H*0.15+this._h(i,51)*H*0.65, 2+this._h(i,52)*4, 0xff7722, 0.055+this._h(i,53)*0.09);
      this._commit(L);
    }

    { const L = this._beginLayer(0.18, -11), { ctx, lw } = L;
      for (let x = 148; x < lw; x += 490) {
        ctx.fillStyle = 'rgba(255,119,34,0.038)'; this._tri(ctx, x-24,H*0.28, x+24,H*0.28, x+38,H*0.84);
        ctx.fillStyle = 'rgba(255,153,68,0.020)'; this._tri(ctx, x-44,H*0.28, x+44,H*0.28, x+58,H*0.96);
      }
      this._commit(L);
    }
  }

  // ─── Stage 7 — Art Gallery ────────────────────────────────────────────────
  _artGallery() {
    const { H } = this;
    this.scene.cameras.main.setBackgroundColor('#120008');

    { const L = this._beginLayer(0.05, -16), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H, 0x0e0006, 0x220012);
      this._commit(L);
    }

    { const L = this._beginLayer(0.15, -15), { ctx, lw } = L;
      this._gradVP(ctx, 0, H * 0.05, lw, H * 0.78, 0x1e0012, 0x2c0018);
      ctx.fillStyle = this._css(this.acc, 0.18); ctx.fillRect(0, H * 0.10, lw, 7);
      for (let x = 32; x < lw; x += 270) {
        const pw = 105 + this._h(x, 0) * 85, ph = 84 + this._h(x, 1) * 72;
        ctx.fillStyle = this._css(this.acc, 0.36); ctx.fillRect(x, H * 0.13, pw + 12, ph + 12);
        const cc = this._h(x, 2) < 0.33 ? 0x8b2020 : this._h(x, 2) < 0.66 ? 0x1e4060 : 0x2c5a1a;
        ctx.fillStyle = this._css(cc, 0.56); ctx.fillRect(x + 6, H * 0.13 + 6, pw, ph);
      }
      this._gradVP(ctx, 0, H * 0.80, lw, H * 0.20, 0x1e0012, 0x0e0006);
      this._commit(L);
    }

    { const L = this._beginLayer(0.33, -14), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H * 0.12, 0x1e0012, 0x300018);
      for (let x = 0; x < lw; x += 475) {
        const pw = 210, ph = 148, px = x + 32, py = H * 0.13;
        ctx.fillStyle = this._css(this._lighten(this.acc, 0.28), 0.66); ctx.fillRect(px - 18, py - 18, pw + 36, ph + 36);
        ctx.fillStyle = this._css(this.acc, 0.80);                       ctx.fillRect(px - 12, py - 12, pw + 24, ph + 24);
        ctx.fillStyle = this._css(this._darken(this.acc, 0.28), 0.70);   ctx.fillRect(px - 6,  py - 6,  pw + 12, ph + 12);
        const palette = [0x8b2020, 0x4a2060, 0x1e4060, 0x3a6020, 0x8b5020, 0x602040];
        const mainC = palette[Math.floor(this._h(x, 5) * palette.length)];
        ctx.fillStyle = this._css(mainC, 0.72); ctx.fillRect(px, py, pw, ph);
        ctx.fillStyle = this._css(this._lighten(mainC, 0.28), 0.34); this._ellipse(ctx, px + pw * 0.5, py + ph * 0.44, pw * 0.29, ph * 0.31);
        ctx.fillStyle = 'rgba(255,255,255,0.044)'; ctx.fillRect(px + 7, py + 7, pw * 0.24, ph - 14);
      }
      for (let x = 295; x < lw; x += 475) {
        ctx.fillStyle = this._css(0x3a2028, 0.88); ctx.fillRect(x - 30, H * 0.54, 60, H * 0.28);
        ctx.fillStyle = this._css(0x4a3038, 0.72);
        ctx.fillRect(x - 37, H * 0.78, 74, 9); ctx.fillRect(x - 37, H * 0.52, 74, 9);
        ctx.fillStyle = this._css(0xc0a0a8, 0.60); this._ellipse(ctx, x, H * 0.45, 23, 29); this._circle(ctx, x, H * 0.35, 20);
      }
      ctx.fillStyle = this._css(0x220012, 0.96); ctx.fillRect(0, H * 0.82, lw, H * 0.18);
      for (let x = 0; x < lw; x += 62) { ctx.fillStyle = this._css(0x3a0020, 0.25); ctx.fillRect(x, H * 0.82, 2, H * 0.18); }
      this._commit(L);
    }

    { const L = this._beginLayer(0.57, -13), { ctx, lw } = L;
      for (let x = 210; x < lw; x += 560) {
        this._ornateCol(ctx, x, H * 0.06, H * 0.76, 19, 0x220012, 0x800020, 0.96);
        ctx.fillStyle = this._css(this.acc, 0.06); this._circle(ctx, x, H * 0.07, 55);
      }
      ctx.fillStyle = this._css(0x2e1a18, 0.80); ctx.fillRect(0, H * 0.06, lw, 9);
      for (let x = 85; x < lw; x += 210) {
        ctx.fillStyle = this._css(0x3a2020, 0.90); this._ellipse(ctx, x, H * 0.075, 11, 7.5);
        ctx.fillStyle = 'rgba(255,245,192,0.26)'; this._circle(ctx, x, H * 0.085, 6);
        ctx.fillStyle = 'rgba(255,245,192,0.055)'; this._tri(ctx, x-20,H*0.095, x+20,H*0.095, x+28,H*0.52);
      }
      ctx.fillStyle = this._css(0x0e0006, 0.90); ctx.fillRect(0, H * 0.83, lw, H * 0.17);
      this._commit(L);
    }

    { const L = this._beginLayer(0.18, -12), { ctx, lw } = L;
      for (let x = 137; x < lw; x += 475) {
        ctx.fillStyle = 'rgba(255,245,192,0.040)'; this._tri(ctx, x-22,H*0.07, x+22,H*0.07, x+36,H*0.57);
        ctx.fillStyle = 'rgba(255,245,192,0.018)'; this._tri(ctx, x-50,H*0.07, x+50,H*0.07, x+66,H*0.68);
      }
      for (let i = 0; i < 25; i++)
        this._star(ctx, this._h(i,61)*lw, H*0.05+this._h(i,62)*H*0.80, 1+this._h(i,60)*5, 0xffd700, 0.036+this._h(i,63)*0.065);
      this._commit(L);
    }

    { const L = this._beginLayer(0.22, -11), { ctx, lw } = L;
      this._commit(L); // placeholder for future motifs
    }
  }

  // ─── Stage 8 — Treasure Vault ─────────────────────────────────────────────
  _treasureVault() {
    const { H } = this;
    this.scene.cameras.main.setBackgroundColor('#05050f');

    { const L = this._beginLayer(0.05, -16), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H, 0x050510, 0x101022);
      for (let x = 500; x < lw; x += 1000) {
        ctx.fillStyle = 'rgba(255,215,0,0.07)'; this._circle(ctx, x, H * 0.76, 280);
        ctx.fillStyle = 'rgba(255,215,0,0.035)'; this._circle(ctx, x, H * 0.76, 420);
      }
      this._commit(L);
    }

    { const L = this._beginLayer(0.15, -15), { ctx, lw } = L;
      this._stoneWall(ctx, 0, H * 0.05, lw, H * 0.77, 0x0f0f1e, 0x070710, 62, 155, 0.90);
      for (let x = 0; x < lw; x += 310) {
        for (let row = 0; row < 3; row++) {
          const cy = H * 0.65 - row * 54;
          ctx.fillStyle = this._css(0x2c2000, 0.82); ctx.fillRect(x + 42, cy, 94, 46);
          ctx.fillStyle = this._css(0x3e2e00, 0.78); ctx.fillRect(x + 42, cy, 94, 13);
          ctx.fillStyle = this._css(this.acc, 0.25);
          ctx.fillRect(x + 42, cy + 7, 94, 5); ctx.fillRect(x + 84, cy, 6, 46);
          ctx.fillStyle = 'rgba(255,215,0,0.36)'; this._circle(ctx, x + 88, cy + 23, 5);
        }
      }
      this._gradVP(ctx, 0, H * 0.80, lw, H * 0.20, 0x1c1800, 0x050510);
      this._commit(L);
    }

    { const L = this._beginLayer(0.33, -14), { ctx, lw } = L;
      this._gradVP(ctx, 0, 0, lw, H * 0.14, 0x0f0f1e, 0x1e1e34);
      const gemCols = [0xff4444, 0x44ff88, 0x4488ff, 0xffd700, 0xff88ff, 0x44ffff];
      for (let x = 0; x < lw; x += 510) {
        ctx.fillStyle = this._css(0x0d0d20, 0.92); ctx.fillRect(x, H * 0.12, 410, H * 0.62);
        for (let i = 0; i < 22; i++) {
          const gx = x + 16 + this._h(i, x) * 378;
          const gy = H * 0.15 + this._h(i + 1, x) * H * 0.56;
          const gc = gemCols[Math.floor(this._h(i * 3, x) * gemCols.length)];
          const gr = 5 + this._h(i, x + 1) * 10;
          this._gem(ctx, gx, gy, gr, gr * 1.35, gc, 0.56);
        }
      }
      for (let x = 85; x < lw; x += 245) {
        const pH = 22 + this._h(x, 7) * 44, pW = 65 + this._h(x, 8) * 85;
        ctx.fillStyle = this._css(this.acc, 0.28); this._ellipse(ctx, x + pW / 2, H * 0.80, pW / 2, pH * 0.31);
        for (let ci = 0; ci < 9; ci++) {
          ctx.fillStyle = this._css(this.acc, 0.50);
          this._ellipse(ctx, x + 9 + this._h(ci, x) * (pW - 18), H * 0.75 - this._h(ci + 1, x) * pH * 0.72, 7.5, 4.5);
        }
      }
      for (let x = 360; x < lw; x += 510) {
        ctx.fillStyle = this._css(0x2a2a42, 0.92); ctx.fillRect(x, H * 0.17, 115, H * 0.62);
        ctx.fillStyle = this._css(0x3a3a52, 0.72); ctx.fillRect(x + 5, H * 0.19, 105, H * 0.58);
        ctx.fillStyle = this._css(this.acc, 0.46);
        for (let ly = H * 0.24; ly < H * 0.72; ly += 52) {
          this._circle(ctx, x + 21, ly, 11); this._circle(ctx, x + 94, ly, 11);
        }
        this._circle(ctx, x + 57, H * 0.48, 18);
        ctx.fillStyle = this._css(0x0f0f1e, 0.70); this._circle(ctx, x + 57, H * 0.48, 9);
      }
      this._gradVP(ctx, 0, H * 0.82, lw, H * 0.18, 0x1c1800, 0x050510);
      this._commit(L);
    }

    { const L = this._beginLayer(0.57, -13), { ctx, lw } = L;
      for (let x = 165; x < lw; x += 575) {
        ctx.fillStyle = this._css(this.acc, 0.56);
        ctx.fillRect(x - 3, H * 0.40, 6, H * 0.42); ctx.fillRect(x - 19, H * 0.82, 38, 8); ctx.fillRect(x - 23, H * 0.40, 46, 8);
        for (let ci = -1; ci <= 1; ci++) {
          const cxi = x + ci * 19;
          ctx.fillStyle = 'rgba(255,245,224,0.70)'; ctx.fillRect(cxi - 3, H * 0.27, 6, H * 0.13);
          ctx.fillStyle = 'rgba(255,204,0,0.54)';   this._circle(ctx, cxi, H * 0.26, 7);
          ctx.fillStyle = 'rgba(255,204,0,0.13)';   this._circle(ctx, cxi, H * 0.26, 24);
        }
      }
      const gemColsD = [0xff4444, 0x44ff88, 0x4488ff, 0xffd700, 0xff88ff, 0x44ffff];
      for (let i = 0; i < 48; i++) {
        const px = this._h(i, 70) * lw, py = H * 0.08 + this._h(i, 71) * H * 0.76;
        this._star(ctx, px, py, 1 + this._h(i, 72) * 5, gemColsD[i % 6], 0.11 + this._h(i, 73) * 0.16);
      }
      ctx.fillStyle = this._css(0x05050f, 0.90); ctx.fillRect(0, H * 0.83, lw, H * 0.17);
      this._commit(L);
    }

    { const L = this._beginLayer(0.20, -12), { ctx, lw } = L;
      for (let x = 205; x < lw; x += 510) {
        ctx.fillStyle = 'rgba(255,215,0,0.048)'; this._tri(ctx, x-38,H*0.82, x+38,H*0.82, x-22,0);
        ctx.fillStyle = 'rgba(255,215,0,0.026)'; this._tri(ctx, x-10,H*0.82, x+10,H*0.82, x+5,0);
      }
      this._commit(L);
    }

    { const L = this._beginLayer(0.06, -11), { ctx, lw } = L;
      for (let i = 0; i < 55; i++) {
        const r = 1 + this._h(i, 80) * 4;
        this._star(ctx, this._h(i,81)*lw, H*0.02+this._h(i,82)*H*0.48, r, 0xffd700, 0.045+this._h(i,83)*0.09);
      }
      this._commit(L);
    }
  }
}
