import typing

GenericType = typing.TypeVar("GenericType")

class ImBuf:
    """ """

    channels: typing.Any
    """ Number of bit-planes."""

    filepath: str
    """ filepath associated with this image.

    :type: str
    """

    planes: typing.Any
    """ Number of bits associated with this image."""

    ppm: typing.Any
    """ pixels per meter."""

    size: typing.Any
    """ size of the image in pixels."""

    def copy(self):
        """

        :return: A copy of the image.
        :rtype: ImBuf
        """
        ...

    def crop(self, min, max):
        """Crop the image.

        :param min: X, Y minimum.
        :param max: X, Y maximum.
        """
        ...

    def free(self):
        """Clear image data immediately (causing an error on re-use)."""
        ...

    def resize(self, size, method: str = "FAST"):
        """Resize the image.

        :param size: New size.
        :param method: Method of resizing ('FAST', 'BILINEAR')
        :type method: str
        """
        ...
