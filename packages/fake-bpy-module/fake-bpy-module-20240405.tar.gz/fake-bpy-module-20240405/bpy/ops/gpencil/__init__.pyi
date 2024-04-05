import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def active_frame_delete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Delete the active frame for the active Grease Pencil Layer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def active_frames_delete_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Delete the active frame(s) of all editable Grease Pencil layers

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def annotate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "DRAW",
    arrowstyle_start: typing.Any = "NONE",
    arrowstyle_end: typing.Any = "NONE",
    use_stabilizer: typing.Union[bool, typing.Any] = False,
    stabilizer_factor: typing.Any = 0.75,
    stabilizer_radius: typing.Any = 35,
    stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement] = None,
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Make annotations on the active data

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param mode: Mode, Way to interpret mouse movements

    DRAW
    Draw Freehand -- Draw freehand stroke(s).

    DRAW_STRAIGHT
    Draw Straight Lines -- Draw straight line segment(s).

    DRAW_POLY
    Draw Poly Line -- Click to place endpoints of straight line segments (connected).

    ERASER
    Eraser -- Erase Annotation strokes.
        :type mode: typing.Any
        :param arrowstyle_start: Start Arrow Style, Stroke start style

    NONE
    None -- Don't use any arrow/style in corner.

    ARROW
    Arrow -- Use closed arrow style.

    ARROW_OPEN
    Open Arrow -- Use open arrow style.

    ARROW_OPEN_INVERTED
    Segment -- Use perpendicular segment style.

    DIAMOND
    Square -- Use square style.
        :type arrowstyle_start: typing.Any
        :param arrowstyle_end: End Arrow Style, Stroke end style

    NONE
    None -- Don't use any arrow/style in corner.

    ARROW
    Arrow -- Use closed arrow style.

    ARROW_OPEN
    Open Arrow -- Use open arrow style.

    ARROW_OPEN_INVERTED
    Segment -- Use perpendicular segment style.

    DIAMOND
    Square -- Use square style.
        :type arrowstyle_end: typing.Any
        :param use_stabilizer: Stabilize Stroke, Helper to draw smooth and clean lines. Press Shift for an invert effect (even if this option is not active)
        :type use_stabilizer: typing.Union[bool, typing.Any]
        :param stabilizer_factor: Stabilizer Stroke Factor, Higher values gives a smoother stroke
        :type stabilizer_factor: typing.Any
        :param stabilizer_radius: Stabilizer Stroke Radius, Minimum distance from last point before stroke continues
        :type stabilizer_radius: typing.Any
        :param stroke: Stroke
        :type stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement]
        :param wait_for_input: Wait for Input, Wait for first click instead of painting immediately
        :type wait_for_input: typing.Union[bool, typing.Any]
    """

    ...

def annotation_active_frame_delete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Delete the active frame for the active Annotation Layer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def annotation_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add new Annotation data-block

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def bake_grease_pencil_animation(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    frame_start: typing.Any = 1,
    frame_end: typing.Any = 250,
    step: typing.Any = 1,
    only_selected: typing.Union[bool, typing.Any] = False,
    frame_target: typing.Any = 1,
    project_type: typing.Any = "KEEP",
):
    """Bake grease pencil object transform to grease pencil keyframes

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param frame_start: Start Frame, The start frame
        :type frame_start: typing.Any
        :param frame_end: End Frame, The end frame of animation
        :type frame_end: typing.Any
        :param step: Step, Step between generated frames
        :type step: typing.Any
        :param only_selected: Only Selected Keyframes, Convert only selected keyframes
        :type only_selected: typing.Union[bool, typing.Any]
        :param frame_target: Target Frame, Destination frame
        :type frame_target: typing.Any
        :param project_type: Projection Type

    KEEP
    No Reproject.

    FRONT
    Front -- Reproject the strokes using the X-Z plane.

    SIDE
    Side -- Reproject the strokes using the Y-Z plane.

    TOP
    Top -- Reproject the strokes using the X-Y plane.

    VIEW
    View -- Reproject the strokes to end up on the same plane, as if drawn from the current viewpoint using 'Cursor' Stroke Placement.

    CURSOR
    Cursor -- Reproject the strokes using the orientation of 3D cursor.
        :type project_type: typing.Any
    """

    ...

def bake_mesh_animation(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    target: typing.Any = "NEW",
    frame_start: typing.Any = 1,
    frame_end: typing.Any = 250,
    step: typing.Any = 1,
    thickness: typing.Any = 1,
    angle: typing.Any = 1.22173,
    offset: typing.Any = 0.001,
    seams: typing.Union[bool, typing.Any] = False,
    faces: typing.Union[bool, typing.Any] = True,
    only_selected: typing.Union[bool, typing.Any] = False,
    frame_target: typing.Any = 1,
    project_type: typing.Any = "VIEW",
):
    """Bake mesh animation to grease pencil strokes

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param target: Target Object, Target grease pencil
        :type target: typing.Any
        :param frame_start: Start Frame, The start frame
        :type frame_start: typing.Any
        :param frame_end: End Frame, The end frame of animation
        :type frame_end: typing.Any
        :param step: Step, Step between generated frames
        :type step: typing.Any
        :param thickness: Thickness
        :type thickness: typing.Any
        :param angle: Threshold Angle, Threshold to determine ends of the strokes
        :type angle: typing.Any
        :param offset: Stroke Offset, Offset strokes from fill
        :type offset: typing.Any
        :param seams: Only Seam Edges, Convert only seam edges
        :type seams: typing.Union[bool, typing.Any]
        :param faces: Export Faces, Export faces as filled strokes
        :type faces: typing.Union[bool, typing.Any]
        :param only_selected: Only Selected Keyframes, Convert only selected keyframes
        :type only_selected: typing.Union[bool, typing.Any]
        :param frame_target: Target Frame, Destination frame
        :type frame_target: typing.Any
        :param project_type: Projection Type

    KEEP
    No Reproject.

    FRONT
    Front -- Reproject the strokes using the X-Z plane.

    SIDE
    Side -- Reproject the strokes using the Y-Z plane.

    TOP
    Top -- Reproject the strokes using the X-Y plane.

    VIEW
    View -- Reproject the strokes to end up on the same plane, as if drawn from the current viewpoint using 'Cursor' Stroke Placement.

    CURSOR
    Cursor -- Reproject the strokes using the orientation of 3D cursor.
        :type project_type: typing.Any
    """

    ...

def blank_frame_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    all_layers: typing.Union[bool, typing.Any] = False,
):
    """Insert a blank frame on the current frame (all subsequently existing frames, if any, are shifted right by one frame)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param all_layers: All Layers, Create blank frame in all layers, not only active
    :type all_layers: typing.Union[bool, typing.Any]
    """

    ...

def brush_reset(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Reset brush to default parameters

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def brush_reset_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Delete all mode brushes and recreate a default set

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def convert(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "PATH",
    bevel_depth: typing.Any = 0.0,
    bevel_resolution: typing.Any = 0,
    use_normalize_weights: typing.Union[bool, typing.Any] = True,
    radius_multiplier: typing.Any = 1.0,
    use_link_strokes: typing.Union[bool, typing.Any] = False,
    timing_mode: typing.Any = "FULL",
    frame_range: typing.Any = 100,
    start_frame: typing.Any = 1,
    use_realtime: typing.Union[bool, typing.Any] = False,
    end_frame: typing.Any = 250,
    gap_duration: typing.Any = 0.0,
    gap_randomness: typing.Any = 0.0,
    seed: typing.Any = 0,
    use_timing_data: typing.Union[bool, typing.Any] = False,
):
    """Convert the active Grease Pencil layer to a new Curve Object

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Type, Which type of curve to convert to

    PATH
    Path -- Animation path.

    CURVE
    Bézier Curve -- Smooth Bézier curve.

    POLY
    Polygon Curve -- Bézier curve with straight-line segments (vector handles).
        :type type: typing.Any
        :param bevel_depth: Bevel Depth
        :type bevel_depth: typing.Any
        :param bevel_resolution: Bevel Resolution, Bevel resolution when depth is non-zero
        :type bevel_resolution: typing.Any
        :param use_normalize_weights: Normalize Weight, Normalize weight (set from stroke width)
        :type use_normalize_weights: typing.Union[bool, typing.Any]
        :param radius_multiplier: Radius Factor, Multiplier for the points' radii (set from stroke width)
        :type radius_multiplier: typing.Any
        :param use_link_strokes: Link Strokes, Whether to link strokes with zero-radius sections of curves
        :type use_link_strokes: typing.Union[bool, typing.Any]
        :param timing_mode: Timing Mode, How to use timing data stored in strokes

    NONE
    No Timing -- Ignore timing.

    LINEAR
    Linear -- Simple linear timing.

    FULL
    Original -- Use the original timing, gaps included.

    CUSTOMGAP
    Custom Gaps -- Use the original timing, but with custom gap lengths (in frames).
        :type timing_mode: typing.Any
        :param frame_range: Frame Range, The duration of evaluation of the path control curve
        :type frame_range: typing.Any
        :param start_frame: Start Frame, The start frame of the path control curve
        :type start_frame: typing.Any
        :param use_realtime: Realtime, Whether the path control curve reproduces the drawing in realtime, starting from Start Frame
        :type use_realtime: typing.Union[bool, typing.Any]
        :param end_frame: End Frame, The end frame of the path control curve (if Realtime is not set)
        :type end_frame: typing.Any
        :param gap_duration: Gap Duration, Custom Gap mode: (Average) length of gaps, in frames (Note: Realtime value, will be scaled if Realtime is not set)
        :type gap_duration: typing.Any
        :param gap_randomness: Gap Randomness, Custom Gap mode: Number of frames that gap lengths can vary
        :type gap_randomness: typing.Any
        :param seed: Random Seed, Custom Gap mode: Random generator seed
        :type seed: typing.Any
        :param use_timing_data: Has Valid Timing, Whether the converted Grease Pencil layer has valid timing data (internal use)
        :type use_timing_data: typing.Union[bool, typing.Any]
    """

    ...

def convert_old_files(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    annotation: typing.Union[bool, typing.Any] = False,
):
    """Convert 2.7x grease pencil files to 2.80

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param annotation: Annotation, Convert to Annotations
    :type annotation: typing.Union[bool, typing.Any]
    """

    ...

def copy(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Copy selected Grease Pencil points and strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def data_unlink(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Unlink active Annotation data-block

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def delete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "POINTS",
):
    """Delete selected Grease Pencil strokes, vertices, or frames

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Type, Method used for deleting Grease Pencil data

    POINTS
    Points -- Delete selected points and split strokes into segments.

    STROKES
    Strokes -- Delete selected strokes.

    FRAME
    Frame -- Delete active frame.
        :type type: typing.Any
    """

    ...

def dissolve(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "POINTS",
):
    """Delete selected points without splitting strokes

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Type, Method used for dissolving stroke points

    POINTS
    Dissolve -- Dissolve selected points.

    BETWEEN
    Dissolve Between -- Dissolve points between selected points.

    UNSELECT
    Dissolve Unselect -- Dissolve all unselected points.
        :type type: typing.Any
    """

    ...

def draw(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "DRAW",
    stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement] = None,
    wait_for_input: typing.Union[bool, typing.Any] = True,
    disable_straight: typing.Union[bool, typing.Any] = False,
    disable_fill: typing.Union[bool, typing.Any] = False,
    disable_stabilizer: typing.Union[bool, typing.Any] = False,
    guide_last_angle: typing.Any = 0.0,
):
    """Draw a new stroke in the active Grease Pencil object

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param mode: Mode, Way to interpret mouse movements

    DRAW
    Draw Freehand -- Draw freehand stroke(s).

    DRAW_STRAIGHT
    Draw Straight Lines -- Draw straight line segment(s).

    ERASER
    Eraser -- Erase Grease Pencil strokes.
        :type mode: typing.Any
        :param stroke: Stroke
        :type stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement]
        :param wait_for_input: Wait for Input, Wait for first click instead of painting immediately
        :type wait_for_input: typing.Union[bool, typing.Any]
        :param disable_straight: No Straight lines, Disable key for straight lines
        :type disable_straight: typing.Union[bool, typing.Any]
        :param disable_fill: No Fill Areas, Disable fill to use stroke as fill boundary
        :type disable_fill: typing.Union[bool, typing.Any]
        :param disable_stabilizer: No Stabilizer
        :type disable_stabilizer: typing.Union[bool, typing.Any]
        :param guide_last_angle: Angle, Speed guide angle
        :type guide_last_angle: typing.Any
    """

    ...

def duplicate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Duplicate the selected Grease Pencil strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def duplicate_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    GPENCIL_OT_duplicate: typing.Any = None,
    TRANSFORM_OT_translate: typing.Any = None,
):
    """Make copies of the selected Grease Pencil strokes and move them

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param GPENCIL_OT_duplicate: Duplicate Strokes, Duplicate the selected Grease Pencil strokes
    :type GPENCIL_OT_duplicate: typing.Any
    :param TRANSFORM_OT_translate: Move, Move selected items
    :type TRANSFORM_OT_translate: typing.Any
    """

    ...

def editmode_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    back: typing.Union[bool, typing.Any] = False,
):
    """Enter/Exit edit mode for Grease Pencil strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param back: Return to Previous Mode, Return to previous mode
    :type back: typing.Union[bool, typing.Any]
    """

    ...

def extract_palette_vertex(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    selected: typing.Union[bool, typing.Any] = False,
    threshold: typing.Any = 1,
):
    """Extract all colors used in Grease Pencil Vertex and create a Palette

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param selected: Only Selected, Convert only selected strokes
    :type selected: typing.Union[bool, typing.Any]
    :param threshold: Threshold
    :type threshold: typing.Any
    """

    ...

def extrude(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Extrude the selected Grease Pencil points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def extrude_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    GPENCIL_OT_extrude: typing.Any = None,
    TRANSFORM_OT_translate: typing.Any = None,
):
    """Extrude selected points and move them

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param GPENCIL_OT_extrude: Extrude Stroke Points, Extrude the selected Grease Pencil points
    :type GPENCIL_OT_extrude: typing.Any
    :param TRANSFORM_OT_translate: Move, Move selected items
    :type TRANSFORM_OT_translate: typing.Any
    """

    ...

def fill(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    on_back: typing.Union[bool, typing.Any] = False,
):
    """Fill with color the shape formed by strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param on_back: Draw on Back, Send new stroke to back
    :type on_back: typing.Union[bool, typing.Any]
    """

    ...

def frame_clean_duplicate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "ALL",
):
    """Remove duplicate keyframes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type
    :type type: typing.Any
    """

    ...

def frame_clean_fill(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "ACTIVE",
):
    """Remove 'no fill' boundary strokes

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param mode: Mode

    ACTIVE
    Active Frame Only -- Clean active frame only.

    ALL
    All Frames -- Clean all frames in all layers.
        :type mode: typing.Any
    """

    ...

def frame_clean_loose(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    limit: typing.Any = 1,
):
    """Remove loose points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param limit: Limit, Number of points to consider stroke as loose
    :type limit: typing.Any
    """

    ...

def frame_duplicate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "ACTIVE",
):
    """Make a copy of the active Grease Pencil Frame

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param mode: Mode

    ACTIVE
    Active -- Duplicate frame in active layer only.

    ALL
    All -- Duplicate active frames in all layers.
        :type mode: typing.Any
    """

    ...

def generate_weights(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "NAME",
    armature: typing.Union[str, int, typing.Any] = "DEFAULT",
    ratio: typing.Any = 0.1,
    decay: typing.Any = 0.8,
):
    """Generate automatic weights for armatures (requires armature modifier)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
    :param armature: Armature, Armature to use
    :type armature: typing.Union[str, int, typing.Any]
    :param ratio: Ratio, Ratio between bone length and influence radius
    :type ratio: typing.Any
    :param decay: Decay, Factor to reduce influence depending of distance to bone axis
    :type decay: typing.Any
    """

    ...

def guide_rotate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    increment: typing.Union[bool, typing.Any] = True,
    angle: typing.Any = 0.0,
):
    """Rotate guide angle

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param increment: Increment, Increment angle
    :type increment: typing.Union[bool, typing.Any]
    :param angle: Angle, Guide angle
    :type angle: typing.Any
    """

    ...

def hide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    unselected: typing.Union[bool, typing.Any] = False,
):
    """Hide selected/unselected Grease Pencil layers

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param unselected: Unselected, Hide unselected rather than selected layers
    :type unselected: typing.Union[bool, typing.Any]
    """

    ...

def image_to_grease_pencil(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    size: typing.Any = 0.005,
    mask: typing.Union[bool, typing.Any] = False,
):
    """Generate a Grease Pencil Object using Image as source

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param size: Point Size, Size used for grease pencil points
    :type size: typing.Any
    :param mask: Generate Mask, Create an inverted image for masking using alpha channel
    :type mask: typing.Union[bool, typing.Any]
    """

    ...

def interpolate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    shift: typing.Any = 0.0,
    layers: typing.Any = "ACTIVE",
    interpolate_selected_only: typing.Union[bool, typing.Any] = False,
    exclude_breakdowns: typing.Union[bool, typing.Any] = False,
    flip: typing.Any = "AUTO",
    smooth_steps: typing.Any = 1,
    smooth_factor: typing.Any = 0.0,
    release_confirm: typing.Union[bool, typing.Any] = False,
):
    """Interpolate grease pencil strokes between frames

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param shift: Shift, Bias factor for which frame has more influence on the interpolated strokes
    :type shift: typing.Any
    :param layers: Layer, Layers included in the interpolation
    :type layers: typing.Any
    :param interpolate_selected_only: Only Selected, Interpolate only selected strokes
    :type interpolate_selected_only: typing.Union[bool, typing.Any]
    :param exclude_breakdowns: Exclude Breakdowns, Exclude existing Breakdowns keyframes as interpolation extremes
    :type exclude_breakdowns: typing.Union[bool, typing.Any]
    :param flip: Flip Mode, Invert destination stroke to match start and end with source stroke
    :type flip: typing.Any
    :param smooth_steps: Iterations, Number of times to smooth newly created strokes
    :type smooth_steps: typing.Any
    :param smooth_factor: Smooth, Amount of smoothing to apply to interpolated strokes, to reduce jitter/noise
    :type smooth_factor: typing.Any
    :param release_confirm: Confirm on Release
    :type release_confirm: typing.Union[bool, typing.Any]
    """

    ...

def interpolate_reverse(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Remove breakdown frames generated by interpolating between two Grease Pencil frames

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def interpolate_sequence(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    step: typing.Any = 1,
    layers: typing.Any = "ACTIVE",
    interpolate_selected_only: typing.Union[bool, typing.Any] = False,
    exclude_breakdowns: typing.Union[bool, typing.Any] = False,
    flip: typing.Any = "AUTO",
    smooth_steps: typing.Any = 1,
    smooth_factor: typing.Any = 0.0,
    type: typing.Any = "LINEAR",
    easing: typing.Any = "AUTO",
    back: typing.Any = 1.702,
    amplitude: typing.Any = 0.15,
    period: typing.Any = 0.15,
):
    """Generate 'in-betweens' to smoothly interpolate between Grease Pencil frames

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param step: Step, Number of frames between generated interpolated frames
        :type step: typing.Any
        :param layers: Layer, Layers included in the interpolation
        :type layers: typing.Any
        :param interpolate_selected_only: Only Selected, Interpolate only selected strokes
        :type interpolate_selected_only: typing.Union[bool, typing.Any]
        :param exclude_breakdowns: Exclude Breakdowns, Exclude existing Breakdowns keyframes as interpolation extremes
        :type exclude_breakdowns: typing.Union[bool, typing.Any]
        :param flip: Flip Mode, Invert destination stroke to match start and end with source stroke
        :type flip: typing.Any
        :param smooth_steps: Iterations, Number of times to smooth newly created strokes
        :type smooth_steps: typing.Any
        :param smooth_factor: Smooth, Amount of smoothing to apply to interpolated strokes, to reduce jitter/noise
        :type smooth_factor: typing.Any
        :param type: Type, Interpolation method to use the next time 'Interpolate Sequence' is run

    LINEAR
    Linear -- Straight-line interpolation between A and B (i.e. no ease in/out).

    CUSTOM
    Custom -- Custom interpolation defined using a curve map.

    SINE
    Sinusoidal -- Sinusoidal easing (weakest, almost linear but with a slight curvature).

    QUAD
    Quadratic -- Quadratic easing.

    CUBIC
    Cubic -- Cubic easing.

    QUART
    Quartic -- Quartic easing.

    QUINT
    Quintic -- Quintic easing.

    EXPO
    Exponential -- Exponential easing (dramatic).

    CIRC
    Circular -- Circular easing (strongest and most dynamic).

    BACK
    Back -- Cubic easing with overshoot and settle.

    BOUNCE
    Bounce -- Exponentially decaying parabolic bounce, like when objects collide.

    ELASTIC
    Elastic -- Exponentially decaying sine wave, like an elastic band.
        :type type: typing.Any
        :param easing: Easing, Which ends of the segment between the preceding and following grease pencil frames easing interpolation is applied to

    AUTO
    Automatic Easing -- Easing type is chosen automatically based on what the type of interpolation used (e.g. 'Ease In' for transitional types, and 'Ease Out' for dynamic effects).

    EASE_IN
    Ease In -- Only on the end closest to the next keyframe.

    EASE_OUT
    Ease Out -- Only on the end closest to the first keyframe.

    EASE_IN_OUT
    Ease In and Out -- Segment between both keyframes.
        :type easing: typing.Any
        :param back: Back, Amount of overshoot for 'back' easing
        :type back: typing.Any
        :param amplitude: Amplitude, Amount to boost elastic bounces for 'elastic' easing
        :type amplitude: typing.Any
        :param period: Period, Time between bounces for elastic easing
        :type period: typing.Any
    """

    ...

def layer_active(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    layer: typing.Any = 0,
):
    """Active Grease Pencil layer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param layer: Grease Pencil Layer
    :type layer: typing.Any
    """

    ...

def layer_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    layer: typing.Any = 0,
    new_layer_name: typing.Union[str, typing.Any] = "",
):
    """Add new layer or note for the active data-block

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param layer: Grease Pencil Layer
    :type layer: typing.Any
    :param new_layer_name: Name, Name of the newly added layer
    :type new_layer_name: typing.Union[str, typing.Any]
    """

    ...

def layer_annotation_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add new Annotation layer or note for the active data-block

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def layer_annotation_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "UP",
):
    """Move the active Annotation layer up/down in the list

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type
    :type type: typing.Any
    """

    ...

def layer_annotation_remove(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Remove active Annotation layer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def layer_change(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    layer: typing.Union[str, int, typing.Any] = "DEFAULT",
):
    """Change active Grease Pencil layer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param layer: Grease Pencil Layer
    :type layer: typing.Union[str, int, typing.Any]
    """

    ...

def layer_duplicate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "ALL",
):
    """Make a copy of the active Grease Pencil layer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
    """

    ...

def layer_duplicate_object(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "ALL",
    only_active: typing.Union[bool, typing.Any] = True,
):
    """Make a copy of the active Grease Pencil layer to selected object

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
    :param only_active: Only Active, Copy only active Layer, uncheck to append all layers
    :type only_active: typing.Union[bool, typing.Any]
    """

    ...

def layer_isolate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    affect_visibility: typing.Union[bool, typing.Any] = False,
):
    """Toggle whether the active layer is the only one that can be edited and/or visible

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param affect_visibility: Affect Visibility, In addition to toggling the editability, also affect the visibility
    :type affect_visibility: typing.Union[bool, typing.Any]
    """

    ...

def layer_mask_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    name: typing.Union[str, typing.Any] = "",
):
    """Add new layer as masking

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param name: Layer, Name of the layer
    :type name: typing.Union[str, typing.Any]
    """

    ...

def layer_mask_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "UP",
):
    """Move the active Grease Pencil mask layer up/down in the list

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type
    :type type: typing.Any
    """

    ...

def layer_mask_remove(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Remove Layer Mask

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def layer_merge(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "ACTIVE",
):
    """Combine Layers

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param mode: Mode

    ACTIVE
    Active -- Combine active layer into the layer below.

    ALL
    All -- Combine all layers into the active layer.
        :type mode: typing.Any
    """

    ...

def layer_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "UP",
):
    """Move the active Grease Pencil layer up/down in the list

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type
    :type type: typing.Any
    """

    ...

def layer_remove(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Remove active Grease Pencil layer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def lock_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Lock all Grease Pencil layers to prevent them from being accidentally modified

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def lock_layer(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Lock and hide any color not used in any layer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def material_hide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    unselected: typing.Union[bool, typing.Any] = False,
):
    """Hide selected/unselected Grease Pencil materials

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param unselected: Unselected, Hide unselected rather than selected colors
    :type unselected: typing.Union[bool, typing.Any]
    """

    ...

def material_isolate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    affect_visibility: typing.Union[bool, typing.Any] = False,
):
    """Toggle whether the active material is the only one that is editable and/or visible

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param affect_visibility: Affect Visibility, In addition to toggling the editability, also affect the visibility
    :type affect_visibility: typing.Union[bool, typing.Any]
    """

    ...

def material_lock_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Lock all Grease Pencil materials to prevent them from being accidentally modified

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def material_lock_unused(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Lock any material not used in any selected stroke

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def material_reveal(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Unhide all hidden Grease Pencil materials

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def material_select(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    deselect: typing.Union[bool, typing.Any] = False,
):
    """Select/Deselect all Grease Pencil strokes using current material

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param deselect: Deselect, Unselect strokes
    :type deselect: typing.Union[bool, typing.Any]
    """

    ...

def material_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    slot: typing.Union[str, int, typing.Any] = "DEFAULT",
):
    """Set active material

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param slot: Material Slot
    :type slot: typing.Union[str, int, typing.Any]
    """

    ...

def material_to_vertex_color(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    remove: typing.Union[bool, typing.Any] = True,
    palette: typing.Union[bool, typing.Any] = True,
    selected: typing.Union[bool, typing.Any] = False,
    threshold: typing.Any = 3,
):
    """Replace materials in strokes with Vertex Color

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param remove: Remove Unused Materials, Remove any unused material after the conversion
    :type remove: typing.Union[bool, typing.Any]
    :param palette: Create Palette, Create a new palette with colors
    :type palette: typing.Union[bool, typing.Any]
    :param selected: Only Selected, Convert only selected strokes
    :type selected: typing.Union[bool, typing.Any]
    :param threshold: Threshold
    :type threshold: typing.Any
    """

    ...

def material_unlock_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Unlock all Grease Pencil materials so that they can be edited

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def materials_copy_to_object(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    only_active: typing.Union[bool, typing.Any] = True,
):
    """Append Materials of the active Grease Pencil to other object

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param only_active: Only Active, Append only active material, uncheck to append all materials
    :type only_active: typing.Union[bool, typing.Any]
    """

    ...

def move_to_layer(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    layer: typing.Any = 0,
    new_layer_name: typing.Union[str, typing.Any] = "",
):
    """Move selected strokes to another layer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param layer: Grease Pencil Layer
    :type layer: typing.Any
    :param new_layer_name: Name, Name of the newly added layer
    :type new_layer_name: typing.Union[str, typing.Any]
    """

    ...

def paintmode_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    back: typing.Union[bool, typing.Any] = False,
):
    """Enter/Exit paint mode for Grease Pencil strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param back: Return to Previous Mode, Return to previous mode
    :type back: typing.Union[bool, typing.Any]
    """

    ...

def paste(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "ACTIVE",
    paste_back: typing.Union[bool, typing.Any] = False,
):
    """Paste previously copied strokes to active layer or to original layer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type
    :type type: typing.Any
    :param paste_back: Paste on Back, Add pasted strokes behind all strokes
    :type paste_back: typing.Union[bool, typing.Any]
    """

    ...

def primitive_box(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    subdivision: typing.Any = 3,
    edges: typing.Any = 1,
    type: typing.Any = "BOX",
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Create predefined grease pencil stroke box shapes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param subdivision: Subdivisions, Number of subdivisions per segment
    :type subdivision: typing.Any
    :param edges: Edges, Number of points per segment
    :type edges: typing.Any
    :param type: Type, Type of shape
    :type type: typing.Any
    :param wait_for_input: Wait for Input
    :type wait_for_input: typing.Union[bool, typing.Any]
    """

    ...

