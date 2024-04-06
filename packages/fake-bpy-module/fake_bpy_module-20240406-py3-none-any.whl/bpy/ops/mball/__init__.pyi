import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def delete_metaelems(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    confirm: typing.Union[bool, typing.Any] = True,
):
    """Delete selected metaball element(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param confirm: Confirm, Prompt for confirmation
    :type confirm: typing.Union[bool, typing.Any]
    """

    ...

def duplicate_metaelems(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Duplicate selected metaball element(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def duplicate_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    MBALL_OT_duplicate_metaelems: typing.Any = None,
    TRANSFORM_OT_translate: typing.Any = None,
):
    """Make copies of the selected metaball elements and move them

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param MBALL_OT_duplicate_metaelems: Duplicate Metaball Elements, Duplicate selected metaball element(s)
    :type MBALL_OT_duplicate_metaelems: typing.Any
    :param TRANSFORM_OT_translate: Move, Move selected items
    :type TRANSFORM_OT_translate: typing.Any
    """

    ...

def hide_metaelems(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    unselected: typing.Union[bool, typing.Any] = False,
):
    """Hide (un)selected metaball element(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param unselected: Unselected, Hide unselected rather than selected
    :type unselected: typing.Union[bool, typing.Any]
    """

    ...

def reveal_metaelems(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    select: typing.Union[bool, typing.Any] = True,
):
    """Reveal all hidden metaball elements

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param select: Select
    :type select: typing.Union[bool, typing.Any]
    """

    ...

def select_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    action: typing.Any = "TOGGLE",
):
    """Change selection of all metaball elements

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

def select_random_metaelems(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    ratio: typing.Any = 0.5,
    seed: typing.Any = 0,
    action: typing.Any = "SELECT",
):
    """Randomly select metaball elements

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
    """

    ...

def select_similar(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "TYPE",
    threshold: typing.Any = 0.1,
):
    """Select similar metaballs by property types

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type
    :type type: typing.Any
    :param threshold: Threshold
    :type threshold: typing.Any
    """

    ...
