from .operators import *


class VIEW3D_PT_AnnotateTelarana(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Telaraña"
    bl_label = "Draw"
    bl_idname = "VIEW3D_PT_AnnotateTelarana"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        gpd = context.annotation_data
        scene = context.scene
        tool_settings = context.tool_settings
        if gpd is not None:
            if gpd.layers.active_note is not None:
                text = gpd.layers.active_note
            else:
                text = ""

            gpl = context.active_annotation_layer
            if gpl is not None:
                layout.label(text="Color")
                row = layout.row(align=True)
                row.prop(gpl, 'color', text='')
                row.popover('TOPBAR_PT_annotation_layers', text=text)

                layout.separator()

        row = layout.row(align=True)
        row.prop(tool_settings, "annotation_stroke_placement_view3d",
                 text="Placement")


class VIEW3D_PT_SimulateTelarana(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Telaraña"
    bl_label = "Simulate"
    bl_idname = "VIEW3D_PT_SimulateTelarana"
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        split = layout.split()
        modTelarana = bpy.data.objects[context.object.name].modifiers["TelaranaCloth"]
        col = split.column()
        col.label(text="Tension")
        col.prop(modTelarana.settings, 'shrink_min', text='')

        col.label(text="Collisions")
        col.prop(modTelarana.collision_settings, 'use_collision', text='Enable object collisions')
        col.prop(modTelarana.collision_settings, 'use_self_collision', text='Enable self collisions')

        row = layout.row()
        row.scale_y = 3
        op = row.operator("object.telarana_functions", text='Apply')
        op.action = 'APPLY_AND_CONVERT_MESH_TO_CURVE'

    @classmethod
    def poll(cls, context):
        return context.object is not None and "Telarana" in context.object and "TelaranaCloth" in context.object.modifiers


class VIEW3D_PT_TelaranaThickness(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Telaraña"
    bl_label = "Geometry"
    bl_idname = "VIEW3D_PT_TelaranaThickness"
    bl_order = 5

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if context.object.type == 'CURVE':
            curveTelarana = bpy.data.curves[context.active_object.data.name]
            row = layout.row()
            row.prop(curveTelarana, "bevel_depth", text="Thickness")

    @classmethod
    def poll(cls, context):
        return context.object is not None and "Telarana" in context.object and "TelaranaCloth" not in context.object.modifiers


class VIEW3D_PT_TelaranaGeometry(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Telaraña"
    bl_label = "Generate"
    bl_idname = "VIEW3D_PT_GenerateTelarana"
    bl_order = 2



    def draw(self, context):
        layout = self.layout
        telarana = context.scene.telarana

        gpd = context.annotation_data
        if gpd is not None:
            gpl = context.active_annotation_layer
            if gpl is not None:
                if hasattr(bpy.context.scene.grease_pencil.layers.active.active_frame, 'strokes'):
                    strokes = bpy.context.scene.grease_pencil.layers.active.active_frame.strokes
                    if len(strokes) >= 2:
                        layout.label(text="Main Threads")
                        row = layout.row(align=True)
                        row.prop(telarana, 'THREAD_COUNT')
                        row.prop(telarana, 'THREAD_STEPS')

                        layout.separator()

                        layout.label(text="Connecting Threads")
                        row = layout.row(align=True)
                        row.prop(telarana, 'THREAD_CONNECTIONS_COUNT')
                        row.prop(telarana, 'THREAD_CONNECTIONS_STEPS')

                        layout.separator()

                        row = layout.row()
                        row.prop(telarana, "RECURSION_LEVELS")

                        # layout.separator()

                        # row = layout.row()
                        # row.prop(telarana, 'TEAR_THREADS', text='Tear threads')

                        # if(scene.TEAR_THREADS):
                        #     row = layout.row()
                        #     row.prop(telarana, 'THREAD_TEARING_AMOUNT')

                        # row = layout.row()
                        # row.prop(telarana, 'COMBINE_THREADS')

                        # if(scene.COMBINE_THREADS):
                        #     row = layout.row()
                        #     row.prop(telarana, 'COMBINE_THREADS_THRESHOLD')

                        layout.separator()

                        row = layout.row()
                        row.prop(telarana, 'DELETE_ANNOTATION',
                                 text='Clear annotations')

                        row = layout.row()
                        row.scale_y = 3.0
                        row.operator('object.create_telarana',
                                     text='Generate',)
                else:
                    layout.label(text="Draw at least two strokes",)

    @ classmethod
    def poll(cls, context):
        return context.active_annotation_layer
