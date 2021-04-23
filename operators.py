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


class RunTelaranaFunctionsOperator(bpy.types.Operator):
    bl_idname = "object.run_telarana_functions"
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
        cs = bpy.context.scene

        SHRINK_FACTOR = 0.0
        BEVEL_DEPTH = cs.BEVEL_DEPTH/1000000

        obj = createTelaranaObject(
            cs.THREAD_COUNT, cs.THREAD_STEPS, cs.THREAD_CONNECTIONS_COUNT, cs.THREAD_CONNECTIONS_STEPS, cs.RECURSION_LEVELS)
        addClothModifier(obj, SHRINK_FACTOR)

        if cs.TEAR_THREADS:
            tearThreads(obj, cs.THREAD_TEARING_AMOUNT)

        if cs.COMBINE_THREADS:
            combineThreads(obj, cs.COMBINE_THREADS_THRESHOLD)

        if(cs.DELETE_ANNOTATION == 1):
            context.active_annotation_layer.clear()

        return {'FINISHED'}
