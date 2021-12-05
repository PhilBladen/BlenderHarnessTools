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

from typing import List
import bpy
from bpy.app.handlers import persistent
from bpy.utils import (
        register_class,
        unregister_class
        )
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        Scene,
        WindowManager,
        Curve
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
    ValidateCableBendRadii,
    MakeCable
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

    # def on_load(self):
    #     print("ONLOAD")

classes = (
    Test_OT_Operator,
    Test_PT_Panel,
    #ValidateCableBendRadii,
    SetCableDiameter,
    HarnessPropertyGroup,
    MakeCable
    )

def update_cable_diameter(self, context):
    active_object = context.active_object
    assert active_object.type == "CURVE"
    curve = active_object.data
    assert isinstance(curve, bpy.types.Curve)
    
    curve.bevel_depth = curve.cable_diameter / 2000 # units mm
    splines: List[bpy.types.Spline] = curve.splines
    for spline in splines:
        bezier_points: List[bpy.types.BezierSplinePoint] = spline.bezier_points
        for point in bezier_points:
            point.radius = 1

# if hasattr(bpy.context.window_manager, "harnesstoolsenabled"):
    # bpy.context.window_manager.harnesstoolsenabled = "DI"

# @persistent
# def load_post_handler(dummy):
    # print("Event: load_post", bpy.data.filepath)
    # bpy.context.window_manager.harnesstoolsenabled = "EN"
    # check_enabled(dummy, bpy.context)

def register():
    for c in classes:
        register_class(c)

    # bpy.app.handlers.load_post.append(load_post_handler)

    Scene.harnesstools = PointerProperty(type=HarnessPropertyGroup)
    # bpy.context.scene.harnesstools.property_unset("enabled")

    Curve.is_cable = BoolProperty(
        default=False
    )

    Curve.minimum_curve_radius = FloatProperty(
        name = "Min. bend radius",
        default = 0.01,
        min = 0,
        unit="LENGTH"
    )

    Curve.cable_diameter = FloatProperty(
        name = "Wire diameter",
        # default = 0.002,
        soft_min = 0.1,
        # soft_max = 0.01,
        # step=0.0001,
        # unit="LENGTH",
        subtype="DISTANCE_CAMERA",
        update=update_cable_diameter
    )

    WindowManager.harnesstoolsenabled = EnumProperty(
        name="Curvature check",
        description="Automatic cable minimum bend radius validation",
        items=[ ('DI', "Disabled", ""),
                ('EN', "Enabled", "")],
        # default="DI",
        options={"SKIP_SAVE"},
        update=check_enabled,
        # get=get_enabled,
        # set=setter,
    )
    # WindowManager.harnesstoolsenabled = "DI"

    # bpy.types.WindowManager.harnesstoolsenabled = None

def unregister():
    bpy.context.window_manager.harnesstoolsenabled = "DI"
    del WindowManager.harnesstoolsenabled
    del bpy.types.Scene.harnesstools
    
    # bpy.app.handlers.load_post.remove(load_post_handler)

    ValidateCableBendRadii.unregsiter_handlers()
    for c in classes:
        unregister_class(c)
