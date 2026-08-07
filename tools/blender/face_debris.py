import bpy, bmesh, math, os
import numpy as np

# Delete small floating scan-debris islands hovering in front of the face.
# The head/body is one huge island; face flaps are small (<500 verts) and sit
# in the face box, offset off the surface.
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul"

obj = bpy.data.objects['JandeModel']
me = obj.data
n = len(me.vertices)
V = np.empty(n * 3)
me.vertices.foreach_get('co', V)
V = V.reshape(n, 3)
X, Y, Z = V[:, 0], V[:, 1], V[:, 2]
crown_z = float(Z.max())

# island labeling via edges
island_id = np.full(n, -1, dtype=np.int64)
adj = [[] for _ in range(n)]
for e in me.edges:
    a, b = e.vertices
    adj[a].append(b); adj[b].append(a)
cur = 0
for seed in range(n):
    if island_id[seed] >= 0: continue
    stack = [seed]; island_id[seed] = cur
    while stack:
        v = stack.pop()
        for nb in adj[v]:
            if island_id[nb] < 0:
                island_id[nb] = cur; stack.append(nb)
    cur += 1
counts = np.bincount(island_id, minlength=cur)
print(f'islands: {cur}, biggest: {counts.max()}')

# nose tip = front-most legit surface point of the face
mh = (Z > crown_z - 0.30) & (Z < crown_z - 0.05) & (np.abs(X) < 0.12)
ny = float(Y[mh].min())
# debris = islands floating strictly IN FRONT of the nose plane in the face zone.
# The real face surface can never be in front of its own nose tip.
kill = set()
for isl in range(cur):
    m = island_id == isl
    cy = float(Y[m].mean()); czz = float(Z[m].mean()); cxx = float(X[m].mean())
    if cy < ny - 0.005 and abs(cxx) < 0.14 and crown_z - 0.35 < czz < crown_z:
        kill.add(int(isl))
print(f'nose_y={ny:.3f}; deleting {len(kill)} debris islands, verts: {sum(counts[k] for k in kill)}')

if kill:
    kill_mask = np.isin(island_id, list(kill))
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    doomed = [bm.verts[i] for i in range(n) if kill_mask[i]]
    bmesh.ops.delete(bm, geom=doomed, context='VERTS')
    bm.to_mesh(me)
    bm.free()
    me.update()

# re-render the face check
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
sc.render.filepath = os.path.join(OUT, 'face_check.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_mainfile()
print('DEBRIS_DONE')
