import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def bake_action(
    obj: bpy.types.Object, action, frames, bake_options
) -> bpy.types.Action:
    """

        :param obj: Object to bake.
        :type obj: bpy.types.Object
        :param action: An action to bake the data into, or None for a new action
    to be created.
        :param frames: Frames to bake.
        :return: an action or None
        :rtype: bpy.types.Action
    """

    ...

def bake_action_iter(obj: bpy.types.Object, action, bake_options) -> bpy.types.Action:
    """An coroutine that bakes action for a single object.

        :param obj: Object to bake.
        :type obj: bpy.types.Object
        :param action: An action to bake the data into, or None for a new action
    to be created.
        :param bake_options: Boolean options of what to include into the action bake.
        :return: an action or None
        :rtype: bpy.types.Action
    """

    ...

def bake_action_objects(
    object_action_pairs, frames, bake_options
) -> typing.Iterable[bpy.types.Action]:
    """A version of `bake_action_objects_iter` that takes frames and returns the output.

    :param frames: Frames to bake.
    :return: A sequence of Action or None types (aligned with object_action_pairs)
    :rtype: typing.Iterable[bpy.types.Action]
    """

    ...

def bake_action_objects_iter(object_action_pairs, bake_options):
    """An coroutine that bakes actions for multiple objects.

        :param object_action_pairs: Sequence of object action tuples,
    action is the destination for the baked data. When None a new action will be created.
    """

    ...
