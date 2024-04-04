import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def change_effect_input(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    swap: typing.Any = "A_B",
):
    """Undocumented, consider contributing.

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param swap: Swap, The effect inputs to swap
    :type swap: typing.Any
    """

    ...

def change_effect_type(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "CROSS",
):
    """Undocumented, consider contributing.

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Type, Sequencer effect type

    CROSS
    Crossfade -- Crossfade effect strip type.

    ADD
    Add -- Add effect strip type.

    SUBTRACT
    Subtract -- Subtract effect strip type.

    ALPHA_OVER
    Alpha Over -- Alpha Over effect strip type.

    ALPHA_UNDER
    Alpha Under -- Alpha Under effect strip type.

    GAMMA_CROSS
    Gamma Cross -- Gamma Cross effect strip type.

    MULTIPLY
    Multiply -- Multiply effect strip type.

    OVER_DROP
    Alpha Over Drop -- Alpha Over Drop effect strip type.

    WIPE
    Wipe -- Wipe effect strip type.

    GLOW
    Glow -- Glow effect strip type.

    TRANSFORM
    Transform -- Transform effect strip type.

    COLOR
    Color -- Color effect strip type.

    SPEED
    Speed -- Color effect strip type.

    MULTICAM
    Multicam Selector.

    ADJUSTMENT
    Adjustment Layer.

    GAUSSIAN_BLUR
    Gaussian Blur.

    TEXT
    Text.

    COLORMIX
    Color Mix.
        :type type: typing.Any
    """

    ...

def change_path(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    filepath: typing.Union[str, typing.Any] = "",
    directory: typing.Union[str, typing.Any] = "",
    files: bpy.types.bpy_prop_collection[bpy.types.OperatorFileListElement] = None,
    hide_props_region: typing.Union[bool, typing.Any] = True,
    check_existing: typing.Union[bool, typing.Any] = False,
    filter_blender: typing.Union[bool, typing.Any] = False,
    filter_backup: typing.Union[bool, typing.Any] = False,
    filter_image: typing.Union[bool, typing.Any] = False,
    filter_movie: typing.Union[bool, typing.Any] = False,
    filter_python: typing.Union[bool, typing.Any] = False,
    filter_font: typing.Union[bool, typing.Any] = False,
    filter_sound: typing.Union[bool, typing.Any] = False,
    filter_text: typing.Union[bool, typing.Any] = False,
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
    relative_path: typing.Union[bool, typing.Any] = True,
    display_type: typing.Any = "DEFAULT",
    sort_method: typing.Union[str, int, typing.Any] = "",
    use_placeholders: typing.Union[bool, typing.Any] = False,
):
    """Undocumented, consider contributing.

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param filepath: File Path, Path to file
        :type filepath: typing.Union[str, typing.Any]
        :param directory: Directory, Directory of the file
        :type directory: typing.Union[str, typing.Any]
        :param files: Files
        :type files: bpy.types.bpy_prop_collection[bpy.types.OperatorFileListElement]
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
        :param relative_path: Relative Path, Select the file relative to the blend file
        :type relative_path: typing.Union[bool, typing.Any]
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
        :param use_placeholders: Use Placeholders, Use placeholders for missing frames of the strip
        :type use_placeholders: typing.Union[bool, typing.Any]
    """

    ...

def change_scene(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    scene: typing.Union[str, int, typing.Any] = "",
):
    """Change Scene assigned to Strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param scene: Scene
    :type scene: typing.Union[str, int, typing.Any]
    """

    ...

