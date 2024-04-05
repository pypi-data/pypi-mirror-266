import typing

GenericType = typing.TypeVar("GenericType")

def BoolProperty(
    name: str = "",
    description: str = "",
    translation_context: str = "*",
    default=False,
    options: set = {'"ANIMATABLE"'},
    override: set = None(),
    tags: set = None(),
    subtype: str = "NONE",
    update: typing.Any = None,
    get: typing.Any = None,
    set: typing.Any = None,
):
    """Returns a new boolean property definition.

        :param name: Name used in the user interface.
        :type name: str
        :param description: Text used for the tooltip and api documentation.
        :type description: str
        :param translation_context: Text used as context to disambiguate translations.
        :type translation_context: str
        :param options: Enumerator in `rna_enum_property_flag_items`.
        :type options: set
        :param override: Enumerator in `rna_enum_property_override_flag_items`.
        :type override: set
        :param tags: Enumerator of tags that are defined by parent class.
        :type tags: set
        :param subtype: Enumerator in `rna_enum_property_subtype_number_items`.
        :type subtype: str
        :param update: Function to be called when this value is modified,
    This function must take 2 values (self, context) and return None.
    Warning there are no safety checks to avoid infinite recursion.
        :type update: typing.Any
        :param get: Function to be called when this value is 'read',
    This function must take 1 value (self) and return the value of the property.
        :type get: typing.Any
        :param set: Function to be called when this value is 'written',
    This function must take 2 values (self, value) and return None.
        :type set: typing.Any
    """

    ...

def BoolVectorProperty(
    name: str = "",
    description: str = "",
    translation_context: str = "*",
    default: typing.Sequence = (False, False, False),
    options: set = {'"ANIMATABLE"'},
    override: set = None(),
    tags: set = None(),
    subtype: str = "NONE",
    size: typing.Sequence[int] = 3,
    update: typing.Any = None,
    get: typing.Any = None,
    set: typing.Any = None,
):
    """Returns a new vector boolean property definition.

        :param name: Name used in the user interface.
        :type name: str
        :param description: Text used for the tooltip and api documentation.
        :type description: str
        :param translation_context: Text used as context to disambiguate translations.
        :type translation_context: str
        :param default: sequence of booleans the length of size.
        :type default: typing.Sequence
        :param options: Enumerator in `rna_enum_property_flag_items`.
        :type options: set
        :param override: Enumerator in `rna_enum_property_override_flag_items`.
        :type override: set
        :param tags: Enumerator of tags that are defined by parent class.
        :type tags: set
        :param subtype: Enumerator in `rna_enum_property_subtype_number_array_items`.
        :type subtype: str
        :param size: Vector dimensions in [1, 32]. An int sequence can be used to define multi-dimension arrays.
        :type size: typing.Sequence[int]
        :param update: Function to be called when this value is modified,
    This function must take 2 values (self, context) and return None.
    Warning there are no safety checks to avoid infinite recursion.
        :type update: typing.Any
        :param get: Function to be called when this value is 'read',
    This function must take 1 value (self) and return the value of the property.
        :type get: typing.Any
        :param set: Function to be called when this value is 'written',
    This function must take 2 values (self, value) and return None.
        :type set: typing.Any
    """

    ...

def CollectionProperty(
    type=None,
    name: str = "",
    description: str = "",
    translation_context: str = "*",
    options: set = {'"ANIMATABLE"'},
    override: set = None(),
    tags: set = None(),
):
    """Returns a new collection property definition.

    :param type: A subclass of `bpy.types.PropertyGroup`.
    :param name: Name used in the user interface.
    :type name: str
    :param description: Text used for the tooltip and api documentation.
    :type description: str
    :param translation_context: Text used as context to disambiguate translations.
    :type translation_context: str
    :param options: Enumerator in `rna_enum_property_flag_items`.
    :type options: set
    :param override: Enumerator in `rna_enum_property_override_flag_collection_items`.
    :type override: set
    :param tags: Enumerator of tags that are defined by parent class.
    :type tags: set
    """

    ...

