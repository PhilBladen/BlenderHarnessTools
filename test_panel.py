import bpy

class Test_PT_Panel(bpy.types.Panel):
    bl_idname = "Test_PT_Panel"
    bl_label = "Harness Tools"
    bl_category = "STAR-XL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        row = layout.row()
        row.operator("view3d.cursor_center", text="Center 3D cursor")

        # row = layout.row(align=True)
        # row.prop(context.scene.harnesstools, "enabled", expand=True)
        # layout.prop(context.scene.harnesstools, "color")

        row = layout.row()
        row.prop(context.scene.harnesstools, "enabled", expand=True)

        row = layout.row()
        row.operator("object.test_ot_selectcurves", text="Validate bend radii")

        row = layout.row()
        row.prop(context.scene.harnesstools, "color")

        row = layout.row()
        row.prop(context.scene.harnesstools, "line_width")

        

