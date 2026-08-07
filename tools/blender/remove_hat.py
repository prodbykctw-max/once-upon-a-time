import bpy, bmesh, math, os
import numpy as np

# DELETE the beanie geometry from the scan. The hair volume already occupies
# this space, so the opening is invisible - and the hat no longer exists.
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul"

obj = bpy.data.objects['JandeModel']
me = obj.data
n = len(me.vertices)
V = np.empty(n * 3)
me.vertices.foreach_get('co', V)
V = V.reshape(n, 3)
X, Y, Z = V[:, 0], V[:, 1], V[:, 2]
# anchor to the NOSE TIP (never part of any cut) - crown_z is unsafe once cut
mh = (Z > 0.55) & (Z < 0.90) & (np.abs(X) < 0.12)
nose_z = float(Z[mh][np.argmin(Y[mh])])
slab = (Z > nose_z - 0.05) & (Z < nose_z + 0.05) & (np.abs(X) < 0.14)
head_cy = float(Y[slab].mean())

# beanie region measured from the renders: dome above the forehead skin edge
# (z > 0.795) plus the lower band around the back of the head (down to 0.75
# behind the ears). Brows sit at ~0.78 and stay untouched.
dome = Z > (nose_z + 0.096)
back_band = (Z > (nose_z + 0.051)) & (Y > head_cy + 0.055)
side_band = (Z > (nose_z + 0.037)) & (np.abs(X) > 0.07) & (Y > head_cy - 0.06)
nape_wisps = (Y > 0.12) & (Z > 0.40) & (Z < 0.78) & (np.abs(X) < 0.2)
ear_band = (Z > nose_z + 0.02) & (np.abs(X) > 0.095) & (Y > head_cy - 0.10)
kill_mask = dome | back_band | side_band | nape_wisps | ear_band
print(f'nose_z={nose_z:.3f} head_cy={head_cy:.3f} deleting {int(kill_mask.sum())} of {n}')

bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
doomed = [bm.verts[i] for i in range(n) if kill_mask[i]]
bmesh.ops.delete(bm, geom=doomed, context='VERTS')
bm.to_mesh(me)
bm.free()
me.update()

# ══ FITTED HAIR DOME: bottom edge follows the measured cut curve ══
for _o in [o for o in bpy.data.objects if o.name.split('.')[0] in ('HairDome', 'CrownOrn', 'Ridge')]:
    bpy.data.objects.remove(_o, do_unlink=True)
V2 = np.empty(len(me.vertices) * 3)
me.vertices.foreach_get('co', V2)
V2 = V2.reshape(-1, 3)
X2, Y2, Z2 = V2[:, 0], V2[:, 1], V2[:, 2]
rad2 = np.sqrt(X2 ** 2 + (Y2 - head_cy) ** 2)
skull = (Z2 > 0.66) & (rad2 < 0.17)
az = np.arctan2(X2[skull], -(Y2[skull] - head_cy))
sz = Z2[skull]; sr = rad2[skull]
BINS = 32
cut_z = np.zeros(BINS); cut_r = np.zeros(BINS)
for b in range(BINS):
    a0 = -math.pi + 2 * math.pi * b / BINS
    a1 = a0 + 2 * math.pi / BINS
    m2 = (az >= a0) & (az < a1)
    if m2.any():
        top = np.argsort(sz[m2])[-6:]
        cut_z[b] = float(sz[m2][top].mean())
        cut_r[b] = float(sr[m2][top].mean())
    else:
        cut_z[b] = 0.75; cut_r[b] = 0.10
# smooth the curve around the ring
for _ in range(2):
    cut_z = (np.roll(cut_z, 1) + cut_z + np.roll(cut_z, -1)) / 3
    cut_r = (np.roll(cut_r, 1) + cut_r + np.roll(cut_r, -1)) / 3
DOME_TOP = float(cut_z.max()) + 0.115
dverts, dfaces = [], []
RINGS_D = 10
import random as _rnd
_rnd.seed(3)
for ri in range(RINGS_D + 1):
    t = ri / RINGS_D
    ang_t = t * math.pi / 2
    prof = math.sin(ang_t)
    for b in range(BINS + 1):
        bb = b % BINS
        phi = -math.pi + 2 * math.pi * b / BINS
        bot_z = cut_z[bb] - 0.028
        # brow clamp with smooth taper into the sides (no helmet corners)
        ap = abs(phi)
        if ap < math.radians(60):
            k = min(1.0, max(0.0, (math.radians(60) - ap) / math.radians(15)))
            k = k * k * (3 - 2 * k)
            bot_z = max(bot_z, bot_z * (1 - k) + (nose_z + 0.092) * k)
        z = DOME_TOP - (DOME_TOP - bot_z) * (1 - math.cos(ang_t))
        back_w = 0.010 + 0.008 * max(0.0, -math.cos(phi))
        rr = (cut_r[bb] + back_w) * prof * (1 + 0.03 * math.sin(phi * 5 + t * 7))
        dverts.append((math.sin(phi) * rr, head_cy - math.cos(phi) * rr * 1.03, z))
for ri in range(RINGS_D):
    for b in range(BINS):
        a2 = ri * (BINS + 1) + b
        b2 = a2 + 1
        c2 = b2 + BINS + 1
        d2 = a2 + BINS + 1
        dfaces.append((a2, b2, c2, d2))
dme = bpy.data.meshes.new('HairDome')
dme.from_pydata(dverts, [], dfaces)
dme.update()
dome_o = bpy.data.objects.new('HairDome', dme)
bpy.context.scene.collection.objects.link(dome_o)
hairmat = bpy.data.materials.new('HairMatte')
hairmat.use_nodes = True
_hb = hairmat.node_tree.nodes['Principled BSDF']
_hb.inputs['Base Color'].default_value = (0.115, 0.038, 0.016, 1)
_hb.inputs['Roughness'].default_value = 0.8
dome_o.data.materials.append(hairmat)
sm = dome_o.modifiers.new('Sub', 'SUBSURF'); sm.levels = 2; sm.render_levels = 2
for p in dme.polygons: p.use_smooth = True
# gold ornament on the dome crown
gold_m = bpy.data.materials.get('Gold')
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=(0, head_cy, DOME_TOP + 0.002), segments=12, ring_count=8)
orn = bpy.context.active_object
orn.name = 'CrownOrn'
if gold_m: orn.data.materials.append(gold_m)

# verify: face + side render
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 96
sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.render.resolution_x = 480
sc.render.resolution_y = 580
cam = bpy.data.objects.get('PrevCam')
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 0.42
cam.location = (0, -1.6, 0.72)
cam.rotation_euler = (math.pi / 2, 0, 0)
sc.camera = cam
sc.render.filepath = os.path.join(OUT, 'nohat_front.png')
bpy.ops.render.render(write_still=True)
cam.location = (1.6, 0, 0.72)
cam.rotation_euler = (math.pi / 2, 0, math.pi / 2)
sc.render.filepath = os.path.join(OUT, 'nohat_side.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_mainfile()
print('HAT_REMOVED')
