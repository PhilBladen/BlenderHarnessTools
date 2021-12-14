import bpy

class HARNESS_PT_Panel(bpy.types.Panel):
    bl_idname = "HARNESS_PT_Panel"
    bl_label = "Harness Tools"
    bl_category = "STAR-XL"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context: bpy.context):
        return context.active_object.type == "CURVE"

    def draw(self, context: bpy.context):
        layout = self.layout
        layout.use_property_split = True # Annotate properties with names
        layout.use_property_decorate = False  # No keyframe marker

        row = layout.row()
        row.label(text="Local properties:")

        if hasattr(context.active_object.data, "is_cable") and context.active_object.data.is_cable:
            row = layout.row()
            row.prop(context.active_object.data, "cable_diameter")

            row = layout.row()
            row.prop(context.active_object.data, "minimum_curve_radius")
        else:
            row = layout.row()
            row.operator("object.make_cable")


        row = layout.row()
        row.label(text="Global properties:")

        row = layout.row()
        row.prop(context.window_manager, "harnesstoolsenabled", expand=True)

        row = layout.row()
        row.prop(context.scene.harnesstools, "color")

        row = layout.row()
        row.prop(context.scene.harnesstools, "line_width")
        

