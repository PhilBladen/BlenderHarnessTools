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

from . operators import (
    Test_OT_Operator,
    SetCableDiameter,
    ValidateCableBendRadii
)
from . test_panel import Test_PT_Panel

v = ValidateCableBendRadii()

def check_enabled(self, context):
    enabled = bpy.context.window_manager.harnesstoolsenabled == "EN"
    if enabled:
        args = (v, context)
        v.register_handlers(args, context)
    else:
        v.unregsiter_handlers()

class HarnessPropertyGroup(PropertyGroup):
    # def get_enabled(self):
    #     # if not hasattr(self, "boo"):
    #         # self.boo = "random"
    #         # return 1
    #     return self["enabled"]

    # def setter(self, value):
    #     self["enabled"] = value


    color: FloatVectorProperty(
        name="Line colour",
        default=(1.0, 0.0, 0.0, 1),
        size=4,
        subtype="COLOR",
        min=0,
        max=1
    )
    line_width: IntProperty(
        name = "Line width",
        default = 1,
        min = 1,
        max = 10,
        subtype="PIXEL"
    )
    cable_diameter: FloatProperty(
        name = "Diameter",
        # default = 0.002,
        soft_min = 0.1,
        # soft_max = 0.01,
        # step=0.0001,
        # unit="LENGTH",
        subtype="DISTANCE_CAMERA"
    )

    # def on_load(self):
    #     print("ONLOAD")

classes = (
    Test_OT_Operator,
    Test_PT_Panel,
    #ValidateCableBendRadii,
    SetCableDiameter,
    HarnessPropertyGroup
    )

def register():
    for c in classes:
        register_class(c)
    Scene.harnesstools = PointerProperty(type=HarnessPropertyGroup)
    # bpy.context.scene.harnesstools.property_unset("enabled")

    bpy.types.Curve.minimum_curve_radius = FloatProperty(
        name = "Min. bend radius",
        default = 0.01,
        min = 0,
        unit="LENGTH"
    )

    bpy.types.WindowManager.harnesstoolsenabled = EnumProperty(
        name="Curvature check",
        description="Automatic cable minimum bend radius validation",
        items=[ ('EN', "Enabled", ""),
                ('DI', "Disabled", "")],
        # default="DI",
        options={"SKIP_SAVE"},
        update=check_enabled,
        # get=get_enabled,
        # set=setter,
    )

    # bpy.types.WindowManager.harnesstoolsenabled = None

def unregister():
    ValidateCableBendRadii.unregsiter_handlers()
    for c in classes:
        unregister_class(c)
    del bpy.types.WindowManager.harnesstoolsenabled
    del bpy.types.Scene.harnesstools
