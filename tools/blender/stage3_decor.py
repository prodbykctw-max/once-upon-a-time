FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\decor_3.png"

reset_scene()

gold    = gold_mat()
wax     = metal_mat('Wax', tone=(0.96, 0.94, 0.90), rough=0.4, metallic=0.0)
crystal = metal_mat('Crystal', tone=(0.9, 0.95, 1.0), rough=0.02, metallic=1.0)
# faint self-glow so the teardrops shimmer instead of going black against transparency
cb = crystal.node_tree.nodes['Principled BSDF']
cb.inputs['Emission Color'].default_value = (0.85, 0.92, 1.0, 1)
cb.inputs['Emission Strength'].default_value = 0.5
flame   = emissive_mat('Flame', color=(1.0, 0.48, 0.08), strength=11)

# --- base (tapered profile) ---
cyl((0, 0, 0.035), 0.30, 0.07, gold, verts=48, name='Base1')
bpy.ops.mesh.primitive_cone_add(radius1=0.26, radius2=0.10, depth=0.14, location=(0, 0, 0.14), vertices=48)
cone = bpy.context.active_object
bpy.ops.object.shade_smooth()
cone.data.materials.append(gold)
sphere((0, 0, 0.24), 0.10, gold, name='BaseKnop')

# --- stem ---
cyl((0, 0, 0.85), 0.045, 1.2, gold, verts=32, name='Stem')
sphere((0, 0, 0.62), 0.085, gold, name='Knop1')
sphere((0, 0, 1.05), 0.075, gold, name='Knop2')
sphere((0, 0, 1.45), 0.09, gold, name='Hub')

# --- arms (diagonal cylinders, XZ plane) ---
# outer pair: hub -> (+-0.54, 1.58)
for s in (-1, 1):
    cyl((s * 0.27, 0, 1.51), 0.032, 0.58, gold, rot=(0, s * math.radians(75.5), 0), verts=24, name='ArmOuter')
    # inner pair: hub -> (+-0.27, 1.62)
    cyl((s * 0.135, 0, 1.535), 0.030, 0.34, gold, rot=(0, s * math.radians(58), 0), verts=24, name='ArmInner')
# center riser
cyl((0, 0, 1.585), 0.05, 0.27, gold, verts=24, name='Riser')

# --- cups, candles, flames ---
# (x, cup_z): outer lower, inner mid, center highest
spots = [(-0.54, 1.60), (-0.27, 1.66), (0.0, 1.74), (0.27, 1.66), (0.54, 1.60)]
for cx, cz in spots:
    cyl((cx, 0, cz), 0.075, 0.035, gold, verts=32, name='Cup')
    cyl((cx, 0, cz + 0.155), 0.034, 0.26, wax, verts=24, name='Candle')
    top = cz + 0.155 + 0.13
    f = sphere((cx, 0, top + 0.065), 0.033, flame, name='Flame')
    f.scale = (1, 1, 1.9)
    point_light((cx, -0.12, top + 0.08), 20, (1, 0.55, 0.2), radius=0.03)

# --- crystal teardrop drops ---
drops = [(-0.54, 1.50), (0.54, 1.50), (-0.40, 1.42), (0.40, 1.42),
         (-0.27, 1.56), (0.27, 1.56), (-0.14, 1.47), (0.14, 1.47)]
for dx, dz in drops:
    lk = sphere((dx, 0, dz + 0.045), 0.013, crystal, name='Link')
    d = sphere((dx, 0, dz), 0.030, crystal, name='Drop')
    d.scale = (1, 1, 1.6)

# --- lighting: warm key + cool fill, flames add local glow ---
warm_rig()
point_light((0, -1.6, 0.35), 40, (1, 0.85, 0.6))

decor_cam()
render_to(OUT, 288, 480, transparent=True, samples=160)
