import Phaser from 'phaser';

// Parallel scene drawn on top of the game. Holds the HUD (stage name, hearts)
// and the on-screen touch controls. Touch state is pushed to GameScene through
// the registry event bus so the two scenes stay decoupled.
export default class UIScene extends Phaser.Scene {
  constructor() {
    super('UI');
  }

  create() {
    const { width, height } = this.scale;
    this.touch = { left: false, right: false, up: false, attack: false, dash: false, block: false };

    // ── stage banner ──
    const stage = this.registry.get('stageName') || '';
    this.stageText = this.add.text(width / 2, 30, stage.toUpperCase(), {
      fontFamily: 'Cinzel, serif', fontSize: '22px', color: '#ffd700',
    }).setOrigin(0.5, 0).setScrollFactor(0);

    this.registry.events.on('stage-changed', (lvl) => {
      this.stageText.setText(lvl.name.toUpperCase());
    });

    // ── hearts ──
    this.hearts = [];
    for (let i = 0; i < 5; i++) {
      const h = this.add.text(24 + i * 30, 24, '♥', {
        fontSize: '26px', color: '#ff2d8a',
      }).setScrollFactor(0);
      this.hearts.push(h);
    }

    // ── touch controls (only show on touch devices) ──
    const isTouch = this.sys.game.device.input.touch || window.innerWidth < 820;
    if (isTouch) this.buildTouchControls(width, height);

    // keyboard hint on desktop
    if (!isTouch) {
      this.add.text(width / 2, height - 26,
        '← → MOVE   SPACE JUMP   Z ATTACK   SHIFT DASH   K BLOCK', {
          fontFamily: 'monospace', fontSize: '12px', color: '#ffffff',
        }).setOrigin(0.5).setScrollFactor(0).setAlpha(0.35);
    }
  }

  buildTouchControls(width, height) {
    const mk = (x, y, r, label, key) => {
      const btn = this.add.circle(x, y, r, 0xffffff, 0.12)
        .setStrokeStyle(2, 0xffffff, 0.3).setScrollFactor(0).setInteractive();
      this.add.text(x, y, label, {
        fontFamily: 'monospace', fontSize: '13px', color: '#ffffff',
      }).setOrigin(0.5).setScrollFactor(0);
      btn.on('pointerdown', () => { this.touch[key] = true; this.emit(); });
      btn.on('pointerup', () => { this.touch[key] = false; this.emit(); });
      btn.on('pointerout', () => { this.touch[key] = false; this.emit(); });
      return btn;
    };

    // left cluster: d-pad
    mk(80, height - 150, 38, '←', 'left');
    mk(176, height - 150, 38, '→', 'right');
    // right cluster: actions
    mk(width - 90, height - 170, 44, 'JUMP', 'up');
    mk(width - 170, height - 110, 34, '⚔', 'attack');
    mk(width - 90, height - 90, 34, 'DASH', 'dash');
    mk(width - 30, height - 150, 30, 'K', 'block');
  }

  emit() {
    this.registry.events.emit('touch', { ...this.touch });
  }

  // call from GameScene to update hearts: scene.get('UI').setHearts(n)
  setHearts(n) {
    this.hearts.forEach((h, i) => h.setColor(i < n ? '#ff2d8a' : '#3a0014'));
  }
}
