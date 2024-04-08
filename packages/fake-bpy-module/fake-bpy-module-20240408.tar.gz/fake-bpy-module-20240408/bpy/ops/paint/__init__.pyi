import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def add_simple_uvs(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add cube map UVs on mesh

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def add_texture_paint_slot(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "BASE_COLOR",
    slot_type: typing.Any = "IMAGE",
    name: typing.Union[str, typing.Any] = "Untitled",
    color: typing.Any = (0.0, 0.0, 0.0, 1.0),
    width: typing.Any = 1024,
    height: typing.Any = 1024,
    alpha: typing.Union[bool, typing.Any] = True,
    generated_type: typing.Union[str, int] = "BLANK",
    float: typing.Union[bool, typing.Any] = False,
    domain: typing.Union[str, int] = "POINT",
    data_type: typing.Union[str, int] = "FLOAT_COLOR",
):
    """Add a paint slot

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Material Layer Type, Material layer type of new paint slot
    :type type: typing.Any
    :param slot_type: Slot Type, Type of new paint slot
    :type slot_type: typing.Any
    :param name: Name, Name for new paint slot source
    :type name: typing.Union[str, typing.Any]
    :param color: Color, Default fill color
    :type color: typing.Any
    :param width: Width, Image width
    :type width: typing.Any
    :param height: Height, Image height
    :type height: typing.Any
    :param alpha: Alpha, Create an image with an alpha channel
    :type alpha: typing.Union[bool, typing.Any]
    :param generated_type: Generated Type, Fill the image with a grid for UV map testing
    :type generated_type: typing.Union[str, int]
    :param float: 32-bit Float, Create image with 32-bit floating-point bit depth
    :type float: typing.Union[bool, typing.Any]
    :param domain: Domain, Type of element that attribute is stored on
    :type domain: typing.Union[str, int]
    :param data_type: Data Type, Type of data stored in attribute
    :type data_type: typing.Union[str, int]
    """

    ...

def brush_colors_flip(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Swap primary and secondary brush colors

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def brush_select(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    sculpt_tool: typing.Union[str, int] = "DRAW",
    vertex_tool: typing.Union[str, int] = "DRAW",
    weight_tool: typing.Union[str, int] = "DRAW",
    image_tool: typing.Union[str, int] = "DRAW",
    gpencil_tool: typing.Union[str, int] = "DRAW",
    gpencil_vertex_tool: typing.Union[str, int] = "DRAW",
    gpencil_sculpt_tool: typing.Union[str, int] = "SMOOTH",
    gpencil_weight_tool: typing.Union[str, int] = "WEIGHT",
    curves_sculpt_tool: typing.Union[str, int] = "COMB",
    toggle: typing.Union[bool, typing.Any] = False,
    create_missing: typing.Union[bool, typing.Any] = False,
):
    """Select a paint mode's brush by tool type

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param sculpt_tool: sculpt_tool
    :type sculpt_tool: typing.Union[str, int]
    :param vertex_tool: vertex_tool
    :type vertex_tool: typing.Union[str, int]
    :param weight_tool: weight_tool
    :type weight_tool: typing.Union[str, int]
    :param image_tool: image_tool
    :type image_tool: typing.Union[str, int]
    :param gpencil_tool: gpencil_tool
    :type gpencil_tool: typing.Union[str, int]
    :param gpencil_vertex_tool: gpencil_vertex_tool
    :type gpencil_vertex_tool: typing.Union[str, int]
    :param gpencil_sculpt_tool: gpencil_sculpt_tool
    :type gpencil_sculpt_tool: typing.Union[str, int]
    :param gpencil_weight_tool: gpencil_weight_tool
    :type gpencil_weight_tool: typing.Union[str, int]
    :param curves_sculpt_tool: curves_sculpt_tool
    :type curves_sculpt_tool: typing.Union[str, int]
    :param toggle: Toggle, Toggle between two brushes rather than cycling
    :type toggle: typing.Union[bool, typing.Any]
    :param create_missing: Create Missing, If the requested brush type does not exist, create a new brush
    :type create_missing: typing.Union[bool, typing.Any]
    """

    ...

def face_select_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    action: typing.Any = "TOGGLE",
):
    """Change selection for all faces

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

def face_select_hide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    unselected: typing.Union[bool, typing.Any] = False,
):
    """Hide selected faces

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param unselected: Unselected, Hide unselected rather than selected objects
    :type unselected: typing.Union[bool, typing.Any]
    """

    ...

def face_select_less(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    face_step: typing.Union[bool, typing.Any] = True,
):
    """Deselect Faces connected to existing selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param face_step: Face Step, Also deselect faces that only touch on a corner
    :type face_step: typing.Union[bool, typing.Any]
    """

    ...

def face_select_linked(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Select linked faces

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def face_select_linked_pick(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    deselect: typing.Union[bool, typing.Any] = False,
):
    """Select linked faces under the cursor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param deselect: Deselect, Deselect rather than select items
    :type deselect: typing.Union[bool, typing.Any]
    """

    ...

def face_select_loop(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    select: typing.Union[bool, typing.Any] = True,
    extend: typing.Union[bool, typing.Any] = False,
):
    """Select face loop under the cursor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param select: Select, If false, faces will be deselected
    :type select: typing.Union[bool, typing.Any]
    :param extend: Extend, Extend the selection
    :type extend: typing.Union[bool, typing.Any]
    """

    ...

def face_select_more(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    face_step: typing.Union[bool, typing.Any] = True,
):
    """Select Faces connected to existing selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param face_step: Face Step, Also select faces that only touch on a corner
    :type face_step: typing.Union[bool, typing.Any]
    """

    ...

def face_vert_reveal(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    select: typing.Union[bool, typing.Any] = True,
):
    """Reveal hidden faces and vertices

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param select: Select, Specifies whether the newly revealed geometry should be selected
    :type select: typing.Union[bool, typing.Any]
    """

    ...

def grab_clone(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    delta: typing.Any = (0.0, 0.0),
):
    """Move the clone source image

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param delta: Delta, Delta offset of clone image in 0.0 to 1.0 coordinates
    :type delta: typing.Any
    """

    ...

def hide_show(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    xmin: typing.Any = 0,
    xmax: typing.Any = 0,
    ymin: typing.Any = 0,
    ymax: typing.Any = 0,
    wait_for_input: typing.Union[bool, typing.Any] = True,
    action: typing.Any = "HIDE",
    area: typing.Any = "Inside",
    use_front_faces_only: typing.Union[bool, typing.Any] = False,
):
    """Hide/show some vertices

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param xmin: X Min
        :type xmin: typing.Any
        :param xmax: X Max
        :type xmax: typing.Any
        :param ymin: Y Min
        :type ymin: typing.Any
        :param ymax: Y Max
        :type ymax: typing.Any
        :param wait_for_input: Wait for Input
        :type wait_for_input: typing.Union[bool, typing.Any]
        :param action: Visibility Action, Whether to hide or show vertices

    HIDE
    Hide -- Hide vertices.

    SHOW
    Show -- Show vertices.
        :type action: typing.Any
        :param area: Visibility Area, Which vertices to hide or show

    OUTSIDE
    Outside -- Hide or show vertices outside the selection.

    Inside
    Inside -- Hide or show vertices inside the selection.
        :type area: typing.Any
        :param use_front_faces_only: Front Faces Only, Affect only faces facing towards the view
        :type use_front_faces_only: typing.Union[bool, typing.Any]
    """

    ...

def hide_show_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    action: typing.Any = "HIDE",
):
    """Hide/show all vertices

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param action: Visibility Action, Whether to hide or show vertices

    HIDE
    Hide -- Hide vertices.

    SHOW
    Show -- Show vertices.
        :type action: typing.Any
    """

    ...

def hide_show_lasso_gesture(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    path: bpy.types.bpy_prop_collection[bpy.types.OperatorMousePath] = None,
    action: typing.Any = "HIDE",
    area: typing.Any = "Inside",
    use_front_faces_only: typing.Union[bool, typing.Any] = False,
):
    """Hide/show some vertices

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param path: Path
        :type path: bpy.types.bpy_prop_collection[bpy.types.OperatorMousePath]
        :param action: Visibility Action, Whether to hide or show vertices

    HIDE
    Hide -- Hide vertices.

    SHOW
    Show -- Show vertices.
        :type action: typing.Any
        :param area: Visibility Area, Which vertices to hide or show

    OUTSIDE
    Outside -- Hide or show vertices outside the selection.

    Inside
    Inside -- Hide or show vertices inside the selection.
        :type area: typing.Any
        :param use_front_faces_only: Front Faces Only, Affect only faces facing towards the view
        :type use_front_faces_only: typing.Union[bool, typing.Any]
    """

    ...

def hide_show_line_gesture(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    xstart: typing.Any = 0,
    xend: typing.Any = 0,
    ystart: typing.Any = 0,
    yend: typing.Any = 0,
    flip: typing.Union[bool, typing.Any] = False,
    cursor: typing.Any = 5,
    action: typing.Any = "HIDE",
    area: typing.Any = "Inside",
    use_front_faces_only: typing.Union[bool, typing.Any] = False,
    use_limit_to_segment: typing.Union[bool, typing.Any] = False,
):
    """Hide/show some vertices

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param xstart: X Start
        :type xstart: typing.Any
        :param xend: X End
        :type xend: typing.Any
        :param ystart: Y Start
        :type ystart: typing.Any
        :param yend: Y End
        :type yend: typing.Any
        :param flip: Flip
        :type flip: typing.Union[bool, typing.Any]
        :param cursor: Cursor, Mouse cursor style to use during the modal operator
        :type cursor: typing.Any
        :param action: Visibility Action, Whether to hide or show vertices

    HIDE
    Hide -- Hide vertices.

    SHOW
    Show -- Show vertices.
        :type action: typing.Any
        :param area: Visibility Area, Which vertices to hide or show

    OUTSIDE
    Outside -- Hide or show vertices outside the selection.

    Inside
    Inside -- Hide or show vertices inside the selection.
        :type area: typing.Any
        :param use_front_faces_only: Front Faces Only, Affect only faces facing towards the view
        :type use_front_faces_only: typing.Union[bool, typing.Any]
        :param use_limit_to_segment: Limit to Segment, Apply the gesture action only to the area that is contained within the segment without extending its effect to the entire line
        :type use_limit_to_segment: typing.Union[bool, typing.Any]
    """

    ...

def hide_show_masked(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    action: typing.Any = "HIDE",
):
    """Hide/show all masked vertices above a threshold

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param action: Visibility Action, Whether to hide or show vertices

    HIDE
    Hide -- Hide vertices.

    SHOW
    Show -- Show vertices.
        :type action: typing.Any
    """

    ...

def image_from_view(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    filepath: typing.Union[str, typing.Any] = "",
):
    """Make an image from biggest 3D view for reprojection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param filepath: File Path, Name of the file
    :type filepath: typing.Union[str, typing.Any]
    """

    ...

def image_paint(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement] = None,
    mode: typing.Any = "NORMAL",
):
    """Paint a stroke into the image

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param stroke: Stroke
        :type stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement]
        :param mode: Stroke Mode, Action taken when a paint stroke is made

    NORMAL
    Regular -- Apply brush normally.

    INVERT
    Invert -- Invert action of brush for duration of stroke.

    SMOOTH
    Smooth -- Switch brush to smooth mode for duration of stroke.
        :type mode: typing.Any
    """

    ...

def mask_box_gesture(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    xmin: typing.Any = 0,
    xmax: typing.Any = 0,
    ymin: typing.Any = 0,
    ymax: typing.Any = 0,
    wait_for_input: typing.Union[bool, typing.Any] = True,
    use_front_faces_only: typing.Union[bool, typing.Any] = False,
    mode: typing.Any = "VALUE",
    value: typing.Any = 1.0,
):
    """Add mask within the box as you move the brush

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param xmin: X Min
        :type xmin: typing.Any
        :param xmax: X Max
        :type xmax: typing.Any
        :param ymin: Y Min
        :type ymin: typing.Any
        :param ymax: Y Max
        :type ymax: typing.Any
        :param wait_for_input: Wait for Input
        :type wait_for_input: typing.Union[bool, typing.Any]
        :param use_front_faces_only: Front Faces Only, Affect only faces facing towards the view
        :type use_front_faces_only: typing.Union[bool, typing.Any]
        :param mode: Mode

    VALUE
    Value -- Set mask to the level specified by the 'value' property.

    VALUE_INVERSE
    Value Inverted -- Set mask to the level specified by the inverted 'value' property.

    INVERT
    Invert -- Invert the mask.
        :type mode: typing.Any
        :param value: Value, Mask level to use when mode is 'Value'; zero means no masking and one is fully masked
        :type value: typing.Any
    """

    ...

def mask_flood_fill(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "VALUE",
    value: typing.Any = 0.0,
):
    """Fill the whole mask with a given value, or invert its values

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param mode: Mode

    VALUE
    Value -- Set mask to the level specified by the 'value' property.

    VALUE_INVERSE
    Value Inverted -- Set mask to the level specified by the inverted 'value' property.

    INVERT
    Invert -- Invert the mask.
        :type mode: typing.Any
        :param value: Value, Mask level to use when mode is 'Value'; zero means no masking and one is fully masked
        :type value: typing.Any
    """

    ...

def mask_lasso_gesture(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    path: bpy.types.bpy_prop_collection[bpy.types.OperatorMousePath] = None,
    use_front_faces_only: typing.Union[bool, typing.Any] = False,
    mode: typing.Any = "VALUE",
    value: typing.Any = 1.0,
):
    """Add mask within the lasso as you move the brush

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param path: Path
        :type path: bpy.types.bpy_prop_collection[bpy.types.OperatorMousePath]
        :param use_front_faces_only: Front Faces Only, Affect only faces facing towards the view
        :type use_front_faces_only: typing.Union[bool, typing.Any]
        :param mode: Mode

    VALUE
    Value -- Set mask to the level specified by the 'value' property.

    VALUE_INVERSE
    Value Inverted -- Set mask to the level specified by the inverted 'value' property.

    INVERT
    Invert -- Invert the mask.
        :type mode: typing.Any
        :param value: Value, Mask level to use when mode is 'Value'; zero means no masking and one is fully masked
        :type value: typing.Any
    """

    ...

def mask_line_gesture(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    xstart: typing.Any = 0,
    xend: typing.Any = 0,
    ystart: typing.Any = 0,
    yend: typing.Any = 0,
    flip: typing.Union[bool, typing.Any] = False,
    cursor: typing.Any = 5,
    use_front_faces_only: typing.Union[bool, typing.Any] = False,
    use_limit_to_segment: typing.Union[bool, typing.Any] = False,
    mode: typing.Any = "VALUE",
    value: typing.Any = 1.0,
):
    """Add mask to the right of a line as you move the brush

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param xstart: X Start
        :type xstart: typing.Any
        :param xend: X End
        :type xend: typing.Any
        :param ystart: Y Start
        :type ystart: typing.Any
        :param yend: Y End
        :type yend: typing.Any
        :param flip: Flip
        :type flip: typing.Union[bool, typing.Any]
        :param cursor: Cursor, Mouse cursor style to use during the modal operator
        :type cursor: typing.Any
        :param use_front_faces_only: Front Faces Only, Affect only faces facing towards the view
        :type use_front_faces_only: typing.Union[bool, typing.Any]
        :param use_limit_to_segment: Limit to Segment, Apply the gesture action only to the area that is contained within the segment without extending its effect to the entire line
        :type use_limit_to_segment: typing.Union[bool, typing.Any]
        :param mode: Mode

    VALUE
    Value -- Set mask to the level specified by the 'value' property.

    VALUE_INVERSE
    Value Inverted -- Set mask to the level specified by the inverted 'value' property.

    INVERT
    Invert -- Invert the mask.
        :type mode: typing.Any
        :param value: Value, Mask level to use when mode is 'Value'; zero means no masking and one is fully masked
        :type value: typing.Any
    """

    ...

def project_image(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    image: typing.Union[str, int, typing.Any] = "",
):
    """Project an edited render from the active camera back onto the object

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param image: Image
    :type image: typing.Union[str, int, typing.Any]
    """

    ...

def sample_color(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    location: typing.Any = (0, 0),
    merged: typing.Union[bool, typing.Any] = False,
    palette: typing.Union[bool, typing.Any] = False,
):
    """Use the mouse to sample a color in the image

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param location: Location
    :type location: typing.Any
    :param merged: Sample Merged, Sample the output display color
    :type merged: typing.Union[bool, typing.Any]
    :param palette: Add to Palette
    :type palette: typing.Union[bool, typing.Any]
    """

    ...

def texture_paint_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Toggle texture paint mode in 3D view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def vert_select_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    action: typing.Any = "TOGGLE",
):
    """Change selection for all vertices

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

