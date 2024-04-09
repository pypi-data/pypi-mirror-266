import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

class ImagePreviewCollection:
    """ """

    def clear(self):
        """ """
        ...

    def close(self):
        """ """
        ...

    def copy(self):
        """ """
        ...

    def fromkeys(self):
        """ """
        ...

    def get(self, key, default):
        """

        :param key:
        :param default:
        """
        ...

    def items(self):
        """ """
        ...

    def keys(self):
        """ """
        ...

    def load(self, name, path, path_type, force_reload):
        """

        :param name:
        :param path:
        :param path_type:
        :param force_reload:
        """
        ...

    def new(self, name):
        """

        :param name:
        """
        ...

    def pop(self):
        """ """
        ...

    def popitem(self):
        """ """
        ...

    def setdefault(self, key, default):
        """

        :param key:
        :param default:
        """
        ...

    def update(self):
        """ """
        ...

    def values(self):
        """ """
        ...

def new() -> ImagePreviewCollection:
    """

    :return: a new preview collection.
    :rtype: ImagePreviewCollection
    """

    ...

def new():
    """ """

    ...

def remove(pcoll: ImagePreviewCollection):
    """Remove the specified previews collection.

    :param pcoll: Preview collection to close.
    :type pcoll: ImagePreviewCollection
    """

    ...

def remove(pcoll):
    """ """

    ...
