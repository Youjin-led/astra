import bpy, math, os, random
from mathutils import Vector

OUT=os.path.dirname(os.path.abspath(__file__))
random.seed(19)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.length_unit='MILLIMETERS'
cols={}
for name in ['01_Back_18mm','02_Boxes_15mm','03_Carved_frame_concept','04_Brass_letters','05_Acrylic_4mm','06_LED_2800K','07_Trophy_placeholders','08_Portrait_placeholder','09_Wall_mount','10_Presentation']:
    c=bpy.data.collections.new(name); scene.collection.children.link(c); cols[name]=c
current='01_Back_18mm'
serif=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf')
def put(o,name):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    cols[current].objects.link(o)
    return o
def mat(name,color,metal=0,rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m
wood=mat('Walnut • procedural grain',(.15,.065,.021),0,.35)
n=wood.node_tree.nodes; l=wood.node_tree.links
tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=7; tex.inputs['Detail'].default_value=3
coord=n.new('ShaderNodeTexCoord'); mapping=n.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=(3,5,65)
l.new(coord.outputs['Generated'],mapping.inputs[0]); l.new(mapping.outputs[0],tex.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.18; ramp.color_ramp.elements[0].color=(.025,.009,.003,1); ramp.color_ramp.elements[1].color=(.28,.115,.035,1)
l.new(tex.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs[0],n.get('Principled BSDF').inputs['Base Color'])
bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.2; bump.inputs['Distance'].default_value=.0007; l.new(tex.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],n.get('Principled BSDF').inputs['Normal'])
carved=mat('Carved walnut highlights',(.32,.145,.047),0,.38)
brass=mat('Brushed brass',(.64,.38,.09),.78,.27)
dark=mat('Black velvet',(.009,.012,.01),0,.85)
glass=mat('Clear acrylic',(.82,.93,1),0,.08)
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=1
glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.49
led=mat('LED warm white 2800K',(1,.49,.15))
led.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1,.43,.1,1)
led.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=6
def cube(name,pos,size,m,bev=.0015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos); o=put(bpy.context.object,name); o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bev:
        mod=o.modifiers.new('Soft machined edges','BEVEL'); mod.width=bev; mod.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def path(name,points,m,r=.003,closed=False):
    d=bpy.data.curves.new(name,'CURVE'); d.dimensions='3D'; d.resolution_u=16; d.bevel_depth=r; d.bevel_resolution=3
    s=d.splines.new('BEZIER'); s.bezier_points.add(len(points)-1)
    for p,v in zip(s.bezier_points,points): p.co=v; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    s.use_cyclic_u=closed; o=bpy.data.objects.new(name,d); cols[current].objects.link(o); d.materials.append(m); return o
def text(name,body,x,z,size,m=brass,y=-.100):
    d=bpy.data.curves.new(name,'FONT'); d.body=body; d.font=serif; d.align_x='CENTER'; d.align_y='CENTER'; d.size=size; d.extrude=.0012; d.bevel_depth=.00035
    o=bpy.data.objects.new(name,d); cols[current].objects.link(o); o.location=(x,y,z); o.rotation_euler=(math.pi/2,0,0); d.materials.append(m); return o
def sphere(name,pos,scale,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=pos); o=put(bpy.context.object,name); o.scale=scale; o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    return o
def cylinder(name,x,y,z,r,depth,m):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=(x,y,z),rotation=(math.pi/2,0,0));o=put(bpy.context.object,name);o.data.materials.append(m);o.modifiers.new('Edge bevel','BEVEL').width=.0008;return o
cube('1200 x 800 x 18 mm load bearing plywood',(0,.009,.4),(1.2,.018,.8),wood)
current='02_Boxes_15mm'
# Front is -Y; backing front Y=0, internal cabinet depth 70 mm.
for name,x,z,w,h in [('Left upper',-.43,.565,.28,.15),('Left middle',-.43,.4,.28,.15),('Center small',0,.35,.4,.15),('Right vertical',.43,.475,.28,.35),('Lower full width',0,.16,1.16,.2)]:
    cube(name+' velvet back',(x,-.001,z),(w,.002,h),dark,0)
    for xx in [x-w/2-.0075,x+w/2+.0075]: cube(name+' side wall',(xx,-.035,z),(.015,.07,h+.03),wood)
    for zz in [z-h/2-.0075,z+h/2+.0075]: cube(name+' shelf',(x,-.035,zz),(w,.07,.015),wood)
    current='05_Acrylic_4mm'; cube(name+' removable acrylic',(x,-.074,z),(w,.004,h),glass,.0005)
    for xx in [x-w/2+.009,x+w/2-.009]:
        for zz in [z-h/2+.009,z+h/2-.009]: cylinder(name+' magnetic fixing',xx,-.078,zz,.004,.003,brass)
    current='06_LED_2800K'; cube(name+' LED top',(x,-.058,z+h/2-.003),(w-.01,.003,.002),led,.0003)
    for xx in [x-w/2+.003,x+w/2-.003]:cube(name+' LED vertical',(xx,-.058,z),(.002,.003,h-.005),led,.0003)
    data=bpy.data.lights.new(name+' warm illumination','AREA'); data.energy=3; data.color=(1,.57,.26); data.shape='RECTANGLE'; data.size=w; data.size_y=.035
    o=bpy.data.objects.new(name+' warm illumination',data); cols[current].objects.link(o);o.location=(x,-.045,z+h/2-.013)
    current='02_Boxes_15mm'
