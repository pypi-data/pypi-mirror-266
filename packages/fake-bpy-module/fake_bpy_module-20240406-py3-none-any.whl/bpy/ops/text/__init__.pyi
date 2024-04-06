import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def autocomplete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Show a list of used text in the open document

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def comment_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "TOGGLE",
):
    """Undocumented, consider contributing.

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type, Add or remove comments
    :type type: typing.Any
    """

    ...

def convert_whitespace(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "SPACES",
):
    """Convert whitespaces by type

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type, Type of whitespace to convert to
    :type type: typing.Any
    """

    ...

def copy(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Copy selected text to clipboard

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def cursor_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    x: typing.Any = 0,
    y: typing.Any = 0,
):
    """Set cursor position

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param x: X
    :type x: typing.Any
    :param y: Y
    :type y: typing.Any
    """

    ...

def cut(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Cut selected text to clipboard

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def delete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "NEXT_CHARACTER",
):
    """Delete text by cursor position

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type, Which part of the text to delete
    :type type: typing.Any
    """

    ...

def duplicate_line(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Duplicate the current line

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def find(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Find specified text

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def find_set_selected(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Find specified text and set as selected

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def indent(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Indent selected text

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def indent_or_autocomplete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Indent selected text or autocomplete

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def insert(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    text: typing.Union[str, typing.Any] = "",
):
    """Insert text at cursor position

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param text: Text, Text to insert at the cursor position
    :type text: typing.Union[str, typing.Any]
    """

    ...

def jump(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    line: typing.Any = 1,
):
    """Jump cursor to line

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param line: Line, Line number to jump to
    :type line: typing.Any
    """

    ...

def jump_to_file_at_point(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    filepath: typing.Union[str, typing.Any] = "",
    line: typing.Any = 0,
    column: typing.Any = 0,
):
    """Jump to a file for the text editor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param filepath: Filepath
    :type filepath: typing.Union[str, typing.Any]
    :param line: Line, Line to jump to
    :type line: typing.Any
    :param column: Column, Column to jump to
    :type column: typing.Any
    """

    ...

def line_break(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Insert line break at cursor position

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def line_number(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """The current line number

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def make_internal(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Make active text file internal

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "LINE_BEGIN",
):
    """Move cursor to position type

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type, Where to move cursor to
    :type type: typing.Any
    """

    ...

def move_lines(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    direction: typing.Any = "DOWN",
):
    """Move the currently selected line(s) up/down

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param direction: Direction
    :type direction: typing.Any
    """

    ...

def move_select(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "LINE_BEGIN",
):
    """Move the cursor while selecting

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type, Where to move cursor to, to make a selection
    :type type: typing.Any
    """

    ...

def new(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Create a new text data-block

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def open(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    filepath: typing.Union[str, typing.Any] = "",
    hide_props_region: typing.Union[bool, typing.Any] = True,
    check_existing: typing.Union[bool, typing.Any] = False,
    filter_blender: typing.Union[bool, typing.Any] = False,
    filter_backup: typing.Union[bool, typing.Any] = False,
    filter_image: typing.Union[bool, typing.Any] = False,
    filter_movie: typing.Union[bool, typing.Any] = False,
    filter_python: typing.Union[bool, typing.Any] = True,
    filter_font: typing.Union[bool, typing.Any] = False,
    filter_sound: typing.Union[bool, typing.Any] = False,
    filter_text: typing.Union[bool, typing.Any] = True,
    filter_archive: typing.Union[bool, typing.Any] = False,
    filter_btx: typing.Union[bool, typing.Any] = False,
    filter_collada: typing.Union[bool, typing.Any] = False,
    filter_alembic: typing.Union[bool, typing.Any] = False,
    filter_usd: typing.Union[bool, typing.Any] = False,
    filter_obj: typing.Union[bool, typing.Any] = False,
    filter_volume: typing.Union[bool, typing.Any] = False,
    filter_folder: typing.Union[bool, typing.Any] = True,
    filter_blenlib: typing.Union[bool, typing.Any] = False,
    filemode: typing.Any = 9,
    display_type: typing.Any = "DEFAULT",
    sort_method: typing.Any = "",
    internal: typing.Union[bool, typing.Any] = False,
):
    """Open a new text data-block

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param filepath: File Path, Path to file
        :type filepath: typing.Union[str, typing.Any]
        :param hide_props_region: Hide Operator Properties, Collapse the region displaying the operator settings
        :type hide_props_region: typing.Union[bool, typing.Any]
        :param check_existing: Check Existing, Check and warn on overwriting existing files
        :type check_existing: typing.Union[bool, typing.Any]
        :param filter_blender: Filter .blend files
        :type filter_blender: typing.Union[bool, typing.Any]
        :param filter_backup: Filter .blend files
        :type filter_backup: typing.Union[bool, typing.Any]
        :param filter_image: Filter image files
        :type filter_image: typing.Union[bool, typing.Any]
        :param filter_movie: Filter movie files
        :type filter_movie: typing.Union[bool, typing.Any]
        :param filter_python: Filter Python files
        :type filter_python: typing.Union[bool, typing.Any]
        :param filter_font: Filter font files
        :type filter_font: typing.Union[bool, typing.Any]
        :param filter_sound: Filter sound files
        :type filter_sound: typing.Union[bool, typing.Any]
        :param filter_text: Filter text files
        :type filter_text: typing.Union[bool, typing.Any]
        :param filter_archive: Filter archive files
        :type filter_archive: typing.Union[bool, typing.Any]
        :param filter_btx: Filter btx files
        :type filter_btx: typing.Union[bool, typing.Any]
        :param filter_collada: Filter COLLADA files
        :type filter_collada: typing.Union[bool, typing.Any]
        :param filter_alembic: Filter Alembic files
        :type filter_alembic: typing.Union[bool, typing.Any]
        :param filter_usd: Filter USD files
        :type filter_usd: typing.Union[bool, typing.Any]
        :param filter_obj: Filter OBJ files
        :type filter_obj: typing.Union[bool, typing.Any]
        :param filter_volume: Filter OpenVDB volume files
        :type filter_volume: typing.Union[bool, typing.Any]
        :param filter_folder: Filter folders
        :type filter_folder: typing.Union[bool, typing.Any]
        :param filter_blenlib: Filter Blender IDs
        :type filter_blenlib: typing.Union[bool, typing.Any]
        :param filemode: File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file
        :type filemode: typing.Any
        :param display_type: Display Type

    DEFAULT
    Default -- Automatically determine display type for files.

    LIST_VERTICAL
    Short List -- Display files as short list.

    LIST_HORIZONTAL
    Long List -- Display files as a detailed list.

    THUMBNAIL
    Thumbnails -- Display files as thumbnails.
        :type display_type: typing.Any
        :param sort_method: File sorting mode

    DEFAULT
    Default -- Automatically determine sort method for files.

    FILE_SORT_ALPHA
    Name -- Sort the file list alphabetically.

    FILE_SORT_EXTENSION
    Extension -- Sort the file list by extension/type.

    FILE_SORT_TIME
    Modified Date -- Sort files by modification time.

    FILE_SORT_SIZE
    Size -- Sort files by size.
        :type sort_method: typing.Any
        :param internal: Make Internal, Make text file internal after loading
        :type internal: typing.Union[bool, typing.Any]
    """

    ...

def overwrite_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Toggle overwrite while typing

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def paste(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    selection: typing.Union[bool, typing.Any] = False,
):
    """Paste text from clipboard

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param selection: Selection, Paste text selected elsewhere rather than copied (X11/Wayland only)
    :type selection: typing.Union[bool, typing.Any]
    """

    ...

def refresh_pyconstraints(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Refresh all pyconstraints

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def reload(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Reload active text data-block from its file

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def replace(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    all: typing.Union[bool, typing.Any] = False,
):
    """Replace text with the specified text

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param all: Replace All, Replace all occurrences
    :type all: typing.Union[bool, typing.Any]
    """

    ...

def replace_set_selected(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Replace text with specified text and set as selected

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def resolve_conflict(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    resolution: typing.Any = "IGNORE",
):
    """When external text is out of sync, resolve the conflict

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param resolution: Resolution, How to solve conflict due to differences in internal and external text
    :type resolution: typing.Any
    """

    ...

def run_script(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Run active script

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def save(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Save active text data-block

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def save_as(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    filepath: typing.Union[str, typing.Any] = "",
    hide_props_region: typing.Union[bool, typing.Any] = True,
    check_existing: typing.Union[bool, typing.Any] = True,
    filter_blender: typing.Union[bool, typing.Any] = False,
    filter_backup: typing.Union[bool, typing.Any] = False,
    filter_image: typing.Union[bool, typing.Any] = False,
    filter_movie: typing.Union[bool, typing.Any] = False,
    filter_python: typing.Union[bool, typing.Any] = True,
    filter_font: typing.Union[bool, typing.Any] = False,
    filter_sound: typing.Union[bool, typing.Any] = False,
    filter_text: typing.Union[bool, typing.Any] = True,
    filter_archive: typing.Union[bool, typing.Any] = False,
    filter_btx: typing.Union[bool, typing.Any] = False,
    filter_collada: typing.Union[bool, typing.Any] = False,
    filter_alembic: typing.Union[bool, typing.Any] = False,
    filter_usd: typing.Union[bool, typing.Any] = False,
    filter_obj: typing.Union[bool, typing.Any] = False,
    filter_volume: typing.Union[bool, typing.Any] = False,
    filter_folder: typing.Union[bool, typing.Any] = True,
    filter_blenlib: typing.Union[bool, typing.Any] = False,
    filemode: typing.Any = 9,
    display_type: typing.Any = "DEFAULT",
    sort_method: typing.Union[str, int, typing.Any] = "",
):
    """Save active text file with options

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param filepath: File Path, Path to file
        :type filepath: typing.Union[str, typing.Any]
        :param hide_props_region: Hide Operator Properties, Collapse the region displaying the operator settings
        :type hide_props_region: typing.Union[bool, typing.Any]
        :param check_existing: Check Existing, Check and warn on overwriting existing files
        :type check_existing: typing.Union[bool, typing.Any]
        :param filter_blender: Filter .blend files
        :type filter_blender: typing.Union[bool, typing.Any]
        :param filter_backup: Filter .blend files
        :type filter_backup: typing.Union[bool, typing.Any]
        :param filter_image: Filter image files
        :type filter_image: typing.Union[bool, typing.Any]
        :param filter_movie: Filter movie files
        :type filter_movie: typing.Union[bool, typing.Any]
        :param filter_python: Filter Python files
        :type filter_python: typing.Union[bool, typing.Any]
        :param filter_font: Filter font files
        :type filter_font: typing.Union[bool, typing.Any]
        :param filter_sound: Filter sound files
        :type filter_sound: typing.Union[bool, typing.Any]
        :param filter_text: Filter text files
        :type filter_text: typing.Union[bool, typing.Any]
        :param filter_archive: Filter archive files
        :type filter_archive: typing.Union[bool, typing.Any]
        :param filter_btx: Filter btx files
        :type filter_btx: typing.Union[bool, typing.Any]
        :param filter_collada: Filter COLLADA files
        :type filter_collada: typing.Union[bool, typing.Any]
        :param filter_alembic: Filter Alembic files
        :type filter_alembic: typing.Union[bool, typing.Any]
        :param filter_usd: Filter USD files
        :type filter_usd: typing.Union[bool, typing.Any]
        :param filter_obj: Filter OBJ files
        :type filter_obj: typing.Union[bool, typing.Any]
        :param filter_volume: Filter OpenVDB volume files
        :type filter_volume: typing.Union[bool, typing.Any]
        :param filter_folder: Filter folders
        :type filter_folder: typing.Union[bool, typing.Any]
        :param filter_blenlib: Filter Blender IDs
        :type filter_blenlib: typing.Union[bool, typing.Any]
        :param filemode: File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file
        :type filemode: typing.Any
        :param display_type: Display Type

    DEFAULT
    Default -- Automatically determine display type for files.

    LIST_VERTICAL
    Short List -- Display files as short list.

    LIST_HORIZONTAL
    Long List -- Display files as a detailed list.

    THUMBNAIL
    Thumbnails -- Display files as thumbnails.
        :type display_type: typing.Any
        :param sort_method: File sorting mode
        :type sort_method: typing.Union[str, int, typing.Any]
    """

    ...

def scroll(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    lines: typing.Any = 1,
):
    """Undocumented, consider contributing.

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param lines: Lines, Number of lines to scroll
    :type lines: typing.Any
    """

    ...

def scroll_bar(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    lines: typing.Any = 1,
):
    """Undocumented, consider contributing.

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param lines: Lines, Number of lines to scroll
    :type lines: typing.Any
    """

    ...

def select_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Select all text

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select_line(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Select text by line

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select_word(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Select word under cursor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def selection_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Set text selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def start_find(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Start searching text

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def to_3d_object(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    split_lines: typing.Union[bool, typing.Any] = False,
):
    """Create 3D text object from active text data-block

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param split_lines: Split Lines, Create one object per line in the text
    :type split_lines: typing.Union[bool, typing.Any]
    """

    ...

def unindent(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Unindent selected text

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def unlink(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Unlink active text data-block

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...
