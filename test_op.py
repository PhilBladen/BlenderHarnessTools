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

    def solveIntersectingPoint(self, zeroCoord, A, B, p1, p2):
        a1 = p1.normal[A]
        b1 = p1.normal[B]
        d1 = p1.constant

        a2 = p2.normal[A]
        b2 = p2.normal[B]
        d2 = p2.constant

        A0 = ((b2 * d1) - (b1 * d2)) / ((a1 * b2 - a2 * b1))
        B0 = ((a1 * d2) - (a2 * d1)) / ((a1 * b2 - a2 * b1))

        point = Vector((0, 0, 0))
        point[zeroCoord] = 0
        point[A] = A0
        point[B] = B0

        return point
    
    # https://math.stackexchange.com/questions/1905533/find-perpendicular-distance-from-point-to-line-in-3d
    def line_to_point_distance(self, point, line_direction, line_point):
        v = point - line_point
        t = v.dot(line_direction)
        P = line_point + t * line_direction
        return (point - P).magnitude
    
    # Functions derived using https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/Bezier/bezier-der.html
    # and Computer Graphics & Geometric Modelling by David Salomon
    def interpolate_spline(self, p0, p1, p2, p3, u):
        v = 1 - u
        return v * v * v * p0 + 3 * u * v * v * p1 + 3 * v * u * u * p2 + u * u * u * p3
    
    def get_spline_curvature(self, p0, p1, p2, p3, u):
        v = 1 - u
        Pt = 3 * v * v * (p1 - p0) + 6 * u * v * (p2 - p1) + 3 * u * u * (p3 - p2)
        Ptt = 6 * v * (p2 - 2 * p1 + p0) + 6 * u * (p3 - 2 * p2 + p1)
        Pt_mag = Pt.magnitude
        return Pt.cross(Ptt).cross(Pt).magnitude / (Pt_mag * Pt_mag * Pt_mag * Pt_mag)

    def get_plane_intersection(self, p1, n1, p2, n2):
        # vertices.append(p1)
        # vertices.append(p1 + n1)
        # #
        # vertices.append(p2)
        # vertices.append(p2 + n2)

        if n1.dot(n2) == 0: # Inline normals - no solution
            return
        
        intersection_point = Vector((p1.dot(n1), p2.dot(n2), p1.x))
        mat = mathutils.Matrix([(n1.x, n1.y, n1.z, 0), (n2.x, n2.y, n2.z, 0), (1, 0, 0, 0), (0, 0, 0, 1)])
        mat.invert()
        intersection_point = mat @ intersection_point
        
        intersection_vector = n1.cross(n2)
        intersection_vector.normalize()

        return intersection_vector, intersection_point
        # curve_radius = self.line_to_point_distance(p1, intersection_vector, intersection_point)

        # print("Curve radius: {0}".format(curve_radius / 2))

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
        # if len(meshes) >= 2:
        #     up_vector = Vector((0, 0, 1))
        #     plane1 = meshes[0]
        #     plane2 = meshes[1]
        #     l1, r1, s1 = plane1.matrix_world.decompose()
        #     l2, r2, s2 = plane2.matrix_world.decompose()
        #     v, p = self.get_plane_intersection(l1, r1 @ up_vector, l2, r2 @ up_vector)
        #     vertices.append(p)
        #     vertices.append(p + v * 10)

        # for m in meshes:
        #     normal = r @ normal
        #     normal.normalize()
            
        #     vertices.append(m.location)
        #     vertices.append(m.location + normal)

        for c in curves:    
            # c.select_set(True)
            d = c.data
            splines = d.splines
            for spline in splines:
                numSegments = len(spline.bezier_points)

                r = spline.resolution_u
                # if spline.use_cyclic_u:
                    # numSegments += 1
                    # print("Added one")

                seg_range = numSegments - 1
                if spline.use_cyclic_u:
                    seg_range += 1

                points = []
                for i in range(seg_range):
                    nextIdx = (i + 1) % numSegments

                    knot1 = c.matrix_world @ spline.bezier_points[i].co
                    handle1 = c.matrix_world @ spline.bezier_points[i].handle_right
                    handle2 = c.matrix_world @ spline.bezier_points[nextIdx].handle_left
                    knot2 = c.matrix_world @ spline.bezier_points[nextIdx].co

                    # _points = mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, r)
                    # for _p in _points:
                    #     p = Vector((_p[0], _p[1], _p[2]))
                    #     p = c.matrix_world @ p
                    #     points.append(p)
                    
                    for i in range(r):
                        u = i * (1 / r)
                        #points.append(c.matrix_world @ self.interpolate_spline(knot1, handle1, handle2, knot2, u))

                        p0 = self.interpolate_spline(knot1, handle1, handle2, knot2, u)
                        p1 = self.interpolate_spline(knot1, handle1, handle2, knot2, u + (1 / r))

                        curvature = self.get_spline_curvature(knot1, handle1, handle2, knot2, u)
                        if curvature > 0:
                            curve_radius = 1 / curvature
                            if (curve_radius < .005):
                                vertices.append(p0)
                                vertices.append(p1)

                assert('3D' == c.data.dimensions)
                for point_index in range(len(points) - 2):
                    p0 = points[point_index]
                    p1 = points[point_index + 1]
                    p2 = points[point_index + 2]

                    # v01 = Vector3D(p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
                    # v12 = Vector3D(p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])

                    v01 = p1 - p0
                    v12 = p2 - p1

                    v01.normalize()
                    v12.normalize()

                    # intersectionLineVector = v01.cross(v12)

                    # v, p = self.get_plane_intersection(p0, v01, p1, v12)

                    # curve_radius = self.line_to_point_distance(p1, v, p)

                    # if (curve_radius < 5):
                    #     vertices.append(p0)
                    #     vertices.append(p1)
                    
                    # print("Curvature: {0}".format(curve_radius));

                    # print("Point X:", p0[0])
                    # print("Point Y:", p0[1])
                    # print("Point Z:", p0[2])
                    # print()

                for point_index in range(len(points) - 1):
                    p0 = points[point_index]
                    p1 = points[point_index + 1]
                    vertices.append((p0.x, p0.y, p0.z))
                    vertices.append((p1.x, p1.y, p1.z))

        self.shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
        self.batch = batch_for_shader(self.shader, "LINES", {"pos": vertices})
    
    def draw_callback(self, op, context):
        # bgl.glLineWidth(5)
        self.shader.bind()
        self.shader.uniform_float("color", (1, 0, 0, 1))
        self.batch.draw(self.shader)