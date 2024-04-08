import typing
import mathutils

GenericType = typing.TypeVar("GenericType")

class KDTree:
    """KdTree(size) -> new kd-tree initialized to hold size items."""

    def balance(self):
        """Balance the tree."""
        ...

    def find(
        self,
        co: typing.Union[typing.Sequence[float], mathutils.Vector],
        filter: typing.Callable = None,
    ) -> typing.Callable:
        """Find nearest point to co.

        :param co: 3d coordinates.
        :type co: typing.Union[typing.Sequence[float], mathutils.Vector]
        :param filter: function which takes an index and returns True for indices to include in the search.
        :type filter: typing.Callable
        :return: Returns (`Vector`, index, distance).
        :rtype: tuple
        """
        ...

    def find_n(self, co: typing.Union[typing.Sequence[float], mathutils.Vector], n):
        """Find nearest n points to co.

        :param co: 3d coordinates.
        :type co: typing.Union[typing.Sequence[float], mathutils.Vector]
        :param n: Number of points to find.
        :return: Returns a list of tuples (`Vector`, index, distance).
        :rtype: list
        """
        ...

    def find_range(
        self, co: typing.Union[typing.Sequence[float], mathutils.Vector], radius
    ):
        """Find all points within radius of co.

        :param co: 3d coordinates.
        :type co: typing.Union[typing.Sequence[float], mathutils.Vector]
        :param radius: Distance to search for points.
        :return: Returns a list of tuples (`Vector`, index, distance).
        :rtype: list
        """
        ...

    def insert(self, co: typing.Union[typing.Sequence[float], mathutils.Vector], index):
        """Insert a point into the KDTree.

        :param co: Point 3d position.
        :type co: typing.Union[typing.Sequence[float], mathutils.Vector]
        :param index: The index of the point.
        """
        ...

    def __init__(self, size):
        """

        :param size:
        """
        ...