def primitive_circle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    subdivision: typing.Any = 94,
    edges: typing.Any = 1,
    type: typing.Any = "CIRCLE",
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Create predefined grease pencil stroke circle shapes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param subdivision: Subdivisions, Number of subdivisions per segment
    :type subdivision: typing.Any
    :param edges: Edges, Number of points per segment
    :type edges: typing.Any
    :param type: Type, Type of shape
    :type type: typing.Any
    :param wait_for_input: Wait for Input
    :type wait_for_input: typing.Union[bool, typing.Any]
    """

    ...

def primitive_curve(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    subdivision: typing.Any = 62,
    edges: typing.Any = 1,
    type: typing.Any = "CURVE",
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Create predefined grease pencil stroke curve shapes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param subdivision: Subdivisions, Number of subdivisions per segment
    :type subdivision: typing.Any
    :param edges: Edges, Number of points per segment
    :type edges: typing.Any
    :param type: Type, Type of shape
    :type type: typing.Any
    :param wait_for_input: Wait for Input
    :type wait_for_input: typing.Union[bool, typing.Any]
    """

    ...

def primitive_line(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    subdivision: typing.Any = 6,
    edges: typing.Any = 1,
    type: typing.Any = "LINE",
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Create predefined grease pencil stroke lines

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param subdivision: Subdivisions, Number of subdivisions per segment
    :type subdivision: typing.Any
    :param edges: Edges, Number of points per segment
    :type edges: typing.Any
    :param type: Type, Type of shape
    :type type: typing.Any
    :param wait_for_input: Wait for Input
    :type wait_for_input: typing.Union[bool, typing.Any]
    """

    ...

def primitive_polyline(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    subdivision: typing.Any = 6,
    edges: typing.Any = 1,
    type: typing.Any = "POLYLINE",
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Create predefined grease pencil stroke polylines

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param subdivision: Subdivisions, Number of subdivisions per segment
    :type subdivision: typing.Any
    :param edges: Edges, Number of points per segment
    :type edges: typing.Any
    :param type: Type, Type of shape
    :type type: typing.Any
    :param wait_for_input: Wait for Input
    :type wait_for_input: typing.Union[bool, typing.Any]
    """

    ...

def recalc_geometry(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Update all internal geometry data

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def reproject(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "VIEW",
    keep_original: typing.Union[bool, typing.Any] = False,
    offset: typing.Any = 0.0,
):
    """Reproject the selected strokes from the current viewpoint as if they had been newly drawn (e.g. to fix problems from accidental 3D cursor movement or accidental viewport changes, or for matching deforming geometry)

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Projection Type

    FRONT
    Front -- Reproject the strokes using the X-Z plane.

    SIDE
    Side -- Reproject the strokes using the Y-Z plane.

    TOP
    Top -- Reproject the strokes using the X-Y plane.

    VIEW
    View -- Reproject the strokes to end up on the same plane, as if drawn from the current viewpoint using 'Cursor' Stroke Placement.

    SURFACE
    Surface -- Reproject the strokes on to the scene geometry, as if drawn using 'Surface' placement.

    CURSOR
    Cursor -- Reproject the strokes using the orientation of 3D cursor.
        :type type: typing.Any
        :param keep_original: Keep Original, Keep original strokes and create a copy before reprojecting
        :type keep_original: typing.Union[bool, typing.Any]
        :param offset: Surface Offset
        :type offset: typing.Any
    """

    ...

def reset_transform_fill(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "ALL",
):
    """Reset any UV transformation and back to default values

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
    """

    ...

def reveal(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    select: typing.Union[bool, typing.Any] = True,
):
    """Show all Grease Pencil layers

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param select: Select
    :type select: typing.Union[bool, typing.Any]
    """

    ...

def sculpt_paint(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement] = None,
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Apply tweaks to strokes by painting over the strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param stroke: Stroke
    :type stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement]
    :param wait_for_input: Wait for Input, Enter a mini 'sculpt-mode' if enabled, otherwise, exit after drawing a single stroke
    :type wait_for_input: typing.Union[bool, typing.Any]
    """

    ...

def sculptmode_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    back: typing.Union[bool, typing.Any] = False,
):
    """Enter/Exit sculpt mode for Grease Pencil strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param back: Return to Previous Mode, Return to previous mode
    :type back: typing.Union[bool, typing.Any]
    """

    ...

def segment_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    modifier: typing.Union[str, typing.Any] = "",
):
    """Add a segment to the dash modifier

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param modifier: Modifier, Name of the modifier to edit
    :type modifier: typing.Union[str, typing.Any]
    """

    ...

def segment_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    modifier: typing.Union[str, typing.Any] = "",
    type: typing.Any = "UP",
):
    """Move the active dash segment up or down

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param modifier: Modifier, Name of the modifier to edit
    :type modifier: typing.Union[str, typing.Any]
    :param type: Type
    :type type: typing.Any
    """

    ...

def segment_remove(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    modifier: typing.Union[str, typing.Any] = "",
    index: typing.Any = 0,
):
    """Remove the active segment from the dash modifier

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param modifier: Modifier, Name of the modifier to edit
    :type modifier: typing.Union[str, typing.Any]
    :param index: Index, Index of the segment to remove
    :type index: typing.Any
    """

    ...

def select(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    extend: typing.Union[bool, typing.Any] = False,
    deselect: typing.Union[bool, typing.Any] = False,
    toggle: typing.Union[bool, typing.Any] = False,
    deselect_all: typing.Union[bool, typing.Any] = False,
    select_passthrough: typing.Union[bool, typing.Any] = False,
    entire_strokes: typing.Union[bool, typing.Any] = False,
    location: typing.Any = (0, 0),
    use_shift_extend: typing.Union[bool, typing.Any] = False,
):
    """Select Grease Pencil strokes and/or stroke points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param extend: Extend, Extend selection instead of deselecting everything first
    :type extend: typing.Union[bool, typing.Any]
    :param deselect: Deselect, Remove from selection
    :type deselect: typing.Union[bool, typing.Any]
    :param toggle: Toggle Selection, Toggle the selection
    :type toggle: typing.Union[bool, typing.Any]
    :param deselect_all: Deselect On Nothing, Deselect all when nothing under the cursor
    :type deselect_all: typing.Union[bool, typing.Any]
    :param select_passthrough: Only Select Unselected, Ignore the select action when the element is already selected
    :type select_passthrough: typing.Union[bool, typing.Any]
    :param entire_strokes: Entire Strokes, Select entire strokes instead of just the nearest stroke vertex
    :type entire_strokes: typing.Union[bool, typing.Any]
    :param location: Location, Mouse location
    :type location: typing.Any
    :param use_shift_extend: Extend
    :type use_shift_extend: typing.Union[bool, typing.Any]
    """

    ...

def select_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    action: typing.Any = "TOGGLE",
):
    """Change selection of all Grease Pencil strokes currently visible

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

def select_alternate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    unselect_ends: typing.Union[bool, typing.Any] = False,
):
    """Select alternative points in same strokes as already selected points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param unselect_ends: Unselect Ends, Do not select the first and last point of the stroke
    :type unselect_ends: typing.Union[bool, typing.Any]
    """

    ...

