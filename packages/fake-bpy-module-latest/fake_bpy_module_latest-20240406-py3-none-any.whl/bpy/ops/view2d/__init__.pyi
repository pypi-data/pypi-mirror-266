import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def edge_pan(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    inside_padding: typing.Any = 1.0,
    outside_padding: typing.Any = 0.0,
    speed_ramp: typing.Any = 1.0,
    max_speed: typing.Any = 500.0,
    delay: typing.Any = 1.0,
    zoom_influence: typing.Any = 0.0,
):
    """Pan the view when the mouse is held at an edge

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param inside_padding: Inside Padding, Inside distance in UI units from the edge of the region within which to start panning
    :type inside_padding: typing.Any
    :param outside_padding: Outside Padding, Outside distance in UI units from the edge of the region at which to stop panning
    :type outside_padding: typing.Any
    :param speed_ramp: Speed Ramp, Width of the zone in UI units where speed increases with distance from the edge
    :type speed_ramp: typing.Any
    :param max_speed: Max Speed, Maximum speed in UI units per second
    :type max_speed: typing.Any
    :param delay: Delay, Delay in seconds before maximum speed is reached
    :type delay: typing.Any
    :param zoom_influence: Zoom Influence, Influence of the zoom factor on scroll speed
    :type zoom_influence: typing.Any
    """

    ...

def ndof(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Use a 3D mouse device to pan/zoom the view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def pan(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    deltax: typing.Any = 0,
    deltay: typing.Any = 0,
):
    """Pan the view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param deltax: Delta X
    :type deltax: typing.Any
    :param deltay: Delta Y
    :type deltay: typing.Any
    """

    ...

def reset(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Reset the view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def scroll_down(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    deltax: typing.Any = 0,
    deltay: typing.Any = 0,
    page: typing.Union[bool, typing.Any] = False,
):
    """Scroll the view down

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param deltax: Delta X
    :type deltax: typing.Any
    :param deltay: Delta Y
    :type deltay: typing.Any
    :param page: Page, Scroll down one page
    :type page: typing.Union[bool, typing.Any]
    """

    ...

def scroll_left(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    deltax: typing.Any = 0,
    deltay: typing.Any = 0,
):
    """Scroll the view left

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param deltax: Delta X
    :type deltax: typing.Any
    :param deltay: Delta Y
    :type deltay: typing.Any
    """

    ...

def scroll_right(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    deltax: typing.Any = 0,
    deltay: typing.Any = 0,
):
    """Scroll the view right

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param deltax: Delta X
    :type deltax: typing.Any
    :param deltay: Delta Y
    :type deltay: typing.Any
    """

    ...

def scroll_up(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    deltax: typing.Any = 0,
    deltay: typing.Any = 0,
    page: typing.Union[bool, typing.Any] = False,
):
    """Scroll the view up

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param deltax: Delta X
    :type deltax: typing.Any
    :param deltay: Delta Y
    :type deltay: typing.Any
    :param page: Page, Scroll up one page
    :type page: typing.Union[bool, typing.Any]
    """

    ...

def scroller_activate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Scroll view by mouse click and drag

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def smoothview(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    xmin: typing.Any = 0,
    xmax: typing.Any = 0,
    ymin: typing.Any = 0,
    ymax: typing.Any = 0,
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Undocumented, consider contributing.

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

def zoom(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    deltax: typing.Any = 0.0,
    deltay: typing.Any = 0.0,
    use_cursor_init: typing.Union[bool, typing.Any] = True,
):
    """Zoom in/out the view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param deltax: Delta X
    :type deltax: typing.Any
    :param deltay: Delta Y
    :type deltay: typing.Any
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
    """Zoom in the view to the nearest item contained in the border

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

def zoom_in(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    zoomfacx: typing.Any = 0.0,
    zoomfacy: typing.Any = 0.0,
):
    """Zoom in the view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param zoomfacx: Zoom Factor X
    :type zoomfacx: typing.Any
    :param zoomfacy: Zoom Factor Y
    :type zoomfacy: typing.Any
    """

    ...

def zoom_out(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    zoomfacx: typing.Any = 0.0,
    zoomfacy: typing.Any = 0.0,
):
    """Zoom out the view

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param zoomfacx: Zoom Factor X
    :type zoomfacx: typing.Any
    :param zoomfacy: Zoom Factor Y
    :type zoomfacy: typing.Any
    """

    ...
