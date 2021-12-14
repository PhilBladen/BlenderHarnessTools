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
    "name" : "Harness Tools",
    "author" : "Phil Bladen",
    "description" : "Adds functionality for managing cables, including cable diameter and minimum bend radius.",
    "blender" : (3, 0, 0),
    "version" : (0, 1, 1),
    "location" : "Properties > Data > Harness Tools",
    "warning" : "Alpha WIP - likely to contain bugs",
    "category" : "Generic"
}

from typing import List

import bpy
from bpy.utils import (
        register_class,
        unregister_class
        )
from bpy.types import (
        PropertyGroup,
        Scene,
        WindowManager,
        Curve,
        BezierSplinePoint,
        Spline,
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
from . control_panel import HARNESS_PT_Panel

v = ValidateCableBendRadii()

def check_enabled(self, context):
    enabled = bpy.context.window_manager.harnesstoolsenabled == "EN"
    if enabled:
        args = (v, context)
        v.register_handlers(args, context)
    else:
        v.unregsiter_handlers()

class HarnessPropertyGroup(PropertyGroup):
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

def update_cable_diameter(self, context):
    active_object = context.active_object
    assert active_object.type == "CURVE"
    curve = active_object.data
    assert isinstance(curve, Curve)
    
    curve.bevel_depth = curve.cable_diameter / 2000 # units mm
    splines: List[Spline] = curve.splines
    for spline in splines:
        bezier_points: List[BezierSplinePoint] = spline.bezier_points
        for point in bezier_points:
            point.radius = 1

classes = (
    Test_OT_Operator,
    HARNESS_PT_Panel,
    SetCableDiameter,
    HarnessPropertyGroup,
    MakeCable
    )

def register():
    for c in classes:
        register_class(c)

    Scene.harnesstools = PointerProperty(type=HarnessPropertyGroup)

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
        soft_min = 0.1,
        subtype="DISTANCE_CAMERA",
        update=update_cable_diameter
    )

    WindowManager.harnesstoolsenabled = EnumProperty(
        name="Curvature check",
        description="Automatic cable minimum bend radius validation",
        items=[ ('DI', "Disabled", ""),
                ('EN', "Enabled", "")],
        options={"SKIP_SAVE"},
        update=check_enabled,
    )

def unregister():
    bpy.context.window_manager.harnesstoolsenabled = "DI"
    del WindowManager.harnesstoolsenabled
    del Scene.harnesstools

    ValidateCableBendRadii.unregsiter_handlers()
    for c in classes:
        unregister_class(c)
