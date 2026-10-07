import os, sys, pathlib
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from project_data import PARTS, PANELS
base=(HERE.parent/'design/create_model.py').read_text()
# Reuse the material and geometry helpers, without executing the older scene.
exec(compile(base.split("cube('1200 x")[0],str(HERE.parent/'design/create_model.py'),'exec'))
OUT=str(HERE)
for p in PARTS:
    current='01_Back_18mm' if p['stage']==1 else ('03_Carved_frame_concept' if p['stage']==7 else '05_Acrylic_4mm' if p['stage']==8 else '02_Boxes_15mm')
    m=glass if p['material'].startswith('Акрил') else wood
    o=cube(p['id']+' | '+p['title'],[a/1000 for a in p['pos']],[a/1000 for a in p['size']],m,.0006)
    o['part_id']=p['id'];o['size_mm']=str(p['size']);o['assembly_stage']=p['stage'];o['material']=p['material']
current='02_Boxes_15mm'
for code,name,x,z,w,h in PANELS:
    cube(name+' velvet liner',(x/1000,-.001,z/1000),(w/1000,.001,h/1000),dark,0)
    current='06_LED_2800K'
    cube(name+' LED',(x/1000,-.053,(z+h/2-4)/1000),((w-12)/1000,.003,.002),led,.0002)
    for side in [-1,1]:cube(name+' LED side',((x+side*(w/2-4))/1000,-.053,z/1000),(.002,.003,(h-8)/1000),led,.0002)
    current='05_Acrylic_4mm'
    for side in [-1,1]:
        for top in [-1,1]:
            cylinder(code+' recessed magnet Ø4', (x+side*(w/2+2.5))/1000,-.069,(z+top*(h/2+2.5))/1000,.002,.002,brass)
    current='02_Boxes_15mm'
# Append only concept ornaments and display placeholders from the first scene.
with bpy.data.libraries.load(str(HERE.parent/'design/astra_display.blend'),link=False) as (src,dst):
    dst.collections=[n for n in src.collections if n in ['03_Carved_frame_concept','04_Brass_letters','07_Trophy_placeholders','08_Portrait_placeholder']]
for c in dst.collections:
    key=c.name.split('.')[0]
    for o in list(c.objects):
        if any(t in o.name for t in ['Decorative side stile','Decorative horizontal rail']):
            bpy.data.objects.remove(o,do_unlink=True);continue
        if key=='03_Carved_frame_concept' and ('Acanthus spiral' in o.name or 'Stylized acanthus leaf' in o.name):
            zs=[(o.matrix_world @ Vector(v)).z for v in o.bound_box]
            if max(zs)<.275:
                bpy.data.objects.remove(o,do_unlink=True);continue
        c.objects.unlink(o);cols[key].objects.link(o)
        if key=='08_Portrait_placeholder':o.location.z+=.018
        if key=='07_Trophy_placeholders' and abs(o.location.x)>.51 and o.location.z<.25:
            bpy.data.objects.remove(o,do_unlink=True);continue
        if key=='07_Trophy_placeholders' and o.location.x<-.25:
            o.location.x+=.015
            if .31<o.location.z<.46:o.location.z-=.015
        o['status']='CONCEPT — not a production CNC detail'
    bpy.data.collections.remove(c)
current='09_Wall_mount'
# Explicit conceptual pair of bevelled cleats; installer must size/approve mounting.
for name,z,y in [('W01 Cabinet cleat',.69,.027),('W02 Wall cleat',.668,.045)]:
    verts=[]
    profile=[(0,0),(.018,0),(.018,.022),(0,.04)]
    for x in [-.5,.5]:
        for dy,dz in profile:verts.append((x,y+dy-.009,z+dz-.02))
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);o=bpy.data.objects.new(name,me);cols[current].objects.link(o);me.materials.append(wood);o['status']='Mounting study only; mating profile and anchors require installer approval'
current='10_Presentation'
floor=mat('Studio charcoal',(.015,.019,.023),0,.8)
cube('Studio floor',(0,0,-.035),(200,200,.01),floor,0)
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.83,-2.5,.96));camera=put(bpy.context.object,'Final view camera');aim(camera,(0,-.015,.4));camera.data.type='ORTHO';camera.data.ortho_scale=1.5;scene.camera=camera
for name,pos,energy,size,color in [('Key',(-1,-1.5,1.6),70,1,(1,.85,.66)),('Fill',(1,-.8,1),40,.8,(.7,.82,1)),('Top',(0,.2,1.5),65,.7,(1,.66,.3))]:
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);cols[current].objects.link(o);o.location=pos;aim(o,(0,0,.4))
scene.world.color=(.05,.05,.05);scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False
scene.render.resolution_x=1280;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.filepath=str(HERE/'final_visual.png');scene.render.image_settings.file_format='PNG'
scene['revision']='V2 | Buildable cabinet layout; conceptual decorative relief and mounting'
scene['dimensions']='Main frame 1200x800 mm; five removable acrylic panels; crown above frame'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_distance=1.7;area.spaces.active.region_3d.view_location=Vector((0,0,.4))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'astra_workshop_v2.blend'))
print('PARTS_MATCHED',len(PARTS))
bpy.ops.render.render(write_still=True)
