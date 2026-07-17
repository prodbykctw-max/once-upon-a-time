# Shared Blender framework for Jande texture overhaul.
# Stage scripts run:  exec(open(FRAMEWORK).read())  at the top.
# Cycles, photoreal procedural PBR materials, reusable cam/light rigs.
import bpy, math, os, random

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 160
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = 'Filmic'
    sc.view_settings.look = 'Medium High Contrast'
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    return sc

def _new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    return m, nt, bsdf

def _tex_coord_chain(nt, scale=(1,1,1)):
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = scale
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    return mp

def wood_mat(name='Wood', tone=(0.28,0.16,0.08), grain_scale=6.0, rough=0.45):
    m, nt, b = _new_mat(name)
    mp = _tex_coord_chain(nt, (1, grain_scale, 1))
    wave = nt.nodes.new('ShaderNodeTexWave')
    wave.inputs['Scale'].default_value = 2.2
    wave.inputs['Distortion'].default_value = 9.0
    wave.inputs['Detail'].default_value = 3.0
    nt.links.new(mp.outputs[0], wave.inputs['Vector'])
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 18.0
    nt.links.new(mp.outputs[0], noise.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*tone, 1)
    ramp.color_ramp.elements[1].color = (tone[0]*1.9, tone[1]*1.8, tone[2]*1.6, 1)
    nt.links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    b.inputs['Roughness'].default_value = rough
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.12
    nt.links.new(wave.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs[0], b.inputs['Normal'])
    return m

def marble_mat(name='Marble', base=(0.86,0.85,0.82), vein=(0.35,0.34,0.36), rough=0.14):
    m, nt, b = _new_mat(name)
    mp = _tex_coord_chain(nt)
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 3.0
    noise.inputs['Detail'].default_value = 12.0
    noise.inputs['Distortion'].default_value = 1.4
    nt.links.new(mp.outputs[0], noise.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.42
    ramp.color_ramp.elements[0].color = (*vein, 1)
    ramp.color_ramp.elements[1].position = 0.55
    ramp.color_ramp.elements[1].color = (*base, 1)
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    return m

def stone_mat(name='Stone', tone=(0.45,0.42,0.38), rough=0.85, scale=4.0, bump=0.35):
    m, nt, b = _new_mat(name)
    mp = _tex_coord_chain(nt)
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = scale
    noise.inputs['Detail'].default_value = 14.0
    noise.inputs['Roughness'].default_value = 0.62
    nt.links.new(mp.outputs[0], noise.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (tone[0]*0.55, tone[1]*0.55, tone[2]*0.55, 1)
    ramp.color_ramp.elements[1].color = (tone[0]*1.25, tone[1]*1.25, tone[2]*1.25, 1)
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    bp = nt.nodes.new('ShaderNodeBump')
    bp.inputs['Strength'].default_value = bump
    nt.links.new(noise.outputs['Fac'], bp.inputs['Height'])
    nt.links.new(bp.outputs[0], b.inputs['Normal'])
    return m

def metal_mat(name='Metal', tone=(0.8,0.78,0.75), rough=0.35, metallic=1.0):
    m, nt, b = _new_mat(name)
    b.inputs['Base Color'].default_value = (*tone, 1)
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Roughness'].default_value = rough
    mp = _tex_coord_chain(nt)
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 30.0
    nt.links.new(mp.outputs[0], noise.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (rough*0.6, rough*0.6, rough*0.6, 1)
    ramp.color_ramp.elements[1].color = (min(1,rough*1.6),)*3 + (1,)
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Roughness'])
    return m

def gold_mat(name='Gold'):
    return metal_mat(name, tone=(0.95, 0.72, 0.22), rough=0.22)

def emissive_mat(name='Glow', color=(1,0.8,0.4), strength=6.0):
    m, nt, b = _new_mat(name)
    b.inputs['Emission Color'].default_value = (*color, 1)
    b.inputs['Emission Strength'].default_value = strength
    b.inputs['Base Color'].default_value = (*color, 1)
    return m

def fabric_mat(name='Fabric', tone=(0.4,0.05,0.08), rough=0.9):
    m, nt, b = _new_mat(name)
    b.inputs['Base Color'].default_value = (*tone, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Sheen Weight'].default_value = 1.0
    return m

def cube(loc, scale, mat=None, rot=(0,0,0), name='Cube'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    if mat: o.data.materials.append(mat)
    return o

def cyl(loc, radius, depth, mat=None, rot=(0,0,0), verts=32, name='Cyl'):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    if mat: o.data.materials.append(mat)
    return o

def sphere(loc, radius, mat=None, name='Sph'):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc)
    o = bpy.context.active_object
    o.name = name
    bpy.ops.object.shade_smooth()
    if mat: o.data.materials.append(mat)
    return o

def plane(loc, size, mat=None, rot=(0,0,0), name='Plane'):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    if mat: o.data.materials.append(mat)
    return o

def ortho_cam(loc, rot, ortho_scale):
    cd = bpy.data.cameras.new('Cam')
    cd.type = 'ORTHO'
    cd.ortho_scale = ortho_scale
    c = bpy.data.objects.new('Cam', cd)
    bpy.context.scene.collection.objects.link(c)
    c.location = loc
    c.rotation_euler = rot
    bpy.context.scene.camera = c
    return c

def persp_cam(loc, rot, lens=32):
    cd = bpy.data.cameras.new('Cam')
    cd.lens = lens
    c = bpy.data.objects.new('Cam', cd)
    bpy.context.scene.collection.objects.link(c)
    c.location = loc
    c.rotation_euler = rot
    bpy.context.scene.camera = c
    return c

# Camera rigs for the three tile types. Content plane: XZ at y=0, camera looks +Y.
def wall_cam():
    # frames 1.5 wide x 2.0 tall (144x192 ratio)
    return ortho_cam((0,-4,0), (math.pi/2,0,0), 2.0)

def floor_cam():
    # top-down, frames 2x2
    return ortho_cam((0,0,4), (0,0,0), 2.0)

def decor_cam():
    # frames 1.5 wide x 2.5 tall (144x240 ratio); prop stands on z=0..2.2
    return ortho_cam((0,-4,1.1), (math.pi/2,0,0), 2.5)

def area_light(loc, energy=400, size=3.0, color=(1,0.95,0.88), rot=(0,0,0)):
    ld = bpy.data.lights.new('Area', 'AREA')
    ld.energy = energy
    ld.size = size
    ld.color = color
    lo = bpy.data.objects.new('Area', ld)
    bpy.context.scene.collection.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = rot
    return lo

def point_light(loc, energy=150, color=(1,0.75,0.4), radius=0.15):
    ld = bpy.data.lights.new('Pt', 'POINT')
    ld.energy = energy
    ld.color = color
    ld.shadow_soft_size = radius
    lo = bpy.data.objects.new('Pt', ld)
    bpy.context.scene.collection.objects.link(lo)
    lo.location = loc
    return lo

def warm_rig():
    # warm key from upper-left-front, cool fill from right, subtle rim
    area_light((-2.2,-3.0,2.4), 500, 3.5, (1,0.9,0.75), (math.radians(60),0,math.radians(-28)))
    area_light((2.4,-2.6,1.2), 140, 3.0, (0.75,0.82,1.0), (math.radians(75),0,math.radians(30)))

def render_to(path, w, h, transparent=False, samples=None):
    sc = bpy.context.scene
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.film_transparent = transparent
    if samples: sc.cycles.samples = samples
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print('RENDERED:', path)
