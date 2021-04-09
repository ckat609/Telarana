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


def processThreads(acc, thread):
    verts = acc['verts'] + thread['verts']
    l = len(acc['verts'])

    lt2 = len(thread2['edges'])-1
    i = 0

    # edges = [(edge[0]+l, edge[1]+l) for edge in thread2['edges']]
    edges = []
    for edge in thread2['edges']:
        found1 = None
        found2 = None

        if i == 0:
            try:
                found1 = thread1['verts'].index(thread2['verts'][edge[0]])
                # print(f"PASS1: {thread1['verts'][found1]} - {thread2['verts'][edge[0]]}")
            except ValueError:
                pass

        if i == lt2:
            print(f"{thread2['verts'][edge[1]]}")
            try:
                found2 = thread1['verts'].index(thread2['verts'][edge[1]])
                print(f"PASS2: {thread1['verts'][found2]} - {thread2['verts'][edge[1]]}")
            except ValueError:
                pass

        edges.append((found1 or edge[0]+l, found2 or edge[1]+l))
        i += 1

    pins = [n+l for n in thread2['pins']]

    return {'verts': verts, 'edges': acc['edges'] + edges, 'pins': acc['pins'] + pins}


class CreateTelaranaOperator(bpy.types.Operator):
    bl_idname = "object.create_telarana"
    bl_label = "Create Telarana"

    def execute(self, context):
        THREAD_COUNT = 150
        THREAD_STEPS = 20
        THREAD_CONNECTIONS_COUNT = 100
        THREAD_CONNECTIONS_STEPS = 10

        mainThreads = []
        connectedThreads = []

        layers = bpy.context.scene.grease_pencil.layers
        strokes = layers.active.active_frame.strokes

        for i in range(THREAD_COUNT):
            threadRoots = getThreadRoots(strokes)
            mThread = addThread(threadRoots, THREAD_STEPS)
            mThread['pins'] = makePins(mThread)
            mainThreads.append(mThread)

        for j in range(THREAD_CONNECTIONS_COUNT):
            l1, l2 = random.sample(mainThreads, k=2)

            randVert1 = random.randrange(1, len(l1['verts']) - 1)
            randVert2 = random.randrange(1, len(l2['verts']) - 1)
            p1 = l1['verts'][randVert1]
            p2 = l2['verts'][randVert2]

            cThread = addThread({'p1': p1, 'p2': p2}, THREAD_CONNECTIONS_STEPS)
            connectedThreads.append(cThread)

        allThreads = mainThreads + connectedThreads
        mesh = reduce(processThreads, allThreads, {
                      'verts': [], 'edges': [], 'pins': []})

        meshTelarana = bpy.data.meshes.new("Telarana")
        objTelarana = bpy.data.objects.new("Telarana", meshTelarana)
        bpy.context.collection.objects.link(objTelarana)

        objTelarana.vertex_groups.new(name='pins')

        meshTelarana.from_pydata(mesh['verts'], mesh['edges'], [])
        meshTelarana.update()

        objTelarana.vertex_groups['pins'].add(mesh['pins'], 1.0, 'ADD')

        return {'FINISHED'}
