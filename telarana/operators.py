# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import random
import math
import numpy
from functools import reduce


def getThreadRoots(strokes):
    s1, s2 = random.sample(list(strokes), k=2)

    p1 = random.choice(list(s1.points))
    p2 = random.choice(list(s2.points))

    return {'p1': tuple(p1.co), 'p2': tuple(p2.co)}


def addThread(roots, segments=5):
    verts = []
    edges = []
    pins = []
    vCount = segments + 1
    subdivs = 1/(segments)

    v1 = numpy.array(roots['p1'])
    v2 = numpy.array(roots['p2'])
    v3 = v2-v1

    d = math.pow(math.pow(v2[0] - v1[0], 2) + math.pow(v2[1] -
                 v1[1], 2) + math.pow(v2[2] - v1[2], 2), 0.5)
    p = v3/d

    for i in range(vCount):
        lastVert = vCount - 1

        vertCount = v2 if i == lastVert else v1+(d*(i*subdivs)*p)
        verts.append(tuple(vertCount))

        if(i < lastVert):
            edges.append((i, i+1))
    return {'verts': verts, 'edges': edges, 'pins': []}


def makePins(thread):
    return [0, len(thread['verts'])-1]


def connectThreads(mesh):
    vertLookup = {}
    outputVerts = []

    for vert in mesh['verts']:
        if vert not in vertLookup:
            vertLookup[vert] = len(outputVerts)
            outputVerts.append(vert)

    outputEdges = []

    for edge in mesh['edges']:
        v1 = mesh['verts'][edge[0]]
        v2 = mesh['verts'][edge[1]]
        outputEdges.append((vertLookup[v1], vertLookup[v2]))

    outputPins = []

    for pin in mesh['pins']:
        v = mesh['verts'][pin]
        outputPins.append(vertLookup[v])

    return {'verts': outputVerts, 'edges': outputEdges, 'pins': outputPins}


def processThreads(acc, thread):
    verts = acc['verts'] + thread['verts']
    l = len(acc['verts'])

    edges = [(edge[0]+l, edge[1]+l) for edge in thread['edges']]
    pins = [n+l for n in thread['pins']]

    return {'verts': verts, 'edges': acc['edges'] + edges, 'pins': acc['pins'] + pins}


def createConnectingThreads(threads, threadCount, threadSteps):
    connectedThreads = []

    for j in range(threadCount):
        l1, l2 = random.sample(threads, k=2)

        firstLastVert = 0
        randVert1 = random.randrange(
            firstLastVert, len(l1['verts']) - firstLastVert)
        randVert2 = random.randrange(
            firstLastVert, len(l2['verts']) - firstLastVert)
        p1 = l1['verts'][randVert1]
        p2 = l2['verts'][randVert2]

        cThread = addThread({'p1': p1, 'p2': p2}, threadSteps)
        connectedThreads.append(cThread)

    return connectedThreads


def createThreadsRecursively(threads, threadCount, threadSteps, count):
    if(count <= 0):
        return threads

    newThreads = threads + \
        createConnectingThreads(threads, threadCount, threadSteps)

    return createThreadsRecursively(newThreads, threadCount, threadSteps, count-1)


def createThreadsRecursivelyWill(threads, threadCount, threadSteps, count):
    if(count <= 0):
        return threads

    newThreads = createConnectingThreads(threads, threadCount, threadSteps)

    return threads + createThreadsRecursively(newThreads, threadCount, threadSteps, count-1)


def createMainThreads(strokes, threadCount, threadSteps):
    mainThreads = []
    for i in range(threadCount):
        threadRoots = getThreadRoots(strokes)
        thread = addThread(threadRoots, threadSteps)
        thread['pins'] = makePins(thread)
        mainThreads.append(thread)
    return mainThreads


def createTelaranaObject(threadCount, threadSteps, threadConnectionCount, threadConnectionSteps, recursionsLevels):
    layers = bpy.context.scene.grease_pencil.layers
    strokes = layers.active.active_frame.strokes

    mainThreads = createMainThreads(strokes, threadCount, threadSteps)
    connectedThreads = createThreadsRecursivelyWill(
        mainThreads, threadConnectionCount, threadConnectionSteps, recursionsLevels)

    allThreads = mainThreads + connectedThreads
    mesh = reduce(processThreads, allThreads, {
                  'verts': [], 'edges': [], 'pins': []})
    connectedMesh = connectThreads(mesh)

    meshTelarana = bpy.data.meshes.new("Telarana")
    objTelarana = bpy.data.objects.new("Telarana", meshTelarana)
    bpy.context.collection.objects.link(objTelarana)

    objTelarana.vertex_groups.new(name='pins')

    meshTelarana.from_pydata(
        connectedMesh['verts'], connectedMesh['edges'], [])
    meshTelarana.update()

    objTelarana.vertex_groups['pins'].add(connectedMesh['pins'], 1.0, 'ADD')
    objTelarana["Telarana"] = 1

    bpy.context.view_layer.objects.active = objTelarana
    objTelarana.select_set(True)

    return objTelarana


def addClothModifier(obj, shrink):
    mod = obj.modifiers.new('Telarana', 'CLOTH')
    mod.settings.vertex_group_mass = "pins"
    mod.settings.shrink_min = shrink
    mod.settings.bending_model = 'LINEAR'

    return mod


