import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def action_pushdown(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    track_index: typing.Any = -1,
):
    """Push action down onto the top of the NLA stack as a new strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param track_index: Track Index, Index of NLA action track to perform pushdown operation on
    :type track_index: typing.Any
    """

    ...

def action_sync_length(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    active: typing.Union[bool, typing.Any] = True,
):
    """Synchronize the length of the referenced Action with the length used in the strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param active: Active Strip Only, Only sync the active length for the active strip
    :type active: typing.Union[bool, typing.Any]
    """

    ...

def action_unlink(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    force_delete: typing.Union[bool, typing.Any] = False,
):
    """Unlink this action from the active action slot (and/or exit Tweak Mode)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param force_delete: Force Delete, Clear Fake User and remove copy stashed in this data-block's NLA stack
    :type force_delete: typing.Union[bool, typing.Any]
    """

    ...

def actionclip_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    action: typing.Union[str, int, typing.Any] = "",
):
    """Add an Action-Clip strip (i.e. an NLA Strip referencing an Action) to the active track

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param action: Action
    :type action: typing.Union[str, int, typing.Any]
    """

    ...

def apply_scale(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Apply scaling of selected strips to their referenced Actions

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def bake(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    frame_start: typing.Any = 1,
    frame_end: typing.Any = 250,
    step: typing.Any = 1,
    only_selected: typing.Union[bool, typing.Any] = True,
    visual_keying: typing.Union[bool, typing.Any] = False,
    clear_constraints: typing.Union[bool, typing.Any] = False,
    clear_parents: typing.Union[bool, typing.Any] = False,
    use_current_action: typing.Union[bool, typing.Any] = False,
    clean_curves: typing.Union[bool, typing.Any] = False,
    bake_types: typing.Any = {'"POSE"'},
    channel_types: typing.Any = {
        '"PROPS"',
        '"LOCATION"',
        '"BBONE"',
        '"SCALE"',
        '"ROTATION"',
    },
):
    """Bake all selected objects location/scale/rotation animation to an action

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param frame_start: Start Frame, Start frame for baking
        :type frame_start: typing.Any
        :param frame_end: End Frame, End frame for baking
        :type frame_end: typing.Any
        :param step: Frame Step, Number of frames to skip forward while baking each frame
        :type step: typing.Any
        :param only_selected: Only Selected Bones, Only key selected bones (Pose baking only)
        :type only_selected: typing.Union[bool, typing.Any]
        :param visual_keying: Visual Keying, Keyframe from the final transformations (with constraints applied)
        :type visual_keying: typing.Union[bool, typing.Any]
        :param clear_constraints: Clear Constraints, Remove all constraints from keyed object/bones, and do 'visual' keying
        :type clear_constraints: typing.Union[bool, typing.Any]
        :param clear_parents: Clear Parents, Bake animation onto the object then clear parents (objects only)
        :type clear_parents: typing.Union[bool, typing.Any]
        :param use_current_action: Overwrite Current Action, Bake animation into current action, instead of creating a new one (useful for baking only part of bones in an armature)
        :type use_current_action: typing.Union[bool, typing.Any]
        :param clean_curves: Clean Curves, After baking curves, remove redundant keys
        :type clean_curves: typing.Union[bool, typing.Any]
        :param bake_types: Bake Data, Which data's transformations to bake

    POSE
    Pose -- Bake bones transformations.

    OBJECT
    Object -- Bake object transformations.
        :type bake_types: typing.Any
        :param channel_types: Channels, Which channels to bake

    LOCATION
    Location -- Bake location channels.

    ROTATION
    Rotation -- Bake rotation channels.

    SCALE
    Scale -- Bake scale channels.

    BBONE
    B-Bone -- Bake B-Bone channels.

    PROPS
    Custom Properties -- Bake custom properties.
        :type channel_types: typing.Any
    """

    ...

def channels_click(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    extend: typing.Union[bool, typing.Any] = False,
):
    """Handle clicks to select NLA tracks

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param extend: Extend Select
    :type extend: typing.Union[bool, typing.Any]
    """

    ...

def clear_scale(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Reset scaling of selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def click_select(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    wait_to_deselect_others: typing.Union[bool, typing.Any] = False,
    mouse_x: typing.Any = 0,
    mouse_y: typing.Any = 0,
    extend: typing.Union[bool, typing.Any] = False,
    deselect_all: typing.Union[bool, typing.Any] = False,
):
    """Handle clicks to select NLA Strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param wait_to_deselect_others: Wait to Deselect Others
    :type wait_to_deselect_others: typing.Union[bool, typing.Any]
    :param mouse_x: Mouse X
    :type mouse_x: typing.Any
    :param mouse_y: Mouse Y
    :type mouse_y: typing.Any
    :param extend: Extend Select
    :type extend: typing.Union[bool, typing.Any]
    :param deselect_all: Deselect On Nothing, Deselect all when nothing under the cursor
    :type deselect_all: typing.Union[bool, typing.Any]
    """

    ...

def delete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Delete selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def duplicate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    linked: typing.Union[bool, typing.Any] = False,
):
    """Duplicate selected NLA-Strips, adding the new strips to new track(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param linked: Linked, When duplicating strips, assign new copies of the actions they use
    :type linked: typing.Union[bool, typing.Any]
    """

    ...

def duplicate_linked_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    NLA_OT_duplicate: typing.Any = None,
    TRANSFORM_OT_translate: typing.Any = None,
):
    """Duplicate Linked selected NLA-Strips, adding the new strips to new track(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param NLA_OT_duplicate: Duplicate Strips, Duplicate selected NLA-Strips, adding the new strips to new track(s)
    :type NLA_OT_duplicate: typing.Any
    :param TRANSFORM_OT_translate: Move, Move selected items
    :type TRANSFORM_OT_translate: typing.Any
    """

    ...

