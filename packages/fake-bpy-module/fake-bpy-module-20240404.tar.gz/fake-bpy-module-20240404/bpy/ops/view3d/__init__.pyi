import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def bone_select_menu(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    name: typing.Union[str, int, typing.Any] = "",
    extend: typing.Union[bool, typing.Any] = False,
    deselect: typing.Union[bool, typing.Any] = False,
    toggle: typing.Union[bool, typing.Any] = False,
):
    """Menu bone selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param name: Bone Name
    :type name: typing.Union[str, int, typing.Any]
    :param extend: Extend
    :type extend: typing.Union[bool, typing.Any]
    :param deselect: Deselect
    :type deselect: typing.Union[bool, typing.Any]
    :param toggle: Toggle
    :type toggle: typing.Union[bool, typing.Any]
    """

    ...

def camera_background_image_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    filepath: typing.Union[str, typing.Any] = "",
    relative_path: typing.Union[bool, typing.Any] = True,
    name: typing.Union[str, typing.Any] = "",
    session_uid: typing.Any = 0,
):
    """Add a new background image to the active camera

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param filepath: Filepath, Path to image file
    :type filepath: typing.Union[str, typing.Any]
    :param relative_path: Relative Path, Select the file relative to the blend file
    :type relative_path: typing.Union[bool, typing.Any]
    :param name: Name, Name of the data-block to use by the operator
    :type name: typing.Union[str, typing.Any]
    :param session_uid: Session UID, Session UID of the data-block to use by the operator
    :type session_uid: typing.Any
    """

    ...

def camera_background_image_remove(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    index: typing.Any = 0,
):
    """Remove a background image from the camera

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param index: Index, Background image index to remove
    :type index: typing.Any
    """

    ...

