import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def attribute_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value_float: typing.Any = 0.0,
    value_float_vector_2d: typing.Any = (0.0, 0.0),
    value_float_vector_3d: typing.Any = (0.0, 0.0, 0.0),
    value_int: typing.Any = 0,
    value_int_vector_2d: typing.Any = (0, 0),
    value_color: typing.Any = (1.0, 1.0, 1.0, 1.0),
    value_bool: typing.Union[bool, typing.Any] = False,
):
    """Set values of the active attribute for selected elements

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value_float: Value
    :type value_float: typing.Any
    :param value_float_vector_2d: Value
    :type value_float_vector_2d: typing.Any
    :param value_float_vector_3d: Value
    :type value_float_vector_3d: typing.Any
    :param value_int: Value
    :type value_int: typing.Any
    :param value_int_vector_2d: Value
    :type value_int_vector_2d: typing.Any
    :param value_color: Value
    :type value_color: typing.Any
    :param value_bool: Value
    :type value_bool: typing.Union[bool, typing.Any]
    """

    ...

def convert_from_particle_system(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add a new curves object based on the current state of the particle system

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def convert_to_particle_system(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add a new or update an existing hair particle system on the surface object

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def curve_type_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Union[str, int] = "POLY",
):
    """Set type of selected curves

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type, Curve type
    :type type: typing.Union[str, int]
    """

    ...

def cyclic_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Make active curve closed/opened loop

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def delete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Remove selected control points or curves

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def draw(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    error_threshold: typing.Any = 0.0,
    fit_method: typing.Union[str, int] = "REFIT",
    corner_angle: typing.Any = 1.22173,
    use_cyclic: typing.Union[bool, typing.Any] = True,
    stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement] = None,
    wait_for_input: typing.Union[bool, typing.Any] = True,
    is_curve_2d: typing.Union[bool, typing.Any] = False,
    bezier_as_nurbs: typing.Union[bool, typing.Any] = False,
):
    """Draw a freehand curve

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param error_threshold: Error, Error distance threshold (in object units)
    :type error_threshold: typing.Any
    :param fit_method: Fit Method
    :type fit_method: typing.Union[str, int]
    :param corner_angle: Corner Angle
    :type corner_angle: typing.Any
    :param use_cyclic: Cyclic
    :type use_cyclic: typing.Union[bool, typing.Any]
    :param stroke: Stroke
    :type stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement]
    :param wait_for_input: Wait for Input
    :type wait_for_input: typing.Union[bool, typing.Any]
    :param is_curve_2d: Curve 2D
    :type is_curve_2d: typing.Union[bool, typing.Any]
    :param bezier_as_nurbs: As NURBS
    :type bezier_as_nurbs: typing.Union[bool, typing.Any]
    """

    ...

def duplicate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Copy selected points or curves

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def duplicate_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    CURVES_OT_duplicate: typing.Any = None,
    TRANSFORM_OT_translate: typing.Any = None,
):
    """Make copies of selected elements and move them

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param CURVES_OT_duplicate: Duplicate, Copy selected points or curves
    :type CURVES_OT_duplicate: typing.Any
    :param TRANSFORM_OT_translate: Move, Move selected items
    :type TRANSFORM_OT_translate: typing.Any
    """

    ...

def extrude(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Extrude selected control point(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def extrude_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    CURVES_OT_extrude: typing.Any = None,
    TRANSFORM_OT_translate: typing.Any = None,
):
    """Extrude curve and move result

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param CURVES_OT_extrude: Extrude, Extrude selected control point(s)
    :type CURVES_OT_extrude: typing.Any
    :param TRANSFORM_OT_translate: Move, Move selected items
    :type TRANSFORM_OT_translate: typing.Any
    """

    ...

def sculptmode_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Enter/Exit sculpt mode for curves

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    action: typing.Any = "TOGGLE",
):
    """(De)select all control points

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param action: Action, Selection action to execute

    TOGGLE
    Toggle -- Toggle selection for all elements.

    SELECT
    Select -- Select all elements.

    DESELECT
    Deselect -- Deselect all elements.

    INVERT
    Invert -- Invert selection of all elements.
        :type action: typing.Any
    """

    ...

def select_ends(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    amount_start: typing.Any = 0,
    amount_end: typing.Any = 1,
):
    """Select end points of curves

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param amount_start: Amount Front, Number of points to select from the front
    :type amount_start: typing.Any
    :param amount_end: Amount Back, Number of points to select from the back
    :type amount_end: typing.Any
    """

    ...

def select_less(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Shrink the selection by one point

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select_linked(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Select all points in curves with any point selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select_more(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Grow the selection by one point

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select_random(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    seed: typing.Any = 0,
    probability: typing.Any = 0.5,
):
    """Randomizes existing selection or create new random selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param seed: Seed, Source of randomness
    :type seed: typing.Any
    :param probability: Probability, Chance of every point or curve being included in the selection
    :type probability: typing.Any
    """

    ...

def set_selection_domain(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    domain: typing.Union[str, int] = "POINT",
):
    """Change the mode used for selection masking in curves sculpt mode

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param domain: Domain
    :type domain: typing.Union[str, int]
    """

    ...

def snap_curves_to_surface(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    attach_mode: typing.Any = "NEAREST",
):
    """Move curves so that the first point is exactly on the surface mesh

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param attach_mode: Attach Mode, How to find the point on the surface to attach to

    NEAREST
    Nearest -- Find the closest point on the surface for the root point of every curve and move the root there.

    DEFORM
    Deform -- Re-attach curves to a deformed surface using the existing attachment information. This only works when the topology of the surface mesh has not changed.
        :type attach_mode: typing.Any
    """

    ...

def subdivide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    number_cuts: typing.Any = 1,
):
    """Subdivide selected curve segments

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param number_cuts: Number of Cuts
    :type number_cuts: typing.Any
    """

    ...

def surface_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Use the active object as surface for selected curves objects and set it as the parent

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def switch_direction(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Reverse the direction of the selected curves

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def tilt_clear(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Clear the tilt of selected control points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...
