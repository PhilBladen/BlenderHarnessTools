import bpy
import bgl
import mathutils.geometry
from mathutils import Vector
import gpu
from gpu_extras.batch import batch_for_shader

class Vector3D:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Vector3D(x, y, z)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        return Vector3D(x, y, z)
    
    def __str__(self):
        return "Vector ({0}, {1}, {2})".format(self.x, self.y, self.z)

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

    def __init__(self):
        self.draw_handle = None
        self.draw_event = None

    def invoke(self, context, event):
        self.create_batch()

        args = (self, context)
        self.register_handlers(args, context)

        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}
    
    def register_handlers(self, args, context):
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback, args, "WINDOW", "POST_VIEW")
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window) # TODO hmm
    
    def unregsiter_handlers(self, context):
        context.window_manager.event_timer_remove(self.draw_event)
        self.draw_event = None
        
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, "WINDOW")
        self.draw_handle = None

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        
        if event.type in {"ESC"}:
            self.unregsiter_handlers(context)
            return {"CANCELLED"}
        
        return {"PASS_THROUGH"}
    
    # def finish(self):
    #     self.unregsiter_handlers(context) # TODO hmm
    #     return {"FINISHED"}

    def create_batch(self):
        objects = bpy.context.scene.objects
        curves = []
        for obj in objects:
            if obj.type == "CURVE":
                curves.append(obj)

        points = []
        for c in curves:    
            c.select_set(True)
            d = c.data
            splines = d.splines
            spline = splines[0]
            numSegments = len(spline.bezier_points)

            r = spline.resolution_u
            # if spline.use_cyclic_u:
                # numSegments += 1

            for i in range(numSegments - 1):
                nextIdx = (i + 1) % numSegments

                knot1 = spline.bezier_points[i].co
                handle1 = spline.bezier_points[i].handle_right
                handle2 = spline.bezier_points[nextIdx].handle_left
                knot2 = spline.bezier_points[nextIdx].co

                _points = mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, r)
                for _p in _points:
                    p = Vector((_p[0], _p[1], _p[2]))
                    p = c.matrix_world @ p
                    points.append(p)
                # points.extend(_points)

            assert('3D' == c.data.dimensions)
            for pointIndex in range(len(points) - 2):
                p0 = points[pointIndex]
                p1 = points[pointIndex + 1]
                p2 = points[pointIndex + 2]

                # v01 = Vector3D(p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
                # v12 = Vector3D(p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])

                v01 = p1 - p0
                v12 = p2 - p1


                
                print("Curvature: {0}".format(v12 - v01));

                # crudeCurvature = 

                # print("Point X:", p0[0])
                # print("Point Y:", p0[1])
                # print("Point Z:", p0[2])
                # print()

        vertices = []#[(0, 3, 3), (0, 4, 4), (0, 6, 2), (0, 3, 3)]
        for p in points:
            vertices.append((p.x, p.y, p.z))
        self.shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
        self.batch = batch_for_shader(self.shader, "LINE_STRIP", {"pos": vertices})
    
    def draw_callback(self, op, context):
        bgl.glLineWidth(5)
        self.shader.bind()
        self.shader.uniform_float("color", (1, 0, 0, 1))
        self.batch.draw(self.shader)

    # def execute(self, context):
    #     objects = bpy.context.scene.objects

    #     curves = []
    #     for obj in objects:
    #         if obj.type == "CURVE":
    #             curves.append(obj)

    #     for c in curves:    
    #         c.select_set(True)
    #         d = c.data
    #         splines = d.splines
    #         spline = splines[0]
    #         numSegments = len(spline.bezier_points)

    #         r = spline.resolution_u
    #         if spline.use_cyclic_u:
    #             numSegments += 1

    #         points = []
    #         for i in range(numSegments):
    #             nextIdx = (i + 1) % numSegments

    #             knot1 = spline.bezier_points[i].co
    #             handle1 = spline.bezier_points[i].handle_right
    #             handle2 = spline.bezier_points[nextIdx].handle_left
    #             knot2 = spline.bezier_points[nextIdx].co

    #             _points = mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, r)
    #             for p in _points:
    #                 points.append(Vector3D(p[0], p[1], p[2]))
    #             # points.extend(_points)

    #         assert('3D' == c.data.dimensions)
    #         for pointIndex in range(len(points) - 2):
    #             p0 = points[pointIndex]
    #             p1 = points[pointIndex + 1]
    #             p2 = points[pointIndex + 2]

    #             # v01 = Vector3D(p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    #             # v12 = Vector3D(p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])

    #             v01 = p1 - p0
    #             v12 = p2 - p1


                
    #             print("Curvature: {0}".format(v12 - v01));

    #             # crudeCurvature = 

    #             # print("Point X:", p0[0])
    #             # print("Point Y:", p0[1])
    #             # print("Point Z:", p0[2])
    #             # print()

    #         splineCount = 0
    #         pointCount = 0
    #         for s in splines:
    #             splineCount += 1
    #             for p in s.points:
    #                 pointCount += 1
    #         pass


        
    #     return {'FINISHED'}
