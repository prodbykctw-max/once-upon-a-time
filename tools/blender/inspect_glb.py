import bpy, sys

GLB = r"C:\Users\Owner\Downloads\1784330987247_0e2840b2-5ea2-4f1e-b174-e3c6b981c2da_bundle_glb.glb"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)

print("=== OBJECTS ===")
for o in bpy.data.objects:
    info = f"{o.name} :: {o.type}"
    if o.type == 'MESH':
        info += f" verts={len(o.data.vertices)} mats={[m.name for m in o.data.materials]}"
    if o.type == 'ARMATURE':
        info += f" bones={len(o.data.bones)}: {[b.name for b in o.data.bones][:20]}"
    print(info)

print("=== ANIMATIONS ===")
for a in bpy.data.actions:
    print(f"action: {a.name} frames={a.frame_range}")

print("=== MATERIALS ===")
for m in bpy.data.materials:
    print(f"mat: {m.name}")

# overall bounds
import numpy as np
allv = []
for o in bpy.data.objects:
    if o.type == 'MESH':
        vs = np.empty(len(o.data.vertices)*3)
        o.data.vertices.foreach_get('co', vs)
        vs = vs.reshape(-1,3)
        # world transform
        import mathutils
        M = np.array(o.matrix_world)
        vh = np.c_[vs, np.ones(len(vs))]
        wv = (vh @ M.T)[:, :3]
        allv.append(wv)
if allv:
    allv = np.concatenate(allv)
    print(f"=== BOUNDS === min={allv.min(axis=0)} max={allv.max(axis=0)} size={allv.max(axis=0)-allv.min(axis=0)}")
print("INSPECT_DONE")
