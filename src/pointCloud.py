import os
import bpy
import bmesh
import math

#--------------------------------------------------------------------#
def prepareMaterial():
    #create the material which is used for coloring
    found = mat_name in bpy.data.materials
    if found == True:
        return
    bpy.data.materials.new(name=mat_name)

#--------------------------------------------------------------------#
def prepareHelperGeometry():
    #create parent object to which the particles are attached (0,0,0) root_name 오브젝트를 만들어 냄
    found = root_name in bpy.data.objects
    if found == True:
        obj = bpy.data.objects[root_name]
        return
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    obj = bpy.context.active_object
    obj.name = root_name
    obj.location = (0, 0, 0)
    return obj

#--------------------------------------------------------------------#
def prepareParticleMesh():
    #--- create mesh which is copied later on for each particle
    #    the effort for copying the vertex data is needed for the
    #    definition of the UV-texture coordinates later on
    #first check if it exists already
    found = mesh_name in bpy.data.meshes
    if found == True:
        mesh = bpy.data.meshes[mesh_name]
        return mesh

    #if not create a base sphere to use its geometry
    parentObj = root_obj
    temp_name = "sphere_geo"
    #start with a helper geometry
    sphere = bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=4, size=1)
    geoObj = bpy.context.active_object
    geoObj.name = temp_name
    #access vertices and faces
    verts = [vert.co for vert in geoObj.data.vertices]
    plain_verts = [vert.to_tuple() for vert in verts]
    faces = []
    for polygon in geoObj.data.polygons:
        faces.append(polygon.vertices[:])
    #bind created geometry to global mesh
    mesh = bpy.data.meshes.new(mesh_name)
    mesh.from_pydata(verts, [], faces)
    mesh.validate(True)
    mesh.show_normal_face = True
    #remove helper geometry
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[temp_name].select = True
    bpy.ops.object.delete()

    return mesh

#--------------------------------------------------------------------#
def loadPointDataFile(count):
    file = open(data_file, "r")
    content = file.readlines()[:count]
    file.close()
    return content

#--------------------------------------------------------------------#
def parseData(data):
    #deselect all other objects if any
    for obj in bpy.data.objects:
        obj.select = False

    i = 0
    for line in data:
        numbers_str = line.split()
        numbers_float = [float(x) for x in numbers_str]
        sphere = createParticleObject(numbers_float)
        sphere.parent = root_obj

        t0  = numbers_float[3]
        tau = numbers_float[4]
        #set material
        setUVTextures(sphere.data, mat_name, t0, tau)
        sphere.select = True

        #print some progress info
        i=i+1
        if (i%100 == 0):
            #join the created objects to a single one
            bpy.context.scene.objects.active = bpy.data.objects[sphere.name]
            bpy.ops.object.join()
            print("read {} points".format(i))

#--------------------------------------------------------------------#
def createParticleObject(rec_pnt):
    mesh = base_mesh.copy()
    obj = bpy.data.objects.new("particle", mesh)
    bpy.context.scene.objects.link(obj)
    obj.scale = sphere_scale

    x = rec_pnt[0]
    y = rec_pnt[1]
    z = rec_pnt[2]

    obj.location = x, y, z
    return obj

#--------------------------------------------------------------------#
def setUVTextures(particle_data, mat_name, t0, tau):
    particle_data.materials.append(bpy.data.materials[mat_name])
    #t0 and tau define the coloring encoded in texture coordinates
    #map the values to [0.0, 1.0] intervals for u and v
    u = (t0 - t0_min) / (t0_max - t0_min);
    v = (tau - tau_min) / (tau_max - tau_min);
    #clamp to [0.0, 1.0]
    u = min(1.0, max(u, 0.0));
    v = min(1.0, max(v, 0.0));
    #create uv-coordintes
    particle_data.uv_textures.new("t0_texture")
    bm = bmesh.new()
    bm.from_mesh(particle_data)
    bm.faces.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv[0]

    nFaces = len(bm.faces)
    for fi in range(nFaces):
        bm.faces[fi].loops[-1][uv_layer].uv = (u,v)
        bm.faces[fi].loops[ 0][uv_layer].uv = (u,v)
        bm.faces[fi].loops[ 1][uv_layer].uv = (u,v)
        bm.faces[fi].loops[ 2][uv_layer].uv = (u,v)
    bm.to_mesh(particle_data)

#--------------------------------------------------------------------#
#---                 define some global variables                 ---#
#define the location of the data file
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_file  = script_dir + "/point_data.txt"

mat_name  = "particle_material"
root_name = "particle_root"
mesh_name = "base_mesh"
data      = None    #holds a list with the loaded data

#scaling factors needed for coloring and particle size
t0_min = 0.0
t0_max = 10.0
tau_min = 0.0
tau_max = 10.0
sphere_scale = (0.025, 0.025, 0.025)

#---                         do the magic                          ---#
#create needed stuff 매터리얼이 없으면 만들어 놓음. 칼라를 입히기 위해서
prepareMaterial();
root_obj  = prepareHelperGeometry()  #particles are attached to this  기준 좌표 (0,0,0)
base_mesh = prepareParticleMesh()     #is copied for each particle

#data = loadPointDataFile(100)     #read first 100 particles
data = loadPointDataFile(10000)   #read first 1000 particles
print(data)
parseData(data)