import Phaser from 'phaser';
import { FRAME } from '../scenes/BootScene.js';

// Jandé player. Wraps an arcade-physics sprite and drives animations from state.
// Display is scaled down from the 256px art to a ~110px tall character; the
// physics body is a tight box (not the whole frame) so collisions feel right.
const DISPLAY_SCALE = 0.62;          // 256 * 0.62 ≈ 159px sprite on screen
const BODY_W = 42;
const BODY_H = 96;
const RUN_SPEED = 320;
const JUMP_V = -720;
const DASH_V = 720;

export default class Player extends Phaser.Physics.Arcade.Sprite {
  constructor(scene, x, y) {
    super(scene, x, y, 'jande_idle', 0);
    scene.add.existing(this);
    scene.physics.add.existing(this);

    this.setScale(DISPLAY_SCALE);
    this.setCollideWorldBounds(true);
    // tight collision body, centered on the character's torso/legs
    this.body.setSize(BODY_W / DISPLAY_SCALE, BODY_H / DISPLAY_SCALE);
    this.body.setOffset(
      (FRAME - BODY_W / DISPLAY_SCALE) / 2,
      FRAME - BODY_H / DISPLAY_SCALE - FRAME * 0.04,
    );

    this.state = 'idle';
    this.facing = 1;
    this.isDashing = false;
    this.dashCooldown = 0;
    this.attacking = false;

    this.play('jande_idle');

    // when a one-shot anim finishes, fall back to movement state
    this.on('animationcomplete', (anim) => {
      if (anim.key === 'jande_attack') this.attacking = false;
    });
  }

  // controls: { left, right, up, attack, dash, block } booleans
  update(dt, controls) {
    if (this.dashCooldown > 0) this.dashCooldown -= dt;

    // DASH
    if (controls.dash && !this.isDashing && this.dashCooldown <= 0) {
      this.isDashing = true;
      this.dashCooldown = 600;
      this.setVelocityX(this.facing * DASH_V);
      this.scene.time.delayedCall(180, () => { this.isDashing = false; });
      this.play('jande_dash', true);
      this.state = 'dash';
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

      // attack
      if (controls.attack && !this.attacking) {
        this.attacking = true;
        this.play('jande_attack', true);
      }
    }

    this.updateAnimation(controls);
  }

  updateAnimation(controls) {
    if (this.attacking || this.isDashing) return; // one-shots own the sprite

    const onGround = this.body.blocked.down;
    let next;
    if (controls.block && onGround) next = 'jande_block';
    else if (!onGround) next = 'jande_jump';
    else if (Math.abs(this.body.velocity.x) > 10) next = 'jande_run';
    else next = 'jande_idle';

    if (this.anims.currentAnim?.key !== next) this.play(next, true);
  }
}
