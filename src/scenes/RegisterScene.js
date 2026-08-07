import Phaser from 'phaser';

// Email-capture screen shown once per device (stores to localStorage).
// Falls back gracefully if EmailJS credentials are absent.
export default class RegisterScene extends Phaser.Scene {
  constructor() { super('Register'); }

  create() {
    const { width: W, height: H } = this.scale;

    // If already registered, skip straight through.
    if (localStorage.getItem('jande_email')) {
      this.scene.start('Title');
      return;
    }

    this.cameras.main.setBackgroundColor('#04000c');
    this._overlay = null;

    // ── decorative stars ───────────────────────────────────────────────────
    for (let i = 0; i < 80; i++) {
      const s = this.add.circle(
        Phaser.Math.Between(0, W), Phaser.Math.Between(0, H),
        Phaser.Math.FloatBetween(0.5, 1.8), 0xffd700, 0,
      );
      this.tweens.add({
        targets: s, alpha: Phaser.Math.FloatBetween(0.15, 0.55),
        delay: Phaser.Math.Between(0, 1600),
        duration: Phaser.Math.Between(700, 1400),
        yoyo: true, repeat: -1,
      });
    }

    // ── frosted card ───────────────────────────────────────────────────────
    const cardW = Math.min(480, W - 48);
    const cardH = 340;
    const cx    = W / 2;
    const cy    = H / 2;

    const card = this.add.graphics();
    card.fillStyle(0x0a0018, 0.92);
    card.fillRoundedRect(cx - cardW / 2, cy - cardH / 2, cardW, cardH, 18);
    card.lineStyle(1.5, 0xffd700, 0.4);
    card.strokeRoundedRect(cx - cardW / 2, cy - cardH / 2, cardW, cardH, 18);
    card.setDepth(2);

    // ── title ──────────────────────────────────────────────────────────────
    this.add.text(cx, cy - cardH / 2 + 38, 'JOIN THE STORY', {
      fontFamily: 'Cinzel, serif', fontSize: '22px', color: '#ffd700',
    }).setOrigin(0.5).setDepth(3);

    this.add.text(cx, cy - cardH / 2 + 72, 'Enter your email to unlock the full experience', {
      fontFamily: 'Raleway, serif', fontSize: '13px', color: '#cccccc',
    }).setOrigin(0.5).setDepth(3);

    // ── HTML email input ───────────────────────────────────────────────────
    this._inputEl = this._buildInput(cx, cy - 18, cardW - 64);

    // ── status text ────────────────────────────────────────────────────────
    this._statusText = this.add.text(cx, cy + 40, '', {
      fontFamily: 'Raleway, serif', fontSize: '13px', color: '#ff6666',
    }).setOrigin(0.5).setDepth(3);

    // ── submit button ──────────────────────────────────────────────────────
    this._makeButton(cx, cy + 80, "LET'S GO", 0xffd700, 0x04000c, () => this._submit());

    // ── guest link ─────────────────────────────────────────────────────────
    const guest = this.add.text(cx, cy + cardH / 2 - 28, 'Skip — play as guest', {
      fontFamily: 'Raleway, serif', fontSize: '13px', color: '#888888',
    }).setOrigin(0.5).setDepth(3).setInteractive({ useHandCursor: true });
    guest.on('pointerover',  () => guest.setColor('#aaaaaa'));
    guest.on('pointerout',   () => guest.setColor('#888888'));
    guest.on('pointerdown',  () => this._advance(null));

    // ── fade in ────────────────────────────────────────────────────────────
    this.cameras.main.fadeIn(500, 0, 0, 0);
  }

  // ── helpers ──────────────────────────────────────────────────────────────