def select_box(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    xmin: typing.Any = 0,
    xmax: typing.Any = 0,
    ymin: typing.Any = 0,
    ymax: typing.Any = 0,
    wait_for_input: typing.Union[bool, typing.Any] = True,
    mode: typing.Any = "SET",
):
    """Select Grease Pencil strokes within a rectangular region

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
        :param mode: Mode

    SET
    Set -- Set a new selection.

    ADD
    Extend -- Extend existing selection.

    SUB
    Subtract -- Subtract existing selection.

    XOR
    Difference -- Invert existing selection.

    AND
    Intersect -- Intersect existing selection.
        :type mode: typing.Any
    """

    ...

def select_circle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    x: typing.Any = 0,
    y: typing.Any = 0,
    radius: typing.Any = 25,
    wait_for_input: typing.Union[bool, typing.Any] = True,
    mode: typing.Any = "SET",
):
    """Select Grease Pencil strokes using brush selection

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param x: X
        :type x: typing.Any
        :param y: Y
        :type y: typing.Any
        :param radius: Radius
        :type radius: typing.Any
        :param wait_for_input: Wait for Input
        :type wait_for_input: typing.Union[bool, typing.Any]
        :param mode: Mode

    SET
    Set -- Set a new selection.

    ADD
    Extend -- Extend existing selection.

    SUB
    Subtract -- Subtract existing selection.
        :type mode: typing.Any
    """

    ...

