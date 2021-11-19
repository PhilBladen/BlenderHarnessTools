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

bl_info = {
    "name" : "STAR-XL Utils",
    "author" : "Phil Bladen",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

import bpy
import bgl
import gpu
from gpu_extras.batch import batch_for_shader

from . test_op import Test_OT_Operator
from . test_op import Test_OT_SelectCurvesOperator
from . test_panel import Test_PT_Panel

classes = (Test_OT_Operator, Test_PT_Panel, Test_OT_SelectCurvesOperator)

register, unregister = bpy.utils.register_classes_factory(classes)


# coords = [(0, 0, 0), (0, 0, 10)]
# shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
# batch = batch_for_shader(shader, 'LINES', {"pos": coords})

# def draw():
#     bgl.glLineWidth(5)
#     shader.bind()
#     shader.uniform_float("color", (1, 0, 0, 1))
#     batch.draw(shader)

# bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')

# def register():
#     ...

# def unregister():
#     ...
