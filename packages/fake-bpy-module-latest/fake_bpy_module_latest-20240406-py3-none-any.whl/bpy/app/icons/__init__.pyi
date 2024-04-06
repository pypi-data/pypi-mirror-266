import typing

GenericType = typing.TypeVar("GenericType")

def new_triangles(
    range: tuple, coords: typing.Sequence[bytes], colors: typing.Sequence[bytes]
):
    """Create a new icon from triangle geometry.

    :param range: Pair of ints.
    :type range: tuple
    :param coords: Sequence of bytes (6 floats for one triangle) for (X, Y) coordinates.
    :type coords: typing.Sequence[bytes]
    :param colors: Sequence of ints (12 for one triangles) for RGBA.
    :type colors: typing.Sequence[bytes]
    :return: Unique icon value (pass to interface icon_value argument).
    """

    ...

def new_triangles_from_file(filepath: str):
    """Create a new icon from triangle geometry.

    :param filepath: File path.
    :type filepath: str
    :return: Unique icon value (pass to interface icon_value argument).
    """

    ...

def release(icon_id):
    """Release the icon."""

    ...
