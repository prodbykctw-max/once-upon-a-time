import Phaser from 'phaser';
import levels from '../data/levels.json';

// Frame layout of each processed sheet (matches public/assets/sprites/manifest.json).
// All cells are 256x256, one row, N frames. Re-run the sprite processor if you
// regenerate art and these counts change.
export const SHEETS = {
  idle:   { frames: 6,  fps: 8,  repeat: -1 },
  run:    { frames: 8,  fps: 14, repeat: -1 },
  jump:   { frames: 6,  fps: 10, repeat: 0  },
  attack: { frames: 8,  fps: 18, repeat: 0  },
  dash:   { frames: 5,  fps: 16, repeat: 0  },
  block:  { frames: 3,  fps: 10, repeat: -1 },
  dance:  { frames: 6,  fps: 10, repeat: -1 },
};
export const FRAME = 256;

export default class BootScene extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  preload() {
    // simple loading bar
    const { width, height } = this.scale;
    const bar = this.add.graphics();
    const box = this.add.graphics();
    box.fillStyle(0x111018, 0.9).fillRect(width / 2 - 160, height / 2 - 14, 320, 28);
    this.load.on('progress', (v) => {
      bar.clear().fillStyle(0xffd700, 1)
        .fillRect(width / 2 - 156, height / 2 - 10, 312 * v, 20);
    });
    this.load.on('complete', () => { bar.destroy(); box.destroy(); });

    // Load each animation sheet as a spritesheet with fixed frame size.
    Object.keys(SHEETS).forEach((key) => {
      this.load.spritesheet(`jande_${key}`, `assets/sprites/${key}.png`, {
        frameWidth: FRAME,
        frameHeight: FRAME,
      });
    });
  }

  create() {
    // Build one animation per sheet.
    Object.entries(SHEETS).forEach(([key, cfg]) => {
      this.anims.create({
        key: `jande_${key}`,
        frames: this.anims.generateFrameNumbers(`jande_${key}`, { start: 0, end: cfg.frames - 1 }),
        frameRate: cfg.fps,
        repeat: cfg.repeat,
      });
    });

    // Stash level data on the registry so any scene can read it.
    this.registry.set('levels', levels.levels);
    this.registry.set('levelIndex', 0);

    this.scene.start('Title');
  }
}
