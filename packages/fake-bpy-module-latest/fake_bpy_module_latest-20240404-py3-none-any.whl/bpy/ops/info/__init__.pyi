import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def report_copy(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Copy selected reports to clipboard

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def report_delete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Delete selected reports

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def report_replay(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Replay selected reports

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def reports_display_update(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Update the display of reports in Blender UI (internal use)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    action: typing.Any = "SELECT",
):
    """Change selection of all visible reports

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
    xmin: typing.Any = 0,
    xmax: typing.Any = 0,
    ymin: typing.Any = 0,
    ymax: typing.Any = 0,
    wait_for_input: typing.Union[bool, typing.Any] = True,
    mode: typing.Any = "SET",
):
    """Toggle box selection

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
        :type mode: typing.Any
    """

    ...

def select_pick(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    report_index: typing.Any = 0,
    extend: typing.Union[bool, typing.Any] = False,
):
    """Select reports by index

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param report_index: Report, Index of the report
    :type report_index: typing.Any
    :param extend: Extend, Extend report selection
    :type extend: typing.Union[bool, typing.Any]
    """

    ...
