import bpy
import random
import math
import numpy


def getThreadRoots(strokes):
    s1, s2 = random.sample(list(strokes), k=2)

    p1 = random.choice(list(s1.points))
    p2 = random.choice(list(s2.points))

    return {'p1': tuple(p1.co), 'p2': tuple(p2.co)}


def addThread(roots, steps=5, savePins=False):
    verts = []
    edges = []
    pins = []
    steps += 1
    subdivs = 1/(steps-1)

    v1 = numpy.array(roots['p1'])
    v2 = numpy.array(roots['p2'])
    v3 = v2-v1

    d = math.pow(math.pow(v2[0] - v1[0], 2) + math.pow(v2[1] - v1[1], 2) + math.pow(v2[2] - v1[2], 2), 0.5)
    p = v3/d

    for i in range(steps):
        vertCountStep = v1+(d*(i*subdivs)*p)
        verts.append(tuple(vertCountStep))

        lastVert = steps - 1

        if(i < lastVert):
            edges.append((i, i+1))

        if((i == 0 or i == lastVert) and savePins):
            pins.append(i)

    return {'verts': verts, 'edges': edges, 'pins': pins}


def processThreads(roots, connections=5):
    rootVerts = roots[0]['verts']
    steps = len(rootVerts)
    verts = []
    edges = []
    pins = []

    for t in range(len(roots)):
        tVerts = roots[t]['verts']
        tPins = roots[t]['pins']
        for v in range(len(tVerts)):
            v_idx = v+(t*steps)

            verts.append(tVerts[v])
            lastVert = len(tVerts) - 1

            if(v < lastVert - 1):
                edges.append((v_idx, v_idx+1))

            if((v == 0 or v == lastVert) and (v in tPins)):
                pins.append(v_idx)

    return {'verts': verts, 'edges': edges, 'pins': pins}


def dedupeVerts(mesh):
    res = [idx for idx, val in enumerate(mesh) if val in mesh[:idx]]

    return True


class CreateTelaranaOperator(bpy.types.Operator):
    bl_idname = "object.create_telarana"
    bl_label = "Create Telarana"

    def execute(self, context):
        THREAD_COUNT = 3
        THREAD_CONNECTIONS = 10
        THREAD_STEPS = 5
        THREAD_CONNECTION_STEPS = 3

        roots = []

        layers = bpy.context.scene.grease_pencil.layers
        strokes = layers.active.active_frame.strokes

        for i in range(THREAD_COUNT):
            threadRoots = getThreadRoots(strokes)
            roots.append(addThread(threadRoots, THREAD_STEPS, True))

        for j in range(THREAD_CONNECTIONS):
            l1, l2 = random.sample(roots, k=2)
            # p1 = random.sample(list(enumerate(l1['verts'])), k=1)
            # p2 = random.sample(list(enumerate(l2['verts'])), k=1)

            randVert1 = random.randrange(1, len(l1['verts']) - 1)
            randVert2 = random.randrange(1, len(l2['verts']) - 1)
            p1 = l1['verts'][randVert1]
            p2 = l2['verts'][randVert2]

            # p1 = l1[1]['verts']
            # p2 = l2[1]['verts']
            # print(f"RV1: {randVert1}\nRV2: {randVert2}")
            print(f"L1: {l1}\nL2: {l2}")
            print(f"P1: {p1}\nP2: {p2}")

            roots.append(addThread({'p1': p1, 'p2': p2}, steps=THREAD_CONNECTION_STEPS))

        mainThreads = processThreads(roots, THREAD_CONNECTIONS)

        meshTelarana = bpy.data.meshes.new("Telarana")
        objTelarana = bpy.data.objects.new("Telarana", meshTelarana)
        bpy.context.collection.objects.link(objTelarana)

        objTelarana.vertex_groups.new(name='pins')

        meshTelarana.from_pydata(mainThreads['verts'], mainThreads['edges'], [])
        meshTelarana.update()

        objTelarana.vertex_groups['pins'].add(mainThreads['pins'], 1.0, 'ADD')

        return {'FINISHED'}
