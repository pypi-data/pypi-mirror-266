import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def bbone_resize(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = (1.0, 1.0, 1.0),
    orient_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    orient_matrix: typing.Any = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    orient_matrix_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    constraint_axis: typing.Union[typing.List[bool], typing.Any] = (
        False,
        False,
        False,
    ),
    mirror: typing.Union[bool, typing.Any] = False,
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Scale selected bendy bones display size

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Display Size
    :type value: typing.Any
    :param orient_type: Orientation, Transformation orientation
    :type orient_type: typing.Union[str, int, typing.Any]
    :param orient_matrix: Matrix
    :type orient_matrix: typing.Any
    :param orient_matrix_type: Matrix Orientation
    :type orient_matrix_type: typing.Union[str, int, typing.Any]
    :param constraint_axis: Constraint Axis
    :type constraint_axis: typing.Union[typing.List[bool], typing.Any]
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def bend(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    mirror: typing.Union[bool, typing.Any] = False,
    use_proportional_edit: typing.Union[bool, typing.Any] = False,
    proportional_edit_falloff: typing.Union[str, int] = "SMOOTH",
    proportional_size: typing.Any = 1.0,
    use_proportional_connected: typing.Union[bool, typing.Any] = False,
    use_proportional_projected: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    gpencil_strokes: typing.Union[bool, typing.Any] = False,
    center_override: typing.Any = (0.0, 0.0, 0.0),
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Bend selected items between the 3D cursor and the mouse

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Angle
    :type value: typing.Any
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param use_proportional_edit: Proportional Editing
    :type use_proportional_edit: typing.Union[bool, typing.Any]
    :param proportional_edit_falloff: Proportional Falloff, Falloff type for proportional editing mode
    :type proportional_edit_falloff: typing.Union[str, int]
    :param proportional_size: Proportional Size
    :type proportional_size: typing.Any
    :param use_proportional_connected: Connected
    :type use_proportional_connected: typing.Union[bool, typing.Any]
    :param use_proportional_projected: Projected (2D)
    :type use_proportional_projected: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param gpencil_strokes: Edit Grease Pencil, Edit selected Grease Pencil strokes
    :type gpencil_strokes: typing.Union[bool, typing.Any]
    :param center_override: Center Override, Force using this center value (when set)
    :type center_override: typing.Any
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def create_orientation(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    name: typing.Union[str, typing.Any] = "",
    use_view: typing.Union[bool, typing.Any] = False,
    use: typing.Union[bool, typing.Any] = False,
    overwrite: typing.Union[bool, typing.Any] = False,
):
    """Create transformation orientation from selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param name: Name, Name of the new custom orientation
    :type name: typing.Union[str, typing.Any]
    :param use_view: Use View, Use the current view instead of the active object to create the new orientation
    :type use_view: typing.Union[bool, typing.Any]
    :param use: Use After Creation, Select orientation after its creation
    :type use: typing.Union[bool, typing.Any]
    :param overwrite: Overwrite Previous, Overwrite previously created orientation with same name
    :type overwrite: typing.Union[bool, typing.Any]
    """

    ...

def delete_orientation(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Delete transformation orientation

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def edge_bevelweight(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    snap: typing.Union[bool, typing.Any] = False,
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Change the bevel weight of edges

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Factor
    :type value: typing.Any
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def edge_crease(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    snap: typing.Union[bool, typing.Any] = False,
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Change the crease of edges

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Factor
    :type value: typing.Any
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def edge_slide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    single_side: typing.Union[bool, typing.Any] = False,
    use_even: typing.Union[bool, typing.Any] = False,
    flipped: typing.Union[bool, typing.Any] = False,
    use_clamp: typing.Union[bool, typing.Any] = True,
    mirror: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    snap_elements: typing.Any = {'"INCREMENT"'},
    use_snap_project: typing.Union[bool, typing.Any] = False,
    snap_target: typing.Union[str, int] = "CLOSEST",
    use_snap_self: typing.Union[bool, typing.Any] = True,
    use_snap_edit: typing.Union[bool, typing.Any] = True,
    use_snap_nonedit: typing.Union[bool, typing.Any] = True,
    use_snap_selectable: typing.Union[bool, typing.Any] = False,
    snap_point: typing.Any = (0.0, 0.0, 0.0),
    correct_uv: typing.Union[bool, typing.Any] = True,
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Slide an edge loop along a mesh

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Factor
    :type value: typing.Any
    :param single_side: Single Side
    :type single_side: typing.Union[bool, typing.Any]
    :param use_even: Even, Make the edge loop match the shape of the adjacent edge loop
    :type use_even: typing.Union[bool, typing.Any]
    :param flipped: Flipped, When Even mode is active, flips between the two adjacent edge loops
    :type flipped: typing.Union[bool, typing.Any]
    :param use_clamp: Clamp, Clamp within the edge extents
    :type use_clamp: typing.Union[bool, typing.Any]
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param snap_elements: Snap to Elements
    :type snap_elements: typing.Any
    :param use_snap_project: Project Individual Elements
    :type use_snap_project: typing.Union[bool, typing.Any]
    :param snap_target: Snap Base, Point on source that will snap to target
    :type snap_target: typing.Union[str, int]
    :param use_snap_self: Target: Include Active
    :type use_snap_self: typing.Union[bool, typing.Any]
    :param use_snap_edit: Target: Include Edit
    :type use_snap_edit: typing.Union[bool, typing.Any]
    :param use_snap_nonedit: Target: Include Non-Edited
    :type use_snap_nonedit: typing.Union[bool, typing.Any]
    :param use_snap_selectable: Target: Exclude Non-Selectable
    :type use_snap_selectable: typing.Union[bool, typing.Any]
    :param snap_point: Point
    :type snap_point: typing.Any
    :param correct_uv: Correct UVs, Correct UV coordinates when transforming
    :type correct_uv: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def from_gizmo(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Transform selected items by mode type

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def mirror(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    orient_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    orient_matrix: typing.Any = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    orient_matrix_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    constraint_axis: typing.Union[typing.List[bool], typing.Any] = (
        False,
        False,
        False,
    ),
    gpencil_strokes: typing.Union[bool, typing.Any] = False,
    center_override: typing.Any = (0.0, 0.0, 0.0),
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Mirror selected items around one or more axes

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param orient_type: Orientation, Transformation orientation
    :type orient_type: typing.Union[str, int, typing.Any]
    :param orient_matrix: Matrix
    :type orient_matrix: typing.Any
    :param orient_matrix_type: Matrix Orientation
    :type orient_matrix_type: typing.Union[str, int, typing.Any]
    :param constraint_axis: Constraint Axis
    :type constraint_axis: typing.Union[typing.List[bool], typing.Any]
    :param gpencil_strokes: Edit Grease Pencil, Edit selected Grease Pencil strokes
    :type gpencil_strokes: typing.Union[bool, typing.Any]
    :param center_override: Center Override, Force using this center value (when set)
    :type center_override: typing.Any
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def push_pull(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    mirror: typing.Union[bool, typing.Any] = False,
    use_proportional_edit: typing.Union[bool, typing.Any] = False,
    proportional_edit_falloff: typing.Union[str, int] = "SMOOTH",
    proportional_size: typing.Any = 1.0,
    use_proportional_connected: typing.Union[bool, typing.Any] = False,
    use_proportional_projected: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    center_override: typing.Any = (0.0, 0.0, 0.0),
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Push/Pull selected items

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Distance
    :type value: typing.Any
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param use_proportional_edit: Proportional Editing
    :type use_proportional_edit: typing.Union[bool, typing.Any]
    :param proportional_edit_falloff: Proportional Falloff, Falloff type for proportional editing mode
    :type proportional_edit_falloff: typing.Union[str, int]
    :param proportional_size: Proportional Size
    :type proportional_size: typing.Any
    :param use_proportional_connected: Connected
    :type use_proportional_connected: typing.Union[bool, typing.Any]
    :param use_proportional_projected: Projected (2D)
    :type use_proportional_projected: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param center_override: Center Override, Force using this center value (when set)
    :type center_override: typing.Any
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def resize(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = (1.0, 1.0, 1.0),
    mouse_dir_constraint: typing.Any = (0.0, 0.0, 0.0),
    orient_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    orient_matrix: typing.Any = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    orient_matrix_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    constraint_axis: typing.Union[typing.List[bool], typing.Any] = (
        False,
        False,
        False,
    ),
    mirror: typing.Union[bool, typing.Any] = False,
    use_proportional_edit: typing.Union[bool, typing.Any] = False,
    proportional_edit_falloff: typing.Union[str, int] = "SMOOTH",
    proportional_size: typing.Any = 1.0,
    use_proportional_connected: typing.Union[bool, typing.Any] = False,
    use_proportional_projected: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    snap_elements: typing.Any = {'"INCREMENT"'},
    use_snap_project: typing.Union[bool, typing.Any] = False,
    snap_target: typing.Union[str, int] = "CLOSEST",
    use_snap_self: typing.Union[bool, typing.Any] = True,
    use_snap_edit: typing.Union[bool, typing.Any] = True,
    use_snap_nonedit: typing.Union[bool, typing.Any] = True,
    use_snap_selectable: typing.Union[bool, typing.Any] = False,
    snap_point: typing.Any = (0.0, 0.0, 0.0),
    gpencil_strokes: typing.Union[bool, typing.Any] = False,
    texture_space: typing.Union[bool, typing.Any] = False,
    remove_on_cancel: typing.Union[bool, typing.Any] = False,
    use_duplicated_keyframes: typing.Union[bool, typing.Any] = False,
    center_override: typing.Any = (0.0, 0.0, 0.0),
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Scale (resize) selected items

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Scale
    :type value: typing.Any
    :param mouse_dir_constraint: Mouse Directional Constraint
    :type mouse_dir_constraint: typing.Any
    :param orient_type: Orientation, Transformation orientation
    :type orient_type: typing.Union[str, int, typing.Any]
    :param orient_matrix: Matrix
    :type orient_matrix: typing.Any
    :param orient_matrix_type: Matrix Orientation
    :type orient_matrix_type: typing.Union[str, int, typing.Any]
    :param constraint_axis: Constraint Axis
    :type constraint_axis: typing.Union[typing.List[bool], typing.Any]
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param use_proportional_edit: Proportional Editing
    :type use_proportional_edit: typing.Union[bool, typing.Any]
    :param proportional_edit_falloff: Proportional Falloff, Falloff type for proportional editing mode
    :type proportional_edit_falloff: typing.Union[str, int]
    :param proportional_size: Proportional Size
    :type proportional_size: typing.Any
    :param use_proportional_connected: Connected
    :type use_proportional_connected: typing.Union[bool, typing.Any]
    :param use_proportional_projected: Projected (2D)
    :type use_proportional_projected: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param snap_elements: Snap to Elements
    :type snap_elements: typing.Any
    :param use_snap_project: Project Individual Elements
    :type use_snap_project: typing.Union[bool, typing.Any]
    :param snap_target: Snap Base, Point on source that will snap to target
    :type snap_target: typing.Union[str, int]
    :param use_snap_self: Target: Include Active
    :type use_snap_self: typing.Union[bool, typing.Any]
    :param use_snap_edit: Target: Include Edit
    :type use_snap_edit: typing.Union[bool, typing.Any]
    :param use_snap_nonedit: Target: Include Non-Edited
    :type use_snap_nonedit: typing.Union[bool, typing.Any]
    :param use_snap_selectable: Target: Exclude Non-Selectable
    :type use_snap_selectable: typing.Union[bool, typing.Any]
    :param snap_point: Point
    :type snap_point: typing.Any
    :param gpencil_strokes: Edit Grease Pencil, Edit selected Grease Pencil strokes
    :type gpencil_strokes: typing.Union[bool, typing.Any]
    :param texture_space: Edit Texture Space, Edit object data texture space
    :type texture_space: typing.Union[bool, typing.Any]
    :param remove_on_cancel: Remove on Cancel, Remove elements on cancel
    :type remove_on_cancel: typing.Union[bool, typing.Any]
    :param use_duplicated_keyframes: Duplicated Keyframes, Transform duplicated keyframes
    :type use_duplicated_keyframes: typing.Union[bool, typing.Any]
    :param center_override: Center Override, Force using this center value (when set)
    :type center_override: typing.Any
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def rotate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    orient_axis: typing.Union[str, int] = "Z",
    orient_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    orient_matrix: typing.Any = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    orient_matrix_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    constraint_axis: typing.Union[typing.List[bool], typing.Any] = (
        False,
        False,
        False,
    ),
    mirror: typing.Union[bool, typing.Any] = False,
    use_proportional_edit: typing.Union[bool, typing.Any] = False,
    proportional_edit_falloff: typing.Union[str, int] = "SMOOTH",
    proportional_size: typing.Any = 1.0,
    use_proportional_connected: typing.Union[bool, typing.Any] = False,
    use_proportional_projected: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    snap_elements: typing.Any = {'"INCREMENT"'},
    use_snap_project: typing.Union[bool, typing.Any] = False,
    snap_target: typing.Union[str, int] = "CLOSEST",
    use_snap_self: typing.Union[bool, typing.Any] = True,
    use_snap_edit: typing.Union[bool, typing.Any] = True,
    use_snap_nonedit: typing.Union[bool, typing.Any] = True,
    use_snap_selectable: typing.Union[bool, typing.Any] = False,
    snap_point: typing.Any = (0.0, 0.0, 0.0),
    gpencil_strokes: typing.Union[bool, typing.Any] = False,
    center_override: typing.Any = (0.0, 0.0, 0.0),
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Rotate selected items

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Angle
    :type value: typing.Any
    :param orient_axis: Axis
    :type orient_axis: typing.Union[str, int]
    :param orient_type: Orientation, Transformation orientation
    :type orient_type: typing.Union[str, int, typing.Any]
    :param orient_matrix: Matrix
    :type orient_matrix: typing.Any
    :param orient_matrix_type: Matrix Orientation
    :type orient_matrix_type: typing.Union[str, int, typing.Any]
    :param constraint_axis: Constraint Axis
    :type constraint_axis: typing.Union[typing.List[bool], typing.Any]
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param use_proportional_edit: Proportional Editing
    :type use_proportional_edit: typing.Union[bool, typing.Any]
    :param proportional_edit_falloff: Proportional Falloff, Falloff type for proportional editing mode
    :type proportional_edit_falloff: typing.Union[str, int]
    :param proportional_size: Proportional Size
    :type proportional_size: typing.Any
    :param use_proportional_connected: Connected
    :type use_proportional_connected: typing.Union[bool, typing.Any]
    :param use_proportional_projected: Projected (2D)
    :type use_proportional_projected: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param snap_elements: Snap to Elements
    :type snap_elements: typing.Any
    :param use_snap_project: Project Individual Elements
    :type use_snap_project: typing.Union[bool, typing.Any]
    :param snap_target: Snap Base, Point on source that will snap to target
    :type snap_target: typing.Union[str, int]
    :param use_snap_self: Target: Include Active
    :type use_snap_self: typing.Union[bool, typing.Any]
    :param use_snap_edit: Target: Include Edit
    :type use_snap_edit: typing.Union[bool, typing.Any]
    :param use_snap_nonedit: Target: Include Non-Edited
    :type use_snap_nonedit: typing.Union[bool, typing.Any]
    :param use_snap_selectable: Target: Exclude Non-Selectable
    :type use_snap_selectable: typing.Union[bool, typing.Any]
    :param snap_point: Point
    :type snap_point: typing.Any
    :param gpencil_strokes: Edit Grease Pencil, Edit selected Grease Pencil strokes
    :type gpencil_strokes: typing.Union[bool, typing.Any]
    :param center_override: Center Override, Force using this center value (when set)
    :type center_override: typing.Any
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def rotate_normal(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    orient_axis: typing.Union[str, int] = "Z",
    orient_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    orient_matrix: typing.Any = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    orient_matrix_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    constraint_axis: typing.Union[typing.List[bool], typing.Any] = (
        False,
        False,
        False,
    ),
    mirror: typing.Union[bool, typing.Any] = False,
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Rotate split normal of selected items

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Angle
    :type value: typing.Any
    :param orient_axis: Axis
    :type orient_axis: typing.Union[str, int]
    :param orient_type: Orientation, Transformation orientation
    :type orient_type: typing.Union[str, int, typing.Any]
    :param orient_matrix: Matrix
    :type orient_matrix: typing.Any
    :param orient_matrix_type: Matrix Orientation
    :type orient_matrix_type: typing.Union[str, int, typing.Any]
    :param constraint_axis: Constraint Axis
    :type constraint_axis: typing.Union[typing.List[bool], typing.Any]
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def select_orientation(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    orientation: typing.Union[str, int, typing.Any] = "GLOBAL",
):
    """Select transformation orientation

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param orientation: Orientation, Transformation orientation
    :type orientation: typing.Union[str, int, typing.Any]
    """

    ...

def seq_slide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = (0.0, 0.0),
    snap: typing.Union[bool, typing.Any] = False,
    view2d_edge_pan: typing.Union[bool, typing.Any] = False,
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Slide a sequence strip in time

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Offset
    :type value: typing.Any
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param view2d_edge_pan: Edge Pan, Enable edge panning in 2D view
    :type view2d_edge_pan: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def shear(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    orient_axis: typing.Union[str, int] = "Z",
    orient_axis_ortho: typing.Union[str, int] = "X",
    orient_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    orient_matrix: typing.Any = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    orient_matrix_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    mirror: typing.Union[bool, typing.Any] = False,
    use_proportional_edit: typing.Union[bool, typing.Any] = False,
    proportional_edit_falloff: typing.Union[str, int] = "SMOOTH",
    proportional_size: typing.Any = 1.0,
    use_proportional_connected: typing.Union[bool, typing.Any] = False,
    use_proportional_projected: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    gpencil_strokes: typing.Union[bool, typing.Any] = False,
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Shear selected items along the given axis

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Offset
    :type value: typing.Any
    :param orient_axis: Axis
    :type orient_axis: typing.Union[str, int]
    :param orient_axis_ortho: Axis Ortho
    :type orient_axis_ortho: typing.Union[str, int]
    :param orient_type: Orientation, Transformation orientation
    :type orient_type: typing.Union[str, int, typing.Any]
    :param orient_matrix: Matrix
    :type orient_matrix: typing.Any
    :param orient_matrix_type: Matrix Orientation
    :type orient_matrix_type: typing.Union[str, int, typing.Any]
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param use_proportional_edit: Proportional Editing
    :type use_proportional_edit: typing.Union[bool, typing.Any]
    :param proportional_edit_falloff: Proportional Falloff, Falloff type for proportional editing mode
    :type proportional_edit_falloff: typing.Union[str, int]
    :param proportional_size: Proportional Size
    :type proportional_size: typing.Any
    :param use_proportional_connected: Connected
    :type use_proportional_connected: typing.Union[bool, typing.Any]
    :param use_proportional_projected: Projected (2D)
    :type use_proportional_projected: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param gpencil_strokes: Edit Grease Pencil, Edit selected Grease Pencil strokes
    :type gpencil_strokes: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def shrink_fatten(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    use_even_offset: typing.Union[bool, typing.Any] = False,
    mirror: typing.Union[bool, typing.Any] = False,
    use_proportional_edit: typing.Union[bool, typing.Any] = False,
    proportional_edit_falloff: typing.Union[str, int] = "SMOOTH",
    proportional_size: typing.Any = 1.0,
    use_proportional_connected: typing.Union[bool, typing.Any] = False,
    use_proportional_projected: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Shrink/fatten selected vertices along normals

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Offset
    :type value: typing.Any
    :param use_even_offset: Offset Even, Scale the offset to give more even thickness
    :type use_even_offset: typing.Union[bool, typing.Any]
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param use_proportional_edit: Proportional Editing
    :type use_proportional_edit: typing.Union[bool, typing.Any]
    :param proportional_edit_falloff: Proportional Falloff, Falloff type for proportional editing mode
    :type proportional_edit_falloff: typing.Union[str, int]
    :param proportional_size: Proportional Size
    :type proportional_size: typing.Any
    :param use_proportional_connected: Connected
    :type use_proportional_connected: typing.Union[bool, typing.Any]
    :param use_proportional_projected: Projected (2D)
    :type use_proportional_projected: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def skin_resize(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = (1.0, 1.0, 1.0),
    orient_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    orient_matrix: typing.Any = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    orient_matrix_type: typing.Union[str, int, typing.Any] = "GLOBAL",
    constraint_axis: typing.Union[typing.List[bool], typing.Any] = (
        False,
        False,
        False,
    ),
    mirror: typing.Union[bool, typing.Any] = False,
    use_proportional_edit: typing.Union[bool, typing.Any] = False,
    proportional_edit_falloff: typing.Union[str, int] = "SMOOTH",
    proportional_size: typing.Any = 1.0,
    use_proportional_connected: typing.Union[bool, typing.Any] = False,
    use_proportional_projected: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    snap_elements: typing.Any = {'"INCREMENT"'},
    use_snap_project: typing.Union[bool, typing.Any] = False,
    snap_target: typing.Union[str, int] = "CLOSEST",
    use_snap_self: typing.Union[bool, typing.Any] = True,
    use_snap_edit: typing.Union[bool, typing.Any] = True,
    use_snap_nonedit: typing.Union[bool, typing.Any] = True,
    use_snap_selectable: typing.Union[bool, typing.Any] = False,
    snap_point: typing.Any = (0.0, 0.0, 0.0),
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Scale selected vertices' skin radii

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Scale
    :type value: typing.Any
    :param orient_type: Orientation, Transformation orientation
    :type orient_type: typing.Union[str, int, typing.Any]
    :param orient_matrix: Matrix
    :type orient_matrix: typing.Any
    :param orient_matrix_type: Matrix Orientation
    :type orient_matrix_type: typing.Union[str, int, typing.Any]
    :param constraint_axis: Constraint Axis
    :type constraint_axis: typing.Union[typing.List[bool], typing.Any]
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param use_proportional_edit: Proportional Editing
    :type use_proportional_edit: typing.Union[bool, typing.Any]
    :param proportional_edit_falloff: Proportional Falloff, Falloff type for proportional editing mode
    :type proportional_edit_falloff: typing.Union[str, int]
    :param proportional_size: Proportional Size
    :type proportional_size: typing.Any
    :param use_proportional_connected: Connected
    :type use_proportional_connected: typing.Union[bool, typing.Any]
    :param use_proportional_projected: Projected (2D)
    :type use_proportional_projected: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param snap_elements: Snap to Elements
    :type snap_elements: typing.Any
    :param use_snap_project: Project Individual Elements
    :type use_snap_project: typing.Union[bool, typing.Any]
    :param snap_target: Snap Base, Point on source that will snap to target
    :type snap_target: typing.Union[str, int]
    :param use_snap_self: Target: Include Active
    :type use_snap_self: typing.Union[bool, typing.Any]
    :param use_snap_edit: Target: Include Edit
    :type use_snap_edit: typing.Union[bool, typing.Any]
    :param use_snap_nonedit: Target: Include Non-Edited
    :type use_snap_nonedit: typing.Union[bool, typing.Any]
    :param use_snap_selectable: Target: Exclude Non-Selectable
    :type use_snap_selectable: typing.Union[bool, typing.Any]
    :param snap_point: Point
    :type snap_point: typing.Any
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def tilt(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    mirror: typing.Union[bool, typing.Any] = False,
    use_proportional_edit: typing.Union[bool, typing.Any] = False,
    proportional_edit_falloff: typing.Union[str, int] = "SMOOTH",
    proportional_size: typing.Any = 1.0,
    use_proportional_connected: typing.Union[bool, typing.Any] = False,
    use_proportional_projected: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Tilt selected control vertices of 3D curve

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Angle
    :type value: typing.Any
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param use_proportional_edit: Proportional Editing
    :type use_proportional_edit: typing.Union[bool, typing.Any]
    :param proportional_edit_falloff: Proportional Falloff, Falloff type for proportional editing mode
    :type proportional_edit_falloff: typing.Union[str, int]
    :param proportional_size: Proportional Size
    :type proportional_size: typing.Any
    :param use_proportional_connected: Connected
    :type use_proportional_connected: typing.Union[bool, typing.Any]
    :param use_proportional_projected: Projected (2D)
    :type use_proportional_projected: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def tosphere(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    mirror: typing.Union[bool, typing.Any] = False,
    use_proportional_edit: typing.Union[bool, typing.Any] = False,
    proportional_edit_falloff: typing.Union[str, int] = "SMOOTH",
    proportional_size: typing.Any = 1.0,
    use_proportional_connected: typing.Union[bool, typing.Any] = False,
    use_proportional_projected: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    gpencil_strokes: typing.Union[bool, typing.Any] = False,
    center_override: typing.Any = (0.0, 0.0, 0.0),
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Move selected items outward in a spherical shape around geometric center

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Factor
    :type value: typing.Any
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param use_proportional_edit: Proportional Editing
    :type use_proportional_edit: typing.Union[bool, typing.Any]
    :param proportional_edit_falloff: Proportional Falloff, Falloff type for proportional editing mode
    :type proportional_edit_falloff: typing.Union[str, int]
    :param proportional_size: Proportional Size
    :type proportional_size: typing.Any
    :param use_proportional_connected: Connected
    :type use_proportional_connected: typing.Union[bool, typing.Any]
    :param use_proportional_projected: Projected (2D)
    :type use_proportional_projected: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param gpencil_strokes: Edit Grease Pencil, Edit selected Grease Pencil strokes
    :type gpencil_strokes: typing.Union[bool, typing.Any]
    :param center_override: Center Override, Force using this center value (when set)
    :type center_override: typing.Any
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def trackball(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = (0.0, 0.0),
    mirror: typing.Union[bool, typing.Any] = False,
    use_proportional_edit: typing.Union[bool, typing.Any] = False,
    proportional_edit_falloff: typing.Union[str, int] = "SMOOTH",
    proportional_size: typing.Any = 1.0,
    use_proportional_connected: typing.Union[bool, typing.Any] = False,
    use_proportional_projected: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    gpencil_strokes: typing.Union[bool, typing.Any] = False,
    center_override: typing.Any = (0.0, 0.0, 0.0),
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Trackball style rotation of selected items

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Angle
    :type value: typing.Any
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param use_proportional_edit: Proportional Editing
    :type use_proportional_edit: typing.Union[bool, typing.Any]
    :param proportional_edit_falloff: Proportional Falloff, Falloff type for proportional editing mode
    :type proportional_edit_falloff: typing.Union[str, int]
    :param proportional_size: Proportional Size
    :type proportional_size: typing.Any
    :param use_proportional_connected: Connected
    :type use_proportional_connected: typing.Union[bool, typing.Any]
    :param use_proportional_projected: Projected (2D)
    :type use_proportional_projected: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param gpencil_strokes: Edit Grease Pencil, Edit selected Grease Pencil strokes
    :type gpencil_strokes: typing.Union[bool, typing.Any]
    :param center_override: Center Override, Force using this center value (when set)
    :type center_override: typing.Any
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def transform(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Union[str, int] = "TRANSLATION",
    value: typing.Any = (0.0, 0.0, 0.0, 0.0),
    orient_axis: typing.Union[str, int] = "Z",
    orient_type: typing.Union[str, int] = "GLOBAL",
    orient_matrix: typing.Any = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    orient_matrix_type: typing.Union[str, int] = "GLOBAL",
    constraint_axis: typing.Union[typing.List[bool], typing.Any] = (
        False,
        False,
        False,
    ),
    mirror: typing.Union[bool, typing.Any] = False,
    use_proportional_edit: typing.Union[bool, typing.Any] = False,
    proportional_edit_falloff: typing.Union[str, int] = "SMOOTH",
    proportional_size: typing.Any = 1.0,
    use_proportional_connected: typing.Union[bool, typing.Any] = False,
    use_proportional_projected: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    snap_elements: typing.Any = {'"INCREMENT"'},
    use_snap_project: typing.Union[bool, typing.Any] = False,
    snap_target: typing.Union[str, int] = "CLOSEST",
    use_snap_self: typing.Union[bool, typing.Any] = True,
    use_snap_edit: typing.Union[bool, typing.Any] = True,
    use_snap_nonedit: typing.Union[bool, typing.Any] = True,
    use_snap_selectable: typing.Union[bool, typing.Any] = False,
    snap_point: typing.Any = (0.0, 0.0, 0.0),
    snap_align: typing.Union[bool, typing.Any] = False,
    snap_normal: typing.Any = (0.0, 0.0, 0.0),
    gpencil_strokes: typing.Union[bool, typing.Any] = False,
    texture_space: typing.Union[bool, typing.Any] = False,
    remove_on_cancel: typing.Union[bool, typing.Any] = False,
    use_duplicated_keyframes: typing.Union[bool, typing.Any] = False,
    center_override: typing.Any = (0.0, 0.0, 0.0),
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
    use_automerge_and_split: typing.Union[bool, typing.Any] = False,
):
    """Transform selected items by mode type

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Mode
    :type mode: typing.Union[str, int]
    :param value: Values
    :type value: typing.Any
    :param orient_axis: Axis
    :type orient_axis: typing.Union[str, int]
    :param orient_type: Orientation, Transformation orientation
    :type orient_type: typing.Union[str, int]
    :param orient_matrix: Matrix
    :type orient_matrix: typing.Any
    :param orient_matrix_type: Matrix Orientation
    :type orient_matrix_type: typing.Union[str, int]
    :param constraint_axis: Constraint Axis
    :type constraint_axis: typing.Union[typing.List[bool], typing.Any]
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param use_proportional_edit: Proportional Editing
    :type use_proportional_edit: typing.Union[bool, typing.Any]
    :param proportional_edit_falloff: Proportional Falloff, Falloff type for proportional editing mode
    :type proportional_edit_falloff: typing.Union[str, int]
    :param proportional_size: Proportional Size
    :type proportional_size: typing.Any
    :param use_proportional_connected: Connected
    :type use_proportional_connected: typing.Union[bool, typing.Any]
    :param use_proportional_projected: Projected (2D)
    :type use_proportional_projected: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param snap_elements: Snap to Elements
    :type snap_elements: typing.Any
    :param use_snap_project: Project Individual Elements
    :type use_snap_project: typing.Union[bool, typing.Any]
    :param snap_target: Snap Base, Point on source that will snap to target
    :type snap_target: typing.Union[str, int]
    :param use_snap_self: Target: Include Active
    :type use_snap_self: typing.Union[bool, typing.Any]
    :param use_snap_edit: Target: Include Edit
    :type use_snap_edit: typing.Union[bool, typing.Any]
    :param use_snap_nonedit: Target: Include Non-Edited
    :type use_snap_nonedit: typing.Union[bool, typing.Any]
    :param use_snap_selectable: Target: Exclude Non-Selectable
    :type use_snap_selectable: typing.Union[bool, typing.Any]
    :param snap_point: Point
    :type snap_point: typing.Any
    :param snap_align: Align with Point Normal
    :type snap_align: typing.Union[bool, typing.Any]
    :param snap_normal: Normal
    :type snap_normal: typing.Any
    :param gpencil_strokes: Edit Grease Pencil, Edit selected Grease Pencil strokes
    :type gpencil_strokes: typing.Union[bool, typing.Any]
    :param texture_space: Edit Texture Space, Edit object data texture space
    :type texture_space: typing.Union[bool, typing.Any]
    :param remove_on_cancel: Remove on Cancel, Remove elements on cancel
    :type remove_on_cancel: typing.Union[bool, typing.Any]
    :param use_duplicated_keyframes: Duplicated Keyframes, Transform duplicated keyframes
    :type use_duplicated_keyframes: typing.Union[bool, typing.Any]
    :param center_override: Center Override, Force using this center value (when set)
    :type center_override: typing.Any
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    :param use_automerge_and_split: Auto Merge & Split, Forces the use of Auto Merge and Split
    :type use_automerge_and_split: typing.Union[bool, typing.Any]
    """

    ...

def translate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = (0.0, 0.0, 0.0),
    orient_type: typing.Union[str, int] = "GLOBAL",
    orient_matrix: typing.Any = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
    orient_matrix_type: typing.Union[str, int] = "GLOBAL",
    constraint_axis: typing.Union[typing.List[bool], typing.Any] = (
        False,
        False,
        False,
    ),
    mirror: typing.Union[bool, typing.Any] = False,
    use_proportional_edit: typing.Union[bool, typing.Any] = False,
    proportional_edit_falloff: typing.Union[str, int] = "SMOOTH",
    proportional_size: typing.Any = 1.0,
    use_proportional_connected: typing.Union[bool, typing.Any] = False,
    use_proportional_projected: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    snap_elements: typing.Any = {'"INCREMENT"'},
    use_snap_project: typing.Union[bool, typing.Any] = False,
    snap_target: typing.Union[str, int] = "CLOSEST",
    use_snap_self: typing.Union[bool, typing.Any] = True,
    use_snap_edit: typing.Union[bool, typing.Any] = True,
    use_snap_nonedit: typing.Union[bool, typing.Any] = True,
    use_snap_selectable: typing.Union[bool, typing.Any] = False,
    snap_point: typing.Any = (0.0, 0.0, 0.0),
    snap_align: typing.Union[bool, typing.Any] = False,
    snap_normal: typing.Any = (0.0, 0.0, 0.0),
    gpencil_strokes: typing.Union[bool, typing.Any] = False,
    cursor_transform: typing.Union[bool, typing.Any] = False,
    texture_space: typing.Union[bool, typing.Any] = False,
    remove_on_cancel: typing.Union[bool, typing.Any] = False,
    use_duplicated_keyframes: typing.Union[bool, typing.Any] = False,
    view2d_edge_pan: typing.Union[bool, typing.Any] = False,
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
    use_automerge_and_split: typing.Union[bool, typing.Any] = False,
):
    """Move selected items

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Move
    :type value: typing.Any
    :param orient_type: Orientation, Transformation orientation
    :type orient_type: typing.Union[str, int]
    :param orient_matrix: Matrix
    :type orient_matrix: typing.Any
    :param orient_matrix_type: Matrix Orientation
    :type orient_matrix_type: typing.Union[str, int]
    :param constraint_axis: Constraint Axis
    :type constraint_axis: typing.Union[typing.List[bool], typing.Any]
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param use_proportional_edit: Proportional Editing
    :type use_proportional_edit: typing.Union[bool, typing.Any]
    :param proportional_edit_falloff: Proportional Falloff, Falloff type for proportional editing mode
    :type proportional_edit_falloff: typing.Union[str, int]
    :param proportional_size: Proportional Size
    :type proportional_size: typing.Any
    :param use_proportional_connected: Connected
    :type use_proportional_connected: typing.Union[bool, typing.Any]
    :param use_proportional_projected: Projected (2D)
    :type use_proportional_projected: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param snap_elements: Snap to Elements
    :type snap_elements: typing.Any
    :param use_snap_project: Project Individual Elements
    :type use_snap_project: typing.Union[bool, typing.Any]
    :param snap_target: Snap Base, Point on source that will snap to target
    :type snap_target: typing.Union[str, int]
    :param use_snap_self: Target: Include Active
    :type use_snap_self: typing.Union[bool, typing.Any]
    :param use_snap_edit: Target: Include Edit
    :type use_snap_edit: typing.Union[bool, typing.Any]
    :param use_snap_nonedit: Target: Include Non-Edited
    :type use_snap_nonedit: typing.Union[bool, typing.Any]
    :param use_snap_selectable: Target: Exclude Non-Selectable
    :type use_snap_selectable: typing.Union[bool, typing.Any]
    :param snap_point: Point
    :type snap_point: typing.Any
    :param snap_align: Align with Point Normal
    :type snap_align: typing.Union[bool, typing.Any]
    :param snap_normal: Normal
    :type snap_normal: typing.Any
    :param gpencil_strokes: Edit Grease Pencil, Edit selected Grease Pencil strokes
    :type gpencil_strokes: typing.Union[bool, typing.Any]
    :param cursor_transform: Transform Cursor
    :type cursor_transform: typing.Union[bool, typing.Any]
    :param texture_space: Edit Texture Space, Edit object data texture space
    :type texture_space: typing.Union[bool, typing.Any]
    :param remove_on_cancel: Remove on Cancel, Remove elements on cancel
    :type remove_on_cancel: typing.Union[bool, typing.Any]
    :param use_duplicated_keyframes: Duplicated Keyframes, Transform duplicated keyframes
    :type use_duplicated_keyframes: typing.Union[bool, typing.Any]
    :param view2d_edge_pan: Edge Pan, Enable edge panning in 2D view
    :type view2d_edge_pan: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    :param use_automerge_and_split: Auto Merge & Split, Forces the use of Auto Merge and Split
    :type use_automerge_and_split: typing.Union[bool, typing.Any]
    """

    ...

def vert_crease(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    snap: typing.Union[bool, typing.Any] = False,
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Change the crease of vertices

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Factor
    :type value: typing.Any
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def vert_slide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    value: typing.Any = 0.0,
    use_even: typing.Union[bool, typing.Any] = False,
    flipped: typing.Union[bool, typing.Any] = False,
    use_clamp: typing.Union[bool, typing.Any] = True,
    mirror: typing.Union[bool, typing.Any] = False,
    snap: typing.Union[bool, typing.Any] = False,
    snap_elements: typing.Any = {'"INCREMENT"'},
    use_snap_project: typing.Union[bool, typing.Any] = False,
    snap_target: typing.Union[str, int] = "CLOSEST",
    use_snap_self: typing.Union[bool, typing.Any] = True,
    use_snap_edit: typing.Union[bool, typing.Any] = True,
    use_snap_nonedit: typing.Union[bool, typing.Any] = True,
    use_snap_selectable: typing.Union[bool, typing.Any] = False,
    snap_point: typing.Any = (0.0, 0.0, 0.0),
    correct_uv: typing.Union[bool, typing.Any] = True,
    release_confirm: typing.Union[bool, typing.Any] = False,
    use_accurate: typing.Union[bool, typing.Any] = False,
):
    """Slide a vertex along a mesh

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param value: Factor
    :type value: typing.Any
    :param use_even: Even, Make the edge loop match the shape of the adjacent edge loop
    :type use_even: typing.Union[bool, typing.Any]
    :param flipped: Flipped, When Even mode is active, flips between the two adjacent edge loops
    :type flipped: typing.Union[bool, typing.Any]
    :param use_clamp: Clamp, Clamp within the edge extents
    :type use_clamp: typing.Union[bool, typing.Any]
    :param mirror: Mirror Editing
    :type mirror: typing.Union[bool, typing.Any]
    :param snap: Use Snapping Options
    :type snap: typing.Union[bool, typing.Any]
    :param snap_elements: Snap to Elements
    :type snap_elements: typing.Any
    :param use_snap_project: Project Individual Elements
    :type use_snap_project: typing.Union[bool, typing.Any]
    :param snap_target: Snap Base, Point on source that will snap to target
    :type snap_target: typing.Union[str, int]
    :param use_snap_self: Target: Include Active
    :type use_snap_self: typing.Union[bool, typing.Any]
    :param use_snap_edit: Target: Include Edit
    :type use_snap_edit: typing.Union[bool, typing.Any]
    :param use_snap_nonedit: Target: Include Non-Edited
    :type use_snap_nonedit: typing.Union[bool, typing.Any]
    :param use_snap_selectable: Target: Exclude Non-Selectable
    :type use_snap_selectable: typing.Union[bool, typing.Any]
    :param snap_point: Point
    :type snap_point: typing.Any
    :param correct_uv: Correct UVs, Correct UV coordinates when transforming
    :type correct_uv: typing.Union[bool, typing.Any]
    :param release_confirm: Confirm on Release, Always confirm operation when releasing button
    :type release_confirm: typing.Union[bool, typing.Any]
    :param use_accurate: Accurate, Use accurate transformation
    :type use_accurate: typing.Union[bool, typing.Any]
    """

    ...

def vertex_random(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    offset: typing.Any = 0.0,
    uniform: typing.Any = 0.0,
    normal: typing.Any = 0.0,
    seed: typing.Any = 0,
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Randomize vertices

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param offset: Amount, Distance to offset
    :type offset: typing.Any
    :param uniform: Uniform, Increase for uniform offset distance
    :type uniform: typing.Any
    :param normal: Normal, Align offset direction to normals
    :type normal: typing.Any
    :param seed: Random Seed, Seed for the random number generator
    :type seed: typing.Any
    :param wait_for_input: Wait for Input
    :type wait_for_input: typing.Union[bool, typing.Any]
    """

    ...

def vertex_warp(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    warp_angle: typing.Any = 6.28319,
    offset_angle: typing.Any = 0.0,
    min: typing.Any = -1.0,
    max: typing.Any = 1.0,
    viewmat: typing.Any = (
        (0.0, 0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0, 0.0),
    ),
    center: typing.Any = (0.0, 0.0, 0.0),
):
    """Warp vertices around the cursor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param warp_angle: Warp Angle, Amount to warp about the cursor
    :type warp_angle: typing.Any
    :param offset_angle: Offset Angle, Angle to use as the basis for warping
    :type offset_angle: typing.Any
    :param min: Min
    :type min: typing.Any
    :param max: Max
    :type max: typing.Any
    :param viewmat: Matrix
    :type viewmat: typing.Any
    :param center: Center
    :type center: typing.Any
    """

    ...
