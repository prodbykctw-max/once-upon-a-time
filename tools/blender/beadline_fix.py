import bpy, math
import numpy as np
sc = bpy.context.scene
# remove the bonnet roll + the two oversized temple spheres (matched by location)
doomed = []
for o in bpy.data.objects:
    if o.name == 'HairlineRoll':
        doomed.append(o)
    elif o.type == 'MESH' and abs(abs(o.location.x) - 0.103) < 0.01 and abs(o.location.z - 0.718) < 0.01:
        doomed.append(o)
for o in doomed: bpy.data.objects.remove(o, do_unlink=True)
print('removed', len(doomed))

copper = bpy.data.materials['Copper']
copper_hi = bpy.data.materials['CopperHi']
obj = bpy.data.objects['JandeModel']
me = obj.data
n = len(me.vertices)
V = np.empty(n * 3)
me.vertices.foreach_get('co', V)
V = V.reshape(n, 3)
X, Y, Z = V[:, 0], V[:, 1], V[:, 2]
# head center from face slab
mh = (Z > 0.55) & (Z < 0.90) & (np.abs(X) < 0.14)
hcx = 0.0
hcy = float(Y[mh].mean())
# skull verts: within 0.16 of head axis, above 0.66
rad = np.sqrt((X - hcx) ** 2 + (Y - hcy) ** 2)
skull = (Z > 0.66) & (rad < 0.17)
az = np.arctan2(X[skull] - hcx, -(Y[skull] - hcy))   # 0 = front
sz = Z[skull]; sx = X[skull]; sy = Y[skull]
# per-azimuth cut line = max remaining z in each bin; bead row along it
BINS = 26
for b in range(BINS):
    a0 = -math.pi + 2 * math.pi * b / BINS
    a1 = a0 + 2 * math.pi / BINS
    m = (az >= a0) & (az < a1)
    if not m.any(): continue
    top = np.argsort(sz[m])[-8:]          # top edge verts of this bin
    bx = float(sx[m][top].mean()); by = float(sy[m][top].mean()); bz = float(sz[m][top].mean())
    # push slightly outward from the head axis
    dx, dy = bx - hcx, by - hcy
    dl = math.hypot(dx, dy) or 1.0
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.032,
        location=(bx + dx / dl * 0.006, by + dy / dl * 0.006, bz + 0.004), segments=12, ring_count=8)
    s2 = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    s2.data.materials.append(copper if b % 2 == 0 else copper_hi)
# renders
sc.render.engine = 'CYCLES'; sc.cycles.samples = 96; sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.render.resolution_x = 480; sc.render.resolution_y = 580
cam = bpy.data.objects.get('PrevCam')
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 0.42
cam.location = (0, -1.6, 0.72); cam.rotation_euler = (math.pi/2, 0, 0)
sc.camera = cam
sc.render.filepath = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\nohat_front.png"
bpy.ops.render.render(write_still=True)
cam.location = (1.6, 0, 0.72); cam.rotation_euler = (math.pi/2, 0, math.pi/2)
sc.render.filepath = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\nohat_side.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_mainfile()
print('BEADLINE_DONE')
