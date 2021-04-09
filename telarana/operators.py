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

        randVert1 = random.randrange(1, len(l1['verts']) - 1)
        randVert2 = random.randrange(1, len(l2['verts']) - 1)
        p1 = l1['verts'][randVert1]
        p2 = l2['verts'][randVert2]

        cThread = addThread({'p1': p1, 'p2': p2}, threadSteps)
        connectedThreads.append(cThread)

    return connectedThreads


def createThreadsRecursively(threads, threadCount, threadSteps, count):
    if(count <= 0):
        return threads

    newThreads = threads + createConnectingThreads(threads, threadCount, threadSteps)

    return createThreadsRecursively(newThreads, threadCount, threadSteps, count-1)


def createThreadsRecursivelyWill(threads, threadCount, threadSteps, count):
    if(count <= 0):
        return threads

    newThreads = createConnectingThreads(threads, threadCount, threadSteps)

    return threads + createThreadsRecursively(newThreads, threadCount, threadSteps, count-1)


class CreateTelaranaOperator(bpy.types.Operator):
    bl_idname = "object.create_telarana"
    bl_label = "Create Telarana"

    def execute(self, context):
        THREAD_COUNT = 5
        THREAD_STEPS = 10
        THREAD_CONNECTIONS_COUNT = 5
        THREAD_CONNECTIONS_STEPS = 10
        RECURSION_LEVELS = 100

        mainThreads = []
        connectedThreads = []

        layers = bpy.context.scene.grease_pencil.layers
        strokes = layers.active.active_frame.strokes

        for i in range(THREAD_COUNT):
            threadRoots = getThreadRoots(strokes)
            mThread = addThread(threadRoots, THREAD_STEPS)
            mThread['pins'] = makePins(mThread)
            mainThreads.append(mThread)

        connectedThreads = createThreadsRecursivelyWill(mainThreads, THREAD_CONNECTIONS_COUNT, THREAD_CONNECTIONS_STEPS, RECURSION_LEVELS)

        allThreads = mainThreads + connectedThreads
        mesh = reduce(processThreads, allThreads, {'verts': [], 'edges': [], 'pins': []})
        connectedMesh = connectThreads(mesh)

        meshTelarana = bpy.data.meshes.new("Telarana")
        objTelarana = bpy.data.objects.new("Telarana", meshTelarana)
        bpy.context.collection.objects.link(objTelarana)

        objTelarana.vertex_groups.new(name='pins')

        meshTelarana.from_pydata(connectedMesh['verts'], connectedMesh['edges'], [])
        meshTelarana.update()

        objTelarana.vertex_groups['pins'].add(connectedMesh['pins'], 1.0, 'ADD')

        return {'FINISHED'}
