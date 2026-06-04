# Once Upon a Time
A bittersweet fairytale Metroidvania inspired by Jandé's song *Once Upon a Time*.

## Quick Start
1. Open Godot 4.6.2 (Standard, NOT .NET)
2. From the Project Manager: **Import** → browse to this folder → select `project.godot`
3. Click **Import & Edit**
4. Press **F5** (or the play button) — the test room runs immediately
5. If asked for a main scene, pick `levels/test_room.tscn`

## Controls
- **A / D** or **Left/Right arrows** — Move
- **Spacebar** — Jump (hold for higher jump, release early for short hop)
- **Left Shift** — Dash (Veil Step) — has i-frames
- **J** — Attack
- **E** — Interact (for save shrines later)
- **Esc** — Pause
- Gamepad: full Xbox/PlayStation support pre-configured

## What's Already Done (Phase 0 — Complete)
- ✅ Project configured for 1920×1080 with proper scaling
- ✅ Compatibility renderer (works on web/mobile/low-end)
- ✅ Input map with 7 actions, keyboard + gamepad bindings
- ✅ Folder structure for the entire game
- ✅ Player controller with momentum, coyote time, jump buffer, variable jump, dash
- ✅ Gown trail secondary animation system
- ✅ Porcelain Guest enemy stub (needs sprite)
- ✅ Test room with platforms

## What You'll See When You Run It
A purple background with brown ground and two gold platforms. Jandé will be invisible (no sprite art yet) but you can move her — watch the bottom of the screen to see the camera tracking. Press F8 to enable Visible Collision Shapes and you'll see the capsule.

## Folder Structure
```
actors/      — Player, enemies, NPCs
abilities/   — Veil Step, Vow of Ascent, etc. (modular)
levels/      — Playable rooms
ui/          — HUD, menus, mobile touch controls
art/         — Imported PNG/SVG assets
audio/       — Music, SFX, ambient
systems/     — Save manager, charm system, dialogue, map
data/        — JSON for stats, dialogue, charms
globals/     — Autoload singletons
```

## Tuning the Feel
Open `actors/player/PlayerJande.tscn`, click the root node, look at the Inspector.
All the movement values are exposed — tweak them while the game is running:
- `max_run_speed` — top speed
- `jump_height` — how high she leaps
- `jump_time_to_peak` vs `jump_time_to_fall` — keep fall time SHORTER than rise time for that Hollow Knight feel
- `dash_speed` and `dash_duration` — feel of Veil Step
- `coyote_time` — grace period after walking off ledge (don't go above 0.15)

## Next Phase: Generate Jandé's Sprite
1. Open Bing Image Creator (free, uses DALL-E 3)
2. Use the master prompt from the design document
3. Generate idle pose first, save as `art/characters/jande_idle.png`
4. In Godot, create a SpriteFrames resource at `actors/player/jande_frames.tres`
5. Add an "idle" animation, drop the PNG in
6. Open `PlayerJande.tscn`, click the Sprite node, assign `jande_frames.tres`
7. Press F5 — she now has a face

## Mobile Export Later
Project → Export → Add Android / iOS preset. The Compatibility renderer is already set, so it'll work out of the box. For HTML5, use the threads-disabled preset.

## Save Often
Commit to git after every session. You'll thank yourself.
