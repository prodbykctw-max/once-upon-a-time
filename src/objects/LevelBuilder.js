import Phaser from 'phaser';

// Builds static platform bodies for a stage. Layouts follow traversability
// rules: ground is continuous except for pits, and every pit/high ledge has
// reachable platforms within jump range (≈4 tiles up, ≈5 across). Distinct
// shapes per stage, themed by color. Tile = 64px.
const T = 64;
const GROUND_Y = 656; // top of the floor

// Each entry: array of [xTile, yTileFromBottom, widthTiles] platforms,
// plus pit ranges [startTile, endTile]. Index matches the 9 stages.
const LAYOUTS = [
  { // 0 Grand Library
    plats: [[6, 3, 3], [11, 5, 3], [16, 3, 4], [30, 4, 3], [35, 6, 3], [40, 4, 3],
            [52, 4, 3], [60, 5, 4], [70, 4, 3], [80, 5, 4], [88, 4, 3]],
    pits: [[22, 26]],
  },
  { // 1 Egyptian Hall — stairs
    plats: [[6, 2, 2], [9, 3, 2], [12, 4, 2], [15, 5, 2], [24, 5, 2], [27, 4, 2],
            [30, 3, 2], [48, 4, 3], [54, 5, 3], [62, 4, 2], [70, 5, 3], [82, 4, 3]],
    pits: [[40, 44]],
  },
  { // 2 Samurai Gallery — ledges + pits
    plats: [[5, 4, 2], [10, 5, 2], [18, 4, 2], [24, 6, 2], [30, 4, 2], [38, 5, 3],
            [46, 4, 2], [58, 5, 2], [66, 4, 3], [76, 5, 2], [84, 4, 3]],
    pits: [[13, 16], [31, 34], [52, 55]],
  },
  { // 3 Royal Chambers — high platforms with steps
    plats: [[5, 4, 3], [10, 6, 2], [14, 8, 3], [20, 6, 2], [26, 4, 3], [40, 6, 3],
            [48, 8, 2], [54, 6, 3], [64, 4, 3], [74, 6, 3], [84, 5, 4]],
    pits: [[33, 36]],
  },
  { // 4 Museum Wing — wide floors
    plats: [[6, 4, 5], [16, 6, 4], [28, 4, 5], [38, 6, 4], [48, 4, 5], [60, 5, 5],
            [72, 6, 4], [82, 4, 4]],
    pits: [[22, 25], [53, 56]],
  },
  { // 5 Tech Manor — floating platforms
    plats: [[6, 4, 2], [11, 6, 2], [16, 4, 2], [21, 6, 2], [26, 4, 2], [42, 6, 2],
            [47, 8, 2], [52, 6, 2], [62, 4, 2], [70, 6, 2], [80, 5, 3]],
    pits: [[34, 38]],
  },
  { // 6 Armory Corridor — flat, bridged pits
    plats: [[5, 4, 4], [12, 4, 4], [19, 4, 4], [30, 5, 3], [38, 4, 4], [48, 5, 4],
            [62, 4, 4], [72, 5, 3], [82, 4, 4]],
    pits: [[24, 27], [55, 58]],
  },
  { // 7 Art Gallery — staggered mid-height
    plats: [[5, 5, 3], [11, 7, 3], [17, 5, 3], [23, 7, 3], [36, 5, 3], [42, 7, 3],
            [50, 5, 3], [60, 6, 3], [70, 5, 3], [80, 6, 3]],
    pits: [[30, 33]],
  },
  { // 8 Treasure Vault — finale
    plats: [[5, 4, 3], [10, 6, 2], [15, 4, 3], [22, 6, 3], [38, 5, 3], [46, 4, 3],
            [54, 6, 4], [64, 4, 3], [74, 6, 3], [84, 5, 4]],
    pits: [[31, 35]],
  },
];

export function buildLevel(scene, group, idx, W, H) {
  const layout = LAYOUTS[idx % LAYOUTS.length];
  const prim = Phaser.Display.Color.HexStringToColor(scene.level.primaryColor).color;
  const acc = Phaser.Display.Color.HexStringToColor(scene.level.accentColor).color;

  // continuous floor with pit gaps
  const floorTiles = Math.ceil(W / T);
  const inPit = (tx) => layout.pits.some(([a, b]) => tx >= a && tx < b);
  for (let tx = 0; tx < floorTiles; tx++) {
    if (inPit(tx)) continue;
    addPlatform(scene, group, tx * T, GROUND_Y, T, H - GROUND_Y, prim, acc, false);
  }

  // floating platforms (carved-wood look via fill + accent top)
  layout.plats.forEach(([tx, tyFromBottom, w]) => {
    const x = tx * T;
    const y = GROUND_Y - tyFromBottom * T;
    addPlatform(scene, group, x, y, w * T, 24, prim, acc, true);
  });

  // boss-arena floor at the far right
  for (let tx = floorTiles - 16; tx < floorTiles; tx++) {
    if (inPit(tx)) continue;
    addPlatform(scene, group, tx * T, GROUND_Y, T, H - GROUND_Y, prim, acc, false);
  }
}

function addPlatform(scene, group, x, y, w, h, prim, acc, isLedge) {
  // visual
  const g = scene.add.graphics();
  g.fillStyle(prim, 0.9).fillRect(x, y, w, h);
  g.fillStyle(0x000000, 0.25).fillRect(x, y + h - 4, w, 4); // bottom shadow
  if (isLedge) {
    g.fillStyle(acc, 0.8).fillRect(x, y, w, 4);             // gold top lip
    g.fillStyle(0xffffff, 0.08).fillRect(x, y + 4, w, 2);   // highlight
  }
  // physics body (invisible zone matching the rect)
  const body = scene.add.zone(x + w / 2, y + h / 2, w, h);
  group.add(body);
  body.body.updateFromGameObject();
}
