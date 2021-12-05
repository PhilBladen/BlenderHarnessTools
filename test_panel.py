import bpy
from . operators import ValidateCableBendRadii

class Test_PT_Panel(bpy.types.Panel):
    bl_idname = "Test_PT_Panel"
    bl_label = "Harness Tools"
    bl_category = "STAR-XL"
    bl_space_type = "PROPERTIES"#"VIEW_3D"
    bl_region_type = "WINDOW"#"UI"
    bl_context = "data"

    @classmethod
    def poll(cls, context: bpy.context):
        return context.active_object.type == "CURVE"

    def draw(self, context: bpy.context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        # row = layout.row()
        # row.operator("view3d.cursor_center", text="Center 3D cursor")

        # row = layout.row(align=True)
        # row.prop(context.scene.harnesstools, "enabled", expand=True)
        # layout.prop(context.scene.harnesstools, "color")

        row = layout.row()
        row.label(text="Local properties:")

        if hasattr(context.active_object.data, "is_cable") and context.active_object.data.is_cable:
            row = layout.row()
            row.prop(context.active_object.data, "cable_diameter")

            row = layout.row()
            # row.operator("object.set_cable_diameter")
            row.prop(context.active_object.data, "minimum_curve_radius")
        else:
            row = layout.row()
            row.operator("object.make_cable")

        # row = layout.row()
        # row.prop(ValidateCableBendRadii, "test_prop", text="He")


        row = layout.row()
        row.label(text="Global properties:")

        row = layout.row()
        row.prop(context.window_manager, "harnesstoolsenabled", expand=True)

        row = layout.row()
        row.operator("object.test_ot_selectcurves", text="Validate bend radii")

        row = layout.row()
        row.prop(context.scene.harnesstools, "color")

        row = layout.row()
        row.prop(context.scene.harnesstools, "line_width")

        # row = layout.row()
        # row.operator("object.set_cable_diameter")
        # row.prop(context.scene.harnesstools, "cable_diameter", text="")
        

