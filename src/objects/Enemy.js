import Phaser from 'phaser';

// Per-type configuration: speed (px/s), base hp, texture display size, physics body size.
// BOSS hp is intentionally low here — callers should set it externally after construction
// (e.g. enemy.hp = scene.level.bossHp or a fixed value per stage).
const CFG = {
  VOID:   { speed: 160, hp: 60,  texW: 48, texH: 64, bodyW: 36, bodyH: 60 },
  LANCER: { speed: 90,  hp: 45,  texW: 44, texH: 60, bodyW: 32, bodyH: 56 },
  WARDEN: { speed: 110, hp: 120, texW: 56, texH: 68, bodyW: 44, bodyH: 64 },
  BOSS:   { speed: 140, hp: 300, texW: 80, texH: 96, bodyW: 64, bodyH: 88 },
};

// Death-burst palette shared across all types.
const BURST_COLORS = [0xff2d8a, 0xffd700, 0xc8a0ff];

export default class Enemy extends Phaser.Physics.Arcade.Sprite {
  /**
   * @param {Phaser.Scene} scene
   * @param {number} x
   * @param {number} y
   * @param {'VOID'|'LANCER'|'WARDEN'|'BOSS'} type
   */
  constructor(scene, x, y, type) {
    const cfg = CFG[type];
    super(scene, x, y, `enemy_${type.toLowerCase()}`);

    scene.add.existing(this);
    scene.physics.add.existing(this);

    this.type  = type;
    this.cfg   = cfg;
    this.hp    = cfg.hp;
    this.maxHp = cfg.hp;

    // Display size matches the configured texture dimensions.
    this.setDisplaySize(cfg.texW, cfg.texH);

    // Physics body — tight box independent of display scale.
    this.body.setSize(cfg.bodyW, cfg.bodyH);
    this.body.setOffset(
      (cfg.texW - cfg.bodyW) / 2,
      (cfg.texH - cfg.bodyH),
    );

    this.setCollideWorldBounds(true);
    this.setDepth(5);

    // Timers (all in ms, counted down each update).
    this.invCd   = 0;   // invincibility after taking a hit
    this.shootCd = 0;   // cooldown between LANCER / BOSS shots

    // BOSS-only: phase and AI cycle timer.
    if (type === 'BOSS') {
      this.phase      = 1;
      this._bossCycle = 0; // position within the current phase period (ms)
      this.setTint(0xdd88ff);
    }
  }

  /**
   * Call every frame from a scene's update method.
   * @param {number} dt  - delta time in ms from Phaser's update(time, delta)
   * @param {Phaser.Physics.Arcade.Sprite} player
   */
  update(dt, player) {
    if (!this.active) return;

    // Tick timers.
    if (this.invCd   > 0) this.invCd   -= dt;
    if (this.shootCd > 0) this.shootCd -= dt;

    const dx = player.x - this.x;
    const dy = player.y - this.y;
    const dist = Math.abs(dx);
    const dir  = dx >= 0 ? 1 : -1;

    // Face the player.
    this.setFlipX(dir < 0);

    switch (this.type) {
      case 'VOID':
        this._updateVoid(dist, dir);
        break;
      case 'LANCER':
        this._updateLancer(dt, dist, dir, dy);
        break;
      case 'WARDEN':
        this._updateWarden(dist, dir);
        break;
      case 'BOSS':
        this._updateBoss(dt, dist, dir, dy);
        break;
    }
  }

  // ── VOID: simple melee chaser ────────────────────────────────────────────

  _updateVoid(dist, dir) {
    if (dist <= 480) {
      this.setVelocityX(dir * this.cfg.speed);
    } else {
      this.setVelocityX(0);
    }
  }

  // ── LANCER: ranged, backs off when too close ─────────────────────────────

  _updateLancer(dt, dist, dir, dy) {
    if (dist < 110) {
      // Too close — back away.
      this.setVelocityX(-dir * this.cfg.speed);
    } else if (dist <= 420) {
      // Mid range — slow drift to maintain distance.
      this.setVelocityX(dir * 45);
    } else {
      this.setVelocityX(0);
    }

    // Shoot when within 400px horizontal and 110px vertical and cooldown ready.
    if (dist <= 400 && Math.abs(dy) <= 110 && this.shootCd <= 0) {
      this._emitShot(dir);
      this.shootCd = 2200;
    }
  }

