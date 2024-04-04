import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def add_feather_vertex(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    location: typing.Any = (0.0, 0.0),
):
    """Add vertex to feather

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param location: Location, Location of vertex in normalized space
    :type location: typing.Any
    """

    ...

def add_feather_vertex_slide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    MASK_OT_add_feather_vertex: typing.Any = None,
    MASK_OT_slide_point: typing.Any = None,
):
    """Add new vertex to feather and slide it

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param MASK_OT_add_feather_vertex: Add Feather Vertex, Add vertex to feather
    :type MASK_OT_add_feather_vertex: typing.Any
    :param MASK_OT_slide_point: Slide Point, Slide control points
    :type MASK_OT_slide_point: typing.Any
    """

    ...

def add_vertex(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    location: typing.Any = (0.0, 0.0),
):
    """Add vertex to active spline

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param location: Location, Location of vertex in normalized space
    :type location: typing.Any
    """

    ...

def add_vertex_slide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    MASK_OT_add_vertex: typing.Any = None,
    MASK_OT_slide_point: typing.Any = None,
):
    """Add new vertex and slide it

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param MASK_OT_add_vertex: Add Vertex, Add vertex to active spline
    :type MASK_OT_add_vertex: typing.Any
    :param MASK_OT_slide_point: Slide Point, Slide control points
    :type MASK_OT_slide_point: typing.Any
    """

    ...

def copy_splines(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Copy the selected splines to the internal clipboard

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def cyclic_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Toggle cyclic for selected splines

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
    """Delete selected control points or splines

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
):
    """Duplicate selected control points and segments between them

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def duplicate_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    MASK_OT_duplicate: typing.Any = None,
    TRANSFORM_OT_translate: typing.Any = None,
):
    """Duplicate mask and move

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param MASK_OT_duplicate: Duplicate Mask, Duplicate selected control points and segments between them
    :type MASK_OT_duplicate: typing.Any
    :param TRANSFORM_OT_translate: Move, Move selected items
    :type TRANSFORM_OT_translate: typing.Any
    """

    ...

def feather_weight_clear(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Reset the feather weight to zero

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def handle_type_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "AUTO",
):
    """Set type of handles for selected control points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type, Spline type
    :type type: typing.Any
    """

    ...

def hide_view_clear(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    select: typing.Union[bool, typing.Any] = True,
):
    """Reveal temporarily hidden mask layers

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param select: Select
    :type select: typing.Union[bool, typing.Any]
    """

    ...

def hide_view_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    unselected: typing.Union[bool, typing.Any] = False,
):
    """Temporarily hide mask layers

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param unselected: Unselected, Hide unselected rather than selected layers
    :type unselected: typing.Union[bool, typing.Any]
    """

    ...

def layer_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    direction: typing.Any = "UP",
):
    """Move the active layer up/down in the list

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param direction: Direction, Direction to move the active layer
    :type direction: typing.Any
    """

    ...

def layer_new(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    name: typing.Union[str, typing.Any] = "",
):
    """Add new mask layer for masking

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param name: Name, Name of new mask layer
    :type name: typing.Union[str, typing.Any]
    """

    ...

def layer_remove(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Remove mask layer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def new(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    name: typing.Union[str, typing.Any] = "",
):
    """Create new mask

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param name: Name, Name of new mask
    :type name: typing.Union[str, typing.Any]
    """

    ...

def normals_make_consistent(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Recalculate the direction of selected handles

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def parent_clear(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Clear the mask's parenting

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def parent_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Set the mask's parenting

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def paste_splines(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Paste splines from the internal clipboard

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def primitive_circle_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    size: typing.Any = 100.0,
    location: typing.Any = (0.0, 0.0),
):
    """Add new circle-shaped spline

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param size: Size, Size of new circle
    :type size: typing.Any
    :param location: Location, Location of new circle
    :type location: typing.Any
    """

    ...

def primitive_square_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    size: typing.Any = 100.0,
    location: typing.Any = (0.0, 0.0),
):
    """Add new square-shaped spline

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param size: Size, Size of new circle
    :type size: typing.Any
    :param location: Location, Location of new circle
    :type location: typing.Any
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
    location: typing.Any = (0.0, 0.0),
):
    """Select spline points

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
    :param location: Location, Location of vertex in normalized space
    :type location: typing.Any
    """

    ...

def select_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    action: typing.Any = "TOGGLE",
):
    """Change selection of all curve points

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
    """Select curve points using box selection

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
    """Select curve points using circle selection

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
    """Select curve points using lasso selection

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
        :type mode: typing.Any
    """

    ...

def select_less(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Deselect spline points at the boundary of each selection region

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
    """Select all curve points linked to already selected ones

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select_linked_pick(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    deselect: typing.Union[bool, typing.Any] = False,
):
    """(De)select all points linked to the curve under the mouse cursor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param deselect: Deselect
    :type deselect: typing.Union[bool, typing.Any]
    """

    ...

def select_more(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Select more spline points connected to initial selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def shape_key_clear(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Remove mask shape keyframe for active mask layer at the current frame

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def shape_key_feather_reset(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Reset feather weights on all selected points animation values

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def shape_key_insert(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Insert mask shape keyframe for active mask layer at the current frame

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def shape_key_rekey(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    location: typing.Union[bool, typing.Any] = True,
    feather: typing.Union[bool, typing.Any] = True,
):
    """Recalculate animation data on selected points for frames selected in the dopesheet

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param location: Location
    :type location: typing.Union[bool, typing.Any]
    :param feather: Feather
    :type feather: typing.Union[bool, typing.Any]
    """

    ...

def slide_point(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    slide_feather: typing.Union[bool, typing.Any] = False,
    is_new_point: typing.Union[bool, typing.Any] = False,
):
    """Slide control points

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param slide_feather: Slide Feather, First try to slide feather instead of vertex
    :type slide_feather: typing.Union[bool, typing.Any]
    :param is_new_point: Slide New Point, Newly created vertex is being slid
    :type is_new_point: typing.Union[bool, typing.Any]
    """

    ...

def slide_spline_curvature(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Slide a point on the spline to define its curvature

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def switch_direction(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Switch direction of selected splines

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...
