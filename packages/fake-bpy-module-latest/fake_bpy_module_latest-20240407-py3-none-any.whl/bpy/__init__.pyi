import typing
import bpy.types

from . import app
from . import msgbus
from . import ops
from . import path
from . import props
from . import types
from . import utils

GenericType = typing.TypeVar("GenericType")
context: bpy.types.Context

data: bpy.types.BlendData
""" Access to Blender's internal data
"""
