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
from .operators import *

bl_info = {
    "name": "Telaraña",
    "author": "Armando Tello, Will Wright",
    "blender": (2, 92, 0),
    "version": (1, 0, 0),
    "description": "Generates a cobweb using the current grease pencil layer strokes",
    "location": "VIEW3D > OBJECT",
    "category": "Object",
    "website": "www.armandotello.com"
}

classesToRegisterUnregister = [
    CreateTelaranaOperator,
    RunTelaranaFunctionsOperator,
    VIEW3D_PT_AnnotateTelarana,
    VIEW3D_PT_GenerateTelarana,
    VIEW3D_PT_SimulateTelarana,
    VIEW3D_PT_ConvertTelarana,
]


def register():
    for c in classesToRegisterUnregister:
        bpy.utils.register_class(c)


def unregister():
    for c in classesToRegisterUnregister:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
