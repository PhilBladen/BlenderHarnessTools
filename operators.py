from typing import (ClassVar, List)
import bpy
import bgl
from bpy_types import (Operator)
from mathutils.geometry import interpolate_bezier
from mathutils import Vector
from gpu.shader import from_builtin
from gpu_extras.batch import batch_for_shader
from bpy.props import (FloatVectorProperty, FloatProperty)

from math import inf
import time

def current_milli_time():
    return round(time.time() * 1000)

class SplineDefinition:
    # See https://www.geeksforgeeks.org/cubic-bezier-curve-implementation-in-c/ for point definition
    # a, b, c and d are the coefficients of the cubic polynomial: P(u)=au^3+bu^2+cu+d
    def __init__(self, p0: Vector, p1: Vector, p2: Vector, p3: Vector) -> None:
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.a = -p0 + 3 * p1 - 3 * p2 + p3
        self.b = 3 * p0 - 6 * p1 + 3 * p2
        self.c = -3 * p0 + 3 * p1
        self.d = p0
    
    # From https://www.geeksforgeeks.org/cubic-bezier-curve-implementation-in-c/
    def interpolate(self, u: float) -> Vector:
        v = 1 - u
        u2 = u * u
        v2 = v * v
        a = v2 * v
        b = 3 * u * v2
        c = 3 * v * u2
        d = u2 * u
        return v2 * v * self.p0 + 3 * u * v2 * self.p1 + 3 * v * u2 * self.p2 + u2 * u * self.p3
        return (a * self.p0.x + b * self.p1.x + c * self.p2.x + d * self.p3.x, 
                a * self.p0.y + b * self.p1.y + c * self.p2.y + d * self.p3.y,
                a * self.p0.z + b * self.p1.z + c * self.p2.z + d * self.p3.z)
    
    # Curvature equation from Computer Graphics & Geometric Modelling by David Salomon
    def get_curvature(self, u: float) -> float:
        Pu = 3 * self.a * u * u + 2 * self.b * u + self.c # First derivative
        Puu = 6 * self.a * u + 2 * self.b # Second derivative
        Pu_mag = Pu.magnitude
        kappa = (Pu.cross(Puu) / (Pu_mag * Pu_mag * Pu_mag)).magnitude
        return kappa
    
    def get_bend_radius(self, u: float) -> float:
        kappa = self.get_curvature(u)
        if kappa == 0:
            return inf
        return 1 / kappa

class Test_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.cursor_center"
    bl_label = "Simple operator"
    bl_description = "Center 3D cursor"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_center()
        return {'FINISHED'}

class MakeCable(Operator):
    bl_idname = "object.make_cable"
    bl_label = "Make cable"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.context):
        return context.object.mode == "OBJECT"

    def invoke(self, context: bpy.context, event):
        curve: bpy.types.Curve = context.active_object.data

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True, properties=True)
        context.active_object.lock_scale = [True, True, True]

        mean_radius = 0
        total_points = 0
        splines: List[bpy.types.Spline] = curve.splines
        for spline in splines:
            bezier_points: List[bpy.types.BezierSplinePoint] = spline.bezier_points
            for point in bezier_points:
                mean_radius += point.radius
                total_points += 1
                point.radius = 1
        mean_radius /= total_points

        curve.cable_diameter = curve.bevel_depth * 2000 * mean_radius

        d: bpy.types.Driver = curve.driver_add("bevel_depth").driver
        d.use_self = True
        d.expression = "self['cable_diameter'] / 2000"
        
        curve.is_cable = True

        return {"FINISHED"}

class SetCableDiameter(bpy.types.Operator):
    bl_idname = "object.set_cable_diameter"
    bl_label = "Set Diameter"
    
    def invoke(self, context: bpy.context, event):
        active_object = context.active_object
        assert active_object.type == "CURVE"
        curve = active_object.data
        assert isinstance(curve, bpy.types.Curve)
        
        curve.bevel_depth = context.scene.harnesstools.cable_diameter / 2000 # units mm
        splines: List[bpy.types.Spline] = curve.splines
        for spline in splines:
            bezier_points: List[bpy.types.BezierSplinePoint] = spline.bezier_points
            for point in bezier_points:
                point.radius = 1
            # [0].radius = 1
            # spline.bezier_points[3].radius = 1
        


        return {"FINISHED"}