def camera_to_view(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Set camera view to active view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def camera_to_view_selected(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Move the camera so selected objects are framed

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def clear_render_border(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Clear the boundaries of the border render and disable border render

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def clip_border(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    xmin: typing.Any = 0,
    xmax: typing.Any = 0,
    ymin: typing.Any = 0,
    ymax: typing.Any = 0,
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Set the view clipping region

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
    """

    ...

def copybuffer(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Copy the selected objects to the internal clipboard

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def cursor3d(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    use_depth: typing.Union[bool, typing.Any] = True,
    orientation: typing.Any = "VIEW",
):
    """Set the location of the 3D cursor

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param use_depth: Surface Project, Project onto the surface
        :type use_depth: typing.Union[bool, typing.Any]
        :param orientation: Orientation, Preset viewpoint to use

    NONE
    None -- Leave orientation unchanged.

    VIEW
    View -- Orient to the viewport.

    XFORM
    Transform -- Orient to the current transform setting.

    GEOM
    Geometry -- Match the surface normal.
        :type orientation: typing.Any
    """

    ...

def dolly(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mx: typing.Any = 0,
    my: typing.Any = 0,
    delta: typing.Any = 0,
    use_cursor_init: typing.Union[bool, typing.Any] = True,
):
    """Dolly in/out in the view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mx: Region Position X
    :type mx: typing.Any
    :param my: Region Position Y
    :type my: typing.Any
    :param delta: Delta
    :type delta: typing.Any
    :param use_cursor_init: Use Mouse Position, Allow the initial mouse position to be used
    :type use_cursor_init: typing.Union[bool, typing.Any]
    """

    ...

def drop_world(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    name: typing.Union[str, typing.Any] = "",
    session_uid: typing.Any = 0,
):
    """Drop a world into the scene

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param name: Name, Name of the data-block to use by the operator
    :type name: typing.Union[str, typing.Any]
    :param session_uid: Session UID, Session UID of the data-block to use by the operator
    :type session_uid: typing.Any
    """

    ...

def edit_mesh_extrude_individual_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Extrude each individual face separately along local normals

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def edit_mesh_extrude_manifold_normal(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Extrude manifold region along normals

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def edit_mesh_extrude_move_normal(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    dissolve_and_intersect: typing.Union[bool, typing.Any] = False,
):
    """Extrude region together along the average normal

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param dissolve_and_intersect: dissolve_and_intersect, Dissolves adjacent faces and intersects new geometry
    :type dissolve_and_intersect: typing.Union[bool, typing.Any]
    """

    ...

def edit_mesh_extrude_move_shrink_fatten(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Extrude region together along local normals

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def fly(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Interactively fly around the scene

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def interactive_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    primitive_type: typing.Any = "CUBE",
    plane_origin_base: typing.Any = "EDGE",
    plane_origin_depth: typing.Any = "EDGE",
    plane_aspect_base: typing.Any = "FREE",
    plane_aspect_depth: typing.Any = "FREE",
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Interactively add an object

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param primitive_type: Primitive
        :type primitive_type: typing.Any
        :param plane_origin_base: Origin, The initial position for placement

    EDGE
    Edge -- Start placing the edge position.

    CENTER
    Center -- Start placing the center position.
        :type plane_origin_base: typing.Any
        :param plane_origin_depth: Origin, The initial position for placement

    EDGE
    Edge -- Start placing the edge position.

    CENTER
    Center -- Start placing the center position.
        :type plane_origin_depth: typing.Any
        :param plane_aspect_base: Aspect, The initial aspect setting

    FREE
    Free -- Use an unconstrained aspect.

    FIXED
    Fixed -- Use a fixed 1:1 aspect.
        :type plane_aspect_base: typing.Any
        :param plane_aspect_depth: Aspect, The initial aspect setting

    FREE
    Free -- Use an unconstrained aspect.

    FIXED
    Fixed -- Use a fixed 1:1 aspect.
        :type plane_aspect_depth: typing.Any
        :param wait_for_input: Wait for Input
        :type wait_for_input: typing.Union[bool, typing.Any]
    """

    ...

def localview(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    frame_selected: typing.Union[bool, typing.Any] = True,
):
    """Toggle display of selected object(s) separately and centered in view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param frame_selected: Frame Selected, Move the view to frame the selected objects
    :type frame_selected: typing.Union[bool, typing.Any]
    """

    ...

def localview_remove_from(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Move selected objects out of local view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    use_cursor_init: typing.Union[bool, typing.Any] = True,
):
    """Move the view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param use_cursor_init: Use Mouse Position, Allow the initial mouse position to be used
    :type use_cursor_init: typing.Union[bool, typing.Any]
    """

    ...

def navigate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Interactively navigate around the scene (uses the mode (walk/fly) preference)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def ndof_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Pan and rotate the view with the 3D mouse

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def ndof_orbit(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Orbit the view using the 3D mouse

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def ndof_orbit_zoom(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Orbit and zoom the view using the 3D mouse

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def ndof_pan(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Pan the view with the 3D mouse

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def object_as_camera(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Set the active object as the active camera for this view or scene

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def object_mode_pie_or_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Undocumented, consider contributing.

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def pastebuffer(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    autoselect: typing.Union[bool, typing.Any] = True,
    active_collection: typing.Union[bool, typing.Any] = True,
):
    """Paste objects from the internal clipboard

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param autoselect: Select, Select pasted objects
    :type autoselect: typing.Union[bool, typing.Any]
    :param active_collection: Active Collection, Put pasted objects in the active collection
    :type active_collection: typing.Union[bool, typing.Any]
    """

    ...

def render_border(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    xmin: typing.Any = 0,
    xmax: typing.Any = 0,
    ymin: typing.Any = 0,
    ymax: typing.Any = 0,
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Set the boundaries of the border render and enable border render

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
    """

    ...

def rotate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    use_cursor_init: typing.Union[bool, typing.Any] = True,
):
    """Rotate the view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param use_cursor_init: Use Mouse Position, Allow the initial mouse position to be used
    :type use_cursor_init: typing.Union[bool, typing.Any]
    """

    ...

def ruler_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add ruler

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def ruler_remove(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Undocumented, consider contributing.

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
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
    center: typing.Union[bool, typing.Any] = False,
    enumerate: typing.Union[bool, typing.Any] = False,
    object: typing.Union[bool, typing.Any] = False,
    location: typing.Any = (0, 0),
):
    """Select and activate item(s)

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
    :param center: Center, Use the object center when selecting, in edit mode used to extend object selection
    :type center: typing.Union[bool, typing.Any]
    :param enumerate: Enumerate, List objects under the mouse (object mode only)
    :type enumerate: typing.Union[bool, typing.Any]
    :param object: Object, Use object selection (edit mode only)
    :type object: typing.Union[bool, typing.Any]
    :param location: Location, Mouse location
    :type location: typing.Any
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
    """Select items using box selection

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
    """Select items using circle selection

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

def select_lasso(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    path: bpy.types.bpy_prop_collection[bpy.types.OperatorMousePath] = None,
    mode: typing.Any = "SET",
):
    """Select items using lasso selection

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param path: Path
        :type path: bpy.types.bpy_prop_collection[bpy.types.OperatorMousePath]
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

def select_menu(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    name: typing.Union[str, int, typing.Any] = "",
    extend: typing.Union[bool, typing.Any] = False,
    deselect: typing.Union[bool, typing.Any] = False,
    toggle: typing.Union[bool, typing.Any] = False,
):
    """Menu object selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param name: Object Name
    :type name: typing.Union[str, int, typing.Any]
    :param extend: Extend
    :type extend: typing.Union[bool, typing.Any]
    :param deselect: Deselect
    :type deselect: typing.Union[bool, typing.Any]
    :param toggle: Toggle
    :type toggle: typing.Union[bool, typing.Any]
    """

    ...

def smoothview(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Undocumented, consider contributing.

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def snap_cursor_to_active(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Snap 3D cursor to the active item

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def snap_cursor_to_center(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Snap 3D cursor to the world origin

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def snap_cursor_to_grid(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Snap 3D cursor to the nearest grid division

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
    """Snap 3D cursor to the middle of the selected item(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def snap_selected_to_active(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Snap selected item(s) to the active item

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def snap_selected_to_cursor(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    use_offset: typing.Union[bool, typing.Any] = True,
):
    """Snap selected item(s) to the 3D cursor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param use_offset: Offset, If the selection should be snapped as a whole or by each object center
    :type use_offset: typing.Union[bool, typing.Any]
    """

    ...

def snap_selected_to_grid(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Snap selected item(s) to their nearest grid division

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def toggle_matcap_flip(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Flip MatCap

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def toggle_shading(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "WIREFRAME",
):
    """Toggle shading type in 3D viewport

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Type, Shading type to toggle

    WIREFRAME
    Wireframe -- Toggle wireframe shading.

    SOLID
    Solid -- Toggle solid shading.

    MATERIAL
    Material Preview -- Toggle material preview shading.

    RENDERED
    Rendered -- Toggle rendered shading.
        :type type: typing.Any
    """

    ...

def toggle_xray(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Transparent scene display. Allow selecting through items

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def transform_gizmo_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    extend: typing.Union[bool, typing.Any] = False,
    type: typing.Any = {},
):
    """Set the current transform gizmo

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param extend: Extend
    :type extend: typing.Union[bool, typing.Any]
    :param type: Type
    :type type: typing.Any
    """

    ...

def view_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    use_all_regions: typing.Union[bool, typing.Any] = False,
    center: typing.Union[bool, typing.Any] = False,
):
    """View all objects in scene

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param use_all_regions: All Regions, View selected for all regions
    :type use_all_regions: typing.Union[bool, typing.Any]
    :param center: Center
    :type center: typing.Union[bool, typing.Any]
    """

    ...

def view_axis(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "LEFT",
    align_active: typing.Union[bool, typing.Any] = False,
    relative: typing.Union[bool, typing.Any] = False,
):
    """Use a preset viewpoint

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: View, Preset viewpoint to use

    LEFT
    Left -- View from the left.

    RIGHT
    Right -- View from the right.

    BOTTOM
    Bottom -- View from the bottom.

    TOP
    Top -- View from the top.

    FRONT
    Front -- View from the front.

    BACK
    Back -- View from the back.
        :type type: typing.Any
        :param align_active: Align Active, Align to the active object's axis
        :type align_active: typing.Union[bool, typing.Any]
        :param relative: Relative, Rotate relative to the current orientation
        :type relative: typing.Union[bool, typing.Any]
    """

    ...

def view_camera(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Toggle the camera view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def view_center_camera(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Center the camera view, resizing the view to fit its bounds

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def view_center_cursor(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Center the view so that the cursor is in the middle of the view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def view_center_lock(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Center the view lock offset

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def view_center_pick(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Center the view to the Z-depth position under the mouse cursor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def view_lock_clear(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Clear all view locking

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def view_lock_to_active(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Lock the view to the active object/bone

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def view_orbit(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    angle: typing.Any = 0.0,
    type: typing.Any = "ORBITLEFT",
):
    """Orbit the view

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param angle: Roll
        :type angle: typing.Any
        :param type: Orbit, Direction of View Orbit

    ORBITLEFT
    Orbit Left -- Orbit the view around to the left.

    ORBITRIGHT
    Orbit Right -- Orbit the view around to the right.

    ORBITUP
    Orbit Up -- Orbit the view up.

    ORBITDOWN
    Orbit Down -- Orbit the view down.
        :type type: typing.Any
    """

    ...

def view_pan(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "PANLEFT",
):
    """Pan the view in a given direction

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Pan, Direction of View Pan

    PANLEFT
    Pan Left -- Pan the view to the left.

    PANRIGHT
    Pan Right -- Pan the view to the right.

    PANUP
    Pan Up -- Pan the view up.

    PANDOWN
    Pan Down -- Pan the view down.
        :type type: typing.Any
    """

    ...

def view_persportho(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Switch the current view from perspective/orthographic projection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def view_roll(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    angle: typing.Any = 0.0,
    type: typing.Any = "ANGLE",
):
    """Roll the view

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param angle: Roll
        :type angle: typing.Any
        :param type: Roll Angle Source, How roll angle is calculated

    ANGLE
    Roll Angle -- Roll the view using an angle value.

    LEFT
    Roll Left -- Roll the view around to the left.

    RIGHT
    Roll Right -- Roll the view around to the right.
        :type type: typing.Any
    """

    ...

def view_selected(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    use_all_regions: typing.Union[bool, typing.Any] = False,
):
    """Move the view to the selection center

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param use_all_regions: All Regions, View selected for all regions
    :type use_all_regions: typing.Union[bool, typing.Any]
    """

    ...

def walk(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Interactively walk around the scene

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def zoom(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mx: typing.Any = 0,
    my: typing.Any = 0,
    delta: typing.Any = 0,
    use_cursor_init: typing.Union[bool, typing.Any] = True,
):
    """Zoom in/out in the view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mx: Region Position X
    :type mx: typing.Any
    :param my: Region Position Y
    :type my: typing.Any
    :param delta: Delta
    :type delta: typing.Any
    :param use_cursor_init: Use Mouse Position, Allow the initial mouse position to be used
    :type use_cursor_init: typing.Union[bool, typing.Any]
    """

    ...

def zoom_border(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    xmin: typing.Any = 0,
    xmax: typing.Any = 0,
    ymin: typing.Any = 0,
    ymax: typing.Any = 0,
    wait_for_input: typing.Union[bool, typing.Any] = True,
    zoom_out: typing.Union[bool, typing.Any] = False,
):
    """Zoom in the view to the nearest object contained in the border

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
    :param zoom_out: Zoom Out
    :type zoom_out: typing.Union[bool, typing.Any]
    """

    ...

def zoom_camera_1_to_1(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Match the camera to 1:1 to the render output

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...