def EnumProperty(
    items: typing.Union[typing.Iterable[typing.Iterable[str]], typing.Callable],
    name: str = "",
    description: str = "",
    translation_context: str = "*",
    default: typing.Union[str, set] = None,
    options: set = {'"ANIMATABLE"'},
    override: set = None(),
    tags: set = None(),
    update: typing.Any = None,
    get: typing.Any = None,
    set: typing.Any = None,
):
    """Returns a new enumerator property definition.

        :param items: sequence of enum items formatted:
    [(identifier, name, description, icon, number), ...].

    The first three elements of the tuples are mandatory.

    identifier

    The identifier is used for Python access.

    name

    Name for the interface.

    description

    Used for documentation and tooltips.

    icon

    An icon string identifier or integer icon value
    (e.g. returned by `bpy.types.UILayout.icon`)

    number

    Unique value used as the identifier for this item (stored in file data).
    Use when the identifier may need to change. If the ENUM_FLAG option is used,
    the values are bit-masks and should be powers of two.

    When an item only contains 4 items they define (identifier, name, description, number).

    Separators may be added using None instead of a tuple.
    For dynamic values a callback can be passed which returns a list in
    the same format as the static list.
    This function must take 2 arguments (self, context), context may be None.

    There is a known bug with using a callback,
    Python must keep a reference to the strings returned by the callback or Blender
    will misbehave or even crash.
        :type items: typing.Union[typing.Iterable[typing.Iterable[str]], typing.Callable]
        :param name: Name used in the user interface.
        :type name: str
        :param description: Text used for the tooltip and api documentation.
        :type description: str
        :param translation_context: Text used as context to disambiguate translations.
        :type translation_context: str
        :param default: The default value for this enum, a string from the identifiers used in items, or integer matching an item number.
    If the ENUM_FLAG option is used this must be a set of such string identifiers instead.
    WARNING: Strings cannot be specified for dynamic enums
    (i.e. if a callback function is given as items parameter).
        :type default: typing.Union[str, set]
        :param options: Enumerator in `rna_enum_property_flag_enum_items`.
        :type options: set
        :param override: Enumerator in `rna_enum_property_override_flag_items`.
        :type override: set
        :param tags: Enumerator of tags that are defined by parent class.
        :type tags: set
        :param update: Function to be called when this value is modified,
    This function must take 2 values (self, context) and return None.
    Warning there are no safety checks to avoid infinite recursion.
        :type update: typing.Any
        :param get: Function to be called when this value is 'read',
    This function must take 1 value (self) and return the value of the property.
        :type get: typing.Any
        :param set: Function to be called when this value is 'written',
    This function must take 2 values (self, value) and return None.
        :type set: typing.Any
    """

    ...