def duplicate_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    NLA_OT_duplicate: typing.Any = None,
    TRANSFORM_OT_translate: typing.Any = None,
):
    """Duplicate selected NLA-Strips, adding the new strips to new track(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param NLA_OT_duplicate: Duplicate Strips, Duplicate selected NLA-Strips, adding the new strips to new track(s)
    :type NLA_OT_duplicate: typing.Any
    :param TRANSFORM_OT_translate: Move, Move selected items
    :type TRANSFORM_OT_translate: typing.Any
    """

    ...

def fmodifier_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Union[str, int] = "NULL",
    only_active: typing.Union[bool, typing.Any] = True,
):
    """Add F-Modifier to the active/selected NLA-Strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type
    :type type: typing.Union[str, int]
    :param only_active: Only Active, Only add a F-Modifier of the specified type to the active strip
    :type only_active: typing.Union[bool, typing.Any]
    """

    ...

def fmodifier_copy(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Copy the F-Modifier(s) of the active NLA-Strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def fmodifier_paste(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    only_active: typing.Union[bool, typing.Any] = True,
    replace: typing.Union[bool, typing.Any] = False,
):
    """Add copied F-Modifiers to the selected NLA-Strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param only_active: Only Active, Only paste F-Modifiers on active strip
    :type only_active: typing.Union[bool, typing.Any]
    :param replace: Replace Existing, Replace existing F-Modifiers, instead of just appending to the end of the existing list
    :type replace: typing.Union[bool, typing.Any]
    """

    ...

def make_single_user(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    confirm: typing.Union[bool, typing.Any] = True,
):
    """Make linked action local to each strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param confirm: Confirm, Prompt for confirmation
    :type confirm: typing.Union[bool, typing.Any]
    """

    ...

def meta_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add new meta-strips incorporating the selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def meta_remove(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Separate out the strips held by the selected meta-strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def move_down(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Move selected strips down a track if there's room

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def move_up(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Move selected strips up a track if there's room

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def mute_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Mute or un-mute selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def previewrange_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Set Preview Range based on extends of selected strips

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
    """Select or deselect all NLA-Strips

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

def select_box(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    axis_range: typing.Union[bool, typing.Any] = False,
    tweak: typing.Union[bool, typing.Any] = False,
    xmin: typing.Any = 0,
    xmax: typing.Any = 0,
    ymin: typing.Any = 0,
    ymax: typing.Any = 0,
    wait_for_input: typing.Union[bool, typing.Any] = True,
    mode: typing.Any = "SET",
):
    """Use box selection to grab NLA-Strips

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param axis_range: Axis Range
        :type axis_range: typing.Union[bool, typing.Any]
        :param tweak: Tweak, Operator has been activated using a click-drag event
        :type tweak: typing.Union[bool, typing.Any]
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
        :type mode: typing.Any
    """

    ...

def select_leftright(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "CHECK",
    extend: typing.Union[bool, typing.Any] = False,
):
    """Select strips to the left or the right of the current frame

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
    :param extend: Extend Select
    :type extend: typing.Union[bool, typing.Any]
    """

    ...

def selected_objects_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Make selected objects appear in NLA Editor by adding Animation Data

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def snap(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "CFRA",
):
    """Move start of strips to specified time

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type
    :type type: typing.Any
    """

    ...

def soundclip_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add a strip for controlling when speaker plays its sound clip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def split(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Split selected strips at their midpoints

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def swap(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Swap order of selected strips within tracks

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def tracks_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    above_selected: typing.Union[bool, typing.Any] = False,
):
    """Add NLA-Tracks above/after the selected tracks

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param above_selected: Above Selected, Add a new NLA Track above every existing selected one
    :type above_selected: typing.Union[bool, typing.Any]
    """

    ...

def tracks_delete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Delete selected NLA-Tracks and the strips they contain

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def transition_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add a transition strip between two adjacent selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def tweakmode_enter(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    isolate_action: typing.Union[bool, typing.Any] = False,
    use_upper_stack_evaluation: typing.Union[bool, typing.Any] = False,
):
    """Enter tweaking mode for the action referenced by the active strip to edit its keyframes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param isolate_action: Isolate Action, Enable 'solo' on the NLA Track containing the active strip, to edit it without seeing the effects of the NLA stack
    :type isolate_action: typing.Union[bool, typing.Any]
    :param use_upper_stack_evaluation: Evaluate Upper Stack, In tweak mode, display the effects of the tracks above the tweak strip
    :type use_upper_stack_evaluation: typing.Union[bool, typing.Any]
    """

    ...

def tweakmode_exit(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    isolate_action: typing.Union[bool, typing.Any] = False,
):
    """Exit tweaking mode for the action referenced by the active strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param isolate_action: Isolate Action, Disable 'solo' on any of the NLA Tracks after exiting tweak mode to get things back to normal
    :type isolate_action: typing.Union[bool, typing.Any]
    """

    ...

def view_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Reset viewable area to show full strips range

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def view_frame(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Move the view to the current frame

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def view_selected(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Reset viewable area to show selected strips range

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...
