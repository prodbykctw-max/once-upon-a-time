import Phaser from 'phaser';
import { FRAME } from '../scenes/BootScene.js';

// Jandé player. Wraps an arcade-physics sprite and drives animations from state.
const DISPLAY_SCALE  = 0.62;   // 256 * 0.62 ≈ 159px sprite on screen
// Attack frames are drawn slightly smaller inside the 256px cell — scale up to match.
// Adjust ATTACK_SCALE_MULT if she still looks too small or too big on attack.
const ATTACK_SCALE_MULT = 1.25;

const BODY_W     = 42;
const BODY_H     = 96;
const RUN_SPEED  = 320;
const JUMP_V     = -1100;  // gravity 1200 → max height ≈ 504px; reaches all platforms
const DASH_V     = 820;

export default class Player extends Phaser.Physics.Arcade.Sprite {
  constructor(scene, x, y) {
    super(scene, x, y, 'jande_idle', 0);
    scene.add.existing(this);
    scene.physics.add.existing(this);

    this.setScale(DISPLAY_SCALE);
    this.setCollideWorldBounds(true);
    // tight collision body centered on torso/legs
    this.body.setSize(BODY_W / DISPLAY_SCALE, BODY_H / DISPLAY_SCALE);
    this.body.setOffset(
      (FRAME - BODY_W / DISPLAY_SCALE) / 2,
      FRAME - BODY_H / DISPLAY_SCALE - FRAME * 0.04,
    );

    this.state       = 'idle';
    this.facing      = 1;
    this.isDashing   = false;
    this.dashCooldown = 0;
    this.attacking   = false;
    this._blocking   = false;

    this.play('jande_idle');

    // One-shot animations: restore scale + state on completion
    this.on('animationcomplete', (anim) => {
      if (anim.key === 'jande_attack') {
        this.attacking = false;
        this.setScale(DISPLAY_SCALE);
      }
    });
  }

  // controls: { left, right, up, attack, dash, block } booleans
  update(dt, controls) {
    if (this.dashCooldown > 0) this.dashCooldown -= dt;

    // ── DASH ──
    if (controls.dash && !this.isDashing && this.dashCooldown <= 0) {
      this.isDashing    = true;
      this.dashCooldown = 600;
      this.setVelocityX(this.facing * DASH_V);
      this.scene.time.delayedCall(190, () => { this.isDashing = false; });
      this.play('jande_dash', true);
      this.state = 'dash';
      this._spawnDashTrail();
    }

    if (!this.isDashing) {
      // horizontal movement
      if (controls.left) {
        this.setVelocityX(-RUN_SPEED);
        this.facing = -1;
        this.setFlipX(true);
      } else if (controls.right) {
        this.setVelocityX(RUN_SPEED);
        this.facing = 1;
        this.setFlipX(false);
      } else {
        this.setVelocityX(0);
      }

      // jump (only when on floor)
      if (controls.up && this.body.blocked.down) {
        this.setVelocityY(JUMP_V);
      }

      // attack (scale up to compensate for smaller art in attack frames)
      if (controls.attack && !this.attacking) {
        this.attacking = true;
        this.setScale(DISPLAY_SCALE * ATTACK_SCALE_MULT);
        this.play('jande_attack', true);
      }
    }

    this.updateAnimation(controls);
  }

  updateAnimation(controls) {
    if (this.attacking || this.isDashing) return; // one-shots own the sprite

    const onGround = this.body.blocked.down;
    let next;
    if (controls.block && onGround) {
      next = 'jande_block';
    } else if (!onGround) {
      next = 'jande_jump';
    } else if (Math.abs(this.body.velocity.x) > 10) {
      next = 'jande_run';
    } else {
      next = 'jande_idle';
    }

    // Only start a new animation when the key changes.
    // For block (repeat:0), once it completes the sprite holds on the last
    // frame automatically — we don't force-restart it while the key matches.
    if (this.anims.currentAnim?.key !== next) {
      this.play(next, true);
    }
  }

  // Spawn a trail of glowing blue orbs that expand and fade
  _spawnDashTrail() {
    const COUNT = 7;
    for (let i = 0; i < COUNT; i++) {
      this.scene.time.delayedCall(i * 22, () => {
        if (!this.active) return;
        const orb = this.scene.add.circle(
          this.x - this.facing * i * 18,   // trail behind the player
          this.y + 22,                      // roughly waist height
          18, 0x2266ff, 0.78,
        );
        orb.setDepth(this.depth - 1);
        this.scene.tweens.add({
          targets:  orb,
          alpha:    0,
          scaleX:   2.8,
          scaleY:   2.8,
          duration: 260,
          ease:     'Cubic.easeOut',
          onComplete: () => orb.destroy(),
        });
      });
    }
  }
}
