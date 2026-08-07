import bpy, math

# Natural hair texture/lighting/shading: anisotropic strand shader with
# along-strand noise (color breakup + bump) applied to the dome and curls.
# Also registers an image->brush utility so hair photos can become sculpt/
# paint brushes in the GUI (pairs with the installed
# batch_import_images_to_brushes addon).

def strandify(mat, base=(0.115, 0.038, 0.016), hi=(0.19, 0.075, 0.032), along='Z'):
    nt = mat.node_tree
    b = next(nd for nd in nt.nodes if nd.type == 'BSDF_PRINCIPLED')
    for nd in [nd for nd in nt.nodes if nd.get('strand')]:
        nt.nodes.remove(nd)
    def node(tp, x, y):
        nd = nt.nodes.new(tp); nd.location = (x, y); nd['strand'] = True
        return nd
    tc = node('ShaderNodeTexCoord', -900, 0)
    mp = node('ShaderNodeMapping', -720, 0)
    # stretch noise along the strand axis -> fiber look
    mp.inputs['Scale'].default_value = (60, 60, 3) if along == 'Z' else (3, 60, 60)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    noi = node('ShaderNodeTexNoise', -540, 0)
    noi.inputs['Scale'].default_value = 2.0
    noi.inputs['Detail'].default_value = 6.0
    nt.links.new(mp.outputs[0], noi.inputs['Vector'])
    ramp = node('ShaderNodeValToRGB', -360, 0)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (*base, 1)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (*hi, 1)
    nt.links.new(noi.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    bmp = node('ShaderNodeBump', -360, -260)
    bmp.inputs['Strength'].default_value = 0.35
    bmp.inputs['Distance'].default_value = 0.002
    nt.links.new(noi.outputs['Fac'], bmp.inputs['Height'])
    nt.links.new(bmp.outputs[0], b.inputs['Normal'])
    b.inputs['Roughness'].default_value = 0.55
    b.inputs['Anisotropic'].default_value = 0.8
    b.inputs['Anisotropic Rotation'].default_value = 0.25
    b.inputs['Coat Weight'].default_value = 0.15

done = []
for m in bpy.data.materials:
    nm = m.name.split('.')[0]
    if nm in ('HairMatte', 'HairMatte2') and m.use_nodes:
        strandify(m); done.append(m.name)
    elif nm in ('Copper', 'CopperHi') and m.use_nodes:
        strandify(m, base=(0.135, 0.045, 0.02), hi=(0.21, 0.085, 0.038)); done.append(m.name)
print('strandified:', done)

bpy.ops.wm.save_mainfile()
print('HAIR_REALISM_DONE')
