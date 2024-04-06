import typing
import bpy_types

GenericType = typing.TypeVar("GenericType")

class UnifiedPaintPanel:
    """ """

    def get_brush_mode(self, context):
        """

        :param context:
        """
        ...

    def paint_settings(self, context):
        """

        :param context:
        """
        ...

    def prop_unified(
        self,
        layout,
        context,
        brush,
        prop_name,
        unified_name,
        pressure_name,
        icon,
        text,
        slider,
        header,
    ):
        """

        :param layout:
        :param context:
        :param brush:
        :param prop_name:
        :param unified_name:
        :param pressure_name:
        :param icon:
        :param text:
        :param slider:
        :param header:
        """
        ...

    def prop_unified_color(self, parent, context, brush, prop_name, text):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param text:
        """
        ...

    def prop_unified_color_picker(
        self, parent, context, brush, prop_name, value_slider
    ):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param value_slider:
        """
        ...

class VIEW3D_MT_tools_projectpaint_clone(bpy_types._GenericUI):
    """ """

    bl_label: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def append(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def as_pointer(self):
        """ """
        ...

    def bl_rna_get_subclass(self):
        """ """
        ...

    def bl_rna_get_subclass_py(self):
        """ """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_collapsible(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    def draw_preset(self, _context):
        """

        :param _context:
        """
        ...

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def get(self):
        """ """
        ...

    def id_properties_clear(self):
        """ """
        ...

    def id_properties_ensure(self):
        """ """
        ...

    def id_properties_ui(self):
        """ """
        ...

    def is_extended(self):
        """ """
        ...

    def is_property_hidden(self):
        """ """
        ...

    def is_property_overridable_library(self):
        """ """
        ...

    def is_property_readonly(self):
        """ """
        ...

    def is_property_set(self):
        """ """
        ...

    def items(self):
        """ """
        ...

    def keyframe_delete(self):
        """ """
        ...

    def keyframe_insert(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def path_from_id(self):
        """ """
        ...

    def path_menu(
        self,
        searchpaths,
        operator,
        props_default,
        prop_filepath,
        filter_ext,
        filter_path,
        display_name,
        add_operator,
    ):
        """

        :param searchpaths:
        :param operator:
        :param props_default:
        :param prop_filepath:
        :param filter_ext:
        :param filter_path:
        :param display_name:
        :param add_operator:
        """
        ...

    def path_resolve(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def prepend(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def remove(self, draw_func):
        """

        :param draw_func:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class BrushPanel(UnifiedPaintPanel):
    """ """

    def get_brush_mode(self, context):
        """

        :param context:
        """
        ...

    def paint_settings(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def prop_unified(
        self,
        layout,
        context,
        brush,
        prop_name,
        unified_name,
        pressure_name,
        icon,
        text,
        slider,
        header,
    ):
        """

        :param layout:
        :param context:
        :param brush:
        :param prop_name:
        :param unified_name:
        :param pressure_name:
        :param icon:
        :param text:
        :param slider:
        :param header:
        """
        ...

    def prop_unified_color(self, parent, context, brush, prop_name, text):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param text:
        """
        ...

    def prop_unified_color_picker(
        self, parent, context, brush, prop_name, value_slider
    ):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param value_slider:
        """
        ...

class BrushSelectPanel(UnifiedPaintPanel):
    """ """

    bl_label: typing.Any
    """ """

    def draw(self, context):
        """

        :param context:
        """
        ...

    def get_brush_mode(self, context):
        """

        :param context:
        """
        ...

    def paint_settings(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def prop_unified(
        self,
        layout,
        context,
        brush,
        prop_name,
        unified_name,
        pressure_name,
        icon,
        text,
        slider,
        header,
    ):
        """

        :param layout:
        :param context:
        :param brush:
        :param prop_name:
        :param unified_name:
        :param pressure_name:
        :param icon:
        :param text:
        :param slider:
        :param header:
        """
        ...

    def prop_unified_color(self, parent, context, brush, prop_name, text):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param text:
        """
        ...

    def prop_unified_color_picker(
        self, parent, context, brush, prop_name, value_slider
    ):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param value_slider:
        """
        ...

class ClonePanel(UnifiedPaintPanel):
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_header(self, context):
        """

        :param context:
        """
        ...

    def get_brush_mode(self, context):
        """

        :param context:
        """
        ...

    def paint_settings(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def prop_unified(
        self,
        layout,
        context,
        brush,
        prop_name,
        unified_name,
        pressure_name,
        icon,
        text,
        slider,
        header,
    ):
        """

        :param layout:
        :param context:
        :param brush:
        :param prop_name:
        :param unified_name:
        :param pressure_name:
        :param icon:
        :param text:
        :param slider:
        :param header:
        """
        ...

    def prop_unified_color(self, parent, context, brush, prop_name, text):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param text:
        """
        ...

    def prop_unified_color_picker(
        self, parent, context, brush, prop_name, value_slider
    ):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param value_slider:
        """
        ...

class ColorPalettePanel(UnifiedPaintPanel):
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    def draw(self, context):
        """

        :param context:
        """
        ...

    def get_brush_mode(self, context):
        """

        :param context:
        """
        ...

    def paint_settings(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def prop_unified(
        self,
        layout,
        context,
        brush,
        prop_name,
        unified_name,
        pressure_name,
        icon,
        text,
        slider,
        header,
    ):
        """

        :param layout:
        :param context:
        :param brush:
        :param prop_name:
        :param unified_name:
        :param pressure_name:
        :param icon:
        :param text:
        :param slider:
        :param header:
        """
        ...

    def prop_unified_color(self, parent, context, brush, prop_name, text):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param text:
        """
        ...

    def prop_unified_color_picker(
        self, parent, context, brush, prop_name, value_slider
    ):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param value_slider:
        """
        ...

class DisplayPanel(UnifiedPaintPanel):
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_header(self, context):
        """

        :param context:
        """
        ...

    def get_brush_mode(self, context):
        """

        :param context:
        """
        ...

    def paint_settings(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def prop_unified(
        self,
        layout,
        context,
        brush,
        prop_name,
        unified_name,
        pressure_name,
        icon,
        text,
        slider,
        header,
    ):
        """

        :param layout:
        :param context:
        :param brush:
        :param prop_name:
        :param unified_name:
        :param pressure_name:
        :param icon:
        :param text:
        :param slider:
        :param header:
        """
        ...

    def prop_unified_color(self, parent, context, brush, prop_name, text):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param text:
        """
        ...

    def prop_unified_color_picker(
        self, parent, context, brush, prop_name, value_slider
    ):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param value_slider:
        """
        ...

class FalloffPanel(UnifiedPaintPanel):
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    def draw(self, context):
        """

        :param context:
        """
        ...

    def get_brush_mode(self, context):
        """

        :param context:
        """
        ...

    def paint_settings(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def prop_unified(
        self,
        layout,
        context,
        brush,
        prop_name,
        unified_name,
        pressure_name,
        icon,
        text,
        slider,
        header,
    ):
        """

        :param layout:
        :param context:
        :param brush:
        :param prop_name:
        :param unified_name:
        :param pressure_name:
        :param icon:
        :param text:
        :param slider:
        :param header:
        """
        ...

    def prop_unified_color(self, parent, context, brush, prop_name, text):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param text:
        """
        ...

    def prop_unified_color_picker(
        self, parent, context, brush, prop_name, value_slider
    ):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param value_slider:
        """
        ...

class SmoothStrokePanel(UnifiedPaintPanel):
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_header(self, context):
        """

        :param context:
        """
        ...

    def get_brush_mode(self, context):
        """

        :param context:
        """
        ...

    def paint_settings(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def prop_unified(
        self,
        layout,
        context,
        brush,
        prop_name,
        unified_name,
        pressure_name,
        icon,
        text,
        slider,
        header,
    ):
        """

        :param layout:
        :param context:
        :param brush:
        :param prop_name:
        :param unified_name:
        :param pressure_name:
        :param icon:
        :param text:
        :param slider:
        :param header:
        """
        ...

    def prop_unified_color(self, parent, context, brush, prop_name, text):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param text:
        """
        ...

    def prop_unified_color_picker(
        self, parent, context, brush, prop_name, value_slider
    ):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param value_slider:
        """
        ...

class StrokePanel(UnifiedPaintPanel):
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_ui_units_x: typing.Any
    """ """

    def draw(self, context):
        """

        :param context:
        """
        ...

    def get_brush_mode(self, context):
        """

        :param context:
        """
        ...

    def paint_settings(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def prop_unified(
        self,
        layout,
        context,
        brush,
        prop_name,
        unified_name,
        pressure_name,
        icon,
        text,
        slider,
        header,
    ):
        """

        :param layout:
        :param context:
        :param brush:
        :param prop_name:
        :param unified_name:
        :param pressure_name:
        :param icon:
        :param text:
        :param slider:
        :param header:
        """
        ...

    def prop_unified_color(self, parent, context, brush, prop_name, text):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param text:
        """
        ...

    def prop_unified_color_picker(
        self, parent, context, brush, prop_name, value_slider
    ):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param value_slider:
        """
        ...

class TextureMaskPanel(UnifiedPaintPanel):
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    def draw(self, context):
        """

        :param context:
        """
        ...

    def get_brush_mode(self, context):
        """

        :param context:
        """
        ...

    def paint_settings(self, context):
        """

        :param context:
        """
        ...

    def poll(self, context):
        """

        :param context:
        """
        ...

    def prop_unified(
        self,
        layout,
        context,
        brush,
        prop_name,
        unified_name,
        pressure_name,
        icon,
        text,
        slider,
        header,
    ):
        """

        :param layout:
        :param context:
        :param brush:
        :param prop_name:
        :param unified_name:
        :param pressure_name:
        :param icon:
        :param text:
        :param slider:
        :param header:
        """
        ...

    def prop_unified_color(self, parent, context, brush, prop_name, text):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param text:
        """
        ...

    def prop_unified_color_picker(
        self, parent, context, brush, prop_name, value_slider
    ):
        """

        :param parent:
        :param context:
        :param brush:
        :param prop_name:
        :param value_slider:
        """
        ...

def brush_basic__draw_color_selector(context, layout, brush, gp_settings, props):
    """ """

    ...

def brush_basic_gpencil_paint_settings(layout, context, brush, compact):
    """ """

    ...

def brush_basic_gpencil_sculpt_settings(layout, _context, brush, compact):
    """ """

    ...

def brush_basic_gpencil_vertex_settings(layout, _context, brush, compact):
    """ """

    ...

def brush_basic_gpencil_weight_settings(layout, _context, brush, compact):
    """ """

    ...

def brush_basic_grease_pencil_paint_settings(layout, context, brush, compact):
    """ """

    ...

def brush_basic_texpaint_settings(layout, context, brush, compact):
    """ """

    ...

def brush_mask_texture_settings(layout, brush):
    """ """

    ...

def brush_settings(layout, context, brush, popover):
    """ """

    ...

def brush_settings_advanced(layout, context, brush, popover):
    """ """

    ...

def brush_shared_settings(layout, context, brush, popover):
    """ """

    ...

def brush_texture_settings(layout, brush, sculpt):
    """ """

    ...

def draw_color_settings(context, layout, brush, color_type):
    """ """

    ...