def copy(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Copy the selected strips to the internal clipboard

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def crossfade_sounds(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Do cross-fading volume animation of two selected sound strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def cursor_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    location: typing.Any = (0.0, 0.0),
):
    """Set 2D cursor location

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param location: Location, Cursor location in normalized preview coordinates
    :type location: typing.Any
    """

    ...

def deinterlace_selected_movies(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Deinterlace all selected movie sources

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def delete(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    delete_data: typing.Union[bool, typing.Any] = False,
    use_retiming_mode: typing.Union[bool, typing.Any] = False,
):
    """Delete selected strips from the sequencer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param delete_data: Delete Data, After removing the Strip, delete the associated data also
    :type delete_data: typing.Union[bool, typing.Any]
    :param use_retiming_mode: Use Retiming Data, Operate on retiming data instead of strips
    :type use_retiming_mode: typing.Union[bool, typing.Any]
    """

    ...

def duplicate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Duplicate the selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def duplicate_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    SEQUENCER_OT_duplicate: typing.Any = None,
    TRANSFORM_OT_seq_slide: typing.Any = None,
):
    """Duplicate selected strips and move them

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param SEQUENCER_OT_duplicate: Duplicate Strips, Duplicate the selected strips
    :type SEQUENCER_OT_duplicate: typing.Any
    :param TRANSFORM_OT_seq_slide: Sequence Slide, Slide a sequence strip in time
    :type TRANSFORM_OT_seq_slide: typing.Any
    """

    ...

def effect_strip_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "CROSS",
    frame_start: typing.Any = 0,
    frame_end: typing.Any = 0,
    channel: typing.Any = 1,
    replace_sel: typing.Union[bool, typing.Any] = True,
    overlap: typing.Union[bool, typing.Any] = False,
    overlap_shuffle_override: typing.Union[bool, typing.Any] = False,
    color: typing.Any = (0.0, 0.0, 0.0),
):
    """Add an effect to the sequencer, most are applied on top of existing strips

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Type, Sequencer effect type

    CROSS
    Crossfade -- Crossfade effect strip type.

    ADD
    Add -- Add effect strip type.

    SUBTRACT
    Subtract -- Subtract effect strip type.

    ALPHA_OVER
    Alpha Over -- Alpha Over effect strip type.

    ALPHA_UNDER
    Alpha Under -- Alpha Under effect strip type.

    GAMMA_CROSS
    Gamma Cross -- Gamma Cross effect strip type.

    MULTIPLY
    Multiply -- Multiply effect strip type.

    OVER_DROP
    Alpha Over Drop -- Alpha Over Drop effect strip type.

    WIPE
    Wipe -- Wipe effect strip type.

    GLOW
    Glow -- Glow effect strip type.

    TRANSFORM
    Transform -- Transform effect strip type.

    COLOR
    Color -- Color effect strip type.

    SPEED
    Speed -- Color effect strip type.

    MULTICAM
    Multicam Selector.

    ADJUSTMENT
    Adjustment Layer.

    GAUSSIAN_BLUR
    Gaussian Blur.

    TEXT
    Text.

    COLORMIX
    Color Mix.
        :type type: typing.Any
        :param frame_start: Start Frame, Start frame of the sequence strip
        :type frame_start: typing.Any
        :param frame_end: End Frame, End frame for the color strip
        :type frame_end: typing.Any
        :param channel: Channel, Channel to place this strip into
        :type channel: typing.Any
        :param replace_sel: Replace Selection, Replace the current selection
        :type replace_sel: typing.Union[bool, typing.Any]
        :param overlap: Allow Overlap, Don't correct overlap on new sequence strips
        :type overlap: typing.Union[bool, typing.Any]
        :param overlap_shuffle_override: Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips
        :type overlap_shuffle_override: typing.Union[bool, typing.Any]
        :param color: Color, Initialize the strip with this color
        :type color: typing.Any
    """

    ...

def enable_proxies(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    proxy_25: typing.Union[bool, typing.Any] = False,
    proxy_50: typing.Union[bool, typing.Any] = False,
    proxy_75: typing.Union[bool, typing.Any] = False,
    proxy_100: typing.Union[bool, typing.Any] = False,
    overwrite: typing.Union[bool, typing.Any] = False,
):
    """Enable selected proxies on all selected Movie and Image strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param proxy_25: 25%
    :type proxy_25: typing.Union[bool, typing.Any]
    :param proxy_50: 50%
    :type proxy_50: typing.Union[bool, typing.Any]
    :param proxy_75: 75%
    :type proxy_75: typing.Union[bool, typing.Any]
    :param proxy_100: 100%
    :type proxy_100: typing.Union[bool, typing.Any]
    :param overwrite: Overwrite
    :type overwrite: typing.Union[bool, typing.Any]
    """

    ...

