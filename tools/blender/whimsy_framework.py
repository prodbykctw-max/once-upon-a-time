# Shared whimsy render framework — bright pastel fairytale.
# exec() this at the top of whimsy scene scripts.
import bpy, math, os, random
from mathutils import Vector

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 128
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = 'AgX'   # bright pastels, graceful highlight rolloff
    sc.view_settings.look = 'AgX - Punchy'
    sc.view_settings.exposure = 0.6
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    return sc

def srgb(r, g, b):
    def f(c):
        c /= 255.0
        return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
    return (f(r), f(g), f(b))

def mat(name, tone, rough=0.55, metal=0.0, emit=0.0, emit_col=None, sheen=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*tone, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if sheen: b.inputs['Sheen Weight'].default_value = sheen
    if emit > 0:
        ec = emit_col if emit_col else tone
        b.inputs['Emission Color'].default_value = (*ec, 1)
        b.inputs['Emission Strength'].default_value = emit
    if alpha < 1.0:
        b.inputs['Alpha'].default_value = alpha
        m.blend_method = 'BLEND'
    return m

def cube(loc, scale, m=None, rot=(0,0,0), name='c'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = scale
    if m: o.data.materials.append(m)
    return o

def cyl(loc, r, d, m=None, rot=(0,0,0), v=32, name='cy'):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v)
    o = bpy.context.active_object; o.name = name
    if m: o.data.materials.append(m)
    return o

def cone(loc, r1, r2, d, m=None, rot=(0,0,0), v=32, name='co'):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=d, location=loc, rotation=rot, vertices=v)
    o = bpy.context.active_object; o.name = name
    if m: o.data.materials.append(m)
    return o

def ball(loc, r, m=None, name='b', smooth=True):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=24, ring_count=14)
    o = bpy.context.active_object; o.name = name
    if smooth: bpy.ops.object.shade_smooth()
    if m: o.data.materials.append(m)
    return o

def torus(loc, R, r, m=None, rot=(0,0,0), name='t'):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    bpy.ops.object.shade_smooth()
    if m: o.data.materials.append(m)
    return o

def plane(loc, size, m=None, rot=(0,0,0), name='p'):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    if m: o.data.materials.append(m)
    return o

def ortho_cam(loc, rot, scale):
    cd = bpy.data.cameras.new('Cam'); cd.type = 'ORTHO'; cd.ortho_scale = scale
    c = bpy.data.objects.new('Cam', cd); bpy.context.scene.collection.objects.link(c)
    c.location = loc; c.rotation_euler = rot; bpy.context.scene.camera = c
    return c

def persp_cam(loc, rot, lens=24, shift_y=0.0):
    cd = bpy.data.cameras.new('Cam'); cd.lens = lens; cd.shift_y = shift_y
    c = bpy.data.objects.new('Cam', cd); bpy.context.scene.collection.objects.link(c)
    c.location = loc; c.rotation_euler = rot; bpy.context.scene.camera = c
    return c

def wall_cam():   # portrait 144x192 -> visible x[-0.75,0.75] z[-1,1]
    return ortho_cam((0,-4,0), (math.pi/2,0,0), 2.0)
def floor_cam():  # top-down 96x96 square -> x,y[-1,1]
    return ortho_cam((0,0,4), (0,0,0), 2.0)
def decor_cam():  # portrait 144x240 -> x[-0.75,0.75] z[-0.15,2.35]
    return ortho_cam((0,-4,1.1), (math.pi/2,0,0), 2.5)

def area(loc, e, size, col, rot):
    ld = bpy.data.lights.new('A','AREA'); ld.energy=e; ld.size=size; ld.color=col
    lo = bpy.data.objects.new('A', ld); bpy.context.scene.collection.objects.link(lo)
    lo.location=loc; lo.rotation_euler=rot; return lo

def point(loc, e, col, r=0.15):
    ld = bpy.data.lights.new('P','POINT'); ld.energy=e; ld.color=col; ld.shadow_soft_size=r
    lo = bpy.data.objects.new('P', ld); bpy.context.scene.collection.objects.link(lo)
    lo.location=loc; return lo

def sky_world(top=(0.6,0.8,1.0), strength=0.9):
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Strength'].default_value = strength
    bg.inputs['Color'].default_value = (*top, 1)
    return w

def highkey(warm=(1,0.97,0.9), cool=(0.85,0.9,1.0), key=55, fill=28):
    # bright, soft, minimal-shadow fairytale lighting (world does most of the work)
    area((-2.0,-3.2,2.4), key, 4.0, warm, (math.radians(58),0,math.radians(-26)))
    area((2.2,-2.8,1.4), fill, 3.6, cool, (math.radians(70),0,math.radians(30)))

def render_to(path, w, h, transparent=True, samples=None):
    sc = bpy.context.scene
    sc.render.resolution_x = w; sc.render.resolution_y = h
    sc.render.film_transparent = transparent
    if samples: sc.cycles.samples = samples
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print('RENDERED:', path)

# pastel palette (linear) — shared whimsy colors
PAL = {
 'sky':      srgb(180,214,244),
 'skyhi':    srgb(210,232,250),
 'honey':    srgb(216,180,130),
 'honey_dk': srgb(180,142,96),
 'gold':     srgb(232,196,110),
 'goldmet':  (0.80,0.62,0.22),
 'leaf':     srgb(150,200,120),
 'leaf_dk':  srgb(110,165,90),
 'rose':     srgb(244,150,190),
 'rose_dk':  srgb(214,110,160),
 'blossom':  srgb(248,196,222),
 'pink':     srgb(244,196,222),
 'pink_dk':  srgb(226,160,196),
 'cream':    srgb(248,242,230),
 'marble':   srgb(238,236,230),
 'water':    srgb(150,206,224),
 'water_dk': srgb(110,180,206),
 'lav':      srgb(206,186,232),
 'lav_dk':   srgb(176,150,214),
 'dusk':     srgb(120,124,190),
 'dusk_dk':  srgb(86,90,150),
 'sunset':   srgb(255,168,128),
 'sunset_hi':srgb(255,206,150),
 'coral':    srgb(255,150,120),
 'red':      srgb(214,96,96),
 'white':    srgb(250,248,244),
 'glow_pk':  srgb(255,180,210),
 'glow_yl':  srgb(255,236,170),
}
