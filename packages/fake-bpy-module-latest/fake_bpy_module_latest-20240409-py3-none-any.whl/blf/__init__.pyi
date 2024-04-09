import typing

GenericType = typing.TypeVar("GenericType")

def aspect(fontid, aspect):
    """Set the aspect for drawing text.

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param aspect: The aspect ratio for text drawing to use.
    """

    ...

def clipping(fontid, xmin, ymin, xmax, ymax):
    """Set the clipping, enable/disable using CLIPPING.

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param xmin: Clip the drawing area by these bounds.
    :param ymin: Clip the drawing area by these bounds.
    :param xmax: Clip the drawing area by these bounds.
    :param ymax: Clip the drawing area by these bounds.
    """

    ...

def color(fontid, r, g, b, a):
    """Set the color for drawing text.

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param r: red channel 0.0 - 1.0.
    :param g: green channel 0.0 - 1.0.
    :param b: blue channel 0.0 - 1.0.
    :param a: alpha channel 0.0 - 1.0.
    """

    ...

def dimensions(fontid, text: str):
    """Return the width and height of the text.

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param text: the text to draw.
    :type text: str
    :return: the width and height of the text.
    """

    ...

def disable(fontid, option):
    """Disable option.

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param option: One of ROTATION, CLIPPING, SHADOW or KERNING_DEFAULT.
    """

    ...

def draw(fontid, text: str):
    """Draw text in the current context.

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param text: the text to draw.
    :type text: str
    """

    ...

def enable(fontid, option):
    """Enable option.

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param option: One of ROTATION, CLIPPING, SHADOW or KERNING_DEFAULT.
    """

    ...

def load(filepath: typing.Union[str, bytes]):
    """Load a new font.

    :param filepath: the filepath of the font.
    :type filepath: typing.Union[str, bytes]
    :return: the new font's fontid or -1 if there was an error.
    """

    ...

def position(fontid, x, y, z):
    """Set the position for drawing text.

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param x: X axis position to draw the text.
    :param y: Y axis position to draw the text.
    :param z: Z axis position to draw the text.
    """

    ...

def rotation(fontid, angle):
    """Set the text rotation angle, enable/disable using ROTATION.

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param angle: The angle for text drawing to use.
    """

    ...

def shadow(fontid, level, r, g, b, a):
    """Shadow options, enable/disable using SHADOW .

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param level: The blur level, can be 3, 5 or 0.
    :param r: Shadow color (red channel 0.0 - 1.0).
    :param g: Shadow color (green channel 0.0 - 1.0).
    :param b: Shadow color (blue channel 0.0 - 1.0).
    :param a: Shadow color (alpha channel 0.0 - 1.0).
    """

    ...

def shadow_offset(fontid, x, y):
    """Set the offset for shadow text.

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param x: Vertical shadow offset value in pixels.
    :param y: Horizontal shadow offset value in pixels.
    """

    ...

def size(fontid, size):
    """Set the size for drawing text.

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param size: Point size of the font.
    """

    ...

def unload(filepath: typing.Union[str, bytes]):
    """Unload an existing font.

    :param filepath: the filepath of the font.
    :type filepath: typing.Union[str, bytes]
    """

    ...

def word_wrap(fontid, wrap_width):
    """Set the wrap width, enable/disable using WORD_WRAP.

    :param fontid: The id of the typeface as returned by `blf.load`, for default font use 0.
    :param wrap_width: The width (in pixels) to wrap words at.
    """

    ...

CLIPPING: typing.Any
""" Constant value 2
"""

MONOCHROME: typing.Any
""" Constant value 128
"""

ROTATION: typing.Any
""" Constant value 1
"""

SHADOW: typing.Any
""" Constant value 4
"""

WORD_WRAP: typing.Any
""" Constant value 64
"""