def select_first(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    only_selected_strokes: typing.Union[bool, typing.Any] = False,
    extend: typing.Union[bool, typing.Any] = False,
):
    """Select first point in Grease Pencil strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param only_selected_strokes: Selected Strokes Only, Only select the first point of strokes that already have points selected
    :type only_selected_strokes: typing.Union[bool, typing.Any]
    :param extend: Extend, Extend selection instead of deselecting all other selected points
    :type extend: typing.Union[bool, typing.Any]
    """

    ...

def select_grouped(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "LAYER",
):
    """Select all strokes with similar characteristics

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Type

    LAYER
    Layer -- Shared layers.

    MATERIAL
    Material -- Shared materials.
        :type type: typing.Any
    """

    ...

def select_lasso(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "SET",
    path: bpy.types.bpy_prop_collection[bpy.types.OperatorMousePath] = None,
):
    """Select Grease Pencil strokes using lasso selection

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param mode: Mode

    SET
    Set -- Set a new selection.

    ADD
    Extend -- Extend existing selection.

    SUB
    Subtract -- Subtract existing selection.

    XOR
    Difference -- Invert existing selection.

    AND
    Intersect -- Intersect existing selection.
        :type mode: typing.Any
        :param path: Path
        :type path: bpy.types.bpy_prop_collection[bpy.types.OperatorMousePath]
    """

    ...

