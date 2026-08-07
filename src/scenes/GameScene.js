import Phaser from 'phaser';
import Player from '../objects/Player.js';
import { buildLevel } from '../objects/LevelBuilder.js';
import { BackgroundBuilder } from '../objects/BackgroundBuilder.js';

// Main playfield. One instance handles whichever stage is active (read from
// the registry). Platforms are static physics bodies; the player collides with
// them via a single collider. Backgrounds are layered tiles for parallax depth.
export default class GameScene extends Phaser.Scene {
  constructor() {
    super('Game');
  }

  create() {
    const levels = this.registry.get('levels');
    const idx = this.registry.get('levelIndex') || 0;
    this.level = levels[idx];

    // ── world bounds (wide side-scroller) ──
    const W = 6400;
    const H = 720;
    this.physics.world.setBounds(0, 0, W, H);
    this.cameras.main.setBounds(0, 0, W, H);

    // ── themed painted background (parallax layers) ──
    // Set a base colour immediately so the screen isn't black while backgrounds render
    this.cameras.main.setBackgroundColor(this.level.primaryColor);
    new BackgroundBuilder(this, W, H, idx).build();

    // ── platforms from the level builder ──
    this.platforms = this.physics.add.staticGroup();
    buildLevel(this, this.platforms, idx, W, H);

    // ── player ──
    this.player = new Player(this, 160, H - 220);
    this.physics.add.collider(this.player, this.platforms);
    this.cameras.main.startFollow(this.player, true, 0.1, 0.1);
    this.cameras.main.setDeadzone(200, 120);

    // ── input: keyboard ──
    this.keys = this.input.keyboard.addKeys({
      left: 'LEFT', right: 'RIGHT', up: 'SPACE', up2: 'UP',
      attack: 'Z', dash: 'SHIFT', block: 'K',
      left2: 'A', right2: 'D',
    });

    // ── input: touch (set by UIScene via registry events) ──
    this.touch = { left: false, right: false, up: false, attack: false, dash: false, block: false };
    this.registry.events.on('touch', (state) => { this.touch = state; });

    // launch the parallel UI/HUD scene
    this.scene.launch('UI');

    // tell UI which stage we're on
    this.registry.set('stageName', `${this.level.name}`);
    this.registry.events.emit('stage-changed', this.level);
  }

  update(time, delta) {
    const k = this.keys;
    const t = this.touch;
    const controls = {
      left: k.left.isDown || k.left2.isDown || t.left,
      right: k.right.isDown || k.right2.isDown || t.right,
      up: k.up.isDown || k.up2.isDown || t.up,
      attack: k.attack.isDown || t.attack,
      dash: k.dash.isDown || t.dash,
      block: k.block.isDown || t.block,
    };
    this.player.update(delta, controls);

    // expose player x for UI/progress
    this.registry.set('playerX', this.player.x);
  }
}
