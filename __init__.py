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
from bpy.utils import (
        register_class,
        unregister_class
        )
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        Scene
        )
from bpy.props import (
        BoolProperty,
        IntProperty,
        FloatProperty,
        EnumProperty,
        CollectionProperty,
        StringProperty,
        FloatVectorProperty,
        PointerProperty
        )

from . test_op import Test_OT_Operator
from . test_op import ValidateCableBendRadii
from . test_panel import Test_PT_Panel

class HarnessPropertyGroup(PropertyGroup):
    custom_1: FloatProperty(name="My Float")
    custom_2: IntProperty(name="My Int")
    enabled: bpy.props.EnumProperty(
        name="Validate",
        description="Apply Data to attribute.",
        items=[ ('EN', "Enabled", ""),
                ('DI', "Disabled", "")])
    color: FloatVectorProperty(
        name="Colour",
        default=(0.2, 0.9, 0.9, 1),
        size=4,
        subtype="COLOR",
        min=0,
        max=1
    )
    line_width: IntProperty(
        name = "Line width",
        default = 1,
        min = 1,
        max = 10
    )

classes = (
    Test_OT_Operator,
    Test_PT_Panel,
    ValidateCableBendRadii,
    HarnessPropertyGroup
    )

def register():
    for c in classes:
        register_class(c)
    Scene.harnesstools = PointerProperty(type=HarnessPropertyGroup)

def unregister():
    ValidateCableBendRadii.unregsiter_handlers()
    for c in classes:
        unregister_class(c)