def FloatProperty(
    name: str = "",
    description: str = "",
    translation_context: str = "*",
    default=0.0,
    min=-3.402823e38,
    max=3.402823e38,
    soft_min=-3.402823e38,
    soft_max=3.402823e38,
    step=3,
    precision=2,
    options: set = {'"ANIMATABLE"'},
    override: set = None(),
    tags: set = None(),
    subtype: str = "NONE",
    unit: str = "NONE",
    update: typing.Any = None,
    get: typing.Any = None,
    set: typing.Any = None,
):
    """Returns a new float (single precision) property definition.

        :param name: Name used in the user interface.
        :type name: str
        :param description: Text used for the tooltip and api documentation.
        :type description: str
        :param translation_context: Text used as context to disambiguate translations.
        :type translation_context: str
        :param min: Hard minimum, trying to assign a value below will silently assign this minimum instead.
        :param max: Hard maximum, trying to assign a value above will silently assign this maximum instead.
        :param soft_min: Soft minimum (>= min), user won't be able to drag the widget below this value in the UI.
        :param soft_max: Soft maximum (<= max), user won't be able to drag the widget above this value in the UI.
        :param step: Step of increment/decrement in UI, in [1, 100], defaults to 3 (WARNING: actual value is /100).
        :param precision: Maximum number of decimal digits to display, in [0, 6]. Fraction is automatically hidden for exact integer values of fields with unit 'NONE' or 'TIME' (frame count) and step divisible by 100.
        :param options: Enumerator in `rna_enum_property_flag_items`.
        :type options: set
        :param override: Enumerator in `rna_enum_property_override_flag_items`.
        :type override: set
        :param tags: Enumerator of tags that are defined by parent class.
        :type tags: set
        :param subtype: Enumerator in `rna_enum_property_subtype_number_items`.
        :type subtype: str
        :param unit: Enumerator in `rna_enum_property_unit_items`.
        :type unit: str
        :param update: Function to be called when this value is modified,
    This function must take 2 values (self, context) and return None.
    Warning there are no safety checks to avoid infinite recursion.
        :type update: typing.Any
        :param get: Function to be called when this value is 'read',
    This function must take 1 value (self) and return the value of the property.
        :type get: typing.Any
        :param set: Function to be called when this value is 'written',
    This function must take 2 values (self, value) and return None.
        :type set: typing.Any
    """

    ...

def FloatVectorProperty(
    name: str = "",
    description: str = "",
    translation_context: str = "*",
    default: typing.Sequence = (0.0, 0.0, 0.0),
    min=None,
    max=None,
    soft_min=None,
    soft_max=None,
    step=3,
    precision=2,
    options: set = {'"ANIMATABLE"'},
    override: set = None(),
    tags: set = None(),
    subtype: str = "NONE",
    unit: str = "NONE",
    size: typing.Sequence[int] = 3,
    update: typing.Any = None,
    get: typing.Any = None,
    set: typing.Any = None,
):
    """Returns a new vector float property definition.

        :param name: Name used in the user interface.
        :type name: str
        :param description: Text used for the tooltip and api documentation.
        :type description: str
        :param translation_context: Text used as context to disambiguate translations.
        :type translation_context: str
        :param default: sequence of floats the length of size.
        :type default: typing.Sequence
        :param min: Hard minimum, trying to assign a value below will silently assign this minimum instead.
        :param max: Hard maximum, trying to assign a value above will silently assign this maximum instead.
        :param soft_min: Soft minimum (>= min), user won't be able to drag the widget below this value in the UI.
        :param soft_max: Soft maximum (<= max), user won't be able to drag the widget above this value in the UI.
        :param step: Step of increment/decrement in UI, in [1, 100], defaults to 3 (WARNING: actual value is /100).
        :param precision: Maximum number of decimal digits to display, in [0, 6]. Fraction is automatically hidden for exact integer values of fields with unit 'NONE' or 'TIME' (frame count) and step divisible by 100.
        :param options: Enumerator in `rna_enum_property_flag_items`.
        :type options: set
        :param override: Enumerator in `rna_enum_property_override_flag_items`.
        :type override: set
        :param tags: Enumerator of tags that are defined by parent class.
        :type tags: set
        :param subtype: Enumerator in `rna_enum_property_subtype_number_array_items`.
        :type subtype: str
        :param unit: Enumerator in `rna_enum_property_unit_items`.
        :type unit: str
        :param size: Vector dimensions in [1, 32]. An int sequence can be used to define multi-dimension arrays.
        :type size: typing.Sequence[int]
        :param update: Function to be called when this value is modified,
    This function must take 2 values (self, context) and return None.
    Warning there are no safety checks to avoid infinite recursion.
        :type update: typing.Any
        :param get: Function to be called when this value is 'read',
    This function must take 1 value (self) and return the value of the property.
        :type get: typing.Any
        :param set: Function to be called when this value is 'written',
    This function must take 2 values (self, value) and return None.
        :type set: typing.Any
    """

    ...

