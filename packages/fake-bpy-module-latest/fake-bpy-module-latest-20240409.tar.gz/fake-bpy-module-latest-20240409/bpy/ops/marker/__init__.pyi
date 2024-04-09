import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add a new time marker

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def camera_bind(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Bind the selected camera to a marker on the current frame

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def delete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    confirm: typing.Union[bool, typing.Any] = True,
):
    """Delete selected time marker(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param confirm: Confirm, Prompt for confirmation
    :type confirm: typing.Union[bool, typing.Any]
    """

    ...

def duplicate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    frames: typing.Any = 0,
):
    """Duplicate selected time marker(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param frames: Frames
    :type frames: typing.Any
    """

    ...

def make_links_scene(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    scene: typing.Union[str, int, typing.Any] = "",
):
    """Copy selected markers to another scene

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param scene: Scene
    :type scene: typing.Union[str, int, typing.Any]
    """

    ...

def move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    frames: typing.Any = 0,
    tweak: typing.Union[bool, typing.Any] = False,
):
    """Move selected time marker(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param frames: Frames
    :type frames: typing.Any
    :param tweak: Tweak, Operator has been activated using a click-drag event
    :type tweak: typing.Union[bool, typing.Any]
    """

    ...

def rename(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    name: typing.Union[str, typing.Any] = "RenamedMarker",
):
    """Rename first selected time marker

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param name: Name, New name for marker
    :type name: typing.Union[str, typing.Any]
    """

    ...

def select(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    wait_to_deselect_others: typing.Union[bool, typing.Any] = False,
    mouse_x: typing.Any = 0,
    mouse_y: typing.Any = 0,
    extend: typing.Union[bool, typing.Any] = False,
    camera: typing.Union[bool, typing.Any] = False,
):
    """Select time marker(s)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param wait_to_deselect_others: Wait to Deselect Others
    :type wait_to_deselect_others: typing.Union[bool, typing.Any]
    :param mouse_x: Mouse X
    :type mouse_x: typing.Any
    :param mouse_y: Mouse Y
    :type mouse_y: typing.Any
    :param extend: Extend, Extend the selection
    :type extend: typing.Union[bool, typing.Any]
    :param camera: Camera, Select the camera
    :type camera: typing.Union[bool, typing.Any]
    """

    ...

def select_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    action: typing.Any = "TOGGLE",
):
    """Change selection of all time markers

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
    tweak: typing.Union[bool, typing.Any] = False,
):
    """Select all time markers using box selection

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
        :param tweak: Tweak, Operator has been activated using a click-drag event
        :type tweak: typing.Union[bool, typing.Any]
    """

    ...

def select_leftright(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "LEFT",
    extend: typing.Union[bool, typing.Any] = False,
):
    """Select markers on and left/right of the current frame

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Any
    :param extend: Extend Select
    :type extend: typing.Union[bool, typing.Any]
    """

    ...