def addMaterial(obj):
    mat = bpy.data.materials.get('Telarana')

    if mat is None:
        mat = bpy.data.materials.new('Telarana')
    obj.data.materials.append(mat)

    mat.use_nodes = True

    if mat.node_tree.nodes.get('ShaderNodeBsdfTranslucent') is not None:
        mat.node_tree.nodes.remove(mat.node_tree.nodes.get('Principled BSDF'))
        matOut = mat.node_tree.nodes.get('Material Output')
        translucent = mat.node_tree.nodes.new('ShaderNodeBsdfTranslucent')
        translucent.inputs['Color'].default_value = (1, 1, 1, 1)
        mat.node_tree.links.new(matOut.inputs[0], translucent.outputs[0])

    return mat


class CreateTelaranaOperator(bpy.types.Operator):
    bl_idname = "object.create_telarana"
    bl_label = "Create Telarana"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        cs = bpy.context.scene
        THREAD_COUNT = cs.THREAD_COUNT
        THREAD_STEPS = cs.THREAD_STEPS
        THREAD_CONNECTIONS_COUNT = cs.THREAD_CONNECTIONS_COUNT
        THREAD_CONNECTIONS_STEPS = cs.THREAD_CONNECTIONS_STEPS
        RECURSION_LEVELS = cs.RECURSION_LEVELS

        SHRINK_FACTOR = 0.3
        BEVEL_DEPTH = cs.BEVEL_DEPTH/1000000

        obj = createTelaranaObject(
            THREAD_COUNT, THREAD_STEPS, THREAD_CONNECTIONS_COUNT, THREAD_CONNECTIONS_STEPS, RECURSION_LEVELS)
        addClothModifier(obj, SHRINK_FACTOR)
        addMaterial(obj)

        if(cs.DELETE_ANNOTATION == 1):
            context.active_annotation_layer.clear()

        return {'FINISHED'}


class VIEW3D_PT_TelaranaAnnotations(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Telarana"
    bl_label = "Annotations"
    bl_idname = "VIEW3D_PT_TelaranaAnnotations"
    bl_order = 0

    def draw(self, context):
        gpl = context.active_annotation_layer
        gpd = context.annotation_data
        scene = context.scene
        tool_settings = context.tool_settings
        # tool_settings.annotation_stroke_placement_view3d = 'SURFACE'
        text = gpd.layers.active_note

        layout = self.layout
        split = layout.split()

        layout.label(text="Color")
        row = layout.row(align=True)
        row.prop(gpl, 'color', text='')
        row.popover('TOPBAR_PT_annotation_layers', text=text)

        layout.separator()

        row = layout.row(align=True)
        row.prop(tool_settings, "annotation_stroke_placement_view3d",
                 text="Placement")


class VIEW3D_PT_TelaranaSim(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Telarana"
    bl_label = "Simulation"
    bl_idname = "VIEW3D_PT_TelaranaSim"
    bl_order = 3

    bpy.types.Scene.BEVEL_DEPTH = bpy.props.IntProperty(
        name='Thickness', default=3, min=1, step=1, description='Thread thickness in microns')

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        split = layout.split()
        modTelarana = bpy.data.objects[context.object.name].modifiers["Telarana"]
        col = split.column()
        col.label(text="Tension")
        col.prop(modTelarana.settings, 'shrink_min', text='')

        col.label(text="Collisions")
        col.prop(modTelarana.collision_settings,
                 'use_collision', text='Enable object collisions')
        col.prop(modTelarana.collision_settings,
                 'use_self_collision', text='Enable self collisions')

    @classmethod
    def poll(cls, context):
        return context.object is not None and "Telarana" in context.object


class VIEW3D_PT_CreateTelarana(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Telarana"
    bl_label = "Generate"
    bl_idname = "VIEW3D_PT_CreateTelarana"
    bl_order = 2

    scene = bpy.types.Scene

    scene.THREAD_COUNT = bpy.props.IntProperty(
        name='Count', default=5, min=2, max=250, step=1, description='Main thread count')
    scene.THREAD_STEPS = bpy.props.IntProperty(
        name='Subdivisions', default=10, min=5, max=50, step=1, description='Main thread subdivisions')
    scene.THREAD_CONNECTIONS_COUNT = bpy.props.IntProperty(
        name='Count', default=5, min=2, max=250, step=1, description='Connecthing thread count')
    scene.THREAD_CONNECTIONS_STEPS = bpy.props.IntProperty(
        name='Subdivisions', default=10, min=0, max=50, step=1, description='Connecting thread subdivisions')
    scene.RECURSION_LEVELS = bpy.props.IntProperty(
        name='Levels', default=100, min=1, max=250, step=1, description='Recursion levels')
    scene.DELETE_ANNOTATION = bpy.props.BoolProperty(
        name="Delete annotations", default=False)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        strokes = bpy.context.scene.grease_pencil.layers.active.active_frame.strokes

        if len(strokes) >= 2:
            layout.label(text="Main Threads")
            row = layout.row(align=True)
            row.prop(scene, 'THREAD_COUNT')
            row.prop(scene, 'THREAD_STEPS')

            layout.separator()

            layout.label(text="Connecting Threads")
            row = layout.row(align=True)
            row.prop(scene, 'THREAD_CONNECTIONS_COUNT')
            row.prop(scene, 'THREAD_CONNECTIONS_STEPS')

            layout.separator()

            layout.label(text="Levels")
            row = layout.row()
            row.prop(scene, "RECURSION_LEVELS", text='')

            layout.separator()

            row = layout.row()
            row.prop(scene, 'DELETE_ANNOTATION')

            row = layout.row()
            row.scale_y = 3.0
            row.operator('object.create_telarana', text='Generate')
        else:
            layout.label(
                text="Add at least two strokes",)
