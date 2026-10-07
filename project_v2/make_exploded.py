import bpy, pathlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parent
original=bpy.context.scene;original.name='01 Assembled cabinet'
bpy.ops.scene.new(type='FULL_COPY');s=bpy.context.scene;s.name='02 Exploded layers'
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1);return m
colors={'01':material('Layer — backing',(.34,.42,.48)),'02':material('Layer — boxes',(.63,.48,.31)),'03':material('Layer — decor',(.49,.3,.13)),'04':material('Layer — letters',(.9,.61,.18)),'05':material('Layer — acrylic illustration',(.34,.7,.83))}
shifts={'01':.26,'02':.08,'03':-.22,'04':-.34,'05':-.45,'09':.38}
for o in s.objects:
    key=next((c.name[:2] for c in o.users_collection if c.name[:2] in shifts or c.name[:2] in ['06','07','08']),None)
    if key in ['06','07','08','09']:o.hide_render=True;continue
    if key in shifts:
        o.location.y+=shifts[key]
        if hasattr(o.data,'materials') and key in colors:
            o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(colors[key])
    if o.type=='MESH' and o.name.startswith('Studio floor'):o.hide_render=True
s.camera.location=(1.55,-2.1,1.12);s.camera.rotation_euler=(Vector((0,-.07,.4))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=1.78
s.render.filepath=str(ROOT/'exploded_layers.png');s.cycles.samples=32
s['description']='Illustrative exploded layers. Opaque blue shows acrylic clearly. Displacements are not assembly dimensions.'
bpy.context.window.scene=original
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'astra_workshop_v2.blend'))
bpy.ops.render.render(write_still=True,scene=s.name)
print('EXPLODED_SCENE_SAVED')