  _buildInput(cx, cy, w) {
    const el = document.createElement('input');
    el.type        = 'email';
    el.placeholder = 'your@email.com';

    // Get the actual canvas scale factor so we position the HTML element correctly
    const canvas   = this.game.canvas;
    const scaleX   = canvas.offsetWidth  / this.scale.width;
    const scaleY   = canvas.offsetHeight / this.scale.height;
    const rect     = canvas.getBoundingClientRect();

    const iw = w * scaleX;
    const ih = 42 * scaleY;
    const ix = rect.left + cx * scaleX - iw / 2;
    const iy = rect.top  + cy * scaleY - ih / 2;

    Object.assign(el.style, {
      position:    'fixed',
      left:        `${ix}px`,
      top:         `${iy}px`,
      width:       `${iw}px`,
      height:      `${ih}px`,
      fontSize:    `${Math.round(15 * scaleY)}px`,
      fontFamily:  'Raleway, sans-serif',
      background:  'rgba(255,255,255,0.07)',
      border:      '1.5px solid rgba(255,215,0,0.45)',
      borderRadius:'8px',
      color:       '#ffffff',
      padding:     '0 14px',
      outline:     'none',
      boxSizing:   'border-box',
      zIndex:      '100',
    });

    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this._submit();
    });

    document.body.appendChild(el);
    this._overlay = el;

    // Placeholder colour (requires ::placeholder pseudo, handled inline via JS trick)
    el.addEventListener('focus', () => {
      el.style.borderColor = 'rgba(255,215,0,0.9)';
      el.style.background  = 'rgba(255,255,255,0.11)';
    });
    el.addEventListener('blur', () => {
      el.style.borderColor = 'rgba(255,215,0,0.45)';
      el.style.background  = 'rgba(255,255,255,0.07)';
    });

    this.time.delayedCall(200, () => el.focus());
    return el;
  }

  _makeButton(x, y, label, fillCol, textCol, cb) {
    const bw = 200, bh = 42;
    const bg = this.add.graphics().setDepth(3);
    bg.fillStyle(fillCol, 1);
    bg.fillRoundedRect(x - bw / 2, y - bh / 2, bw, bh, 10);

    const txt = this.add.text(x, y, label, {
      fontFamily: 'Cinzel, serif', fontSize: '15px',
      fontStyle: 'bold', color: textCol === 0x04000c ? '#04000c' : '#ffd700',
    }).setOrigin(0.5).setDepth(4);

    const zone = this.add.zone(x, y, bw, bh).setDepth(5).setInteractive({ useHandCursor: true });
    zone.on('pointerover',  () => { bg.clear(); bg.fillStyle(0xffe033, 1); bg.fillRoundedRect(x - bw / 2, y - bh / 2, bw, bh, 10); });
    zone.on('pointerout',   () => { bg.clear(); bg.fillStyle(fillCol, 1); bg.fillRoundedRect(x - bw / 2, y - bh / 2, bw, bh, 10); });
    zone.on('pointerdown',  cb);
  }

  _submit() {
    const email = (this._overlay?.value || '').trim().toLowerCase();
    if (!email || !email.includes('@')) {
      this._statusText.setText('Please enter a valid email address.');
      this._statusText.setColor('#ff6666');
      return;
    }
    this._statusText.setText('Sending…').setColor('#ffd700');
    this._sendEmail(email).then(() => {
      this._advance(email);
    }).catch(() => {
      // EmailJS failed — store locally and continue anyway
      this._advance(email);
    });
  }

  async _sendEmail(email) {
    const serviceId  = import.meta.env.VITE_EMAILJS_SERVICE_ID;
    const templateId = import.meta.env.VITE_EMAILJS_TEMPLATE_ID;
    const publicKey  = import.meta.env.VITE_EMAILJS_PUBLIC_KEY;

    if (!serviceId || !templateId || !publicKey) return; // no creds — skip silently

    const res = await fetch('https://api.emailjs.com/api/v1.0/email/send', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        service_id:  serviceId,
        template_id: templateId,
        user_id:     publicKey,
        template_params: { email, game: 'Once Upon A Time', artist: 'Jandé' },
      }),
    });
    if (!res.ok) throw new Error('EmailJS error');
  }

  _advance(email) {
    if (email) localStorage.setItem('jande_email', email);
    this._cleanup();
    this.cameras.main.fadeOut(400, 0, 0, 0);
    this.time.delayedCall(420, () => this.scene.start('Title'));
  }

  _cleanup() {
    if (this._overlay) {
      this._overlay.remove();
      this._overlay = null;
    }
  }

  // Ensure the HTML input is removed if the scene shuts down unexpectedly.
  shutdown() { this._cleanup(); }
  destroy()  { this._cleanup(); }
}