def IntProperty(
    name: str = "",
    description: str = "",
    translation_context: str = "*",
    default=0,
    min=None,
    max=None,
    soft_min=None,
    soft_max=None,
    step=1,
    options: set = {'"ANIMATABLE"'},
    override: set = None(),
    tags: set = None(),
    subtype: str = "NONE",
    update: typing.Any = None,
    get: typing.Any = None,
    set: typing.Any = None,
):
    """Returns a new int property definition.

        :param name: Name used in the user interface.
        :type name: str
        :param description: Text used for the tooltip and api documentation.
        :type description: str
        :param translation_context: Text used as context to disambiguate translations.
        :type translation_context: str
        :param min: Hard minimum, trying to assign a value below will silently assign this minimum instead.
        :param max: Hard maximum, trying to assign a value above will silently assign this maximum instead.
        :param soft_min: Soft minimum (>= min), user won't be able to drag the widget below this value in the UI.
        :param soft_max: Soft maximum (<= max), user won't be able to drag the widget above this value in the UI.
        :param step: Step of increment/decrement in UI, in [1, 100], defaults to 1 (WARNING: unused currently!).
        :param options: Enumerator in `rna_enum_property_flag_items`.
        :type options: set
        :param override: Enumerator in `rna_enum_property_override_flag_items`.
        :type override: set
        :param tags: Enumerator of tags that are defined by parent class.
        :type tags: set
        :param subtype: Enumerator in `rna_enum_property_subtype_number_items`.
        :type subtype: str
        :param update: Function to be called when this value is modified,
    This function must take 2 values (self, context) and return None.
    Warning there are no safety checks to avoid infinite recursion.
        :type update: typing.Any
        :param get: Function to be called when this value is 'read',
    This function must take 1 value (self) and return the value of the property.
        :type get: typing.Any
        :param set: Function to be called when this value is 'written',
    This function must take 2 values (self, value) and return None.
        :type set: typing.Any
    """

    ...

def IntVectorProperty(
    name: str = "",
    description: str = "",
    translation_context: str = "*",
    default: typing.Sequence = (0, 0, 0),
    min=None,
    max=None,
    soft_min=None,
    soft_max=None,
    step=1,
    options: set = {'"ANIMATABLE"'},
    override: set = None(),
    tags: set = None(),
    subtype: str = "NONE",
    size: typing.Sequence[int] = 3,
    update: typing.Any = None,
    get: typing.Any = None,
    set: typing.Any = None,
):
    """Returns a new vector int property definition.

        :param name: Name used in the user interface.
        :type name: str
        :param description: Text used for the tooltip and api documentation.
        :type description: str
        :param translation_context: Text used as context to disambiguate translations.
        :type translation_context: str
        :param default: sequence of ints the length of size.
        :type default: typing.Sequence
        :param min: Hard minimum, trying to assign a value below will silently assign this minimum instead.
        :param max: Hard maximum, trying to assign a value above will silently assign this maximum instead.
        :param soft_min: Soft minimum (>= min), user won't be able to drag the widget below this value in the UI.
        :param soft_max: Soft maximum (<= max), user won't be able to drag the widget above this value in the UI.
        :param step: Step of increment/decrement in UI, in [1, 100], defaults to 1 (WARNING: unused currently!).
        :param options: Enumerator in `rna_enum_property_flag_items`.
        :type options: set
        :param override: Enumerator in `rna_enum_property_override_flag_items`.
        :type override: set
        :param tags: Enumerator of tags that are defined by parent class.
        :type tags: set
        :param subtype: Enumerator in `rna_enum_property_subtype_number_array_items`.
        :type subtype: str
        :param size: Vector dimensions in [1, 32]. An int sequence can be used to define multi-dimension arrays.
        :type size: typing.Sequence[int]
        :param update: Function to be called when this value is modified,
    This function must take 2 values (self, context) and return None.
    Warning there are no safety checks to avoid infinite recursion.
        :type update: typing.Any
        :param get: Function to be called when this value is 'read',
    This function must take 1 value (self) and return the value of the property.
        :type get: typing.Any
        :param set: Function to be called when this value is 'written',
    This function must take 2 values (self, value) and return None.
        :type set: typing.Any
    """

    ...

