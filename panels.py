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

    bpy.types.Scene.BEVEL_DEPTH = bpy.props.IntProperty(
        name='Thickness', default=3, min=1, step=1, description='Thread thickness in microns')

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        split = layout.split()
        modTelarana = bpy.data.objects[context.object.name].modifiers["TelaranaCloth"]
        col = split.column()
        col.label(text="Tension")
        col.prop(modTelarana.settings, 'shrink_min', text='')

        col.label(text="Collisions")
        col.prop(modTelarana.collision_settings,
                 'use_collision', text='Enable object collisions')
        col.prop(modTelarana.collision_settings,
                 'use_self_collision', text='Enable self collisions')

        row = layout.row()
        row.scale_y = 3
        op = row.operator("object.run_telarana_functions", text='Apply')
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

    scene = bpy.types.Scene

    scene.THREAD_COUNT = bpy.props.IntProperty(name='Count', default=50, min=2, max=250, step=1, description='Main thread count')
    scene.THREAD_STEPS = bpy.props.IntProperty(name='Subdivisions', default=10, min=5, max=50, step=1, description='Main thread subdivisions')
    scene.THREAD_CONNECTIONS_COUNT = bpy.props.IntProperty(name='Count', default=50, min=2, max=250, step=1, description='Connecthing thread count')
    scene.THREAD_CONNECTIONS_STEPS = bpy.props.IntProperty(name='Subdivisions', default=10, min=0, max=50, step=1, description='Connecting thread subdivisions')
    scene.RECURSION_LEVELS = bpy.props.IntProperty(name='Levels', default=10, min=1, max=250, step=1, description='Recursion levels')
    scene.TEAR_THREADS = bpy.props.BoolProperty(name='Tear threads', default=False)
    scene.THREAD_TEARING_AMOUNT = bpy.props.FloatProperty(name='Ratio', default=1, min=1, max=10, step=0.1, description='Thread tearing amount')
    scene.DELETE_ANNOTATION = bpy.props.BoolProperty(name='Delete annotations', default=False)
    scene.COMBINE_THREADS = bpy.props.BoolProperty(name='Combine threads', default=True)
    scene.COMBINE_THREADS_THRESHOLD = bpy.props.FloatProperty(name='Threshold', default=0.5, min=0, max=1, step=0.01, description='Combine thread vertices threshold')

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        gpd = context.annotation_data
        if gpd is not None:
            gpl = context.active_annotation_layer
            if gpl is not None:
                if hasattr(bpy.context.scene.grease_pencil.layers.active.active_frame, 'strokes'):
                    strokes = bpy.context.scene.grease_pencil.layers.active.active_frame.strokes
                    if len(strokes) >= 2:
                        layout.label(text="Main Threads")
                        row = layout.row(align=True)
                        row.prop(scene, 'THREAD_COUNT')
                        row.prop(scene, 'THREAD_STEPS')

                        layout.separator()

                        layout.label(text="Connecting Threads")
                        row = layout.row(align=True)
                        row.prop(scene, 'THREAD_CONNECTIONS_COUNT')
                        row.prop(scene, 'THREAD_CONNECTIONS_STEPS')

                        layout.separator()

                        row = layout.row()
                        row.prop(scene, "RECURSION_LEVELS")

                        # layout.separator()

                        # row = layout.row()
                        # row.prop(scene, 'TEAR_THREADS', text='Tear threads')

                        # if(scene.TEAR_THREADS):
                        #     row = layout.row()
                        #     row.prop(scene, 'THREAD_TEARING_AMOUNT')

                        # row = layout.row()
                        # row.prop(scene, 'COMBINE_THREADS')

                        # if(scene.COMBINE_THREADS):
                        #     row = layout.row()
                        #     row.prop(scene, 'COMBINE_THREADS_THRESHOLD')

                        layout.separator()

                        row = layout.row()
                        row.prop(scene, 'DELETE_ANNOTATION',
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
