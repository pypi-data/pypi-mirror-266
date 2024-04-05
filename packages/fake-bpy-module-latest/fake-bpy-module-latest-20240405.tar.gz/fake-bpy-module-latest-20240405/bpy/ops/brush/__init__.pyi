import typing
import bpy.types

GenericType = typing.TypeVar("GenericType")

def add(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add brush by mode type

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def add_gpencil(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Add brush for Grease Pencil

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def curve_preset(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    shape: typing.Any = "SMOOTH",
):
    """Set brush shape

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param shape: Mode
    :type shape: typing.Any
    """

    ...

def reset(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
):
    """Return brush to defaults based on current tool

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    """

    ...

def scale_size(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    scalar: typing.Any = 1.0,
):
    """Change brush size by a scalar

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param scalar: Scalar, Factor to scale brush size by
    :type scalar: typing.Any
    """

    ...

def sculpt_curves_falloff_preset(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    shape: typing.Any = "SMOOTH",
):
    """Set Curve Falloff Preset

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param shape: Mode
    :type shape: typing.Any
    """

    ...

def stencil_control(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mode: typing.Any = "TRANSLATION",
    texmode: typing.Any = "PRIMARY",
):
    """Control the stencil brush

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mode: Tool
    :type mode: typing.Any
    :param texmode: Tool
    :type texmode: typing.Any
    """

    ...

def stencil_fit_image_aspect(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    use_repeat: typing.Union[bool, typing.Any] = True,
    use_scale: typing.Union[bool, typing.Any] = True,
    mask: typing.Union[bool, typing.Any] = False,
):
    """When using an image texture, adjust the stencil size to fit the image aspect ratio

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param use_repeat: Use Repeat, Use repeat mapping values
    :type use_repeat: typing.Union[bool, typing.Any]
    :param use_scale: Use Scale, Use texture scale values
    :type use_scale: typing.Union[bool, typing.Any]
    :param mask: Modify Mask Stencil, Modify either the primary or mask stencil
    :type mask: typing.Union[bool, typing.Any]
    """

    ...

def stencil_reset_transform(
    override_context: typing.Union[dict, bpy.types.Context] = None,
    execution_context: str = None,
    undo: bool = None,
    mask: typing.Union[bool, typing.Any] = False,
):
    """Reset the stencil transformation to the default

    :type override_context: typing.Union[dict, bpy.types.Context]
    :type execution_context: str
    :type undo: bool
    :param mask: Modify Mask Stencil, Modify either the primary or mask stencil
    :type mask: typing.Union[bool, typing.Any]
    """

    ...