def select_last(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    only_selected_strokes: typing.Union[bool, typing.Any] = False,
    extend: typing.Union[bool, typing.Any] = False,
):
    """Select last point in Grease Pencil strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param only_selected_strokes: Selected Strokes Only, Only select the last point of strokes that already have points selected
    :type only_selected_strokes: typing.Union[bool, typing.Any]
    :param extend: Extend, Extend selection instead of deselecting all other selected points
    :type extend: typing.Union[bool, typing.Any]
    """

    ...

def select_less(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Shrink sets of selected Grease Pencil points

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
    """Select all points in same strokes as already selected points

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
    """Grow sets of selected Grease Pencil points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select_random(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    ratio: typing.Any = 0.5,
    seed: typing.Any = 0,
    action: typing.Any = "SELECT",
    unselect_ends: typing.Union[bool, typing.Any] = False,
):
    """Select random points for non selected strokes

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param ratio: Ratio, Portion of items to select randomly
        :type ratio: typing.Any
        :param seed: Random Seed, Seed for the random number generator
        :type seed: typing.Any
        :param action: Action, Selection action to execute

    SELECT
    Select -- Select all elements.

    DESELECT
    Deselect -- Deselect all elements.
        :type action: typing.Any
        :param unselect_ends: Unselect Ends, Do not select the first and last point of the stroke
        :type unselect_ends: typing.Union[bool, typing.Any]
    """

    ...

def select_vertex_color(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    threshold: typing.Any = 0,
):
    """Select all points with similar vertex color of current selected

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param threshold: Threshold, Tolerance of the selection. Higher values select a wider range of similar colors
    :type threshold: typing.Any
    """

    ...

def selection_opacity_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Hide/Unhide selected points for Grease Pencil strokes setting alpha factor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def selectmode_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = 0,
):
    """Set selection mode for Grease Pencil strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Select Mode, Select mode
    :type mode: typing.Any
    """

    ...

