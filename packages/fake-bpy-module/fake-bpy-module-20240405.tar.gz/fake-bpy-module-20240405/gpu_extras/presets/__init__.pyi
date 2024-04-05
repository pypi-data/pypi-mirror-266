import typing
import gpu.types
import mathutils

GenericType = typing.TypeVar("GenericType")

def draw_circle_2d(position: mathutils.Vector, color, radius, segments=None):
    """Draw a circle.

        :param position: Position where the circle will be drawn.
        :type position: mathutils.Vector
        :param color: Color of the circle. To use transparency GL_BLEND has to be enabled.
        :param radius: Radius of the circle.
        :param segments: How many segments will be used to draw the circle.
    Higher values give better results but the drawing will take longer.
    If None or not specified, an automatic value will be calculated.
    """

    ...

def draw_circle_2d(position: mathutils.Vector, color, radius, segments=None):
    """Draw a circle.

        :param position: Position where the circle will be drawn.
        :type position: mathutils.Vector
        :param color: Color of the circle. To use transparency GL_BLEND has to be enabled.
        :param radius: Radius of the circle.
        :param segments: How many segments will be used to draw the circle.
    Higher values give better results but the drawing will take longer.
    If None or not specified, an automatic value will be calculated.
    """

    ...

def draw_circle_2d(position, color, radius, segments):
    """ """

    ...

def draw_texture_2d(
    texture: gpu.types.GPUTexture, position: mathutils.Vector, width, height
):
    """Draw a 2d texture.

        :param texture: GPUTexture to draw (e.g. gpu.texture.from_image(image) for `bpy.types.Image`).
        :type texture: gpu.types.GPUTexture
        :param position: Position of the lower left corner.
        :type position: mathutils.Vector
        :param width: Width of the image when drawn (not necessarily
    the original width of the texture).
        :param height: Height of the image when drawn.
    """

    ...

def draw_texture_2d(
    texture: gpu.types.GPUTexture, position: mathutils.Vector, width, height
):
    """Draw a 2d texture.

        :param texture: GPUTexture to draw (e.g. gpu.texture.from_image(image) for `bpy.types.Image`).
        :type texture: gpu.types.GPUTexture
        :param position: Position of the lower left corner.
        :type position: mathutils.Vector
        :param width: Width of the image when drawn (not necessarily
    the original width of the texture).
        :param height: Height of the image when drawn.
    """

    ...

def draw_texture_2d(texture, position, width, height):
    """ """

    ...