def export_subtitles(
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
    filter_python: typing.Union[bool, typing.Any] = False,
    filter_font: typing.Union[bool, typing.Any] = False,
    filter_sound: typing.Union[bool, typing.Any] = False,
    filter_text: typing.Union[bool, typing.Any] = False,
    filter_archive: typing.Union[bool, typing.Any] = False,
    filter_btx: typing.Union[bool, typing.Any] = False,
    filter_collada: typing.Union[bool, typing.Any] = False,
    filter_alembic: typing.Union[bool, typing.Any] = False,
    filter_usd: typing.Union[bool, typing.Any] = False,
    filter_obj: typing.Union[bool, typing.Any] = False,
    filter_volume: typing.Union[bool, typing.Any] = False,
    filter_folder: typing.Union[bool, typing.Any] = True,
    filter_blenlib: typing.Union[bool, typing.Any] = False,
    filemode: typing.Any = 8,
    display_type: typing.Any = "DEFAULT",
    sort_method: typing.Union[str, int, typing.Any] = "",
):
    """Export .srt file containing text strips

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

def fades_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    duration_seconds: typing.Any = 1.0,
    type: typing.Any = "IN_OUT",
):
    """Adds or updates a fade animation for either visual or audio strips

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param duration_seconds: Fade Duration, Duration of the fade in seconds
        :type duration_seconds: typing.Any
        :param type: Fade Type, Fade in, out, both in and out, to, or from the current frame. Default is both in and out

    IN_OUT
    Fade In and Out -- Fade selected strips in and out.

    IN
    Fade In -- Fade in selected strips.

    OUT
    Fade Out -- Fade out selected strips.

    CURSOR_FROM
    From Current Frame -- Fade from the time cursor to the end of overlapping sequences.

    CURSOR_TO
    To Current Frame -- Fade from the start of sequences under the time cursor to the current frame.
        :type type: typing.Any
    """

    ...

def fades_clear(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Removes fade animation from selected sequences

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def gap_insert(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    frames: typing.Any = 10,
):
    """Insert gap at current frame to first strips at the right, independent of selection or locked state of strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param frames: Frames, Frames to insert after current strip
    :type frames: typing.Any
    """

    ...

def gap_remove(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    all: typing.Union[bool, typing.Any] = False,
):
    """Remove gap at current frame to first strip at the right, independent of selection or locked state of strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param all: All Gaps, Do all gaps to right of current frame
    :type all: typing.Union[bool, typing.Any]
    """

    ...

def image_strip_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    directory: typing.Union[str, typing.Any] = "",
    files: bpy.types.bpy_prop_collection[bpy.types.OperatorFileListElement] = None,
    check_existing: typing.Union[bool, typing.Any] = False,
    filter_blender: typing.Union[bool, typing.Any] = False,
    filter_backup: typing.Union[bool, typing.Any] = False,
    filter_image: typing.Union[bool, typing.Any] = True,
    filter_movie: typing.Union[bool, typing.Any] = False,
    filter_python: typing.Union[bool, typing.Any] = False,
    filter_font: typing.Union[bool, typing.Any] = False,
    filter_sound: typing.Union[bool, typing.Any] = False,
    filter_text: typing.Union[bool, typing.Any] = False,
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
    relative_path: typing.Union[bool, typing.Any] = True,
    show_multiview: typing.Union[bool, typing.Any] = False,
    use_multiview: typing.Union[bool, typing.Any] = False,
    display_type: typing.Any = "DEFAULT",
    sort_method: typing.Any = "",
    frame_start: typing.Any = 0,
    frame_end: typing.Any = 0,
    channel: typing.Any = 1,
    replace_sel: typing.Union[bool, typing.Any] = True,
    overlap: typing.Union[bool, typing.Any] = False,
    overlap_shuffle_override: typing.Union[bool, typing.Any] = False,
    fit_method: typing.Any = "FIT",
    set_view_transform: typing.Union[bool, typing.Any] = True,
    use_placeholders: typing.Union[bool, typing.Any] = False,
):
    """Add an image or image sequence to the sequencer

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param directory: Directory, Directory of the file
        :type directory: typing.Union[str, typing.Any]
        :param files: Files
        :type files: bpy.types.bpy_prop_collection[bpy.types.OperatorFileListElement]
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
        :param relative_path: Relative Path, Select the file relative to the blend file
        :type relative_path: typing.Union[bool, typing.Any]
        :param show_multiview: Enable Multi-View
        :type show_multiview: typing.Union[bool, typing.Any]
        :param use_multiview: Use Multi-View
        :type use_multiview: typing.Union[bool, typing.Any]
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
        :param frame_start: Start Frame, Start frame of the sequence strip
        :type frame_start: typing.Any
        :param frame_end: End Frame, End frame for the color strip
        :type frame_end: typing.Any
        :param channel: Channel, Channel to place this strip into
        :type channel: typing.Any
        :param replace_sel: Replace Selection, Replace the current selection
        :type replace_sel: typing.Union[bool, typing.Any]
        :param overlap: Allow Overlap, Don't correct overlap on new sequence strips
        :type overlap: typing.Union[bool, typing.Any]
        :param overlap_shuffle_override: Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips
        :type overlap_shuffle_override: typing.Union[bool, typing.Any]
        :param fit_method: Fit Method, Scale fit method

    FIT
    Scale to Fit -- Scale image to fit within the canvas.

    FILL
    Scale to Fill -- Scale image to completely fill the canvas.

    STRETCH
    Stretch to Fill -- Stretch image to fill the canvas.

    ORIGINAL
    Use Original Size -- Keep image at its original size.
        :type fit_method: typing.Any
        :param set_view_transform: Set View Transform, Set appropriate view transform based on media color space
        :type set_view_transform: typing.Union[bool, typing.Any]
        :param use_placeholders: Use Placeholders, Use placeholders for missing frames of the strip
        :type use_placeholders: typing.Union[bool, typing.Any]
    """

    ...

def images_separate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    length: typing.Any = 1,
):
    """On image sequence strips, it returns a strip for each image

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param length: Length, Length of each frame
    :type length: typing.Any
    """

    ...

def lock(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Lock strips so they can't be transformed

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def mask_strip_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    frame_start: typing.Any = 0,
    channel: typing.Any = 1,
    replace_sel: typing.Union[bool, typing.Any] = True,
    overlap: typing.Union[bool, typing.Any] = False,
    overlap_shuffle_override: typing.Union[bool, typing.Any] = False,
    mask: typing.Union[str, int, typing.Any] = "",
):
    """Add a mask strip to the sequencer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param frame_start: Start Frame, Start frame of the sequence strip
    :type frame_start: typing.Any
    :param channel: Channel, Channel to place this strip into
    :type channel: typing.Any
    :param replace_sel: Replace Selection, Replace the current selection
    :type replace_sel: typing.Union[bool, typing.Any]
    :param overlap: Allow Overlap, Don't correct overlap on new sequence strips
    :type overlap: typing.Union[bool, typing.Any]
    :param overlap_shuffle_override: Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips
    :type overlap_shuffle_override: typing.Union[bool, typing.Any]
    :param mask: Mask
    :type mask: typing.Union[str, int, typing.Any]
    """

    ...

def meta_make(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Group selected strips into a meta-strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def meta_separate(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Put the contents of a meta-strip back in the sequencer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def meta_toggle(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Toggle a meta-strip (to edit enclosed strips)

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def movie_strip_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    filepath: typing.Union[str, typing.Any] = "",
    directory: typing.Union[str, typing.Any] = "",
    files: bpy.types.bpy_prop_collection[bpy.types.OperatorFileListElement] = None,
    check_existing: typing.Union[bool, typing.Any] = False,
    filter_blender: typing.Union[bool, typing.Any] = False,
    filter_backup: typing.Union[bool, typing.Any] = False,
    filter_image: typing.Union[bool, typing.Any] = False,
    filter_movie: typing.Union[bool, typing.Any] = True,
    filter_python: typing.Union[bool, typing.Any] = False,
    filter_font: typing.Union[bool, typing.Any] = False,
    filter_sound: typing.Union[bool, typing.Any] = False,
    filter_text: typing.Union[bool, typing.Any] = False,
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
    relative_path: typing.Union[bool, typing.Any] = True,
    show_multiview: typing.Union[bool, typing.Any] = False,
    use_multiview: typing.Union[bool, typing.Any] = False,
    display_type: typing.Any = "DEFAULT",
    sort_method: typing.Any = "",
    frame_start: typing.Any = 0,
    channel: typing.Any = 1,
    replace_sel: typing.Union[bool, typing.Any] = True,
    overlap: typing.Union[bool, typing.Any] = False,
    overlap_shuffle_override: typing.Union[bool, typing.Any] = False,
    fit_method: typing.Any = "FIT",
    set_view_transform: typing.Union[bool, typing.Any] = True,
    adjust_playback_rate: typing.Union[bool, typing.Any] = True,
    sound: typing.Union[bool, typing.Any] = True,
    use_framerate: typing.Union[bool, typing.Any] = True,
):
    """Add a movie strip to the sequencer

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param filepath: File Path, Path to file
        :type filepath: typing.Union[str, typing.Any]
        :param directory: Directory, Directory of the file
        :type directory: typing.Union[str, typing.Any]
        :param files: Files
        :type files: bpy.types.bpy_prop_collection[bpy.types.OperatorFileListElement]
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
        :param relative_path: Relative Path, Select the file relative to the blend file
        :type relative_path: typing.Union[bool, typing.Any]
        :param show_multiview: Enable Multi-View
        :type show_multiview: typing.Union[bool, typing.Any]
        :param use_multiview: Use Multi-View
        :type use_multiview: typing.Union[bool, typing.Any]
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
        :param frame_start: Start Frame, Start frame of the sequence strip
        :type frame_start: typing.Any
        :param channel: Channel, Channel to place this strip into
        :type channel: typing.Any
        :param replace_sel: Replace Selection, Replace the current selection
        :type replace_sel: typing.Union[bool, typing.Any]
        :param overlap: Allow Overlap, Don't correct overlap on new sequence strips
        :type overlap: typing.Union[bool, typing.Any]
        :param overlap_shuffle_override: Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips
        :type overlap_shuffle_override: typing.Union[bool, typing.Any]
        :param fit_method: Fit Method, Scale fit method

    FIT
    Scale to Fit -- Scale image to fit within the canvas.

    FILL
    Scale to Fill -- Scale image to completely fill the canvas.

    STRETCH
    Stretch to Fill -- Stretch image to fill the canvas.

    ORIGINAL
    Use Original Size -- Keep image at its original size.
        :type fit_method: typing.Any
        :param set_view_transform: Set View Transform, Set appropriate view transform based on media color space
        :type set_view_transform: typing.Union[bool, typing.Any]
        :param adjust_playback_rate: Adjust Playback Rate, Play at normal speed regardless of scene FPS
        :type adjust_playback_rate: typing.Union[bool, typing.Any]
        :param sound: Sound, Load sound with the movie
        :type sound: typing.Union[bool, typing.Any]
        :param use_framerate: Use Movie Framerate, Use framerate from the movie to keep sound and video in sync
        :type use_framerate: typing.Union[bool, typing.Any]
    """

    ...

def movieclip_strip_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    frame_start: typing.Any = 0,
    channel: typing.Any = 1,
    replace_sel: typing.Union[bool, typing.Any] = True,
    overlap: typing.Union[bool, typing.Any] = False,
    overlap_shuffle_override: typing.Union[bool, typing.Any] = False,
    clip: typing.Union[str, int, typing.Any] = "",
):
    """Add a movieclip strip to the sequencer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param frame_start: Start Frame, Start frame of the sequence strip
    :type frame_start: typing.Any
    :param channel: Channel, Channel to place this strip into
    :type channel: typing.Any
    :param replace_sel: Replace Selection, Replace the current selection
    :type replace_sel: typing.Union[bool, typing.Any]
    :param overlap: Allow Overlap, Don't correct overlap on new sequence strips
    :type overlap: typing.Union[bool, typing.Any]
    :param overlap_shuffle_override: Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips
    :type overlap_shuffle_override: typing.Union[bool, typing.Any]
    :param clip: Clip
    :type clip: typing.Union[str, int, typing.Any]
    """

    ...

def mute(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    unselected: typing.Union[bool, typing.Any] = False,
):
    """Mute (un)selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param unselected: Unselected, Mute unselected rather than selected strips
    :type unselected: typing.Union[bool, typing.Any]
    """

    ...

def offset_clear(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Clear strip offsets from the start and end frames

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def paste(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    keep_offset: typing.Union[bool, typing.Any] = False,
):
    """Paste strips from the internal clipboard

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param keep_offset: Keep Offset, Keep strip offset relative to the current frame when pasting
    :type keep_offset: typing.Union[bool, typing.Any]
    """

    ...

def reassign_inputs(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Reassign the inputs for the effect strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def rebuild_proxy(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Rebuild all selected proxies and timecode indices using the job system

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def refresh_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Refresh the sequencer editor

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def reload(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    adjust_length: typing.Union[bool, typing.Any] = False,
):
    """Reload strips in the sequencer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param adjust_length: Adjust Length, Adjust length of strips to their data length
    :type adjust_length: typing.Union[bool, typing.Any]
    """

    ...

def rename_channel(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Undocumented, consider contributing.

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def rendersize(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Set render size and aspect from active sequence

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def retiming_add_freeze_frame_slide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    SEQUENCER_OT_retiming_freeze_frame_add: typing.Any = None,
    TRANSFORM_OT_seq_slide: typing.Any = None,
):
    """Add freeze frame and move it

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param SEQUENCER_OT_retiming_freeze_frame_add: Add Freeze Frame, Add freeze frame
    :type SEQUENCER_OT_retiming_freeze_frame_add: typing.Any
    :param TRANSFORM_OT_seq_slide: Sequence Slide, Slide a sequence strip in time
    :type TRANSFORM_OT_seq_slide: typing.Any
    """

    ...

def retiming_add_transition_slide(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    SEQUENCER_OT_retiming_transition_add: typing.Any = None,
    TRANSFORM_OT_seq_slide: typing.Any = None,
):
    """Add smooth transition between 2 retimed segments and change its duration

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param SEQUENCER_OT_retiming_transition_add: Add Speed Transition, Add smooth transition between 2 retimed segments
    :type SEQUENCER_OT_retiming_transition_add: typing.Any
    :param TRANSFORM_OT_seq_slide: Sequence Slide, Slide a sequence strip in time
    :type TRANSFORM_OT_seq_slide: typing.Any
    """

    ...

def retiming_freeze_frame_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    duration: typing.Any = 0,
):
    """Add freeze frame

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param duration: Duration, Duration of freeze frame segment
    :type duration: typing.Any
    """

    ...

def retiming_key_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    timeline_frame: typing.Any = 0,
):
    """Add retiming Key

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param timeline_frame: Timeline Frame, Frame where key will be added
    :type timeline_frame: typing.Any
    """

    ...

def retiming_reset(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Reset strip retiming

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def retiming_segment_speed_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    speed: typing.Any = 100.0,
    keep_retiming: typing.Union[bool, typing.Any] = True,
):
    """Set speed of retimed segment

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param speed: Speed, New speed of retimed segment
    :type speed: typing.Any
    :param keep_retiming: Preserve Current Retiming, Keep speed of other segments unchanged, change strip length instead
    :type keep_retiming: typing.Union[bool, typing.Any]
    """

    ...

def retiming_show(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Show retiming keys in selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def retiming_transition_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    duration: typing.Any = 0,
):
    """Add smooth transition between 2 retimed segments

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param duration: Duration, Duration of freeze frame segment
    :type duration: typing.Any
    """

    ...

def sample(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    size: typing.Any = 1,
):
    """Use mouse to sample color in current frame

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param size: Sample Size
    :type size: typing.Any
    """

    ...

def scene_frame_range_update(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Update frame range of scene strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def scene_strip_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    frame_start: typing.Any = 0,
    channel: typing.Any = 1,
    replace_sel: typing.Union[bool, typing.Any] = True,
    overlap: typing.Union[bool, typing.Any] = False,
    overlap_shuffle_override: typing.Union[bool, typing.Any] = False,
    scene: typing.Union[str, int, typing.Any] = "",
):
    """Add a strip to the sequencer using a Blender scene as a source

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param frame_start: Start Frame, Start frame of the sequence strip
    :type frame_start: typing.Any
    :param channel: Channel, Channel to place this strip into
    :type channel: typing.Any
    :param replace_sel: Replace Selection, Replace the current selection
    :type replace_sel: typing.Union[bool, typing.Any]
    :param overlap: Allow Overlap, Don't correct overlap on new sequence strips
    :type overlap: typing.Union[bool, typing.Any]
    :param overlap_shuffle_override: Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips
    :type overlap_shuffle_override: typing.Union[bool, typing.Any]
    :param scene: Scene
    :type scene: typing.Union[str, int, typing.Any]
    """

    ...

def scene_strip_add_new(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    frame_start: typing.Any = 0,
    channel: typing.Any = 1,
    replace_sel: typing.Union[bool, typing.Any] = True,
    overlap: typing.Union[bool, typing.Any] = False,
    overlap_shuffle_override: typing.Union[bool, typing.Any] = False,
    type: typing.Any = "NEW",
):
    """Create a new Strip and assign a new Scene as source

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param frame_start: Start Frame, Start frame of the sequence strip
        :type frame_start: typing.Any
        :param channel: Channel, Channel to place this strip into
        :type channel: typing.Any
        :param replace_sel: Replace Selection, Replace the current selection
        :type replace_sel: typing.Union[bool, typing.Any]
        :param overlap: Allow Overlap, Don't correct overlap on new sequence strips
        :type overlap: typing.Union[bool, typing.Any]
        :param overlap_shuffle_override: Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips
        :type overlap_shuffle_override: typing.Union[bool, typing.Any]
        :param type: Type

    NEW
    New -- Add new Strip with a new empty Scene with default settings.

    EMPTY
    Copy Settings -- Add a new Strip, with an empty scene, and copy settings from the current scene.

    LINK_COPY
    Linked Copy -- Add a Strip and link in the collections from the current scene (shallow copy).

    FULL_COPY
    Full Copy -- Add a Strip and make a full copy of the current scene.
        :type type: typing.Any
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
    deselect: typing.Union[bool, typing.Any] = False,
    toggle: typing.Union[bool, typing.Any] = False,
    deselect_all: typing.Union[bool, typing.Any] = False,
    select_passthrough: typing.Union[bool, typing.Any] = False,
    center: typing.Union[bool, typing.Any] = False,
    linked_handle: typing.Union[bool, typing.Any] = False,
    linked_time: typing.Union[bool, typing.Any] = False,
    side_of_frame: typing.Union[bool, typing.Any] = False,
):
    """Select a strip (last selected becomes the "active strip")

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param wait_to_deselect_others: Wait to Deselect Others
    :type wait_to_deselect_others: typing.Union[bool, typing.Any]
    :param mouse_x: Mouse X
    :type mouse_x: typing.Any
    :param mouse_y: Mouse Y
    :type mouse_y: typing.Any
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
    :param center: Center, Use the object center when selecting, in edit mode used to extend object selection
    :type center: typing.Union[bool, typing.Any]
    :param linked_handle: Linked Handle, Select handles next to the active strip
    :type linked_handle: typing.Union[bool, typing.Any]
    :param linked_time: Linked Time, Select other strips at the same time
    :type linked_time: typing.Union[bool, typing.Any]
    :param side_of_frame: Side of Frame, Select all strips on same side of the current frame as the mouse cursor
    :type side_of_frame: typing.Union[bool, typing.Any]
    """

    ...