def set_active_material(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Set the selected stroke material as the active material

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def snap_cursor_to_selected(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Snap cursor to center of selected points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def snap_to_cursor(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    use_offset: typing.Union[bool, typing.Any] = True,
):
    """Snap selected points/strokes to the cursor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param use_offset: With Offset, Offset the entire stroke instead of selected points only
    :type use_offset: typing.Union[bool, typing.Any]
    """

    ...

def snap_to_grid(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Snap selected points to the nearest grid points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def stroke_apply_thickness(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Apply the thickness change of the layer to its strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def stroke_arrange(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    direction: typing.Any = "UP",
):
    """Arrange selected strokes up/down in the display order of the active layer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param direction: Direction
    :type direction: typing.Any
    """

    ...

def stroke_caps_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "TOGGLE",
):
    """Change stroke caps mode (rounded or flat)

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Type

    TOGGLE
    Both.

    START
    Start.

    END
    End.

    DEFAULT
    Default -- Set as default rounded.
        :type type: typing.Any
    """

    ...

def stroke_change_color(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    material: typing.Union[str, typing.Any] = "",
):
    """Move selected strokes to active material

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param material: Material, Name of the material
    :type material: typing.Union[str, typing.Any]
    """

    ...

def stroke_cutter(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    path: bpy.types.bpy_prop_collection[bpy.types.OperatorMousePath] = None,
    flat_caps: typing.Union[bool, typing.Any] = False,
):
    """Select section and cut

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param path: Path
    :type path: bpy.types.bpy_prop_collection[bpy.types.OperatorMousePath]
    :param flat_caps: Flat Caps
    :type flat_caps: typing.Union[bool, typing.Any]
    """

    ...

def stroke_cyclical_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "TOGGLE",
    geometry: typing.Union[bool, typing.Any] = False,
):
    """Close or open the selected stroke adding a segment from last to first point

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type
    :type type: typing.Any
    :param geometry: Create Geometry, Create new geometry for closing stroke
    :type geometry: typing.Union[bool, typing.Any]
    """

    ...

def stroke_editcurve_set_handle_type(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "AUTOMATIC",
):
    """Set the type of an edit curve handle

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type, Spline type
    :type type: typing.Any
    """

    ...

def stroke_enter_editcurve_mode(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    error_threshold: typing.Any = 0.1,
):
    """Called to transform a stroke into a curve

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param error_threshold: Error Threshold, Threshold on the maximum deviation from the actual stroke
    :type error_threshold: typing.Any
    """

    ...

def stroke_flip(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Change direction of the points of the selected strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def stroke_join(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "JOIN",
    leave_gaps: typing.Union[bool, typing.Any] = False,
):
    """Join selected strokes (optionally as new stroke)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type
    :type type: typing.Any
    :param leave_gaps: Leave Gaps, Leave gaps between joined strokes instead of linking them
    :type leave_gaps: typing.Union[bool, typing.Any]
    """

    ...

def stroke_merge(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "STROKE",
    back: typing.Union[bool, typing.Any] = False,
    additive: typing.Union[bool, typing.Any] = False,
    cyclic: typing.Union[bool, typing.Any] = False,
    clear_point: typing.Union[bool, typing.Any] = False,
    clear_stroke: typing.Union[bool, typing.Any] = False,
):
    """Create a new stroke with the selected stroke points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
    :param back: Draw on Back, Draw new stroke below all previous strokes
    :type back: typing.Union[bool, typing.Any]
    :param additive: Additive Drawing, Add to previous drawing
    :type additive: typing.Union[bool, typing.Any]
    :param cyclic: Cyclic, Close new stroke
    :type cyclic: typing.Union[bool, typing.Any]
    :param clear_point: Dissolve Points, Dissolve old selected points
    :type clear_point: typing.Union[bool, typing.Any]
    :param clear_stroke: Delete Strokes, Delete old selected strokes
    :type clear_stroke: typing.Union[bool, typing.Any]
    """

    ...

def stroke_merge_by_distance(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    threshold: typing.Any = 0.001,
    use_unselected: typing.Union[bool, typing.Any] = False,
):
    """Merge points by distance

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param threshold: Threshold
    :type threshold: typing.Any
    :param use_unselected: Unselected, Use whole stroke, not only selected points
    :type use_unselected: typing.Union[bool, typing.Any]
    """

    ...

def stroke_merge_material(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    hue_threshold: typing.Any = 0.001,
    sat_threshold: typing.Any = 0.001,
    val_threshold: typing.Any = 0.001,
):
    """Replace materials in strokes merging similar

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param hue_threshold: Hue Threshold
    :type hue_threshold: typing.Any
    :param sat_threshold: Saturation Threshold
    :type sat_threshold: typing.Any
    :param val_threshold: Value Threshold
    :type val_threshold: typing.Any
    """

    ...

def stroke_normalize(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "THICKNESS",
    factor: typing.Any = 1.0,
    value: typing.Any = 10,
):
    """Normalize stroke attributes

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param mode: Mode, Attribute to be normalized

    THICKNESS
    Thickness -- Normalizes the stroke thickness by making all points use the same thickness value.

    OPACITY
    Opacity -- Normalizes the stroke opacity by making all points use the same opacity value.
        :type mode: typing.Any
        :param factor: Factor
        :type factor: typing.Any
        :param value: Value, Value
        :type value: typing.Any
    """

    ...

def stroke_outline(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    view_mode: typing.Any = "VIEW",
    material_mode: typing.Any = "ACTIVE",
    thickness: typing.Any = 1,
    keep: typing.Union[bool, typing.Any] = True,
    subdivisions: typing.Any = 3,
    length: typing.Any = 0.0,
):
    """Convert stroke to perimeter

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param view_mode: View
        :type view_mode: typing.Any
        :param material_mode: Material Mode

    ACTIVE
    Active Material.

    KEEP
    Keep Material -- Keep current stroke material.

    NEW
    New Material.
        :type material_mode: typing.Any
        :param thickness: Thickness, Thickness of the stroke perimeter
        :type thickness: typing.Any
        :param keep: Keep Shape, Try to keep global shape when the stroke thickness change
        :type keep: typing.Union[bool, typing.Any]
        :param subdivisions: Subdivisions
        :type subdivisions: typing.Any
        :param length: Sample Length
        :type length: typing.Any
    """

    ...

def stroke_reset_vertex_color(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "BOTH",
):
    """Reset vertex color for all or selected strokes

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param mode: Mode

    STROKE
    Stroke -- Reset Vertex Color to Stroke only.

    FILL
    Fill -- Reset Vertex Color to Fill only.

    BOTH
    Stroke & Fill -- Reset Vertex Color to Stroke and Fill.
        :type mode: typing.Any
    """

    ...

def stroke_sample(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    length: typing.Any = 0.1,
    sharp_threshold: typing.Any = 0.1,
):
    """Sample stroke points to predefined segment length

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param length: Length
    :type length: typing.Any
    :param sharp_threshold: Sharp Threshold
    :type sharp_threshold: typing.Any
    """

    ...

def stroke_separate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "POINT",
):
    """Separate the selected strokes or layer in a new grease pencil object

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param mode: Mode

    POINT
    Selected Points -- Separate the selected points.

    STROKE
    Selected Strokes -- Separate the selected strokes.

    LAYER
    Active Layer -- Separate the strokes of the current layer.
        :type mode: typing.Any
    """

    ...

def stroke_simplify(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    factor: typing.Any = 0.0,
):
    """Simplify selected strokes, reducing number of points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param factor: Factor
    :type factor: typing.Any
    """

    ...

def stroke_simplify_fixed(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    step: typing.Any = 1,
):
    """Simplify selected strokes, reducing number of points using fixed algorithm

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param step: Steps, Number of simplify steps
    :type step: typing.Any
    """

    ...

def stroke_smooth(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    repeat: typing.Any = 2,
    factor: typing.Any = 1.0,
    only_selected: typing.Union[bool, typing.Any] = True,
    smooth_position: typing.Union[bool, typing.Any] = True,
    smooth_thickness: typing.Union[bool, typing.Any] = True,
    smooth_strength: typing.Union[bool, typing.Any] = False,
    smooth_uv: typing.Union[bool, typing.Any] = False,
):
    """Smooth selected strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param repeat: Repeat
    :type repeat: typing.Any
    :param factor: Factor
    :type factor: typing.Any
    :param only_selected: Selected Points, Smooth only selected points in the stroke
    :type only_selected: typing.Union[bool, typing.Any]
    :param smooth_position: Position
    :type smooth_position: typing.Union[bool, typing.Any]
    :param smooth_thickness: Thickness
    :type smooth_thickness: typing.Union[bool, typing.Any]
    :param smooth_strength: Strength
    :type smooth_strength: typing.Union[bool, typing.Any]
    :param smooth_uv: UV
    :type smooth_uv: typing.Union[bool, typing.Any]
    """

    ...

def stroke_split(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Split selected points as new stroke on same frame

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def stroke_start_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Set start point for cyclic strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def stroke_subdivide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    number_cuts: typing.Any = 1,
    factor: typing.Any = 0.0,
    repeat: typing.Any = 1,
    only_selected: typing.Union[bool, typing.Any] = True,
    smooth_position: typing.Union[bool, typing.Any] = True,
    smooth_thickness: typing.Union[bool, typing.Any] = True,
    smooth_strength: typing.Union[bool, typing.Any] = False,
    smooth_uv: typing.Union[bool, typing.Any] = False,
):
    """Subdivide between continuous selected points of the stroke adding a point half way between them

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param number_cuts: Number of Cuts
    :type number_cuts: typing.Any
    :param factor: Smooth
    :type factor: typing.Any
    :param repeat: Repeat
    :type repeat: typing.Any
    :param only_selected: Selected Points, Smooth only selected points in the stroke
    :type only_selected: typing.Union[bool, typing.Any]
    :param smooth_position: Position
    :type smooth_position: typing.Union[bool, typing.Any]
    :param smooth_thickness: Thickness
    :type smooth_thickness: typing.Union[bool, typing.Any]
    :param smooth_strength: Strength
    :type smooth_strength: typing.Union[bool, typing.Any]
    :param smooth_uv: UV
    :type smooth_uv: typing.Union[bool, typing.Any]
    """

    ...

def stroke_trim(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Trim selected stroke to first loop or intersection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def time_segment_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    modifier: typing.Union[str, typing.Any] = "",
):
    """Add a segment to the time modifier

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param modifier: Modifier, Name of the modifier to edit
    :type modifier: typing.Union[str, typing.Any]
    """

    ...

def time_segment_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    modifier: typing.Union[str, typing.Any] = "",
    type: typing.Any = "UP",
):
    """Move the active time segment up or down

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param modifier: Modifier, Name of the modifier to edit
    :type modifier: typing.Union[str, typing.Any]
    :param type: Type
    :type type: typing.Any
    """

    ...

def time_segment_remove(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    modifier: typing.Union[str, typing.Any] = "",
    index: typing.Any = 0,
):
    """Remove the active segment from the time modifier

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param modifier: Modifier, Name of the modifier to edit
    :type modifier: typing.Union[str, typing.Any]
    :param index: Index, Index of the segment to remove
    :type index: typing.Any
    """

    ...

def tint_flip(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Switch tint colors

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def trace_image(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    target: typing.Any = "NEW",
    thickness: typing.Any = 10,
    resolution: typing.Any = 5,
    scale: typing.Any = 1.0,
    sample: typing.Any = 0.0,
    threshold: typing.Any = 0.5,
    turnpolicy: typing.Any = "MINORITY",
    mode: typing.Any = "SINGLE",
    use_current_frame: typing.Union[bool, typing.Any] = True,
    frame_number: typing.Any = 0,
):
    """Extract Grease Pencil strokes from image

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param target: Target Object, Target grease pencil
        :type target: typing.Any
        :param thickness: Thickness
        :type thickness: typing.Any
        :param resolution: Resolution, Resolution of the generated curves
        :type resolution: typing.Any
        :param scale: Scale, Scale of the final stroke
        :type scale: typing.Any
        :param sample: Sample, Distance to sample points, zero to disable
        :type sample: typing.Any
        :param threshold: Color Threshold, Determine the lightness threshold above which strokes are generated
        :type threshold: typing.Any
        :param turnpolicy: Turn Policy, Determines how to resolve ambiguities during decomposition of bitmaps into paths

    BLACK
    Black -- Prefers to connect black (foreground) components.

    WHITE
    White -- Prefers to connect white (background) components.

    LEFT
    Left -- Always take a left turn.

    RIGHT
    Right -- Always take a right turn.

    MINORITY
    Minority -- Prefers to connect the color (black or white) that occurs least frequently in the local neighborhood of the current position.

    MAJORITY
    Majority -- Prefers to connect the color (black or white) that occurs most frequently in the local neighborhood of the current position.

    RANDOM
    Random -- Choose pseudo-randomly.
        :type turnpolicy: typing.Any
        :param mode: Mode, Determines if trace simple image or full sequence

    SINGLE
    Single -- Trace the current frame of the image.

    SEQUENCE
    Sequence -- Trace full sequence.
        :type mode: typing.Any
        :param use_current_frame: Start At Current Frame, Trace Image starting in current image frame
        :type use_current_frame: typing.Union[bool, typing.Any]
        :param frame_number: Trace Frame, Used to trace only one frame of the image sequence, set to zero to trace all
        :type frame_number: typing.Any
    """

    ...

def transform_fill(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "ROTATE",
    location: typing.Any = (0.0, 0.0),
    rotation: typing.Any = 0.0,
    scale: typing.Any = 0.0,
    release_confirm: typing.Union[bool, typing.Any] = False,
):
    """Transform grease pencil stroke fill

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
    :param location: Location
    :type location: typing.Any
    :param rotation: Rotation
    :type rotation: typing.Any
    :param scale: Scale
    :type scale: typing.Any
    :param release_confirm: Confirm on Release
    :type release_confirm: typing.Union[bool, typing.Any]
    """

    ...

def unlock_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Unlock all Grease Pencil layers so that they can be edited

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def vertex_color_brightness_contrast(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "BOTH",
    brightness: typing.Any = 0.0,
    contrast: typing.Any = 0.0,
):
    """Adjust vertex color brightness/contrast

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
    :param brightness: Brightness
    :type brightness: typing.Any
    :param contrast: Contrast
    :type contrast: typing.Any
    """

    ...

def vertex_color_hsv(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "BOTH",
    h: typing.Any = 0.5,
    s: typing.Any = 1.0,
    v: typing.Any = 1.0,
):
    """Adjust vertex color HSV values

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
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
    mode: typing.Any = "BOTH",
):
    """Invert RGB values

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
    """

    ...

def vertex_color_levels(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "BOTH",
    offset: typing.Any = 0.0,
    gain: typing.Any = 1.0,
):
    """Adjust levels of vertex colors

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
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
    mode: typing.Any = "BOTH",
    factor: typing.Any = 1.0,
):
    """Set active color to all selected vertex

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
    :param factor: Factor, Mix Factor
    :type factor: typing.Any
    """

    ...

def vertex_group_assign(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Assign the selected vertices to the active vertex group

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def vertex_group_deselect(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Deselect all selected vertices assigned to the active vertex group

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def vertex_group_invert(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Invert weights to the active vertex group

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def vertex_group_normalize(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Normalize weights to the active vertex group

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def vertex_group_normalize_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    lock_active: typing.Union[bool, typing.Any] = True,
):
    """Normalize all weights of all vertex groups, so that for each vertex, the sum of all weights is 1.0

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param lock_active: Lock Active, Keep the values of the active group while normalizing others
    :type lock_active: typing.Union[bool, typing.Any]
    """

    ...

def vertex_group_remove_from(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Remove the selected vertices from active or all vertex group(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def vertex_group_select(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Select all the vertices assigned to the active vertex group

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def vertex_group_smooth(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    factor: typing.Any = 0.5,
    repeat: typing.Any = 1,
):
    """Smooth weights to the active vertex group

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param factor: Factor
    :type factor: typing.Any
    :param repeat: Iterations
    :type repeat: typing.Any
    """

    ...

def vertex_paint(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement] = None,
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Paint stroke points with a color

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param stroke: Stroke
    :type stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement]
    :param wait_for_input: Wait for Input
    :type wait_for_input: typing.Union[bool, typing.Any]
    """

    ...

def vertexmode_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    back: typing.Union[bool, typing.Any] = False,
):
    """Enter/Exit vertex paint mode for Grease Pencil strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param back: Return to Previous Mode, Return to previous mode
    :type back: typing.Union[bool, typing.Any]
    """

    ...

def weight_paint(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement] = None,
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Draw weight on stroke points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param stroke: Stroke
    :type stroke: bpy.types.bpy_prop_collection[bpy.types.OperatorStrokeElement]
    :param wait_for_input: Wait for Input
    :type wait_for_input: typing.Union[bool, typing.Any]
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

def weight_toggle_direction(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Toggle Add/Subtract for the weight paint draw tool

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def weightmode_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    back: typing.Union[bool, typing.Any] = False,
):
    """Enter/Exit weight paint mode for Grease Pencil strokes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param back: Return to Previous Mode, Return to previous mode
    :type back: typing.Union[bool, typing.Any]
    """

    ...
