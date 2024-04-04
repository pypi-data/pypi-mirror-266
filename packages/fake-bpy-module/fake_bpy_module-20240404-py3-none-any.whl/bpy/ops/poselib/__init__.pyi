import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def apply_pose_asset(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    blend_factor: typing.Any = 1.0,
    flipped: typing.Union[bool, typing.Any] = False,
):
    """Apply the given Pose Action to the rig

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param blend_factor: Blend Factor, Amount that the pose is applied on top of the existing poses. A negative value will subtract the pose instead of adding it
    :type blend_factor: typing.Any
    :param flipped: Apply Flipped, When enabled, applies the pose flipped over the X-axis
    :type flipped: typing.Union[bool, typing.Any]
    """

    ...

def blend_pose_asset(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    blend_factor: typing.Any = 0.0,
    flipped: typing.Union[bool, typing.Any] = False,
    release_confirm: typing.Union[bool, typing.Any] = False,
):
    """Blend the given Pose Action to the rig

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param blend_factor: Blend Factor, Amount that the pose is applied on top of the existing poses. A negative value will subtract the pose instead of adding it
    :type blend_factor: typing.Any
    :param flipped: Apply Flipped, When enabled, applies the pose flipped over the X-axis
    :type flipped: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    """

    ...

def convert_old_object_poselib(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Create a pose asset for each pose marker in this legacy pose library data-block

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def convert_old_poselib(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Create a pose asset for each pose marker in the current action

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def copy_as_asset(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Create a new pose asset on the clipboard, to be pasted into an Asset Browser

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def create_pose_asset(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    pose_name: typing.Union[str, typing.Any] = "",
    activate_new_action: typing.Union[bool, typing.Any] = True,
):
    """Create a new Action that contains the pose of the selected bones, and mark it as Asset. The asset will be stored in the current blend file

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param pose_name: Pose Name
    :type pose_name: typing.Union[str, typing.Any]
    :param activate_new_action: Activate New Action
    :type activate_new_action: typing.Union[bool, typing.Any]
    """

    ...

def paste_asset(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Paste the Asset that was previously copied using Copy As Asset

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def pose_asset_select_bones(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    select: typing.Union[bool, typing.Any] = True,
    flipped: typing.Union[bool, typing.Any] = False,
):
    """Select those bones that are used in this pose

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param select: Select
    :type select: typing.Union[bool, typing.Any]
    :param flipped: Flipped
    :type flipped: typing.Union[bool, typing.Any]
    """

    ...

def restore_previous_action(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Switch back to the previous Action, after creating a pose asset

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...