def select_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    action: typing.Any = "TOGGLE",
):
    """Select or deselect all strips

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
    include_handles: typing.Union[bool, typing.Any] = False,
):
    """Select strips using box selection

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
        :param include_handles: Select Handles, Select the strips and their handles
        :type include_handles: typing.Union[bool, typing.Any]
    """

    ...

def select_grouped(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "TYPE",
    extend: typing.Union[bool, typing.Any] = False,
    use_active_channel: typing.Union[bool, typing.Any] = False,
):
    """Select all strips grouped by various properties

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Type

    TYPE
    Type -- Shared strip type.

    TYPE_BASIC
    Global Type -- All strips of same basic type (graphical or sound).

    TYPE_EFFECT
    Effect Type -- Shared strip effect type (if active strip is not an effect one, select all non-effect strips).

    DATA
    Data -- Shared data (scene, image, sound, etc.).

    EFFECT
    Effect -- Shared effects.

    EFFECT_LINK
    Effect/Linked -- Other strips affected by the active one (sharing some time, and below or effect-assigned).

    OVERLAP
    Overlap -- Overlapping time.
        :type type: typing.Any
        :param extend: Extend, Extend selection instead of deselecting everything first
        :type extend: typing.Union[bool, typing.Any]
        :param use_active_channel: Same Channel, Only consider strips on the same channel as the active one
        :type use_active_channel: typing.Union[bool, typing.Any]
    """

    ...

def select_handles(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    side: typing.Any = "BOTH",
):
    """Select gizmo handles on the sides of the selected strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param side: Side, The side of the handle that is selected
    :type side: typing.Any
    """

    ...

def select_less(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Shrink the current selection of adjacent selected strips

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
    """Select all strips adjacent to the current selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select_linked_pick(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    extend: typing.Union[bool, typing.Any] = False,
):
    """Select a chain of linked strips nearest to the mouse pointer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param extend: Extend, Extend the selection
    :type extend: typing.Union[bool, typing.Any]
    """

    ...

