import Phaser from 'phaser';

export default class TitleScene extends Phaser.Scene {
  constructor() {
    super('Title');
  }

  create() {
    const { width, height } = this.scale;

    // gradient-ish backdrop
    this.cameras.main.setBackgroundColor('#0a0420');
    const g = this.add.graphics();
    g.fillGradientStyle(0x1a0a2e, 0x1a0a2e, 0x04000c, 0x04000c, 1);
    g.fillRect(0, 0, width, height);

    // drifting star field
    for (let i = 0; i < 120; i++) {
      const s = this.add.circle(
        Phaser.Math.Between(0, width),
        Phaser.Math.Between(0, height),
        Phaser.Math.FloatBetween(0.5, 1.8),
        0xffd700,
        Phaser.Math.FloatBetween(0.2, 0.7),
      );
      this.tweens.add({
        targets: s,
        alpha: 0.1,
        duration: Phaser.Math.Between(1200, 3000),
        yoyo: true,
        repeat: -1,
      });
    }

    this.add.text(width / 2, height * 0.34, 'JANDÉ', {
      fontFamily: 'Cinzel, serif', fontSize: '110px', fontStyle: '900',
      color: '#ffd700',
    }).setOrigin(0.5).setShadow(0, 0, '#ffae00', 40);

    this.add.text(width / 2, height * 0.47, 'ONCE UPON A TIME', {
      fontFamily: 'Cinzel, serif', fontSize: '26px', color: '#ffffff',
    }).setOrigin(0.5).setAlpha(0.8);

    this.add.text(width / 2, height * 0.55, '"She traded the veil for the spotlight."', {
      fontFamily: 'Raleway, serif', fontSize: '18px', fontStyle: 'italic', color: '#ffd700',
    }).setOrigin(0.5).setAlpha(0.6);

    const begin = this.add.text(width / 2, height * 0.72, '— BEGIN —', {
      fontFamily: 'Cinzel, serif', fontSize: '24px', color: '#ffd700',
      backgroundColor: '#ffd70011', padding: { x: 24, y: 12 },
    }).setOrigin(0.5).setInteractive({ useHandCursor: true });

    this.tweens.add({ targets: begin, alpha: 0.5, duration: 900, yoyo: true, repeat: -1 });

    const start = () => this.scene.start('Game');
    begin.on('pointerdown', start);
    this.input.keyboard.once('keydown-SPACE', start);
    this.input.keyboard.once('keydown-ENTER', start);
  }
}
