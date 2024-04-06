import typing

GenericType = typing.TypeVar("GenericType")

def clear_by_owner(owner):
    """Clear all subscribers using this owner."""

    ...

def publish_rna(key):
    """Notify subscribers of changes to this property
    (this typically doesn't need to be called explicitly since changes will automatically publish updates).
    In some cases it may be useful to publish changes explicitly using more general keys.

        :param key: Represents the type of data being subscribed to

    Arguments include
    - `bpy.types.Property` instance.
    - `bpy.types.Struct` type.
    - (`bpy.types.Struct`, str) type and property name.
    """

    ...

def subscribe_rna(key, owner: typing.Any, args, notify, options=None()):
    """Register a message bus subscription. It will be cleared when another blend file is
    loaded, or can be cleared explicitly via `bpy.msgbus.clear_by_owner`.

        :param key: Represents the type of data being subscribed to

    Arguments include
    - `bpy.types.Property` instance.
    - `bpy.types.Struct` type.
    - (`bpy.types.Struct`, str) type and property name.
        :param owner: Handle for this subscription (compared by identity).
        :type owner: typing.Any
        :param options: Change the behavior of the subscriber.

    PERSISTENT when set, the subscriber will be kept when remapping ID data.
    """

    ...