def select_more(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Select more strips adjacent to the current selection

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def select_side(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    side: typing.Any = "BOTH",
):
    """Select strips on the nominated side of the selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param side: Side, The side to which the selection is applied
    :type side: typing.Any
    """

    ...

def select_side_of_frame(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    extend: typing.Union[bool, typing.Any] = False,
    side: typing.Any = "LEFT",
):
    """Select strips relative to the current frame

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param extend: Extend, Extend the selection
        :type extend: typing.Union[bool, typing.Any]
        :param side: Side

    LEFT
    Left -- Select to the left of the current frame.

    RIGHT
    Right -- Select to the right of the current frame.

    CURRENT
    Current Frame -- Select intersecting with the current frame.
        :type side: typing.Any
    """

    ...

def set_range_to_strips(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    preview: typing.Union[bool, typing.Any] = False,
):
    """Set the frame range to the selected strips start and end

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param preview: Preview, Set the preview range instead
    :type preview: typing.Union[bool, typing.Any]
    """

    ...

def slip(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    offset: typing.Any = 0,
):
    """Slip the contents of selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param offset: Offset, Offset to the data of the strip
    :type offset: typing.Any
    """

    ...

def snap(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    frame: typing.Any = 0,
):
    """Frame where selected strips will be snapped

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param frame: Frame, Frame where selected strips will be snapped
    :type frame: typing.Any
    """

    ...

def sound_strip_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    filepath: typing.Union[str, typing.Any] = "",
    directory: typing.Union[str, typing.Any] = "",
    files: bpy.types.bpy_prop_collection[bpy.types.OperatorFileListElement] = None,
    check_existing: typing.Union[bool, typing.Any] = False,
    filter_blender: typing.Union[bool, typing.Any] = False,
    filter_backup: typing.Union[bool, typing.Any] = False,
    filter_image: typing.Union[bool, typing.Any] = False,
    filter_movie: typing.Union[bool, typing.Any] = False,
    filter_python: typing.Union[bool, typing.Any] = False,
    filter_font: typing.Union[bool, typing.Any] = False,
    filter_sound: typing.Union[bool, typing.Any] = True,
    filter_text: typing.Union[bool, typing.Any] = False,
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
    relative_path: typing.Union[bool, typing.Any] = True,
    display_type: typing.Any = "DEFAULT",
    sort_method: typing.Any = "",
    frame_start: typing.Any = 0,
    channel: typing.Any = 1,
    replace_sel: typing.Union[bool, typing.Any] = True,
    overlap: typing.Union[bool, typing.Any] = False,
    overlap_shuffle_override: typing.Union[bool, typing.Any] = False,
    cache: typing.Union[bool, typing.Any] = False,
    mono: typing.Union[bool, typing.Any] = False,
):
    """Add a sound strip to the sequencer

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param filepath: File Path, Path to file
        :type filepath: typing.Union[str, typing.Any]
        :param directory: Directory, Directory of the file
        :type directory: typing.Union[str, typing.Any]
        :param files: Files
        :type files: bpy.types.bpy_prop_collection[bpy.types.OperatorFileListElement]
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
        :param relative_path: Relative Path, Select the file relative to the blend file
        :type relative_path: typing.Union[bool, typing.Any]
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
        :param frame_start: Start Frame, Start frame of the sequence strip
        :type frame_start: typing.Any
        :param channel: Channel, Channel to place this strip into
        :type channel: typing.Any
        :param replace_sel: Replace Selection, Replace the current selection
        :type replace_sel: typing.Union[bool, typing.Any]
        :param overlap: Allow Overlap, Don't correct overlap on new sequence strips
        :type overlap: typing.Union[bool, typing.Any]
        :param overlap_shuffle_override: Override Overlap Shuffle Behavior, Use the overlap_mode tool settings to determine how to shuffle overlapping strips
        :type overlap_shuffle_override: typing.Union[bool, typing.Any]
        :param cache: Cache, Cache the sound in memory
        :type cache: typing.Union[bool, typing.Any]
        :param mono: Mono, Merge all the sound's channels into one
        :type mono: typing.Union[bool, typing.Any]
    """

    ...

