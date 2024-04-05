import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

class ImagePreviewCollection:
    """Dictionary-like class of previews.This is a subclass of Python's built-in dict type,
    used to store multiple image previews.
    """

    def clear(self):
        """Clear all previews."""
        ...

    def close(self):
        """Close the collection and clear all previews."""
        ...

    def load(
        self,
        name: str,
        filepath: typing.Union[str, bytes],
        filetype: str,
        force_reload: bool = False,
    ) -> bool:
        """Generate a new preview from given file path.

        :param name: The name (unique id) identifying the preview.
        :type name: str
        :param filepath: The file path to generate the preview from.
        :type filepath: typing.Union[str, bytes]
        :param filetype: The type of file, needed to generate the preview in ['IMAGE', 'MOVIE', 'BLEND', 'FONT'].
        :type filetype: str
        :param force_reload: If True, force running thumbnail manager even if preview already exists in cache.
        :type force_reload: bool
        :return: The Preview matching given name, or a new empty one.
        :rtype: bpy.types.ImagePreview
        """
        ...

    def new(self, name: str) -> str:
        """Generate a new empty preview.

        :param name: The name (unique id) identifying the preview.
        :type name: str
        :return: The Preview matching given name, or a new empty one.
        :rtype: bpy.types.ImagePreview
        """
        ...

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
