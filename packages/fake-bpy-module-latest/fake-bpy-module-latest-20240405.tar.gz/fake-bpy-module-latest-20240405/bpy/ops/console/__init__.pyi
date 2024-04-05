import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def autocomplete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Evaluate the namespace up until the cursor and give a list of options or complete the name if there is only one

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def banner(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Print a message when the terminal initializes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def clear(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    scrollback: typing.Union[bool, typing.Any] = True,
    history: typing.Union[bool, typing.Any] = False,
):
    """Clear text by type

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param scrollback: Scrollback, Clear the scrollback history
    :type scrollback: typing.Union[bool, typing.Any]
    :param history: History, Clear the command history
    :type history: typing.Union[bool, typing.Any]
    """

    ...

def clear_line(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Clear the line and store in history

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def copy(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    delete: typing.Union[bool, typing.Any] = False,
):
    """Copy selected text to clipboard

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param delete: Delete Selection, Whether to delete the selection after copying
    :type delete: typing.Union[bool, typing.Any]
    """

    ...

def copy_as_script(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Copy the console contents for use in a script

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

def execute(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    interactive: typing.Union[bool, typing.Any] = False,
):
    """Execute the current console line as a Python expression

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param interactive: interactive
    :type interactive: typing.Union[bool, typing.Any]
    """

    ...

def history_append(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    text: typing.Union[str, typing.Any] = "",
    current_character: typing.Any = 0,
    remove_duplicates: typing.Union[bool, typing.Any] = False,
):
    """Append history at cursor position

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param text: Text, Text to insert at the cursor position
    :type text: typing.Union[str, typing.Any]
    :param current_character: Cursor, The index of the cursor
    :type current_character: typing.Any
    :param remove_duplicates: Remove Duplicates, Remove duplicate items in the history
    :type remove_duplicates: typing.Union[bool, typing.Any]
    """

    ...

def history_cycle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    reverse: typing.Union[bool, typing.Any] = False,
):
    """Cycle through history

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param reverse: Reverse, Reverse cycle history
    :type reverse: typing.Union[bool, typing.Any]
    """

    ...

def indent(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add 4 spaces at line beginning

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

def language(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    language: typing.Union[str, typing.Any] = "",
):
    """Set the current language for this console

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param language: Language
    :type language: typing.Union[str, typing.Any]
    """

    ...

def move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "LINE_BEGIN",
    select: typing.Union[bool, typing.Any] = False,
):
    """Move cursor position

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type, Where to move cursor to
    :type type: typing.Any
    :param select: Select, Whether to select while moving
    :type select: typing.Union[bool, typing.Any]
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

def scrollback_append(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    text: typing.Union[str, typing.Any] = "",
    type: typing.Any = "OUTPUT",
):
    """Append scrollback text by type

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param text: Text, Text to insert at the cursor position
    :type text: typing.Union[str, typing.Any]
    :param type: Type, Console output type
    :type type: typing.Any
    """

    ...

def select_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Select all the text

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Set the console selection

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
    """Select word at cursor position

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def unindent(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Delete 4 spaces from line beginning

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...
