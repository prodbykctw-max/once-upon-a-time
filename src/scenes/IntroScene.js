import Phaser from 'phaser';

// Animated intro that plays once at launch.
// Tap / click / SPACE / ENTER to skip at any time.
export default class IntroScene extends Phaser.Scene {
  constructor() { super('Intro'); }

  create() {
    const { width: W, height: H } = this.scale;

    // black canvas
    this.cameras.main.setBackgroundColor('#000000');

    // ── star field ─────────────────────────────────────────────────────────
    for (let i = 0; i < 140; i++) {
      const x = Phaser.Math.Between(0, W);
      const y = Phaser.Math.Between(0, H);
      const r = Phaser.Math.FloatBetween(0.5, 2);
      const s = this.add.circle(x, y, r, 0xffd700, 0).setDepth(0);
      this.tweens.add({
        targets: s, alpha: Phaser.Math.FloatBetween(0.2, 0.8),
        delay: Phaser.Math.Between(0, 1400),
        duration: Phaser.Math.Between(600, 1200),
        yoyo: true, repeat: -1,
      });
    }

    // ── central glow ───────────────────────────────────────────────────────
    const glow = this.add.circle(W / 2, H / 2, 260, 0xffd700, 0).setDepth(1);
    this.tweens.add({
      targets: glow, alpha: 0.08, scale: 1.5,
      delay: 400, duration: 1800, ease: 'Sine.easeOut',
    });

    // ── JANDÉ logo ─────────────────────────────────────────────────────────
    const logo = this.add.text(W / 2, H / 2 - 48, 'JANDÉ', {
      fontFamily: 'Cinzel, serif',
      fontSize: '120px', fontStyle: '900',
      color: '#ffd700',
    }).setOrigin(0.5).setAlpha(0).setScale(0.6).setDepth(2);
    logo.setShadow(0, 0, '#ffae00', 60, true);

    this.tweens.add({
      targets: logo,
      alpha: 1, scale: 1,
      delay: 300, duration: 1200, ease: 'Back.easeOut',
    });

    // ── subtitle ───────────────────────────────────────────────────────────
    const sub = this.add.text(W / 2, H / 2 + 62, 'ONCE UPON A TIME', {
      fontFamily: 'Cinzel, serif', fontSize: '26px',
      color: '#ffffff', letterSpacing: 6,
    }).setOrigin(0.5).setAlpha(0).setDepth(2);

    this.tweens.add({
      targets: sub, alpha: 0.85,
      delay: 1200, duration: 900, ease: 'Sine.easeIn',
    });

    // ── tagline ────────────────────────────────────────────────────────────
    const tag = this.add.text(W / 2, H / 2 + 108, '"She traded the veil for the spotlight."', {
      fontFamily: 'Raleway, serif', fontSize: '17px',
      fontStyle: 'italic', color: '#ffd700',
    }).setOrigin(0.5).setAlpha(0).setDepth(2);

    this.tweens.add({
      targets: tag, alpha: 0.60,
      delay: 1900, duration: 900, ease: 'Sine.easeIn',
    });

    // ── skip hint ──────────────────────────────────────────────────────────
    const hint = this.add.text(W / 2, H - 36, 'tap to skip', {
      fontFamily: 'Raleway, serif', fontSize: '13px', color: '#ffffff',
    }).setOrigin(0.5).setAlpha(0).setDepth(2);

    this.tweens.add({
      targets: hint, alpha: 0.35,
      delay: 800, duration: 600, yoyo: true, repeat: -1,
    });

    // ── auto-advance after 5 s ─────────────────────────────────────────────
    this._done = false;
    this.time.delayedCall(5000, () => this._advance());

    // ── skip input ─────────────────────────────────────────────────────────
    this.input.once('pointerdown', () => this._advance());
    this.input.keyboard.once('keydown-SPACE', () => this._advance());
    this.input.keyboard.once('keydown-ENTER', () => this._advance());
  }

  _advance() {
    if (this._done) return;
    this._done = true;
    this.cameras.main.fadeOut(400, 0, 0, 0);
    this.time.delayedCall(420, () => {
      // If already registered skip straight to title, else show registration
      const registered = localStorage.getItem('jande_email');
      this.scene.start(registered ? 'Title' : 'Register');
    });
  }
}