def split(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    frame: typing.Any = 0,
    channel: typing.Any = 0,
    type: typing.Any = "SOFT",
    use_cursor_position: typing.Union[bool, typing.Any] = False,
    side: typing.Any = "MOUSE",
    ignore_selection: typing.Union[bool, typing.Any] = False,
):
    """Split the selected strips in two

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param frame: Frame, Frame where selected strips will be split
    :type frame: typing.Any
    :param channel: Channel, Channel in which strip will be cut
    :type channel: typing.Any
    :param type: Type, The type of split operation to perform on strips
    :type type: typing.Any
    :param use_cursor_position: Use Cursor Position, Split at position of the cursor instead of current frame
    :type use_cursor_position: typing.Union[bool, typing.Any]
    :param side: Side, The side that remains selected after splitting
    :type side: typing.Any
    :param ignore_selection: Ignore Selection, Make cut even if strip is not selected preserving selection state after cut
    :type ignore_selection: typing.Union[bool, typing.Any]
    """

    ...

def split_multicam(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    camera: typing.Any = 1,
):
    """Split multicam strip and select camera

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param camera: Camera
    :type camera: typing.Any
    """

    ...

def strip_color_tag_set(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    color: typing.Union[str, int] = "NONE",
):
    """Set a color tag for the selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param color: Color Tag
    :type color: typing.Union[str, int]
    """

    ...

