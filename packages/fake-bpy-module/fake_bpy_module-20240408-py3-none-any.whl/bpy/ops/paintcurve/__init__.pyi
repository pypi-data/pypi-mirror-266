import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def add_point(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    location: typing.Any = (0, 0),
):
    """Add New Paint Curve Point

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param location: Location, Location of vertex in area space
    :type location: typing.Any
    """

    ...

def add_point_slide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    PAINTCURVE_OT_add_point: typing.Any = None,
    PAINTCURVE_OT_slide: typing.Any = None,
):
    """Add new curve point and slide it

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param PAINTCURVE_OT_add_point: Add New Paint Curve Point, Add New Paint Curve Point
    :type PAINTCURVE_OT_add_point: typing.Any
    :param PAINTCURVE_OT_slide: Slide Paint Curve Point, Select and slide paint curve point
    :type PAINTCURVE_OT_slide: typing.Any
    """

    ...

def cursor(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Place cursor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def delete_point(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Remove Paint Curve Point

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def draw(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Draw curve

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def new(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add new paint curve

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    location: typing.Any = (0, 0),
    toggle: typing.Union[bool, typing.Any] = False,
    extend: typing.Union[bool, typing.Any] = False,
):
    """Select a paint curve point

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param location: Location, Location of vertex in area space
    :type location: typing.Any
    :param toggle: Toggle, (De)select all
    :type toggle: typing.Union[bool, typing.Any]
    :param extend: Extend, Extend selection
    :type extend: typing.Union[bool, typing.Any]
    """

    ...

def slide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    align: typing.Union[bool, typing.Any] = False,
    select: typing.Union[bool, typing.Any] = True,
):
    """Select and slide paint curve point

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param align: Align Handles, Aligns opposite point handle during transform
    :type align: typing.Union[bool, typing.Any]
    :param select: Select, Attempt to select a point handle before transform
    :type select: typing.Union[bool, typing.Any]
    """

    ...
