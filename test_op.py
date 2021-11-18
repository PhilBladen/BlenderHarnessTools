import bpy
import mathutils.geometry

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

    def execute(self, context):
        objects = bpy.context.scene.objects

        curves = []
        for obj in objects:
            if obj.type == "CURVE":
                curves.append(obj)

        for c in curves:    
            c.select_set(True)
            d = c.data
            splines = d.splines
            spline = splines[0]
            numSegments = len(spline.bezier_points)

            r = spline.resolution_u
            if spline.use_cyclic_u:
                numSegments += 1

            points = []
            for i in range(numSegments):
                nextIdx = (i + 1) % numSegments

                knot1 = spline.bezier_points[i].co
                handle1 = spline.bezier_points[i].handle_right
                handle2 = spline.bezier_points[nextIdx].handle_left
                knot2 = spline.bezier_points[nextIdx].co

                _points = mathutils.geometry.interpolate_bezier(knot1, handle1, handle2, knot2, r)
                points.extend(_points)

            assert('3D' == c.data.dimensions)
            for pointVec in points:
                print("Point X:", pointVec[0])
                print("Point Y:", pointVec[1])
                print("Point Z:", pointVec[2])
                print()

            splineCount = 0
            pointCount = 0
            for s in splines:
                splineCount += 1
                for p in s.points:
                    pointCount += 1
            pass


        
        return {'FINISHED'}
