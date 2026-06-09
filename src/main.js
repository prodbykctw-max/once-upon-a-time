import Phaser from 'phaser';
import BootScene from './scenes/BootScene.js';
import TitleScene from './scenes/TitleScene.js';
import GameScene from './scenes/GameScene.js';
import UIScene from './scenes/UIScene.js';

// ── Global game configuration ──
// Phaser handles the render loop, WebGL batching, physics, and input.
// This is what makes it smooth where the hand-rolled canvas version was not:
// sprites are GPU-batched textures, not re-painted shapes every frame.
const config = {
  type: Phaser.AUTO,                // WebGL with Canvas fallback
  backgroundColor: '#04000c',
  pixelArt: false,                  // our sprites are hi-res, keep smoothing
  roundPixels: true,
  scale: {
    mode: Phaser.Scale.FIT,         // letterbox-fit to any screen
    autoCenter: Phaser.Scale.CENTER_BOTH,
    width: 1280,
    height: 720,
  },
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { y: 1600 },
      debug: false,                 // flip true to see hitboxes
    },
  },
  // Scenes run in order; UIScene runs parallel on top of GameScene.
  scene: [BootScene, TitleScene, GameScene, UIScene],
};

// eslint-disable-next-line no-new
new Phaser.Game(config);