current='03_Carved_frame_concept'
for x in [-.5775,.5775]:cube('Decorative side stile',(x,-.067,.4),(.045,.034,.8),wood)
for z in [.023,.777]:cube('Decorative horizontal rail',(0,-.067,z),(1.2,.034,.046),wood)
for x in [-.554,.554]:path('Brass frame inlay',[(x,-.086,.05),(x,-.086,.75)],brass,.001)
def leaf(x,z,angle,length=.035):
    # Raised pointed leaf with a curved ridge: concept carving, separate mesh.
    verts=[]; rings=10
    for i in range(rings+1):
        t=i/rings; w=math.sin(math.pi*t)*length*.23
        for side in [-1,0,1]:
            u=side*w; v=t*length
            verts.append((x+u*math.cos(angle)+v*math.sin(angle),-.092-.007*math.sin(math.pi*t)*(1-abs(side)),z-u*math.sin(angle)+v*math.cos(angle)))
    faces=[]
    for i in range(rings):
        for j in range(2):a=i*3+j;faces.append((a,a+1,a+4,a+3))
    me=bpy.data.meshes.new('Leaf relief');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Stylized acanthus leaf',me);cols[current].objects.link(o);me.materials.append(carved)
    mod=o.modifiers.new('Leaf thickness','SOLIDIFY');mod.thickness=.002
    for p in me.polygons:p.use_smooth=True
def scroll(cx,cz,sign=1,r=.055):
    pts=[]
    for i in range(65):
        t=i/64; a=t*math.pi*3.1; rr=r*(1-.9*t);pts.append((cx+sign*rr*math.cos(a),-.092,cz+rr*math.sin(a)))
    path('Acanthus spiral',pts,carved,.004)
    for i in range(7):
        a=i*.42;leaf(cx+sign*r*math.cos(a),cz+r*math.sin(a),sign*(a+.4),.03+i*.001)
for side in [-1,1]:
    for z in [.09,.7]:scroll(side*.525,z,side,.058)
    for x in [.12,.24,.36]:scroll(side*x,.745,side,.034)
    for x in [.16,.32,.43]:scroll(side*x,.04,side,.028)
    for z,suit in zip([.60,.52,.44,.36],['♠','♥','♦','♣']):
        cube('Suit medallion',(side*.577,-.091,z),(.035,.008,.058),dark)
        text('Suit '+suit,suit,side*.577,z,.034,brass,y=-.098)
    cylinder('Poker chip medallion',side*.495,-.086,.714,.043,.011,carved)
    cylinder('Poker chip brass ring',side*.495,-.094,.714,.033,.004,brass)
    cylinder('Poker chip dark center',side*.495,-.097,.714,.027,.004,dark)
    text('Chip spade','♠',side*.495,.714,.032,y=-.102)
    for i in range(12):
        a=i*math.tau/12; o=cube('Chip edge segment',(side*.495+.038*math.cos(a),-.096,.714+.038*math.sin(a)),(.009,.003,.003),brass,.0005);o.rotation_euler[1]=-a
# Portrait arch and curved name banners.
for radius in [.209,.225,.24]:
    pts=[(radius*math.cos(a),-.085,.443+radius*math.sin(a)) for a in [i*math.pi/40 for i in range(41)]];path('Portrait arch',pts,carved,.005)
for side in [-1,1]:
    for i in range(9):
        a=.2+i*.14;leaf(side*.235*math.cos(a),.443+.235*math.sin(a),side*(-a),.032)
def banner(name,width,z,rise,height):
    vertices=[];N=36
    for i in range(N+1):
        x=(i/N-.5)*width; zz=z+rise*(1-(2*x/width)**2)
        vertices.extend([(x,-.083,zz-height/2),(x,-.083,zz+height/2)])
    faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(N)]
    me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);o=bpy.data.objects.new(name,me);cols[current].objects.link(o);me.materials.append(wood);mod=o.modifiers.new('Solid banner','SOLIDIFY');mod.thickness=.014
    for edge in [-1,1]:path('Banner brass border',[(vertices[2*i][0],-.100,z+rise*(1-(2*vertices[2*i][0]/width)**2)+edge*height/2) for i in range(N+1)],brass,.0016)
banner('Champion banner',.36,.711,.024,.05);banner('Curved name banner',.55,.644,.04,.047);banner('Bottom nameplate',.43,.026,0,.035)
current='04_Brass_letters'
text('Champion lettering','CHAMPION',0,.735,.035)
# Individually placed letters follow the curved nameplate.
body='ANATOLY ZLOTNIKOV';spacing=.029
for i,ch in enumerate(body):
    x=(i-(len(body)-1)/2)*spacing;z=.644+.04*(1-(2*x/.55)**2);o=text('Name letter '+str(i),ch,x,z,.028);o.rotation_euler[1]=math.atan(-.08*x/(.55*.55/4))
