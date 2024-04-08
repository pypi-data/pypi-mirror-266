import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def create(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    name: typing.Union[str, typing.Any] = "Collection",
):
    """Create an object collection from selected objects

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param name: Name, Name of the new collection
    :type name: typing.Union[str, typing.Any]
    """

    ...

def objects_add_active(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    collection: typing.Union[str, int, typing.Any] = "",
):
    """Add the object to an object collection that contains the active object

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param collection: Collection, The collection to add other selected objects to
    :type collection: typing.Union[str, int, typing.Any]
    """

    ...

def objects_remove(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    collection: typing.Union[str, int, typing.Any] = "",
):
    """Remove selected objects from a collection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param collection: Collection, The collection to remove this object from
    :type collection: typing.Union[str, int, typing.Any]
    """

    ...

def objects_remove_active(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    collection: typing.Union[str, int, typing.Any] = "",
):
    """Remove the object from an object collection that contains the active object

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param collection: Collection, The collection to remove other selected objects from
    :type collection: typing.Union[str, int, typing.Any]
    """

    ...

def objects_remove_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Remove selected objects from all collections

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...