class ValidateCableBendRadii:#(bpy.types.Operator):
    bl_idname = "object.test_ot_selectcurves"
    bl_label = "Test_OT_SelectCurves"

    # test_prop = FloatProperty("test prop", default=25)

    draw_handlers = []

    average_calc_time = 0

    def __init__(self):
        pass

    def invoke(self, context, event):
        self.prepare_batch()

        args = (self, context)
        self.register_handlers(args, context)

        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}
    
    def register_handlers(self, args, context):
        # self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback, args, "WINDOW", "POST_VIEW")
        # self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window) # TODO hmm
        self.draw_handlers.append(bpy.types.SpaceView3D.draw_handler_add(self.draw_callback, args, "WINDOW", "POST_VIEW"))

        # bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    
    @classmethod
    def unregsiter_handlers(cls):
        for handler in cls.draw_handlers:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
            except:
                pass
        for handler in cls.draw_handlers:
            cls.draw_handlers.remove(handler)
        
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    def modal(self, context, event):
        # if context.area:
        # bpy.types.SpaceView3D.context.area.tag_redraw()
        # bpy.data.scenes[0].update_tag()#update()
        # bpy.types.Scene.tag
        
        # bpy.context.view_layer.update()
        # bpy.context.view_layer.depsgraph.tag
        # print("Did update")
        
        # print("Event: {0}".format(event))
        
        if event.type in {"ESC"}:
            self.unregsiter_handlers()
            return {"CANCELLED"}
        
        return {"PASS_THROUGH"}

    def prepare_batch(self):
        objects: List[bpy.types.Object] = bpy.context.scene.objects
        curves: List[bpy.types.Object] = []
        meshes = []
        for obj in objects:
            if not obj.visible_get():
                continue
            if obj.type == "CURVE":# and isinstance(obj.data, bpy.types.Curve):
                if not obj.data.is_cable:
                    continue
                curves.append(obj)
            # if obj.type == "MESH":
                # meshes.append(obj)

        vertices = []

        calculation_start_time_ms = current_milli_time()
        num_calculations = 0
        num_curve_segments = 0

        for c in curves:
            d: bpy.types.Curve = c.data
            curve_elements = d.splines
            for curve_element in curve_elements:
                numSegments = len(curve_element.bezier_points)

                r = curve_element.resolution_u
                # if spline.use_cyclic_u:
                    # numSegments += 1
                    # print("Added one")

                seg_range = numSegments - 1
                if curve_element.use_cyclic_u:
                    seg_range += 1

                points = []
                for index in range(seg_range):
                    next_index = (index + 1) % numSegments

                    anchor1 = c.matrix_world @ curve_element.bezier_points[index].co
                    handle1 = c.matrix_world @ curve_element.bezier_points[index].handle_right
                    handle2 = c.matrix_world @ curve_element.bezier_points[next_index].handle_left
                    anchor2 = c.matrix_world @ curve_element.bezier_points[next_index].co
                    spline = SplineDefinition(anchor1, handle1, handle2, anchor2)
                    num_curve_segments += 1

                    bezier_points = interpolate_bezier(anchor1, handle1, handle2, anchor2, r)

                    u = 0
                    s = 1 / r
                    min_allowed_curvature = d.minimum_curve_radius + d.bevel_depth
                    for i in range(len(bezier_points) - 1):
                        bend_radius = spline.get_bend_radius(u + s / 2) # Sample centerpoint between p0 and p1
                        if (bend_radius < min_allowed_curvature):
                            vertices.append(bezier_points[i])
                            vertices.append(bezier_points[i + 1])
                        u += s
                        num_calculations += 1

        calc_time = current_milli_time() - calculation_start_time_ms
        if (self.average_calc_time == 0):
            self.average_calc_time = calc_time
        else:
            self.average_calc_time += (calc_time - self.average_calc_time) * 0.05
        #print("Completed {0} calculations for {2} segments in {1}ms (avg {3})".format(num_calculations, calc_time, num_curve_segments, self.average_calc_time))
        self.shader = from_builtin("3D_UNIFORM_COLOR")
        self.batch = batch_for_shader(self.shader, "LINES", {"pos": vertices})
        # self.batch2 = batch_for_shader(self.shader, "POINTS", {"pos": vertices})

    # # TODO temporary
    # @classmethod
    # def poll(cls, context: bpy.context):
    #     return (context.active_object is not None and
    #             context.active_object.select_get() and
    #             context.active_object.type == 'CURVE')
    
    def draw_callback(self, op, context):
        self.prepare_batch()
        bgl.glLineWidth(context.scene.harnesstools.line_width)
        bgl.glPointSize(context.scene.harnesstools.line_width)
        self.shader.bind()
        c: FloatVectorProperty = context.scene.harnesstools.color
        # c[1] = 0
        self.shader.uniform_float("color", c)
        self.batch.draw(self.shader)
        # self.batch2.draw(self.shader)