def strip_jump(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    next: typing.Union[bool, typing.Any] = True,
    center: typing.Union[bool, typing.Any] = True,
):
    """Move frame to previous edit point

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param next: Next Strip
    :type next: typing.Union[bool, typing.Any]
    :param center: Use Strip Center
    :type center: typing.Union[bool, typing.Any]
    """

    ...

def strip_modifier_add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Union[str, int, typing.Any] = "",
):
    """Add a modifier to the strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param type: Type
    :type type: typing.Union[str, int, typing.Any]
    """

    ...

def strip_modifier_copy(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    type: typing.Any = "REPLACE",
):
    """Copy modifiers of the active strip to all selected strips

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param type: Type

    REPLACE
    Replace -- Replace modifiers in destination.

    APPEND
    Append -- Append active modifiers to selected strips.
        :type type: typing.Any
    """

    ...

def strip_modifier_equalizer_redefine(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    graphs: typing.Any = "SIMPLE",
    name: typing.Union[str, typing.Any] = "Name",
):
    """Redefine equalizer graphs

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param graphs: Graphs, Number of graphs

    SIMPLE
    Unique -- One unique graphical definition.

    DOUBLE
    Double -- Graphical definition in 2 sections.

    TRIPLE
    Triplet -- Graphical definition in 3 sections.
        :type graphs: typing.Any
        :param name: Name, Name of modifier to redefine
        :type name: typing.Union[str, typing.Any]
    """

    ...

