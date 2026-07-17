# Stage 7 ART GALLERY - DECOR tile: marble bust on fluted column (transparent bg)
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import bpy, math

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\decor_7.png"

reset_scene()

bust_m = marble_mat('BustMarble')                                  # bright white
ped_m  = marble_mat('PedMarble', base=(0.78, 0.76, 0.72),
                    vein=(0.40, 0.38, 0.40), rough=0.22)
gold   = gold_mat('TrimGold')

# ---------- fluted column pedestal ----------
cube((0, 0, 0.05), (0.72, 0.72, 0.10), ped_m, name='Plinth')
cyl((0, 0, 0.14), 0.34, 0.08, ped_m, name='BaseTorus')
cyl((0, 0, 0.65), 0.25, 0.92, ped_m, name='Shaft')
# vertical reeds = fluting light/shadow pattern
for k in range(18):
    a = k * 2 * math.pi / 18
    cyl((0.252 * math.cos(a), 0.252 * math.sin(a), 0.65),
        0.033, 0.90, ped_m, name=f'Flute{k}')
cyl((0, 0, 1.125), 0.27, 0.025, gold, name='GoldRing')
cyl((0, 0, 1.17), 0.33, 0.06, ped_m, name='Cap')
cube((0, 0, 1.235), (0.66, 0.66, 0.09), ped_m, name='Abacus')

# ---------- white marble bust ----------
cube((0, 0, 1.325), (0.42, 0.26, 0.07), bust_m, name='BustBase')
cube((0, 0, 1.47), (0.52, 0.20, 0.22), bust_m,
     rot=(0, 0, math.radians(8)), name='Shoulders')
cube((0, 0, 1.56), (0.34, 0.17, 0.12), bust_m,
     rot=(0, 0, math.radians(8)), name='Chest')
cyl((0, -0.01, 1.64), 0.085, 0.20, bust_m, name='Neck')
sphere((0, -0.05, 1.70), 0.09, bust_m, name='Jaw')
sphere((0, -0.02, 1.83), 0.17, bust_m, name='Head')
sphere((-0.032, -0.182, 1.81), 0.05, bust_m, name='Nose')

# ---------- lights / camera (no wall/floor: composited over game walls) ----------
warm_rig()
point_light((0.9, 1.4, 2.1), 300, (0.80, 0.87, 1.0), 0.5)   # cool rim from behind
point_light((-0.5, -2.0, 0.6), 60, (1, 0.9, 0.8), 0.3)      # low warm front fill

decor_cam()
render_to(OUT, 288, 480, transparent=True, samples=160)
