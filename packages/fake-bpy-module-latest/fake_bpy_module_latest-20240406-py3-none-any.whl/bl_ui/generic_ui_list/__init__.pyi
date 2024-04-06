import typing
import bpy_types

GenericType = typing.TypeVar("GenericType")

class GenericUIListOperator:
    """ """

    bl_options: typing.Any
    """ """

    def get_active_index(self, context):
        """

        :param context:
        """
        ...

    def get_list(self, context):
        """

        :param context:
        """
        ...

    def set_active_index(self, context, index):
        """

        :param context:
        :param index:
        """
        ...

class UILIST_OT_entry_add(bpy_types.Operator):
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """ """
        ...

    def get_active_index(self, context):
        """

        :param context:
        """
        ...

    def get_list(self, context):
        """

        :param context:
        """
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

    def path_resolve(self):
        """ """
        ...

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def set_active_index(self, context, index):
        """

        :param context:
        :param index:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class UILIST_OT_entry_move(bpy_types.Operator):
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """ """
        ...

    def get_active_index(self, context):
        """

        :param context:
        """
        ...

    def get_list(self, context):
        """

        :param context:
        """
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

    def path_resolve(self):
        """ """
        ...

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def set_active_index(self, context, index):
        """

        :param context:
        :param index:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

class UILIST_OT_entry_remove(bpy_types.Operator):
    """ """

    bl_idname: typing.Any
    """ """

    bl_label: typing.Any
    """ """

    bl_options: typing.Any
    """ """

    bl_rna: typing.Any
    """ """

    id_data: typing.Any
    """ """

    def as_keywords(self, ignore):
        """

        :param ignore:
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

    def driver_add(self):
        """ """
        ...

    def driver_remove(self):
        """ """
        ...

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """ """
        ...

    def get_active_index(self, context):
        """

        :param context:
        """
        ...

    def get_list(self, context):
        """

        :param context:
        """
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

    def path_resolve(self):
        """ """
        ...

    def poll_message_set(self):
        """ """
        ...

    def pop(self):
        """ """
        ...

    def property_overridable_library_set(self):
        """ """
        ...

    def property_unset(self):
        """ """
        ...

    def set_active_index(self, context, index):
        """

        :param context:
        :param index:
        """
        ...

    def type_recast(self):
        """ """
        ...

    def values(self):
        """ """
        ...

def draw_ui_list(
    layout,
    context,
    class_name,
    unique_id,
    list_path,
    active_index_path,
    insertion_operators,
    move_operators,
    menu_class_name,
    kwargs,
):
    """ """

    ...