def strip_modifier_move(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    name: typing.Union[str, typing.Any] = "Name",
    direction: typing.Any = "UP",
):
    """Move modifier up and down in the stack

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param name: Name, Name of modifier to remove
        :type name: typing.Union[str, typing.Any]
        :param direction: Type

    UP
    Up -- Move modifier up in the stack.

    DOWN
    Down -- Move modifier down in the stack.
        :type direction: typing.Any
    """

    ...

def strip_modifier_remove(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    name: typing.Union[str, typing.Any] = "Name",
):
    """Remove a modifier from the strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param name: Name, Name of modifier to remove
    :type name: typing.Union[str, typing.Any]
    """

    ...

def strip_transform_clear(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    property: typing.Any = "ALL",
):
    """Reset image transformation to default value

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param property: Property, Strip transform property to be reset

    POSITION
    Position -- Reset strip transform location.

    SCALE
    Scale -- Reset strip transform scale.

    ROTATION
    Rotation -- Reset strip transform rotation.

    ALL
    All -- Reset strip transform location, scale and rotation.
        :type property: typing.Any
    """

    ...

def strip_transform_fit(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    fit_method: typing.Any = "FIT",
):
    """Undocumented, consider contributing.

        :type override_context: typing.Union[dict, bpy.types.Context]
        :type execution_context: str
        :type undo: bool
        :param fit_method: Fit Method, Scale fit fit_method

    FIT
    Scale to Fit -- Scale image so fits in preview.

    FILL
    Scale to Fill -- Scale image so it fills preview completely.

    STRETCH
    Stretch to Fill -- Stretch image so it fills preview.
        :type fit_method: typing.Any
    """

    ...

def swap(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    side: typing.Any = "RIGHT",
):
    """Swap active strip with strip to the right or left

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param side: Side, Side of the strip to swap
    :type side: typing.Any
    """

    ...

def swap_data(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Swap 2 sequencer strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def swap_inputs(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Swap the first two inputs for the effect strip

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def unlock(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Unlock strips so they can be transformed

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def unmute(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    unselected: typing.Union[bool, typing.Any] = False,
):
    """Unmute (un)selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param unselected: Unselected, Unmute unselected rather than selected strips
    :type unselected: typing.Union[bool, typing.Any]
    """

    ...

def view_all(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """View all the strips in the sequencer

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def view_all_preview(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Zoom preview to fit in the area

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

def view_ghost_border(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    xmin: typing.Any = 0,
    xmax: typing.Any = 0,
    ymin: typing.Any = 0,
    ymax: typing.Any = 0,
    wait_for_input: typing.Union[bool, typing.Any] = True,
):
    """Set the boundaries of the border used for offset view

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

def view_selected(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Zoom the sequencer on the selected strips

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def view_zoom_ratio(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    ratio: typing.Any = 1.0,
):
    """Change zoom ratio of sequencer preview

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param ratio: Ratio, Zoom ratio, 1.0 is 1:1, higher is zoomed in, lower is zoomed out
    :type ratio: typing.Any
    """

    ...
