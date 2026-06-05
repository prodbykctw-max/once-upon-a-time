import Phaser from 'phaser';
import Player from '../objects/Player.js';
import { buildLevel } from '../objects/LevelBuilder.js';

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
    this.buildBackground(W, H);

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

  buildBackground(W, H) {
    const prim = Phaser.Display.Color.HexStringToColor(this.level.primaryColor).color;
    const acc = Phaser.Display.Color.HexStringToColor(this.level.accentColor).color;

    // far wall (darkest, slowest)
    const far = this.add.rectangle(0, 0, W, H, prim).setOrigin(0).setAlpha(0.25).setScrollFactor(0.2);
    // mid bookshelf band (mid parallax) — drawn as repeating panels
    const mid = this.add.graphics().setScrollFactor(0.5);
    mid.fillStyle(prim, 0.4);
    for (let x = 0; x < W; x += 220) {
      mid.fillRect(x, H * 0.18, 200, H * 0.42);
      // book spines
      for (let bx = x + 8; bx < x + 200; bx += 12) {
        const c = Phaser.Display.Color.Interpolate.ColorWithColor(
          Phaser.Display.Color.IntegerToColor(acc),
          Phaser.Display.Color.IntegerToColor(prim),
          100, Phaser.Math.Between(0, 100),
        );
        mid.fillStyle(Phaser.Display.Color.GetColor(c.r, c.g, c.b), 0.6);
        mid.fillRect(bx, H * 0.2, 8, Phaser.Math.Between(60, 150));
      }
    }
    // warm vignette overlay (static)
    const vig = this.add.graphics().setScrollFactor(0);
    vig.fillStyle(0x000000, 0.35);
    vig.fillRect(0, 0, this.scale.width, 60);
    vig.fillRect(0, this.scale.height - 60, this.scale.width, 60);

    this.cameras.main.setBackgroundColor(this.level.primaryColor);
    // darken
    this.add.rectangle(0, 0, W, H, 0x000000, 0.45).setOrigin(0).setScrollFactor(0).setDepth(-1);
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
