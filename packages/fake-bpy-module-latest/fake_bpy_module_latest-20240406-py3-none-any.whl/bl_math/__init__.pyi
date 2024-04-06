import typing

GenericType = typing.TypeVar("GenericType")

def clamp(value, min=0, max=1):
    """Clamps the float value between minimum and maximum. To avoid
    confusion, any call must use either one or all three arguments.

        :param value: The value to clamp.
        :param min: The minimum value, defaults to 0.
        :param max: The maximum value, defaults to 1.
        :return: The clamped value.
    """

    ...

def lerp(from_value, to_value, factor):
    """Linearly interpolate between two float values based on factor.

    :param from_value: The value to return when factor is 0.
    :param to_value: The value to return when factor is 1.
    :param factor: The interpolation value, normally in [0.0, 1.0].
    :return: The interpolated value.
    """

    ...

def smoothstep(from_value, to_value, value):
    """Performs smooth interpolation between 0 and 1 as value changes between from and to values.
    Outside the range the function returns the same value as the nearest edge.

        :param from_value: The edge value where the result is 0.
        :param to_value: The edge value where the result is 1.
        :return: The interpolated value in [0.0, 1.0].
    """

    ...