text('Bottom lettering','ANATOLY ZLOTNIKOV',0,.026,.024)
text('Left brand','WORLD SERIES',-.415,.689,.013);text('Left poker','POKER',-.415,.667,.023)
text('Right brand','TRITON',.411,.689,.017);text('Right poker','POKER',.411,.667,.014)
path('Crown silhouette',[(-.033,-.1,.771),(-.04,-.1,.795),(-.021,-.1,.785),(0,-.1,.811),(.021,-.1,.785),(.04,-.1,.795),(.033,-.1,.771)],brass,.003)
current='08_Portrait_placeholder'
cube('Portrait placeholder backing',(0,-.011,.52),(.39,.012,.19),dark)
sphere('Schematic portrait bust',(0,-.035,.46),(.095,.028,.075),carved)
sphere('Schematic head',(0,-.053,.575),(.032,.021,.043),carved)
sphere('Cap',(0,-.056,.61),(.038,.025,.014),dark)
cube('Cap peak',(0,-.079,.605),(.078,.029,.005),dark)
for side in [-1,1]:
    path('Raised arm placeholder',[(side*.075,-.045,.49),(side*.137,-.043,.515),(side*.15,-.047,.57)],carved,.022)
    sphere('Raised fist placeholder',(side*.15,-.049,.575),(.016,.018,.02),carved)
    cube('Sunglasses lens',(side*.015,-.074,.582),(.025,.003,.012),dark)
text('Placeholder notice','PORTRAIT / SCULPT REQUIRED',0,.436,.009,y=-.082)
current='07_Trophy_placeholders'
def trophy(x,z,h,style=0):
    cube('Trophy plinth',(x,-.032,z+.008),(.034,.031,.016),dark)
    cube('Trophy engraved band',(x,-.05,z+.009),(.027,.001,.007),brass)
    path('Trophy stem',[(x,-.034,z+.018),(x,-.034,z+h*.6)],brass,.003)
    if style%3==0:
        for side in [-1,1]:path('Cup silhouette',[(x,-.034,z+.025),(x+side*.012,-.034,z+h*.60),(x+side*.024,-.034,z+h)],brass,.002)
        path('Cup rim',[(x+.024*math.cos(i*math.tau/32),-.034+.015*math.sin(i*math.tau/32),z+h) for i in range(32)],brass,.0014,True)
    elif style%3==1:cylinder('Award medal',x,-.035,z+h*.72,.024,.004,brass)
    else:text('Spade award','♠',x,z+h*.68,.066,brass,y=-.039)
for i in range(13):trophy(-.53+i*.088,.07,.09+.034*(i%3),i)
for i,x in enumerate([-.50,-.37]):trophy(x,.325,.125,i)
trophy(.35,.31,.19,0);trophy(.51,.31,.16,2)
cube('Champion belt',(0,-.035,.30),(.18,.028,.026),dark);cube('Belt gold centerpiece',(0,-.054,.31),(.058,.008,.035),brass)
text('Belt mark','WSOP',0,.31,.012,dark,y=-.06)
cube('Cap display',(-.43,-.035,.505),(.10,.04,.008),dark);sphere('Champion cap',(-.43,-.031,.528),(.05,.031,.025),dark);text('Cap label','CHAMPION',-.43,.528,.009,y=-.062)
current='09_Wall_mount'
cleat=cube('French cleat upper – bevel to be engineered',(0,.029,.685),(1.06,.022,.045),wood)
for x in [-.53,.53]:
    for z in [.08,.72]:cube('Rear mounting plate',(x,.025,z),(.032,.01,.04),brass)
current='10_Presentation'
floor=mat('Studio charcoal',(.022,.027,.034),0,.75)
cube('Studio floor',(0,0,-.055),(200,200,.02),floor,0)
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.06,-2.35,1.05));camera=put(bpy.context.object,'Presentation camera');aim(camera,(0,-.015,.405));camera.data.type='ORTHO';camera.data.ortho_scale=1.55;scene.camera=camera
for name,pos,energy,size,color in [('Key',(-1,-1.3,1.8),180,1.1,(1,.84,.65)),('Fill',(1,-.8,1),110,.8,(.65,.8,1)),('Top',(0,.15,1.5),120,.7,(1,.65,.3))]:
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);cols[current].objects.link(o);o.location=pos;aim(o,(0,0,.4))
scene.world.color=(.12,.12,.12)
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(OUT,'astra_preview.png')
scene['design_status']='Concept model from reference. Decorative relief, portrait, trophies and mounting are placeholders; not production/CNC approved.'
scene['dimensions_mm']='1200 W x 800 H; plywood back 18, internal box depth 70, walls 15, acrylic 4; crown rises 14 mm beyond nominal frame.'
# Comfortable material-preview view on opening.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_distance=1.7;area.spaces.active.region_3d.view_location=Vector((0,0,.4))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'astra_display.blend'))
bpy.ops.render.render(write_still=True)
print('MODEL_SAVED',len(bpy.data.objects),'objects')
