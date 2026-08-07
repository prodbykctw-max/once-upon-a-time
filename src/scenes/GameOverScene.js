import Phaser from 'phaser';

// Shown after the player wins all nine stages or loses all lives.
// Receives { won, score, stage } from the scene that starts it.
export default class GameOverScene extends Phaser.Scene {
  constructor() {
    super('GameOver');
  }

  // `data` is the object passed as the second argument to scene.start('GameOver', data).
  create(data) {
    const won   = !!data?.won;
    const score = data?.score  ?? 0;
    const stage = data?.stage  ?? 1;

    const { width: W, height: H } = this.scale;

    // ── black backdrop ────────────────────────────────────────────────────
    this.cameras.main.setBackgroundColor('#000000');

    // ── twinkling star field (mirrors IntroScene pattern) ─────────────────
    for (let i = 0; i < 60; i++) {
      const x = Phaser.Math.Between(0, W);
      const y = Phaser.Math.Between(0, H);
      const r = Phaser.Math.FloatBetween(0.5, 2);
      const s = this.add.circle(x, y, r, 0xffd700, 0).setDepth(0);
      this.tweens.add({
        targets:  s,
        alpha:    Phaser.Math.FloatBetween(0.2, 0.8),
        delay:    Phaser.Math.Between(0, 1400),
        duration: Phaser.Math.Between(600, 1200),
        yoyo:     true,
        repeat:   -1,
      });
    }

    // ── title ─────────────────────────────────────────────────────────────
    const titleText  = won ? 'SHE PREVAILS'  : 'GAME OVER';
    const titleColor = won ? '#ffd700'        : '#ff2d8a';

    this.add.text(W / 2, H * 0.24, titleText, {
      fontFamily: 'Cinzel, serif',
      fontSize:   '64px',
      fontStyle:  '900',
      color:      titleColor,
    }).setOrigin(0.5).setDepth(2).setShadow(0, 0, titleColor, 32, true);

    // ── subtitle quote ─────────────────────────────────────────────────────
    const quote = won
      ? '"The spotlight was always hers to claim."'
      : '"Every curtain call is a chance to rise again."';

    this.add.text(W / 2, H * 0.37, quote, {
      fontFamily: 'Raleway, serif',
      fontSize:   '17px',
      fontStyle:  'italic',
      color:      '#cccccc',
    }).setOrigin(0.5).setDepth(2).setAlpha(0.85);

    // ── score ──────────────────────────────────────────────────────────────
    this.add.text(W / 2, H * 0.50, `SCORE  ${score}`, {
      fontFamily: 'Cinzel, serif',
      fontSize:   '26px',
      color:      '#ffd700',
    }).setOrigin(0.5).setDepth(2);

    // ── stage indicator (loss only) ────────────────────────────────────────
    if (!won) {
      this.add.text(W / 2, H * 0.59, `STAGE ${stage} OF 9`, {
        fontFamily: 'Cinzel, serif',
        fontSize:   '18px',
        color:      '#aaaaaa',
      }).setOrigin(0.5).setDepth(2);
    }

    // ── buttons ────────────────────────────────────────────────────────────
    const btnY = H * (won ? 0.72 : 0.74);

    this._makeButton(W / 2 - 140, btnY, 'PLAY AGAIN', () => {
      this.registry.set('levelIndex', 0);
      this.registry.set('score', 0);
      this.cameras.main.fadeOut(400, 0, 0, 0);
      this.time.delayedCall(420, () => this.scene.start('Game'));
    });

    this._makeButton(W / 2 + 140, btnY, 'TITLE', () => {
      this.registry.set('levelIndex', 0);
      this.registry.set('score', 0);
      this.cameras.main.fadeOut(400, 0, 0, 0);
      this.time.delayedCall(420, () => this.scene.start('Title'));
    });

    // ── fade in ────────────────────────────────────────────────────────────
    this.cameras.main.fadeIn(600, 0, 0, 0);
  }

  // ── helpers ───────────────────────────────────────────────────────────────

  /**
   * Draw a rounded-rect button with a centred label.
   * @param {number}   x   - centre x
   * @param {number}   y   - centre y
   * @param {string}   label
   * @param {Function} cb  - called on pointerdown
   */
  _makeButton(x, y, label, cb) {
    const bw = 200;
    const bh = 48;
    const FILL_NORMAL = 0x1a0a2e;
    const FILL_HOVER  = 0x2e1060;
    const BORDER      = 0xffd700;

    const bg = this.add.graphics().setDepth(3);

    const draw = (fillColor) => {
      bg.clear();
      bg.fillStyle(fillColor, 1);
      bg.fillRoundedRect(x - bw / 2, y - bh / 2, bw, bh, 12);
      bg.lineStyle(1.5, BORDER, 0.7);
      bg.strokeRoundedRect(x - bw / 2, y - bh / 2, bw, bh, 12);
    };

    draw(FILL_NORMAL);

    this.add.text(x, y, label, {
      fontFamily: 'Cinzel, serif',
      fontSize:   '16px',
      fontStyle:  'bold',
      color:      '#ffd700',
    }).setOrigin(0.5).setDepth(4);

    // Invisible interactive zone sits on top of the graphics.
    const zone = this.add.zone(x, y, bw, bh)
      .setDepth(5)
      .setInteractive({ useHandCursor: true });

    zone.on('pointerover',  () => draw(FILL_HOVER));
    zone.on('pointerout',   () => draw(FILL_NORMAL));
    zone.on('pointerdown',  cb);
  }
}
