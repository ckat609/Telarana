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
from .functions import *


class TelaranaSettings(bpy.types.PropertyGroup):
    THREAD_COUNT : bpy.props.IntProperty(name='Count', default=50, min=2, max=250, step=1, description='Main thread count')
    THREAD_STEPS : bpy.props.IntProperty(name='Subdivisions', default=10, min=5, max=50, step=1, description='Main thread subdivisions')
    THREAD_CONNECTIONS_COUNT : bpy.props.IntProperty(name='Count', default=50, min=2, max=250, step=1, description='Connecthing thread count')
    THREAD_CONNECTIONS_STEPS : bpy.props.IntProperty(name='Subdivisions', default=10, min=0, max=50, step=1, description='Connecting thread subdivisions')
    RECURSION_LEVELS : bpy.props.IntProperty(name='Levels', default=10, min=1, max=250, step=1, description='Recursion levels')
    TEAR_THREADS : bpy.props.BoolProperty(name='Tear threads', default=False)
    THREAD_TEARING_AMOUNT : bpy.props.FloatProperty(name='Ratio', default=1, min=1, max=10, step=0.1, description='Thread tearing amount')
    DELETE_ANNOTATION : bpy.props.BoolProperty(name='Delete annotations', default=False)
    COMBINE_THREADS : bpy.props.BoolProperty(name='Combine threads', default=True)
    COMBINE_THREADS_THRESHOLD : bpy.props.FloatProperty(name='Threshold', default=0.5, min=0, max=1, step=0.01, description='Combine thread vertices threshold')
    BEVEL_DEPTH = bpy.props.IntProperty(name='Thickness', default=3, min=1, step=1, description='Thread thickness in microns')

class TelaranaFunctionsOperator(bpy.types.Operator):
    bl_idname = "object.telarana_functions"
    bl_label = "Run Telaraña Functions"
    bl_options = {"REGISTER", "UNDO"}

    action: bpy.props.EnumProperty(items=[('APPLY_AND_CONVERT_MESH_TO_CURVE', 'Convert mesh to curve', 'Convert mesh to curve')])

    def execute(self, context):
        if(self.action == 'APPLY_AND_CONVERT_MESH_TO_CURVE'):
            bpy.ops.object.modifier_apply(modifier='TelaranaCloth')
            obj = context.active_object
            newObj = convertToCurve(obj)
            addMaterial(obj)
        return {'FINISHED'}


class CreateTelaranaOperator(bpy.types.Operator):
    bl_idname = "object.create_telarana"
    bl_label = "Create Telaraña"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        cs = context.scene.telarana

        SHRINK_FACTOR = 0.0
        BEVEL_DEPTH = .000003#cs.BEVEL_DEPTH/1000000

        obj = createTelaranaObject(
            cs.THREAD_COUNT, cs.THREAD_STEPS, cs.THREAD_CONNECTIONS_COUNT, cs.THREAD_CONNECTIONS_STEPS, cs.RECURSION_LEVELS)
        addClothModifier(obj, SHRINK_FACTOR)

        if cs.TEAR_THREADS:
            tearThreads(obj, cs.THREAD_TEARING_AMOUNT)

        # if cs.COMBINE_THREADS:
        #     combineThreads(obj, cs.COMBINE_THREADS_THRESHOLD)

        if(cs.DELETE_ANNOTATION == 1):
            context.active_annotation_layer.clear()

        return {'FINISHED'}
