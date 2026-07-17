import bpy, math
import numpy as np

obj = bpy.data.objects['JandeModel']
drv = bpy.data.objects['Driver']
rig = bpy.data.objects['Rig']

# drop the failed SD modifier
sd = obj.modifiers.get('SD')
if sd: obj.modifiers.remove(sd)
for b in rig.pose.bones:
    b.rotation_mode = 'XYZ'
    b.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()

# transfer bone-heat vertex groups driver -> original (nearest poly interp)
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
drv.select_set(True)
bpy.context.view_layer.objects.active = drv
bpy.ops.object.data_transfer(
    use_create=True, data_type='VGROUP_WEIGHTS',
    vert_mapping='POLYINTERP_NEAREST',
    layers_select_src='ALL', layers_select_dst='NAME')
print('vgroups on scan:', len(obj.vertex_groups))

# armature modifier directly on the textured scan
am = obj.modifiers.get('ARM')
if not am:
    am = obj.modifiers.new('ARM', 'ARMATURE')
am.object = rig
bpy.ops.wm.save_mainfile()

# verify: pose left thigh forward 40deg, measure feet on evaluated mesh
pb = rig.pose.bones
pb['thigh.L'].rotation_euler.x = math.radians(40)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ev = obj.evaluated_get(dg)
me2 = ev.to_mesh()
co = np.empty(len(me2.vertices) * 3)
me2.vertices.foreach_get('co', co)
co = co.reshape(-1, 3)
lf = co[(co[:, 0] > 0.05) & (co[:, 2] < -0.3)]
rf = co[(co[:, 0] < -0.05) & (co[:, 2] < -0.3)]
print('L foot: min z', round(lf[:, 2].min(), 3), 'y mean', round(lf[:, 1].mean(), 3))
print('R foot: min z', round(rf[:, 2].min(), 3), 'y mean', round(rf[:, 1].mean(), 3))
ev.to_mesh_clear()
pb['thigh.L'].rotation_euler.x = 0
bpy.context.view_layer.update()
print('WEIGHTS_DONE')