  // ── WARDEN: slow tank that charges at high speed when close enough ────────

  _updateWarden(dist, dir) {
    if (dist <= 380) {
      this.setVelocityX(dir * this.cfg.speed * 1.8);
    } else {
      this.setVelocityX(0);
    }
  }

  // ── BOSS: two-phase AI on a looping cycle ─────────────────────────────────
  // Phase 1 (100%–50% hp): 5000ms cycle — chase → shoot → charge.
  // Phase 2 (<50% hp):     3500ms cycle — same but faster + double shots.

  _updateBoss(dt, dist, dir, dy) {
    // Check phase flip.
    if (this.phase === 1 && this.hp <= this.maxHp * 0.5) {
      this.phase = 2;
      this.setTint(0xff5555);
      this._bossCycle = 0;
    }

    const period = this.phase === 1 ? 5000 : 3500;
    this._bossCycle = (this._bossCycle + dt) % period;
    const t = this._bossCycle / period; // 0..1 normalised position in cycle

    if (t < 0.45) {
      // Chase segment (first 45% of cycle).
      this.setVelocityX(dir * this.cfg.speed);
    } else if (t < 0.65) {
      // Shoot segment (15% of cycle — fire when in range).
      this.setVelocityX(0);
      if (dist <= 500 && Math.abs(dy) <= 140 && this.shootCd <= 0) {
        this._emitShot(dir);
        if (this.phase === 2) {
          // Double shot: fire a second projectile with slight vertical offset
          // encoded in vx sign to let the receiver add a small spread if desired.
          this.scene.time.delayedCall(120, () => {
            if (this.active) this._emitShot(dir);
          });
        }
        this.shootCd = this.phase === 1 ? 900 : 500;
      }
    } else {
      // Charge segment (remaining 35% of cycle).
      this.setVelocityX(dir * this.cfg.speed * 1.8);
    }
  }

  // ── Projectile event ─────────────────────────────────────────────────────

  _emitShot(dir) {
    // Emit an event rather than spawning directly — keeps Enemy decoupled from
    // whatever projectile system the scene uses.
    this.emit('shoot', {
      x:  this.x + dir * (this.cfg.texW * 0.5 + 8),
      y:  this.y - this.cfg.texH * 0.25,
      vx: dir * 380,
    });
  }

  // ── Damage & death ───────────────────────────────────────────────────────

  /**
   * Apply damage. Returns true if the hit was lethal.
   * @param {number} amount
   * @returns {boolean}
   */
  takeDamage(amount) {
    if (this.invCd > 0) return false;

    this.hp    -= amount;
    this.invCd  = 280;

    if (this.hp <= 0) {
      this._die();
      return true;
    }

    // Flash white, then restore tint (or apply red tint for BOSS phase 2).
    this.setTint(0xffffff);
    this.scene.time.delayedCall(120, () => {
      if (!this.active) return;
      if (this.type === 'BOSS' && this.phase === 2) {
        this.setTint(0xff5555);
      } else if (this.type === 'BOSS') {
        this.setTint(0xdd88ff);
      } else {
        this.clearTint();
      }
    });

    return false;
  }

  _die() {
    const count = this.type === 'BOSS' ? 14 : 7;

    for (let i = 0; i < count; i++) {
      const angle  = (i / count) * Math.PI * 2;
      const speed  = Phaser.Math.Between(60, 160);
      const radius = Phaser.Math.Between(5, 11);
      const color  = Phaser.Utils.Array.GetRandom(BURST_COLORS);

      const particle = this.scene.add.circle(this.x, this.y, radius, color, 1);
      particle.setDepth(6);

      this.scene.tweens.add({
        targets:  particle,
        x:        this.x + Math.cos(angle) * speed,
        y:        this.y + Math.sin(angle) * speed,
        alpha:    0,
        scaleX:   2.4,
        scaleY:   2.4,
        duration: Phaser.Math.Between(320, 520),
        ease:     'Cubic.easeOut',
        onComplete: () => particle.destroy(),
      });
    }

    this.destroy();
  }
}