def PointerProperty(
    type=None,
    name: str = "",
    description: str = "",
    translation_context: str = "*",
    options: set = {'"ANIMATABLE"'},
    override: set = None(),
    tags: set = None(),
    poll: typing.Any = None,
    update: typing.Any = None,
):
    """Returns a new pointer property definition.

        :param type: A subclass of `bpy.types.PropertyGroup` or `bpy.types.ID`.
        :param name: Name used in the user interface.
        :type name: str
        :param description: Text used for the tooltip and api documentation.
        :type description: str
        :param translation_context: Text used as context to disambiguate translations.
        :type translation_context: str
        :param options: Enumerator in `rna_enum_property_flag_items`.
        :type options: set
        :param override: Enumerator in `rna_enum_property_override_flag_items`.
        :type override: set
        :param tags: Enumerator of tags that are defined by parent class.
        :type tags: set
        :param poll: function to be called to determine whether an item is valid for this property.
    The function must take 2 values (self, object) and return Bool.
        :type poll: typing.Any
        :param update: Function to be called when this value is modified,
    This function must take 2 values (self, context) and return None.
    Warning there are no safety checks to avoid infinite recursion.
        :type update: typing.Any
    """

    ...

def RemoveProperty(cls: typing.Any, attr: str):
    """Removes a dynamically defined property.

    :param cls: The class containing the property (must be a positional argument).
    :type cls: typing.Any
    :param attr: Property name (must be passed as a keyword).
    :type attr: str
    """

    ...

def StringProperty(
    name: str = "",
    description: str = "",
    translation_context: str = "*",
    default: str = "",
    maxlen=0,
    options: set = {'"ANIMATABLE"'},
    override: set = None(),
    tags: set = None(),
    subtype: str = "NONE",
    update: typing.Any = None,
    get: typing.Any = None,
    set: typing.Any = None,
    search: typing.Any = None,
    search_options: set = {'"SUGGESTION"'},
):
    """Returns a new string property definition.

        :param name: Name used in the user interface.
        :type name: str
        :param description: Text used for the tooltip and api documentation.
        :type description: str
        :param translation_context: Text used as context to disambiguate translations.
        :type translation_context: str
        :param default: initializer string.
        :type default: str
        :param maxlen: maximum length of the string.
        :param options: Enumerator in `rna_enum_property_flag_items`.
        :type options: set
        :param override: Enumerator in `rna_enum_property_override_flag_items`.
        :type override: set
        :param tags: Enumerator of tags that are defined by parent class.
        :type tags: set
        :param subtype: Enumerator in `rna_enum_property_subtype_string_items`.
        :type subtype: str
        :param update: Function to be called when this value is modified,
    This function must take 2 values (self, context) and return None.
    Warning there are no safety checks to avoid infinite recursion.
        :type update: typing.Any
        :param get: Function to be called when this value is 'read',
    This function must take 1 value (self) and return the value of the property.
        :type get: typing.Any
        :param set: Function to be called when this value is 'written',
    This function must take 2 values (self, value) and return None.
        :type set: typing.Any
        :param search: Function to be called to show candidates for this string (shown in the UI).
    This function must take 3 values (self, context, edit_text)
    and return a sequence, iterator or generator where each item must be:

    A single string (representing a candidate to display).

    A tuple-pair of strings, where the first is a candidate and the second
    is additional information about the candidate.
        :type search: typing.Any
        :param search_options: Set of strings in:

    'SORT' sorts the resulting items.

    'SUGGESTION' lets the user enter values not found in search candidates.
    WARNING disabling this flag causes the search callback to run on redraw,
    so only disable this flag if it's not likely to cause performance issues.
        :type search_options: set
    """

    ...
