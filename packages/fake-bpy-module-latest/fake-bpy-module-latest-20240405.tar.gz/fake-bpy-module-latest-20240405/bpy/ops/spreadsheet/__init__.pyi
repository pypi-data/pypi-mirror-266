import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def add_row_filter_rule(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add a filter to remove rows from the displayed data

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def change_spreadsheet_data_source(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    component_type: typing.Any = 0,
    attribute_domain_type: typing.Any = 0,
):
    """Change visible data source in the spreadsheet

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param component_type: Component Type
    :type component_type: typing.Any
    :param attribute_domain_type: Attribute Domain Type
    :type attribute_domain_type: typing.Any
    """

    ...

def remove_row_filter_rule(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    index: typing.Any = 0,
):
    """Remove a row filter from the rules

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param index: Index
    :type index: typing.Any
    """

    ...

def toggle_pin(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Turn on or off pinning

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...
