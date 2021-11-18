import bpy

class Test_PT_Panel(bpy.types.Panel):
    bl_idname = "Test_PT_Panel"
    bl_label = "Utils"
    bl_category = "STAR-XL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("view3d.cursor_center", text="Center 3D cursor")

        row = layout.row()
        row.operator("object.test_ot_selectcurves", text="Check curve minimum radii")

        