def vert_select_hide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    unselected: typing.Union[bool, typing.Any] = False,
):
    """Hide selected vertices

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param unselected: Unselected, Hide unselected rather than selected vertices
    :type unselected: typing.Union[bool, typing.Any]
    """

    ...

def vert_select_less(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    face_step: typing.Union[bool, typing.Any] = True,
):
    """Deselect Vertices connected to existing selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param face_step: Face Step, Also deselect faces that only touch on a corner
    :type face_step: typing.Union[bool, typing.Any]
    """

    ...

def vert_select_linked(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Select linked vertices

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def vert_select_linked_pick(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    select: typing.Union[bool, typing.Any] = True,
):
    """Select linked vertices under the cursor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param select: Select, Whether to select or deselect linked vertices under the cursor
    :type select: typing.Union[bool, typing.Any]
    """

    ...

def vert_select_more(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    face_step: typing.Union[bool, typing.Any] = True,
):
    """Select Vertices connected to existing selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param face_step: Face Step, Also select faces that only touch on a corner
    :type face_step: typing.Union[bool, typing.Any]
    """

    ...

def vert_select_ungrouped(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    extend: typing.Union[bool, typing.Any] = False,
):
    """Select vertices without a group

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param extend: Extend, Extend the selection
    :type extend: typing.Union[bool, typing.Any]
    """

    ...

def vertex_color_brightness_contrast(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    brightness: typing.Any = 0.0,
    contrast: typing.Any = 0.0,
):
    """Adjust vertex color brightness/contrast

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param brightness: Brightness
    :type brightness: typing.Any
    :param contrast: Contrast
    :type contrast: typing.Any
    """

    ...

def vertex_color_dirt(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    blur_strength: typing.Any = 1.0,
    blur_iterations: typing.Any = 1,
    clean_angle: typing.Any = 3.14159,
    dirt_angle: typing.Any = 0.0,
    dirt_only: typing.Union[bool, typing.Any] = False,
    normalize: typing.Union[bool, typing.Any] = True,
):
    """Generate a dirt map gradient based on cavity

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param blur_strength: Blur Strength, Blur strength per iteration
    :type blur_strength: typing.Any
    :param blur_iterations: Blur Iterations, Number of times to blur the colors (higher blurs more)
    :type blur_iterations: typing.Any
    :param clean_angle: Highlight Angle, Less than 90 limits the angle used in the tonal range
    :type clean_angle: typing.Any
    :param dirt_angle: Dirt Angle, Less than 90 limits the angle used in the tonal range
    :type dirt_angle: typing.Any
    :param dirt_only: Dirt Only, Don't calculate cleans for convex areas
    :type dirt_only: typing.Union[bool, typing.Any]
    :param normalize: Normalize, Normalize the colors, increasing the contrast
    :type normalize: typing.Union[bool, typing.Any]
    """

    ...

def vertex_color_from_weight(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Convert active weight into gray scale vertex colors

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def vertex_color_hsv(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    h: typing.Any = 0.5,
    s: typing.Any = 1.0,
    v: typing.Any = 1.0,
):
    """Adjust vertex color Hue/Saturation/Value

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param h: Hue
    :type h: typing.Any
    :param s: Saturation
    :type s: typing.Any
    :param v: Value
    :type v: typing.Any
    """

    ...

def vertex_color_invert(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Invert RGB values

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def vertex_color_levels(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    offset: typing.Any = 0.0,
    gain: typing.Any = 1.0,
):
    """Adjust levels of vertex colors

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param offset: Offset, Value to add to colors
    :type offset: typing.Any
    :param gain: Gain, Value to multiply colors by
    :type gain: typing.Any
    """

    ...

def vertex_color_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    use_alpha: typing.Union[bool, typing.Any] = True,
):
    """Fill the active vertex color layer with the current paint color

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param use_alpha: Affect Alpha, Set color completely opaque instead of reusing existing alpha
    :type use_alpha: typing.Union[bool, typing.Any]
    """

    ...

def vertex_color_smooth(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Smooth colors across vertices

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def vertex_paint(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement] = None,
    mode: typing.Any = "NORMAL",
):
    """Paint a stroke in the active color attribute layer

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param stroke: Stroke
        :type stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement]
        :param mode: Stroke Mode, Action taken when a paint stroke is made

    NORMAL
    Regular -- Apply brush normally.

    INVERT
    Invert -- Invert action of brush for duration of stroke.

    SMOOTH
    Smooth -- Switch brush to smooth mode for duration of stroke.
        :type mode: typing.Any
    """

    ...

def vertex_paint_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Toggle the vertex paint mode in 3D view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def visibility_invert(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Invert the visibility of all vertices

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def weight_from_bones(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "AUTOMATIC",
):
    """Set the weights of the groups matching the attached armature's selected bones, using the distance between the vertices and the bones

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Type, Method to use for assigning weights

    AUTOMATIC
    Automatic -- Automatic weights from bones.

    ENVELOPES
    From Envelopes -- Weights from envelopes with user defined radius.
        :type type: typing.Any
    """

    ...

def weight_gradient(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "LINEAR",
    xstart: typing.Any = 0,
    xend: typing.Any = 0,
    ystart: typing.Any = 0,
    yend: typing.Any = 0,
    flip: typing.Union[bool, typing.Any] = False,
    cursor: typing.Any = 5,
):
    """Draw a line to apply a weight gradient to selected vertices

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type
    :type type: typing.Any
    :param xstart: X Start
    :type xstart: typing.Any
    :param xend: X End
    :type xend: typing.Any
    :param ystart: Y Start
    :type ystart: typing.Any
    :param yend: Y End
    :type yend: typing.Any
    :param flip: Flip
    :type flip: typing.Union[bool, typing.Any]
    :param cursor: Cursor, Mouse cursor style to use during the modal operator
    :type cursor: typing.Any
    """

    ...

def weight_paint(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement] = None,
    mode: typing.Any = "NORMAL",
):
    """Paint a stroke in the current vertex group's weights

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param stroke: Stroke
        :type stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement]
        :param mode: Stroke Mode, Action taken when a paint stroke is made

    NORMAL
    Regular -- Apply brush normally.

    INVERT
    Invert -- Invert action of brush for duration of stroke.

    SMOOTH
    Smooth -- Switch brush to smooth mode for duration of stroke.
        :type mode: typing.Any
    """

    ...

def weight_paint_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Toggle weight paint mode in 3D view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def weight_sample(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Use the mouse to sample a weight in the 3D view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def weight_sample_group(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Select one of the vertex groups available under current mouse position

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def weight_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Fill the active vertex group with the current paint weight

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...
