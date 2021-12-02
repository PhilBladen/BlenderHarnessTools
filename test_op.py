from typing import ContextManager
import bpy
import bgl
import mathutils.geometry
from mathutils import Vector
import gpu
from gpu_extras.batch import batch_for_shader

import math
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
        return v * v * v * self.p0 + 3 * u * v * v * self.p1 + 3 * v * u * u * self.p2 + u * u * u * self.p3
    
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
            return math.inf
        return 1 / kappa

class Test_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.cursor_center"
    bl_label = "Simple operator"
    bl_description = "Center 3D cursor"
    
    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_center()
        return {'FINISHED'}

class Test_OT_SelectCurvesOperator(bpy.types.Operator):
    bl_idname = "object.test_ot_selectcurves"
    bl_label = "Test_OT_SelectCurves"

    draw_handlers = []

    def __init__(self):
        print("Created Test_OT_SelectCurvesOperator instance") # TODO remove

    def invoke(self, context, event):
        self.create_batch()

        args = (self, context)
        self.register_handlers(args, context)

        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}
    
    def register_handlers(self, args, context):
        # self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback, args, "WINDOW", "POST_VIEW")
        # self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window) # TODO hmm
        self.draw_handlers.append(bpy.types.SpaceView3D.draw_handler_add(self.draw_callback, args, "WINDOW", "POST_VIEW"))
    
    @classmethod
    def unregsiter_handlers(cls):
        for handler in cls.draw_handlers:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
            except:
                pass
        for handler in cls.draw_handlers:
            cls.draw_handlers.remove(handler)

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        
        print("Event: {0}".format(event))
        
        if event.type in {"ESC"}:
            self.unregsiter_handlers()
            return {"CANCELLED"}
        
        return {"PASS_THROUGH"}

    def create_batch(self):
        objects = bpy.context.scene.objects
        curves = []
        meshes = []
        for obj in objects:
            if obj.type == "CURVE":# and isinstance(obj.data, bpy.types.Curve):
                curves.append(obj)
            if obj.type == "MESH":
                meshes.append(obj)

        vertices = []

        calculation_start_time_ms = current_milli_time()

        for c in curves:    
            # c.select_set(True)
            if not "Minimum curvature" in c:
                c["Minimum curvature"] = 0.005

            d = c.data
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
                    
                    # TODO properly center line segment on curvature sample point

                    for index in range(r):
                        u = index * (1 / r)
                        p0 = spline.interpolate(u)
                        p1 = spline.interpolate(u + (1 / r))
                        bend_radius = spline.get_bend_radius(u + (1 / (2 * r))) # Sample centerpoint between p0 and p1
                        if (bend_radius < c["Minimum curvature"]): # TODO add variable curvature allowance
                            vertices.append(p0)
                            vertices.append(p1)

                assert('3D' == c.data.dimensions) # TODO understand
                for point_index in range(len(points) - 1):
                    p0 = points[point_index]
                    p1 = points[point_index + 1]
                    vertices.append((p0.x, p0.y, p0.z))
                    vertices.append((p1.x, p1.y, p1.z))

        print("Calculation time: {0}ms".format(current_milli_time() - calculation_start_time_ms))
        self.shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
        self.batch = batch_for_shader(self.shader, "LINES", {"pos": vertices})

    # TODO temporary
    @classmethod
    def poll(cls, context: bpy.context):
        return (context.active_object is not None and
                context.active_object.select_get() and
                context.active_object.type == 'CURVE')
    
    def draw_callback(self, op, context):
        # bgl.glLineWidth(5)
        self.shader.bind()
        self.shader.uniform_float("color", (1, 0, 0, 1))
        self.batch.draw(self.shader)