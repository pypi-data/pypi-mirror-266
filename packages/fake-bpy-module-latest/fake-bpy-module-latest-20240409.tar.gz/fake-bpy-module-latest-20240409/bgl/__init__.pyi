import typing

GenericType = typing.TypeVar("GenericType")

class Buffer:
    """The Buffer object is simply a block of memory that is delineated and initialized by the
    user. Many OpenGL functions return data to a C-style pointer, however, because this
    is not possible in python the Buffer object can be used to this end. Wherever pointer
    notation is used in the OpenGL functions the Buffer object can be used in it's bgl
    wrapper. In some instances the Buffer object will need to be initialized with the template
    parameter, while in other instances the user will want to create just a blank buffer
    which will be zeroed by default.
    """

    dimensions: typing.Any
    """ The number of dimensions of the Buffer."""

    def to_list(self):
        """The contents of the Buffer as a python list."""
        ...

    def __init__(self, type, dimensions, template=None):
        """This will create a new Buffer object for use with other bgl OpenGL commands.
        Only the type of argument to store in the buffer and the dimensions of the buffer
        are necessary. Buffers are zeroed by default unless a template is supplied, in
        which case the buffer is initialized to the template.

                :param type: The format to store data in. The type should be one of
        GL_BYTE, GL_SHORT, GL_INT, or GL_FLOAT.
                :param dimensions: If the dimensions are specified as an int a linear array will
        be created for the buffer. If a sequence is passed for the dimensions, the buffer
        becomes n-Dimensional, where n is equal to the number of parameters passed in the
        sequence. Example: [256,2] is a two- dimensional buffer while [256,256,4] creates
        a three- dimensional buffer. You can think of each additional dimension as a sub-item
        of the dimension to the left. i.e. [10,2] is a 10 element array each with 2 sub-items.
        [(0,0), (0,1), (1,0), (1,1), (2,0), ...] etc.
                :param template: A sequence of matching dimensions which will be used to initialize
        the Buffer. If a template is not passed in all fields will be initialized to 0.
                :return: The newly created buffer as a PyObject.
        """
        ...

def glActiveTexture(texture):
    """Select active texture unit.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glActiveTexture.xhtml>`__

    :param texture: Constant in GL_TEXTURE0 0 - 8
    """

    ...

def glActiveTexture(p0):
    """ """

    ...

def glAttachShader(program, shader):
    """Attaches a shader object to a program object.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glAttachShader.xhtml>`__

    :param program: Specifies the program object to which a shader object will be attached.
    :param shader: Specifies the shader object that is to be attached.
    """

    ...

def glAttachShader(p0, p1):
    """ """

    ...

def glBeginQuery(p0, p1):
    """ """

    ...

def glBindAttribLocation(p0, p1, p2: str):
    """

    :type p2: str
    """

    ...

def glBindBuffer(p0, p1):
    """ """

    ...

def glBindBufferBase(p0, p1, p2):
    """ """

    ...

def glBindBufferRange(p0, p1, p2, p3, p4):
    """ """

    ...

def glBindFramebuffer(p0, p1):
    """ """

    ...

def glBindRenderbuffer(p0, p1):
    """ """

    ...

def glBindTexture(target: typing.Union[typing.Set[str], typing.Set[int]], texture: int):
    """Bind a named texture to a texturing target`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glBindTexture.xhtml>`__

    :param target: Specifies the target to which the texture is bound.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param texture: Specifies the name of a texture.
    :type texture: int
    """

    ...

def glBindTexture(p0, p1):
    """ """

    ...

def glBindVertexArray(p0):
    """ """

    ...

def glBlendColor(p0, p1, p2, p3):
    """ """

    ...

def glBlendEquation(p0):
    """ """

    ...

def glBlendEquationSeparate(p0, p1):
    """ """

    ...

def glBlendFunc(
    sfactor: typing.Union[typing.Set[str], typing.Set[int]],
    dfactor: typing.Union[typing.Set[str], typing.Set[int]],
):
    """Specify pixel arithmetic`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glBlendFunc.xhtml>`__

        :param sfactor: Specifies how the red, green, blue, and alpha source blending factors are
    computed.
        :type sfactor: typing.Union[typing.Set[str], typing.Set[int]]
        :param dfactor: Specifies how the red, green, blue, and alpha destination
    blending factors are computed.
        :type dfactor: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glBlendFunc(p0, p1):
    """ """

    ...

def glBlitFramebuffer(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9):
    """ """

    ...

def glBufferData(p0, p1, p2: typing.Any, p3):
    """

    :type p2: typing.Any
    """

    ...

def glBufferSubData(p0, p1, p2, p3: typing.Any):
    """

    :type p3: typing.Any
    """

    ...

def glCheckFramebufferStatus(p0):
    """ """

    ...

def glClear(mask):
    """Clear buffers to preset values`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glClear.xhtml>`__

    :param mask: Bitwise OR of masks that indicate the buffers to be cleared.
    """

    ...

def glClear(p0):
    """ """

    ...

def glClearColor(red, green, blue, alpha):
    """Specify clear values for the color buffers`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glClearColor.xhtml>`__

        :param red: Specify the red, green, blue, and alpha values used when the
    color buffers are cleared. The initial values are all 0.
    """

    ...

def glClearColor(p0, p1, p2, p3):
    """ """

    ...

def glClearDepth(depth):
    """Specify the clear value for the depth buffer`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glClearDepth.xhtml>`__

        :param depth: Specifies the depth value used when the depth buffer is cleared.
    The initial value is 1.
    """

    ...

def glClearDepth(p0):
    """ """

    ...

def glClearStencil(s):
    """Specify the clear value for the stencil buffer`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glClearStencil.xhtml>`__

    :param s: Specifies the index used when the stencil buffer is cleared. The initial value is 0.
    """

    ...

def glClearStencil(p0):
    """ """

    ...

def glClipPlane(
    plane: typing.Union[typing.Set[str], typing.Set[int]], equation: Buffer
):
    """Specify a plane against which all geometry is clipped`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glClipPlane.xhtml>`__

        :param plane: Specifies which clipping plane is being positioned.
        :type plane: typing.Union[typing.Set[str], typing.Set[int]]
        :param equation: Specifies the address of an array of four double- precision
    floating-point values. These values are interpreted as a plane equation.
        :type equation: Buffer
    """

    ...

def glColorMask(red: int, green, blue, alpha):
    """Enable and disable writing of frame buffer color components`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glColorMask.xhtml>`__

        :param red: Specify whether red, green, blue, and alpha can or cannot be
    written into the frame buffer. The initial values are all GL_TRUE, indicating that the
    color components can be written.
        :type red: int
    """

    ...

def glColorMask(p0: bool, p1: bool, p2: bool, p3: bool):
    """

    :type p0: bool
    :type p1: bool
    :type p2: bool
    :type p3: bool
    """

    ...

def glCompileShader(shader):
    """Compiles a shader object.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glCompileShader.xhtml>`__

    :param shader: Specifies the shader object to be compiled.
    """

    ...

def glCompileShader(p0):
    """ """

    ...

def glCompressedTexImage1D(p0, p1, p2, p3, p4, p5, p6: typing.Any):
    """

    :type p6: typing.Any
    """

    ...

def glCompressedTexImage2D(p0, p1, p2, p3, p4, p5, p6, p7: typing.Any):
    """

    :type p7: typing.Any
    """

    ...

def glCompressedTexImage3D(p0, p1, p2, p3, p4, p5, p6, p7, p8: typing.Any):
    """

    :type p8: typing.Any
    """

    ...

def glCompressedTexSubImage1D(p0, p1, p2, p3, p4, p5, p6: typing.Any):
    """

    :type p6: typing.Any
    """

    ...

def glCompressedTexSubImage2D(p0, p1, p2, p3, p4, p5, p6, p7, p8: typing.Any):
    """

    :type p8: typing.Any
    """

    ...

def glCopyTexImage1D(p0, p1, p2, p3, p4, p5, p6):
    """ """

    ...

def glCopyTexImage2D(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    level,
    internalformat,
    x,
    y,
    width,
    height,
    border,
):
    """Copy pixels into a 2D texture image`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glCopyTexImage2D.xhtml>`__

        :param target: Specifies the target texture.
        :type target: typing.Union[typing.Set[str], typing.Set[int]]
        :param level: Specifies the level-of-detail number. Level 0 is the base image level.
    Level n is the nth mipmap reduction image.
        :param internalformat: Specifies the number of color components in the texture.
        :param x: Specify the window coordinates of the first pixel that is copied
    from the frame buffer. This location is the lower left corner of a rectangular
    block of pixels.
        :param width: Specifies the width of the texture image. Must be 2n+2(border) for
    some integer n. All implementations support texture images that are at least 64
    texels wide.
        :param height: Specifies the height of the texture image. Must be 2m+2(border) for
    some integer m. All implementations support texture images that are at least 64
    texels high.
        :param border: Specifies the width of the border. Must be either 0 or 1.
    """

    ...

def glCopyTexImage2D(p0, p1, p2, p3, p4, p5, p6, p7):
    """ """

    ...

def glCopyTexSubImage1D(p0, p1, p2, p3, p4, p5):
    """ """

    ...

def glCopyTexSubImage2D(p0, p1, p2, p3, p4, p5, p6, p7):
    """ """

    ...

def glCopyTexSubImage3D(p0, p1, p2, p3, p4, p5, p6, p7, p8):
    """ """

    ...

def glCreateProgram():
    """Creates a program object`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glCreateProgram.xhtml>`__

    :return: The new program or zero if an error occurs.
    """

    ...

def glCreateProgram(p0: typing.Any):
    """

    :type p0: typing.Any
    """

    ...

def glCreateShader(shaderType: GL_GEOMETRY_SHADER):
    """Creates a shader object.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glCreateShader.xhtml>`__

    :param shaderType:
    :type shaderType: GL_GEOMETRY_SHADER
    :return: 0 if an error occurs.
    """

    ...

def glCreateShader(p0):
    """ """

    ...

def glCullFace(mode: typing.Union[typing.Set[str], typing.Set[int]]):
    """Specify whether front- or back-facing facets can be culled`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glCullFace.xhtml>`__

    :param mode: Specifies whether front- or back-facing facets are candidates for culling.
    :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glCullFace(p0):
    """ """

    ...

def glDeleteBuffers(p0, p1):
    """ """

    ...

def glDeleteFramebuffers(p0, p1):
    """ """

    ...

def glDeleteProgram(program):
    """Deletes a program object.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glDeleteProgram.xhtml>`__

    :param program: Specifies the program object to be deleted.
    """

    ...

def glDeleteProgram(p0):
    """ """

    ...

def glDeleteQueries(p0, p1):
    """ """

    ...

def glDeleteRenderbuffers(p0, p1):
    """ """

    ...

def glDeleteShader(shader):
    """Deletes a shader object.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glDeleteShader.xhtml>`__

    :param shader: Specifies the shader object to be deleted.
    """

    ...

def glDeleteShader(p0):
    """ """

    ...

def glDeleteTextures(n, textures: Buffer):
    """Delete named textures`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glDeleteTextures.xhtml>`__

    :param n: Specifies the number of textures to be deleted
    :param textures: Specifies an array of textures to be deleted
    :type textures: Buffer
    """

    ...

def glDeleteTextures(p0, p1):
    """ """

    ...

def glDeleteVertexArrays(p0, p1):
    """ """

    ...

def glDepthFunc(func: typing.Union[typing.Set[str], typing.Set[int]]):
    """Specify the value used for depth buffer comparisons`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glDepthFunc.xhtml>`__

    :param func: Specifies the depth comparison function.
    :type func: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glDepthFunc(p0):
    """ """

    ...

def glDepthMask(flag: int):
    """Enable or disable writing into the depth buffer`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glDepthMask.xhtml>`__

        :param flag: Specifies whether the depth buffer is enabled for writing. If flag is GL_FALSE,
    depth buffer writing is disabled. Otherwise, it is enabled. Initially, depth buffer
    writing is enabled.
        :type flag: int
    """

    ...

def glDepthMask(p0: bool):
    """

    :type p0: bool
    """

    ...

def glDepthRange(zNear, zFar):
    """Specify mapping of depth values from normalized device coordinates to window coordinates`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glDepthRange.xhtml>`__

        :param zNear: Specifies the mapping of the near clipping plane to window coordinates.
    The initial value is 0.
        :param zFar: Specifies the mapping of the far clipping plane to window coordinates.
    The initial value is 1.
    """

    ...

def glDepthRange(p0, p1):
    """ """

    ...

def glDetachShader(program, shader):
    """Detaches a shader object from a program object to which it is attached.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glDetachShader.xhtml>`__

    :param program: Specifies the program object from which to detach the shader object.
    :param shader: pecifies the program object from which to detach the shader object.
    """

    ...

def glDetachShader(p0, p1):
    """ """

    ...

def glDisable(cap: typing.Union[typing.Set[str], typing.Set[int]]):
    """Disable server-side GL capabilities`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glEnable.xhtml>`__

    :param cap: Specifies a symbolic constant indicating a GL capability.
    :type cap: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glDisable(p0):
    """ """

    ...

def glDisableVertexAttribArray(p0):
    """ """

    ...

def glDrawArrays(p0, p1, p2):
    """ """

    ...

def glDrawBuffer(mode: typing.Union[typing.Set[str], typing.Set[int]]):
    """Specify which color buffers are to be drawn into`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glDrawBuffer.xhtml>`__

    :param mode: Specifies up to four color buffers to be drawn into.
    :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glDrawBuffer(p0):
    """ """

    ...

def glDrawBuffers(p0, p1):
    """ """

    ...

def glDrawElements(p0, p1, p2, p3: typing.Any):
    """

    :type p3: typing.Any
    """

    ...

def glDrawRangeElements(p0, p1, p2, p3, p4, p5: typing.Any):
    """

    :type p5: typing.Any
    """

    ...

def glEdgeFlag(flag):
    """B{glEdgeFlag, glEdgeFlagv}Flag edges as either boundary or non-boundary`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glEdgeFlag.xhtml>`__

    :param flag: Specifies the current edge flag value.The initial value is GL_TRUE.
    """

    ...

def glEnable(cap: typing.Union[typing.Set[str], typing.Set[int]]):
    """Enable server-side GL capabilities`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glEnable.xhtml>`__

    :param cap: Specifies a symbolic constant indicating a GL capability.
    :type cap: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glEnable(p0):
    """ """

    ...

def glEnableVertexAttribArray(p0):
    """ """

    ...

def glEndQuery(p0):
    """ """

    ...

def glEvalCoord(u: typing.Any, v: typing.Any):
    """B{glEvalCoord1d, glEvalCoord1f, glEvalCoord2d, glEvalCoord2f, glEvalCoord1dv, glEvalCoord1fv,
    glEvalCoord2dv, glEvalCoord2fv}Evaluate enabled one- and two-dimensional maps`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glEvalCoord.xhtml>`__

        :param u: Specifies a value that is the domain coordinate u to the basis function defined
    in a previous glMap1 or glMap2 command. If the function prototype ends in 'v' then
    u specifies a pointer to an array containing either one or two domain coordinates. The first
    coordinate is u. The second coordinate is v, which is present only in glEvalCoord2 versions.
        :type u: typing.Any
        :param v: Specifies a value that is the domain coordinate v to the basis function defined
    in a previous glMap2 command. This argument is not present in a glEvalCoord1 command.
        :type v: typing.Any
    """

    ...

def glEvalMesh(mode: typing.Union[typing.Set[str], typing.Set[int]], i1, i2):
    """B{glEvalMesh1 or glEvalMesh2}Compute a one- or two-dimensional grid of points or lines`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glEvalMesh.xhtml>`__

        :param mode: In glEvalMesh1, specifies whether to compute a one-dimensional
    mesh of points or lines.
        :type mode: typing.Union[typing.Set[str], typing.Set[int]]
        :param i1: Specify the first and last integer values for the grid domain variable i.
    """

    ...

def glEvalPoint(i, j):
    """B{glEvalPoint1 and glEvalPoint2}Generate and evaluate a single point in a mesh`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glEvalPoint.xhtml>`__

    :param i: Specifies the integer value for grid domain variable i.
    :param j: Specifies the integer value for grid domain variable j (glEvalPoint2 only).
    """

    ...

def glFeedbackBuffer(
    size, type: typing.Union[typing.Set[str], typing.Set[int]], buffer: Buffer
):
    """Controls feedback mode`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glFeedbackBuffer.xhtml>`__

        :param size: Specifies the maximum number of values that can be written into buffer.
        :param type: Specifies a symbolic constant that describes the information that
    will be returned for each vertex.
        :type type: typing.Union[typing.Set[str], typing.Set[int]]
        :param buffer: Returns the feedback data.
        :type buffer: Buffer
    """

    ...

def glFinish():
    """Block until all GL execution is complete`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glFinish.xhtml>`__"""

    ...

def glFinish(p0: typing.Any):
    """

    :type p0: typing.Any
    """

    ...

def glFlush():
    """Force Execution of GL commands in finite time`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glFlush.xhtml>`__"""

    ...

def glFlush(p0: typing.Any):
    """

    :type p0: typing.Any
    """

    ...

def glFog(pname: typing.Union[typing.Set[str], typing.Set[int]], param: typing.Any):
    """B{glFogf, glFogi, glFogfv, glFogiv}Specify fog parameters`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glFog.xhtml>`__

        :param pname: Specifies a single-valued fog parameter. If the function prototype
    ends in 'v' specifies a fog parameter.
        :type pname: typing.Union[typing.Set[str], typing.Set[int]]
        :param param: Specifies the value or values to be assigned to pname. GL_FOG_COLOR
    requires an array of four values. All other parameters accept an array containing
    only a single value.
        :type param: typing.Any
    """

    ...

def glFramebufferRenderbuffer(p0, p1, p2, p3):
    """ """

    ...

def glFramebufferTexture(p0, p1, p2, p3):
    """ """

    ...

def glFrontFace(mode: typing.Union[typing.Set[str], typing.Set[int]]):
    """Define front- and back-facing polygons`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glFrontFace.xhtml>`__

    :param mode: Specifies the orientation of front-facing polygons.
    :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glFrontFace(p0):
    """ """

    ...

def glGenBuffers(p0, p1):
    """ """

    ...

def glGenFramebuffers(p0, p1):
    """ """

    ...

def glGenQueries(p0, p1):
    """ """

    ...

def glGenRenderbuffers(p0, p1):
    """ """

    ...

def glGenTextures(n, textures: Buffer):
    """Generate texture names`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGenTextures.xhtml>`__

    :param n: Specifies the number of textures name to be generated.
    :param textures: Specifies an array in which the generated textures names are stored.
    :type textures: Buffer
    """

    ...

def glGenTextures(p0, p1):
    """ """

    ...

def glGenVertexArrays(p0, p1):
    """ """

    ...

def glGet(pname: typing.Union[typing.Set[str], typing.Set[int]], param: typing.Any):
    """B{glGetBooleanv, glGetfloatv, glGetFloatv, glGetIntegerv}Return the value or values of a selected parameter`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGet.xhtml>`__

    :param pname: Specifies the parameter value to be returned.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param param: Returns the value or values of the specified parameter.
    :type param: typing.Any
    """

    ...

def glGetActiveAttrib(p0, p1, p2, p3, p4, p5, p6):
    """ """

    ...

def glGetActiveUniform(p0, p1, p2, p3, p4, p5, p6):
    """ """

    ...

def glGetActiveUniformBlockName(p0, p1, p2, p3, p4):
    """ """

    ...

def glGetActiveUniformBlockiv(p0, p1, p2, p3):
    """ """

    ...

def glGetActiveUniformName(p0, p1, p2, p3, p4):
    """ """

    ...

def glGetActiveUniformsiv(p0, p1, p2, p3, p4):
    """ """

    ...

def glGetAttachedShaders(program, maxCount, count: Buffer, shaders: Buffer):
    """Returns the handles of the shader objects attached to a program object.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetAttachedShaders.xhtml>`__

    :param program: Specifies the program object to be queried.
    :param maxCount: Specifies the size of the array for storing the returned object names.
    :param count: Returns the number of names actually returned in objects.
    :type count: Buffer
    :param shaders: Specifies an array that is used to return the names of attached shader objects.
    :type shaders: Buffer
    """

    ...

def glGetAttachedShaders(p0, p1, p2, p3):
    """ """

    ...

def glGetAttribLocation(p0, p1: str):
    """

    :type p1: str
    """

    ...

def glGetBooleanv(p0, p1: bool):
    """

    :type p1: bool
    """

    ...

def glGetBufferParameteri64v(p0, p1, p2):
    """ """

    ...

def glGetBufferParameteriv(p0, p1, p2):
    """ """

    ...

def glGetBufferPointerv(p0, p1, p2: typing.Any):
    """

    :type p2: typing.Any
    """

    ...

def glGetBufferSubData(p0, p1, p2, p3: typing.Any):
    """

    :type p3: typing.Any
    """

    ...

def glGetCompressedTexImage(p0, p1, p2: typing.Any):
    """

    :type p2: typing.Any
    """

    ...

def glGetDoublev(p0, p1):
    """ """

    ...

def glGetError():
    """Return error information`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetError.xhtml>`__"""

    ...

def glGetError(p0: typing.Any):
    """

    :type p0: typing.Any
    """

    ...

def glGetFloatv(p0, p1):
    """ """

    ...

def glGetIntegerv(p0, p1):
    """ """

    ...

def glGetLight(
    light: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: Buffer,
):
    """B{glGetLightfv and glGetLightiv}Return light source parameter values`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetLight.xhtml>`__

        :param light: Specifies a light source. The number of possible lights depends on the
    implementation, but at least eight lights are supported. They are identified by symbolic
    names of the form GL_LIGHTi where 0 < i < GL_MAX_LIGHTS.
        :type light: typing.Union[typing.Set[str], typing.Set[int]]
        :param pname: Specifies a light source parameter for light.
        :type pname: typing.Union[typing.Set[str], typing.Set[int]]
        :param params: Returns the requested data.
        :type params: Buffer
    """

    ...

def glGetMap(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    query: typing.Union[typing.Set[str], typing.Set[int]],
    v: Buffer,
):
    """B{glGetMapdv, glGetMapfv, glGetMapiv}Return evaluator parameters`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetMap.xhtml>`__

    :param target: Specifies the symbolic name of a map.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param query: Specifies which parameter to return.
    :type query: typing.Union[typing.Set[str], typing.Set[int]]
    :param v: Returns the requested data.
    :type v: Buffer
    """

    ...

def glGetMaterial(
    face: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: Buffer,
):
    """B{glGetMaterialfv, glGetMaterialiv}Return material parameters`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetMaterial.xhtml>`__

        :param face: Specifies which of the two materials is being queried.
    representing the front and back materials, respectively.
        :type face: typing.Union[typing.Set[str], typing.Set[int]]
        :param pname: Specifies the material parameter to return.
        :type pname: typing.Union[typing.Set[str], typing.Set[int]]
        :param params: Returns the requested data.
        :type params: Buffer
    """

    ...

def glGetMultisamplefv(p0, p1, p2):
    """ """

    ...

def glGetPixelMap(map: typing.Union[typing.Set[str], typing.Set[int]], values: Buffer):
    """B{glGetPixelMapfv, glGetPixelMapuiv, glGetPixelMapusv}Return the specified pixel map`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetPixelMap.xhtml>`__

    :param map: Specifies the name of the pixel map to return.
    :type map: typing.Union[typing.Set[str], typing.Set[int]]
    :param values: Returns the pixel map contents.
    :type values: Buffer
    """

    ...

def glGetProgramInfoLog(program, maxLength, length: Buffer, infoLog: Buffer):
    """Returns the information log for a program object.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetProgramInfoLog.xhtml>`__

    :param program: Specifies the program object whose information log is to be queried.
    :param maxLength: Specifies the size of the character buffer for storing the returned information log.
    :param length: Returns the length of the string returned in infoLog (excluding the null terminator).
    :type length: Buffer
    :param infoLog: Specifies an array of characters that is used to return the information log.
    :type infoLog: Buffer
    """

    ...

def glGetProgramInfoLog(p0, p1, p2, p3):
    """ """

    ...

def glGetProgramiv(program, pname, params: Buffer):
    """Returns a parameter from a program object.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetProgram.xhtml>`__

    :param program: Specifies the program object to be queried.
    :param pname: Specifies the object parameter.
    :param params: Returns the requested object parameter.
    :type params: Buffer
    """

    ...

def glGetProgramiv(p0, p1, p2):
    """ """

    ...

def glGetQueryObjectiv(p0, p1, p2):
    """ """

    ...

def glGetQueryObjectuiv(p0, p1, p2):
    """ """

    ...

def glGetQueryiv(p0, p1, p2):
    """ """

    ...

def glGetShaderInfoLog(program, maxLength, length: Buffer, infoLog: Buffer):
    """Returns the information log for a shader object.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetShaderInfoLog.xhtml>`__

    :param maxLength: Specifies the size of the character buffer for storing the returned information log.
    :param length: Returns the length of the string returned in infoLog (excluding the null terminator).
    :type length: Buffer
    :param infoLog: Specifies an array of characters that is used to return the information log.
    :type infoLog: Buffer
    """

    ...

def glGetShaderInfoLog(p0, p1, p2, p3):
    """ """

    ...

def glGetShaderSource(shader, bufSize, length: Buffer, source: Buffer):
    """Returns the source code string from a shader object`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetShaderSource.xhtml>`__

    :param shader: Specifies the shader object to be queried.
    :param bufSize: Specifies the size of the character buffer for storing the returned source code string.
    :param length: Returns the length of the string returned in source (excluding the null terminator).
    :type length: Buffer
    :param source: Specifies an array of characters that is used to return the source code string.
    :type source: Buffer
    """

    ...

def glGetShaderSource(p0, p1, p2, p3):
    """ """

    ...

def glGetShaderiv(p0, p1, p2):
    """ """

    ...

def glGetString(name: typing.Union[typing.Set[str], typing.Set[int]]):
    """Return a string describing the current GL connection`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetString.xhtml>`__

    :param name: Specifies a symbolic constant.
    :type name: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glGetString(p0) -> str:
    """

    :rtype: str
    """

    ...

def glGetStringi(p0, p1) -> str:
    """

    :rtype: str
    """

    ...

def glGetTexEnv(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: Buffer,
):
    """B{glGetTexEnvfv, glGetTexEnviv}Return texture environment parameters`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetTexEnv.xhtml>`__

    :param target: Specifies a texture environment. Must be GL_TEXTURE_ENV.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies the symbolic name of a texture environment parameter.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param params: Returns the requested data.
    :type params: Buffer
    """

    ...

def glGetTexGen(
    coord: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: Buffer,
):
    """B{glGetTexGendv, glGetTexGenfv, glGetTexGeniv}Return texture coordinate generation parameters`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetTexGen.xhtml>`__

    :param coord: Specifies a texture coordinate.
    :type coord: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies the symbolic name of the value(s) to be returned.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param params: Returns the requested data.
    :type params: Buffer
    """

    ...

def glGetTexImage(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    level,
    format: typing.Union[typing.Set[str], typing.Set[int]],
    type: typing.Union[typing.Set[str], typing.Set[int]],
    pixels: Buffer,
):
    """Return a texture image`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetTexImage.xhtml>`__

        :param target: Specifies which texture is to be obtained.
        :type target: typing.Union[typing.Set[str], typing.Set[int]]
        :param level: Specifies the level-of-detail number of the desired image.
    Level 0 is the base image level. Level n is the nth mipmap reduction image.
        :param format: Specifies a pixel format for the returned data.
        :type format: typing.Union[typing.Set[str], typing.Set[int]]
        :param type: Specifies a pixel type for the returned data.
        :type type: typing.Union[typing.Set[str], typing.Set[int]]
        :param pixels: Returns the texture image. Should be a pointer to an array of the
    type specified by type
        :type pixels: Buffer
    """

    ...

def glGetTexImage(p0, p1, p2, p3, p4: typing.Any):
    """

    :type p4: typing.Any
    """

    ...

def glGetTexLevelParameter(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    level,
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: Buffer,
):
    """B{glGetTexLevelParameterfv, glGetTexLevelParameteriv}return texture parameter values for a specific level of detail`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetTexLevelParameter.xhtml>`__

        :param target: Specifies the symbolic name of the target texture.
        :type target: typing.Union[typing.Set[str], typing.Set[int]]
        :param level: Specifies the level-of-detail number of the desired image.
    Level 0 is the base image level. Level n is the nth mipmap reduction image.
        :param pname: Specifies the symbolic name of a texture parameter.
        :type pname: typing.Union[typing.Set[str], typing.Set[int]]
        :param params: Returns the requested data.
        :type params: Buffer
    """

    ...

def glGetTexLevelParameterfv(p0, p1, p2, p3):
    """ """

    ...

def glGetTexLevelParameteriv(p0, p1, p2, p3):
    """ """

    ...

def glGetTexParameter(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params: Buffer,
):
    """B{glGetTexParameterfv, glGetTexParameteriv}Return texture parameter values`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glGetTexParameter.xhtml>`__

    :param target: Specifies the symbolic name of the target texture.
    :type target: typing.Union[typing.Set[str], typing.Set[int]]
    :param pname: Specifies the symbolic name the target texture.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param params: Returns the texture parameters.
    :type params: Buffer
    """

    ...

def glGetTexParameterfv(p0, p1, p2):
    """ """

    ...

def glGetTexParameteriv(p0, p1, p2):
    """ """

    ...

def glGetUniformBlockIndex(p0, p1: str):
    """

    :type p1: str
    """

    ...

def glGetUniformIndices(p0, p1, p2, p3):
    """ """

    ...

def glGetUniformLocation(p0, p1: str):
    """

    :type p1: str
    """

    ...

def glGetUniformfv(p0, p1, p2):
    """ """

    ...

def glGetUniformiv(p0, p1, p2):
    """ """

    ...

def glGetVertexAttribPointerv(p0, p1, p2: typing.Any):
    """

    :type p2: typing.Any
    """

    ...

def glGetVertexAttribdv(p0, p1, p2):
    """ """

    ...

def glGetVertexAttribfv(p0, p1, p2):
    """ """

    ...

def glGetVertexAttribiv(p0, p1, p2):
    """ """

    ...

def glHint(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    mode: typing.Union[typing.Set[str], typing.Set[int]],
):
    """Specify implementation-specific hints`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glHint.xhtml>`__

        :param target: Specifies a symbolic constant indicating the behavior to be
    controlled.
        :type target: typing.Union[typing.Set[str], typing.Set[int]]
        :param mode: Specifies a symbolic constant indicating the desired behavior.
        :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glHint(p0, p1):
    """ """

    ...

def glIsBuffer(p0) -> bool:
    """

    :rtype: bool
    """

    ...

def glIsEnabled(cap: typing.Union[typing.Set[str], typing.Set[int]]):
    """Test whether a capability is enabled`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glIsEnabled.xhtml>`__

    :param cap: Specifies a constant representing a GL capability.
    :type cap: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glIsEnabled(p0) -> bool:
    """

    :rtype: bool
    """

    ...

def glIsProgram(program):
    """Determines if a name corresponds to a program object`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glIsProgram.xhtml>`__

    :param program: Specifies a potential program object.
    """

    ...

def glIsProgram(p0) -> bool:
    """

    :rtype: bool
    """

    ...

def glIsQuery(p0) -> bool:
    """

    :rtype: bool
    """

    ...

def glIsShader(shader):
    """Determines if a name corresponds to a shader object.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glIsShader.xhtml>`__

    :param shader: Specifies a potential shader object.
    """

    ...

def glIsShader(p0) -> bool:
    """

    :rtype: bool
    """

    ...

def glIsTexture(texture: int):
    """Determine if a name corresponds to a texture`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glIsTexture.xhtml>`__

    :param texture: Specifies a value that may be the name of a texture.
    :type texture: int
    """

    ...

def glIsTexture(p0) -> bool:
    """

    :rtype: bool
    """

    ...

def glIsVertexArray(p0) -> bool:
    """

    :rtype: bool
    """

    ...

def glLight(
    light: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    param: typing.Any,
):
    """B{glLightf,glLighti, glLightfv, glLightiv}Set the light source parameters`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glLight.xhtml>`__

        :param light: Specifies a light. The number of lights depends on the implementation,
    but at least eight lights are supported. They are identified by symbolic names of the
    form GL_LIGHTi where 0 < i < GL_MAX_LIGHTS.
        :type light: typing.Union[typing.Set[str], typing.Set[int]]
        :param pname: Specifies a single-valued light source parameter for light.
        :type pname: typing.Union[typing.Set[str], typing.Set[int]]
        :param param: Specifies the value that parameter pname of light source light will be set to.
    If function prototype ends in 'v' specifies a pointer to the value or values that
    parameter pname of light source light will be set to.
        :type param: typing.Any
    """

    ...

def glLightModel(
    pname: typing.Union[typing.Set[str], typing.Set[int]], param: typing.Any
):
    """B{glLightModelf, glLightModeli, glLightModelfv, glLightModeliv}Set the lighting model parameters`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glLightModel.xhtml>`__

        :param pname: Specifies a single-value light model parameter.
        :type pname: typing.Union[typing.Set[str], typing.Set[int]]
        :param param: Specifies the value that param will be set to. If function prototype ends in 'v'
    specifies a pointer to the value or values that param will be set to.
        :type param: typing.Any
    """

    ...

def glLineWidth(width):
    """Specify the width of rasterized lines.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glLineWidth.xhtml>`__

    :param width: Specifies the width of rasterized lines. The initial value is 1.
    """

    ...

def glLineWidth(p0):
    """ """

    ...

def glLinkProgram(program):
    """Links a program object.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glLinkProgram.xhtml>`__

    :param program: Specifies the handle of the program object to be linked.
    """

    ...

def glLinkProgram(p0):
    """ """

    ...

def glLoadMatrix(m: Buffer):
    """B{glLoadMatrixd, glLoadMatixf}Replace the current matrix with the specified matrix`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glLoadMatrix.xhtml>`__

        :param m: Specifies a pointer to 16 consecutive values, which are used as the elements
    of a 4x4 column-major matrix.
        :type m: Buffer
    """

    ...

def glLogicOp(opcode: typing.Union[typing.Set[str], typing.Set[int]]):
    """Specify a logical pixel operation for color index rendering`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glLogicOp.xhtml>`__

    :param opcode: Specifies a symbolic constant that selects a logical operation.
    :type opcode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glLogicOp(p0):
    """ """

    ...

def glMap1(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    u1: typing.Any,
    u2,
    stride,
    order,
    points: Buffer,
):
    """B{glMap1d, glMap1f}Define a one-dimensional evaluator`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glMap1.xhtml>`__

        :param target: Specifies the kind of values that are generated by the evaluator.
        :type target: typing.Union[typing.Set[str], typing.Set[int]]
        :param u1: Specify a linear mapping of u, as presented to glEvalCoord1, to ^, t
    he variable that is evaluated by the equations specified by this command.
        :type u1: typing.Any
        :param stride: Specifies the number of floats or float (double)s between the beginning
    of one control point and the beginning of the next one in the data structure
    referenced in points. This allows control points to be embedded in arbitrary data
    structures. The only constraint is that the values for a particular control point must
    occupy contiguous memory locations.
        :param order: Specifies the number of control points. Must be positive.
        :param points: Specifies a pointer to the array of control points.
        :type points: Buffer
    """

    ...

def glMap2(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    u1: typing.Any,
    u2,
    ustride,
    uorder,
    v1: typing.Any,
    v2,
    vstride,
    vorder,
    points: Buffer,
):
    """B{glMap2d, glMap2f}Define a two-dimensional evaluator`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glMap2.xhtml>`__

        :param target: Specifies the kind of values that are generated by the evaluator.
        :type target: typing.Union[typing.Set[str], typing.Set[int]]
        :param u1: Specify a linear mapping of u, as presented to glEvalCoord2, to ^, t
    he variable that is evaluated by the equations specified by this command. Initially
    u1 is 0 and u2 is 1.
        :type u1: typing.Any
        :param ustride: Specifies the number of floats or float (double)s between the beginning
    of control point R and the beginning of control point R ij, where i and j are the u
    and v control point indices, respectively. This allows control points to be embedded
    in arbitrary data structures. The only constraint is that the values for a particular
    control point must occupy contiguous memory locations. The initial value of ustride is 0.
        :param uorder: Specifies the dimension of the control point array in the u axis.
    Must be positive. The initial value is 1.
        :param v1: Specify a linear mapping of v, as presented to glEvalCoord2,
    to ^, one of the two variables that are evaluated by the equations
    specified by this command. Initially, v1 is 0 and v2 is 1.
        :type v1: typing.Any
        :param vstride: Specifies the number of floats or float (double)s between the
    beginning of control point R and the beginning of control point R ij,
    where i and j are the u and v control point(indices, respectively.
    This allows control points to be embedded in arbitrary data structures.
    The only constraint is that the values for a particular control point must
    occupy contiguous memory locations. The initial value of vstride is 0.
        :param vorder: Specifies the dimension of the control point array in the v axis.
    Must be positive. The initial value is 1.
        :param points: Specifies a pointer to the array of control points.
        :type points: Buffer
    """

    ...

def glMapBuffer(p0, p1):
    """ """

    ...

def glMapGrid(un, u1: typing.Any, u2, vn, v1: typing.Any, v2):
    """B{glMapGrid1d, glMapGrid1f, glMapGrid2d, glMapGrid2f}Define a one- or two-dimensional mesh`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glMapGrid.xhtml>`__

        :param un: Specifies the number of partitions in the grid range interval
    [u1, u2]. Must be positive.
        :param u1: Specify the mappings for integer grid domain values i=0 and i=un.
        :type u1: typing.Any
        :param vn: Specifies the number of partitions in the grid range interval
    [v1, v2] (glMapGrid2 only).
        :param v1: Specify the mappings for integer grid domain values j=0 and j=vn
    (glMapGrid2 only).
        :type v1: typing.Any
    """

    ...

def glMaterial(
    face: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    params,
):
    """Specify material parameters for the lighting model.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glMaterial.xhtml>`__

        :param face: Specifies which face or faces are being updated. Must be one of:
        :type face: typing.Union[typing.Set[str], typing.Set[int]]
        :param pname: Specifies the single-valued material parameter of the face
    or faces that is being updated. Must be GL_SHININESS.
        :type pname: typing.Union[typing.Set[str], typing.Set[int]]
        :param params: Specifies the value that parameter GL_SHININESS will be set to.
    If function prototype ends in 'v' specifies a pointer to the value or values that
    pname will be set to.
    """

    ...

def glMultMatrix(m: Buffer):
    """B{glMultMatrixd, glMultMatrixf}Multiply the current matrix with the specified matrix`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glMultMatrix.xhtml>`__

        :param m: Points to 16 consecutive values that are used as the elements of a 4x4 column
    major matrix.
        :type m: Buffer
    """

    ...

def glNormal3(nx: typing.Any, ny, nz, v: Buffer):
    """B{Normal3b, Normal3bv, Normal3d, Normal3dv, Normal3f, Normal3fv, Normal3i, Normal3iv,
    Normal3s, Normal3sv}Set the current normal vector`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glNormal.xhtml>`__

        :param nx: Specify the x, y, and z coordinates of the new current normal.
    The initial value of the current normal is the unit vector, (0, 0, 1).
        :type nx: typing.Any
        :param v: Specifies a pointer to an array of three elements: the x, y, and z coordinates
    of the new current normal.
        :type v: Buffer
    """

    ...

def glPixelMap(
    map: typing.Union[typing.Set[str], typing.Set[int]], mapsize, values: Buffer
):
    """B{glPixelMapfv, glPixelMapuiv, glPixelMapusv}Set up pixel transfer maps`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glPixelMap.xhtml>`__

    :param map: Specifies a symbolic map name.
    :type map: typing.Union[typing.Set[str], typing.Set[int]]
    :param mapsize: Specifies the size of the map being defined.
    :param values: Specifies an array of mapsize values.
    :type values: Buffer
    """

    ...

def glPixelStore(
    pname: typing.Union[typing.Set[str], typing.Set[int]], param: typing.Any
):
    """B{glPixelStoref, glPixelStorei}Set pixel storage modes`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glPixelStore.xhtml>`__

        :param pname: Specifies the symbolic name of the parameter to be set.
    Six values affect the packing of pixel data into memory.
    Six more affect the unpacking of pixel data from memory.
        :type pname: typing.Union[typing.Set[str], typing.Set[int]]
        :param param: Specifies the value that pname is set to.
        :type param: typing.Any
    """

    ...

def glPixelStoref(p0, p1):
    """ """

    ...

def glPixelStorei(p0, p1):
    """ """

    ...

def glPixelTransfer(
    pname: typing.Union[typing.Set[str], typing.Set[int]], param: typing.Any
):
    """B{glPixelTransferf, glPixelTransferi}Set pixel transfer modes`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glPixelTransfer.xhtml>`__

    :param pname: Specifies the symbolic name of the pixel transfer parameter to be set.
    :type pname: typing.Union[typing.Set[str], typing.Set[int]]
    :param param: Specifies the value that pname is set to.
    :type param: typing.Any
    """

    ...

def glPointSize(size):
    """Specify the diameter of rasterized points`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glPointSize.xhtml>`__

    :param size: Specifies the diameter of rasterized points. The initial value is 1.
    """

    ...

def glPointSize(p0):
    """ """

    ...

def glPolygonMode(
    face: typing.Union[typing.Set[str], typing.Set[int]],
    mode: typing.Union[typing.Set[str], typing.Set[int]],
):
    """Select a polygon rasterization mode`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glPolygonMode.xhtml>`__

        :param face: Specifies the polygons that mode applies to.
    Must be GL_FRONT for front-facing polygons, GL_BACK for back- facing
    polygons, or GL_FRONT_AND_BACK for front- and back-facing polygons.
        :type face: typing.Union[typing.Set[str], typing.Set[int]]
        :param mode: Specifies how polygons will be rasterized.
    The initial value is GL_FILL for both front- and back- facing polygons.
        :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glPolygonMode(p0, p1):
    """ """

    ...

def glPolygonOffset(factor, units):
    """Set the scale and units used to calculate depth values`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glPolygonOffset.xhtml>`__

        :param factor: Specifies a scale factor that is used to create a variable depth
    offset for each polygon. The initial value is 0.
        :param units: Is multiplied by an implementation-specific value to create a
    constant depth offset. The initial value is 0.
    """

    ...

def glPolygonOffset(p0, p1):
    """ """

    ...

def glRasterPos(x: typing.Any, y, z, w):
    """B{glRasterPos2d, glRasterPos2f, glRasterPos2i, glRasterPos2s, glRasterPos3d,
    glRasterPos3f, glRasterPos3i, glRasterPos3s, glRasterPos4d, glRasterPos4f,
    glRasterPos4i, glRasterPos4s, glRasterPos2dv, glRasterPos2fv, glRasterPos2iv,
    glRasterPos2sv, glRasterPos3dv, glRasterPos3fv, glRasterPos3iv, glRasterPos3sv,
    glRasterPos4dv, glRasterPos4fv, glRasterPos4iv, glRasterPos4sv}Specify the raster position for pixel operations`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glRasterPos.xhtml>`__

        :param x: Specify the x,y,z, and w object coordinates (if present) for the
    raster position.  If function prototype ends in 'v' specifies a pointer to an array of two,
    three, or four elements, specifying x, y, z, and w coordinates, respectively.
        :type x: typing.Any
    """

    ...

def glReadBuffer(mode: typing.Union[typing.Set[str], typing.Set[int]]):
    """Select a color buffer source for pixels.`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glReadBuffer.xhtml>`__

    :param mode: Specifies a color buffer.
    :type mode: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glReadBuffer(p0):
    """ """

    ...

def glReadPixels(
    x,
    y,
    width,
    height,
    format: typing.Union[typing.Set[str], typing.Set[int]],
    type: typing.Union[typing.Set[str], typing.Set[int]],
    pixels: Buffer,
):
    """Read a block of pixels from the frame buffer`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glReadPixels.xhtml>`__

        :param x: Specify the window coordinates of the first pixel that is read
    from the frame buffer. This location is the lower left corner of a rectangular
    block of pixels.
        :param width: Specify the dimensions of the pixel rectangle. width and
    height of one correspond to a single pixel.
        :param format: Specifies the format of the pixel data.
        :type format: typing.Union[typing.Set[str], typing.Set[int]]
        :param type: Specifies the data type of the pixel data.
        :type type: typing.Union[typing.Set[str], typing.Set[int]]
        :param pixels: Returns the pixel data.
        :type pixels: Buffer
    """

    ...

def glReadPixels(p0, p1, p2, p3, p4, p5, p6: typing.Any):
    """

    :type p6: typing.Any
    """

    ...

def glRect(x1: typing.Any, y1, x2: typing.Any, y2, v1: typing.Any, v2):
    """B{glRectd, glRectf, glRecti, glRects, glRectdv, glRectfv, glRectiv, glRectsv}Draw a rectangle`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glRect.xhtml>`__

        :param x1: Specify one vertex of a rectangle
        :type x1: typing.Any
        :param x2: Specify the opposite vertex of the rectangle
        :type x2: typing.Any
        :param v1: Specifies a pointer to one vertex of a rectangle and the pointer
    to the opposite vertex of the rectangle
        :type v1: typing.Any
    """

    ...

def glRenderbufferStorage(p0, p1, p2, p3):
    """ """

    ...

def glRotate(angle: typing.Any, x: typing.Any, y, z):
    """B{glRotated, glRotatef}Multiply the current matrix by a rotation matrix`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glRotate.xhtml>`__

    :param angle: Specifies the angle of rotation in degrees.
    :type angle: typing.Any
    :param x: Specify the x, y, and z coordinates of a vector respectively.
    :type x: typing.Any
    """

    ...

def glSampleCoverage(p0, p1: bool):
    """

    :type p1: bool
    """

    ...

def glSampleMaski(p0, p1):
    """ """

    ...

def glScale(x: typing.Any, y, z):
    """B{glScaled, glScalef}Multiply the current matrix by a general scaling matrix`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glScale.xhtml>`__

    :param x: Specify scale factors along the x, y, and z axes, respectively.
    :type x: typing.Any
    """

    ...

def glScissor(x, y, width, height):
    """Define the scissor box`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glScissor.xhtml>`__

        :param x: Specify the lower left corner of the scissor box. Initially (0, 0).
        :param width: Specify the width and height of the scissor box. When a
    GL context is first attached to a window, width and height are set to the
    dimensions of that window.
    """

    ...

def glScissor(p0, p1, p2, p3):
    """ """

    ...

def glShaderSource(shader, shader_string: str):
    """Replaces the source code in a shader object.`OpenGL Docs <https://www.opengl.org/sdk/docs/man/html/glShaderSource.xhtml>`__

    :param shader: Specifies the handle of the shader object whose source code is to be replaced.
    :param shader_string: The shader string.
    :type shader_string: str
    """

    ...

def glStencilFunc(func: typing.Union[typing.Set[str], typing.Set[int]], ref, mask: int):
    """Set function and reference value for stencil testing`OpenGL Docs <https://www.opengl.org/sdk/docs/man/docbook4/xhtml/glStencilFunc.xhtml>`__

        :param func: Specifies the test function.
        :type func: typing.Union[typing.Set[str], typing.Set[int]]
        :param ref: Specifies the reference value for the stencil test. ref is clamped
    to the range [0,2n-1], where n is the number of bitplanes in the stencil
    buffer. The initial value is 0.
        :param mask: Specifies a mask that is ANDed with both the reference value and
    the stored stencil value when the test is done. The initial value is all 1's.
        :type mask: int
    """

    ...

def glStencilFunc(p0, p1, p2):
    """ """

    ...

def glStencilFuncSeparate(p0, p1, p2, p3):
    """ """

    ...

def glStencilMask(mask: int):
    """Control the writing of individual bits in the stencil planes`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glStencilMask.xhtml>`__

        :param mask: Specifies a bit mask to enable and disable writing of individual bits
    in the stencil planes. Initially, the mask is all 1's.
        :type mask: int
    """

    ...

def glStencilMask(p0):
    """ """

    ...

def glStencilMaskSeparate(p0, p1):
    """ """

    ...

def glStencilOp(
    fail: typing.Union[typing.Set[str], typing.Set[int]],
    zfail: typing.Union[typing.Set[str], typing.Set[int]],
    zpass: typing.Union[typing.Set[str], typing.Set[int]],
):
    """Set stencil test actions`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glStencilOp.xhtml>`__

        :param fail: Specifies the action to take when the stencil test fails.
    The initial value is GL_KEEP.
        :type fail: typing.Union[typing.Set[str], typing.Set[int]]
        :param zfail: Specifies the stencil action when the stencil test passes, but the
    depth test fails. zfail accepts the same symbolic constants as fail.
    The initial value is GL_KEEP.
        :type zfail: typing.Union[typing.Set[str], typing.Set[int]]
        :param zpass: Specifies the stencil action when both the stencil test and the
    depth test pass, or when the stencil test passes and either there is no
    depth buffer or depth testing is not enabled. zpass accepts the same
    symbolic constants
    as fail. The initial value is GL_KEEP.
        :type zpass: typing.Union[typing.Set[str], typing.Set[int]]
    """

    ...

def glStencilOp(p0, p1, p2):
    """ """

    ...

def glStencilOpSeparate(p0, p1, p2, p3):
    """ """

    ...

def glTexCoord(s: typing.Any, t, r, q, v: Buffer):
    """B{glTexCoord1d, glTexCoord1f, glTexCoord1i, glTexCoord1s, glTexCoord2d, glTexCoord2f,
    glTexCoord2i, glTexCoord2s, glTexCoord3d, glTexCoord3f, glTexCoord3i, glTexCoord3s,
    glTexCoord4d, glTexCoord4f, glTexCoord4i, glTexCoord4s, glTexCoord1dv, glTexCoord1fv,
    glTexCoord1iv, glTexCoord1sv, glTexCoord2dv, glTexCoord2fv, glTexCoord2iv,
    glTexCoord2sv, glTexCoord3dv, glTexCoord3fv, glTexCoord3iv, glTexCoord3sv,
    glTexCoord4dv, glTexCoord4fv, glTexCoord4iv, glTexCoord4sv}Set the current texture coordinates`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glTexCoord.xhtml>`__

        :param s: Specify s, t, r, and q texture coordinates. Not all parameters are
    present in all forms of the command.
        :type s: typing.Any
        :param v: Specifies a pointer to an array of one, two, three, or four elements,
    which in turn specify the s, t, r, and q texture coordinates.
        :type v: Buffer
    """

    ...

def glTexEnv(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    param: typing.Any,
):
    """B{glTextEnvf, glTextEnvi, glTextEnvfv, glTextEnviv}Set texture environment parameters`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glTexEnv.xhtml>`__

        :param target: Specifies a texture environment. Must be GL_TEXTURE_ENV.
        :type target: typing.Union[typing.Set[str], typing.Set[int]]
        :param pname: Specifies the symbolic name of a single-valued texture environment
    parameter. Must be GL_TEXTURE_ENV_MODE.
        :type pname: typing.Union[typing.Set[str], typing.Set[int]]
        :param param: Specifies a single symbolic constant. If function prototype ends in 'v'
    specifies a pointer to a parameter array that contains either a single
    symbolic constant or an RGBA color
        :type param: typing.Any
    """

    ...

def glTexGen(
    coord: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    param: typing.Any,
):
    """B{glTexGend, glTexGenf, glTexGeni, glTexGendv, glTexGenfv, glTexGeniv}Control the generation of texture coordinates`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glTexGen.xhtml>`__

        :param coord: Specifies a texture coordinate.
        :type coord: typing.Union[typing.Set[str], typing.Set[int]]
        :param pname: Specifies the symbolic name of the texture- coordinate generation function.
        :type pname: typing.Union[typing.Set[str], typing.Set[int]]
        :param param: Specifies a single-valued texture generation parameter.
    If function prototype ends in 'v' specifies a pointer to an array of texture
    generation parameters. If pname is GL_TEXTURE_GEN_MODE, then the array must
    contain a single symbolic constant. Otherwise, params holds the coefficients
    for the texture-coordinate generation function specified by pname.
        :type param: typing.Any
    """

    ...

def glTexImage1D(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    level,
    internalformat,
    width,
    border,
    format: typing.Union[typing.Set[str], typing.Set[int]],
    type: typing.Union[typing.Set[str], typing.Set[int]],
    pixels: Buffer,
):
    """Specify a one-dimensional texture image`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glTexImage1D.xhtml>`__

        :param target: Specifies the target texture.
        :type target: typing.Union[typing.Set[str], typing.Set[int]]
        :param level: Specifies the level-of-detail number. Level 0 is the base image level.
    Level n is the nth mipmap reduction image.
        :param internalformat: Specifies the number of color components in the texture.
        :param width: Specifies the width of the texture image. Must be 2n+2(border)
    for some integer n. All implementations support texture images that are
    at least 64 texels wide. The height of the 1D texture image is 1.
        :param border: Specifies the width of the border. Must be either 0 or 1.
        :param format: Specifies the format of the pixel data.
        :type format: typing.Union[typing.Set[str], typing.Set[int]]
        :param type: Specifies the data type of the pixel data.
        :type type: typing.Union[typing.Set[str], typing.Set[int]]
        :param pixels: Specifies a pointer to the image data in memory.
        :type pixels: Buffer
    """

    ...

def glTexImage1D(p0, p1, p2, p3, p4, p5, p6, p7: typing.Any):
    """

    :type p7: typing.Any
    """

    ...

def glTexImage2D(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    level,
    internalformat,
    width,
    height,
    border,
    format: typing.Union[typing.Set[str], typing.Set[int]],
    type: typing.Union[typing.Set[str], typing.Set[int]],
    pixels: Buffer,
):
    """Specify a two-dimensional texture image`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glTexImage2D.xhtml>`__

        :param target: Specifies the target texture.
        :type target: typing.Union[typing.Set[str], typing.Set[int]]
        :param level: Specifies the level-of-detail number. Level 0 is the base image level.
    Level n is the nth mipmap reduction image.
        :param internalformat: Specifies the number of color components in the texture.
        :param width: Specifies the width of the texture image. Must be 2n+2(border)
    for some integer n. All implementations support texture images that are at
    least 64 texels wide.
        :param height: Specifies the height of the texture image. Must be 2m+2(border) for
    some integer m. All implementations support texture images that are at
    least 64 texels high.
        :param border: Specifies the width of the border. Must be either 0 or 1.
        :param format: Specifies the format of the pixel data.
        :type format: typing.Union[typing.Set[str], typing.Set[int]]
        :param type: Specifies the data type of the pixel data.
        :type type: typing.Union[typing.Set[str], typing.Set[int]]
        :param pixels: Specifies a pointer to the image data in memory.
        :type pixels: Buffer
    """

    ...

def glTexImage2D(p0, p1, p2, p3, p4, p5, p6, p7, p8: typing.Any):
    """

    :type p8: typing.Any
    """

    ...

def glTexImage2DMultisample(p0, p1, p2, p3, p4, p5: bool):
    """

    :type p5: bool
    """

    ...

def glTexImage3D(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9: typing.Any):
    """

    :type p9: typing.Any
    """

    ...

def glTexImage3DMultisample(p0, p1, p2, p3, p4, p5, p6: bool):
    """

    :type p6: bool
    """

    ...

def glTexParameter(
    target: typing.Union[typing.Set[str], typing.Set[int]],
    pname: typing.Union[typing.Set[str], typing.Set[int]],
    param: typing.Any,
):
    """B{glTexParameterf, glTexParameteri, glTexParameterfv, glTexParameteriv}Set texture parameters`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glTexParameter.xhtml>`__

        :param target: Specifies the target texture.
        :type target: typing.Union[typing.Set[str], typing.Set[int]]
        :param pname: Specifies the symbolic name of a single-valued texture parameter.
        :type pname: typing.Union[typing.Set[str], typing.Set[int]]
        :param param: Specifies the value of pname. If function prototype ends in 'v' specifies
    a pointer to an array where the value or values of pname are stored.
        :type param: typing.Any
    """

    ...

def glTexParameterf(p0, p1, p2):
    """ """

    ...

def glTexParameterfv(p0, p1, p2):
    """ """

    ...

def glTexParameteri(p0, p1, p2):
    """ """

    ...

def glTexParameteriv(p0, p1, p2):
    """ """

    ...

def glTexSubImage1D(p0, p1, p2, p3, p4, p5, p6: typing.Any):
    """

    :type p6: typing.Any
    """

    ...

def glTexSubImage2D(p0, p1, p2, p3, p4, p5, p6, p7, p8: typing.Any):
    """

    :type p8: typing.Any
    """

    ...

def glTexSubImage3D(p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10: typing.Any):
    """

    :type p10: typing.Any
    """

    ...

def glTranslate(x: typing.Any, y, z):
    """B{glTranslatef, glTranslated}Multiply the current matrix by a translation matrix`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glTranslate.xhtml>`__

    :param x: Specify the x, y, and z coordinates of a translation vector.
    :type x: typing.Any
    """

    ...

def glUniform1f(p0, p1):
    """ """

    ...

def glUniform1fv(p0, p1, p2):
    """ """

    ...

def glUniform1i(p0, p1):
    """ """

    ...

def glUniform1iv(p0, p1, p2):
    """ """

    ...

def glUniform2f(p0, p1, p2):
    """ """

    ...

def glUniform2fv(p0, p1, p2):
    """ """

    ...

def glUniform2i(p0, p1, p2):
    """ """

    ...

def glUniform2iv(p0, p1, p2):
    """ """

    ...

def glUniform3f(p0, p1, p2, p3):
    """ """

    ...

def glUniform3fv(p0, p1, p2):
    """ """

    ...

def glUniform3i(p0, p1, p2, p3):
    """ """

    ...

def glUniform3iv(p0, p1, p2):
    """ """

    ...

def glUniform4f(p0, p1, p2, p3, p4):
    """ """

    ...

def glUniform4fv(p0, p1, p2):
    """ """

    ...

def glUniform4i(p0, p1, p2, p3, p4):
    """ """

    ...

def glUniform4iv(p0, p1, p2):
    """ """

    ...

def glUniformBlockBinding(p0, p1, p2):
    """ """

    ...

def glUniformMatrix2fv(p0, p1, p2: bool, p3):
    """

    :type p2: bool
    """

    ...

def glUniformMatrix2x3fv(p0, p1, p2: bool, p3):
    """

    :type p2: bool
    """

    ...

def glUniformMatrix2x4fv(p0, p1, p2: bool, p3):
    """

    :type p2: bool
    """

    ...

def glUniformMatrix3fv(p0, p1, p2: bool, p3):
    """

    :type p2: bool
    """

    ...

def glUniformMatrix3x2fv(p0, p1, p2: bool, p3):
    """

    :type p2: bool
    """

    ...

def glUniformMatrix3x4fv(p0, p1, p2: bool, p3):
    """

    :type p2: bool
    """

    ...

def glUniformMatrix4fv(p0, p1, p2: bool, p3):
    """

    :type p2: bool
    """

    ...

def glUniformMatrix4x2fv(p0, p1, p2: bool, p3):
    """

    :type p2: bool
    """

    ...

def glUniformMatrix4x3fv(p0, p1, p2: bool, p3):
    """

    :type p2: bool
    """

    ...

def glUnmapBuffer(p0) -> bool:
    """

    :rtype: bool
    """

    ...

def glUseProgram(program):
    """Installs a program object as part of current rendering state`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glUseProgram.xhtml>`__

    :param program: Specifies the handle of the program object whose executables are to be used as part of current rendering state.
    """

    ...

def glUseProgram(p0):
    """ """

    ...

def glValidateProgram(program):
    """Validates a program object`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glValidateProgram.xhtml>`__

    :param program: Specifies the handle of the program object to be validated.
    """

    ...

def glValidateProgram(p0):
    """ """

    ...

def glVertexAttrib1d(p0, p1):
    """ """

    ...

def glVertexAttrib1dv(p0, p1):
    """ """

    ...

def glVertexAttrib1f(p0, p1):
    """ """

    ...

def glVertexAttrib1fv(p0, p1):
    """ """

    ...

def glVertexAttrib1s(p0, p1):
    """ """

    ...

def glVertexAttrib1sv(p0, p1):
    """ """

    ...

def glVertexAttrib2d(p0, p1, p2):
    """ """

    ...

def glVertexAttrib2dv(p0, p1):
    """ """

    ...

def glVertexAttrib2f(p0, p1, p2):
    """ """

    ...

def glVertexAttrib2fv(p0, p1):
    """ """

    ...

def glVertexAttrib2s(p0, p1, p2):
    """ """

    ...

def glVertexAttrib2sv(p0, p1):
    """ """

    ...

def glVertexAttrib3d(p0, p1, p2, p3):
    """ """

    ...

def glVertexAttrib3dv(p0, p1):
    """ """

    ...

def glVertexAttrib3f(p0, p1, p2, p3):
    """ """

    ...

def glVertexAttrib3fv(p0, p1):
    """ """

    ...

def glVertexAttrib3s(p0, p1, p2, p3):
    """ """

    ...

def glVertexAttrib3sv(p0, p1):
    """ """

    ...

def glVertexAttrib4Nbv(p0, p1):
    """ """

    ...

def glVertexAttrib4Niv(p0, p1):
    """ """

    ...

def glVertexAttrib4Nsv(p0, p1):
    """ """

    ...

def glVertexAttrib4Nub(p0, p1, p2, p3, p4):
    """ """

    ...

def glVertexAttrib4Nubv(p0, p1):
    """ """

    ...

def glVertexAttrib4Nuiv(p0, p1):
    """ """

    ...

def glVertexAttrib4Nusv(p0, p1):
    """ """

    ...

def glVertexAttrib4bv(p0, p1):
    """ """

    ...

def glVertexAttrib4d(p0, p1, p2, p3, p4):
    """ """

    ...

def glVertexAttrib4dv(p0, p1):
    """ """

    ...

def glVertexAttrib4f(p0, p1, p2, p3, p4):
    """ """

    ...

def glVertexAttrib4fv(p0, p1):
    """ """

    ...

def glVertexAttrib4iv(p0, p1):
    """ """

    ...

def glVertexAttrib4s(p0, p1, p2, p3, p4):
    """ """

    ...

def glVertexAttrib4sv(p0, p1):
    """ """

    ...

def glVertexAttrib4ubv(p0, p1):
    """ """

    ...

def glVertexAttrib4uiv(p0, p1):
    """ """

    ...

def glVertexAttrib4usv(p0, p1):
    """ """

    ...

def glVertexAttribIPointer(p0, p1, p2, p3, p4: typing.Any):
    """

    :type p4: typing.Any
    """

    ...

def glVertexAttribPointer(p0, p1, p2, p3: bool, p4, p5: typing.Any):
    """

    :type p3: bool
    :type p5: typing.Any
    """

    ...

def glViewport(x, y, width, height):
    """Set the viewport`OpenGL Docs <https://khronos.org/registry/OpenGL-Refpages/gl4/html/glViewport.xhtml>`__

        :param x: Specify the lower left corner of the viewport rectangle,
    in pixels. The initial value is (0,0).
        :param width: Specify the width and height of the viewport. When a GL
    context is first attached to a window, width and height are set to the
    dimensions of that window.
    """

    ...

def glViewport(p0, p1, p2, p3):
    """ """

    ...

GL_ACTIVE_ATTRIBUTES: typing.Any
""" 
"""

GL_ACTIVE_ATTRIBUTE_MAX_LENGTH: typing.Any
""" 
"""

GL_ACTIVE_TEXTURE: typing.Any
""" 
"""

GL_ACTIVE_UNIFORMS: typing.Any
""" 
"""

GL_ACTIVE_UNIFORM_BLOCKS: typing.Any
""" 
"""

GL_ACTIVE_UNIFORM_BLOCK_MAX_NAME_LENGTH: typing.Any
""" 
"""

GL_ACTIVE_UNIFORM_MAX_LENGTH: typing.Any
""" 
"""

GL_ALIASED_LINE_WIDTH_RANGE: typing.Any
""" 
"""

GL_ALPHA: typing.Any
""" 
"""

GL_ALREADY_SIGNALED: typing.Any
""" 
"""

GL_ALWAYS: typing.Any
""" 
"""

GL_AND: typing.Any
""" 
"""

GL_AND_INVERTED: typing.Any
""" 
"""

GL_AND_REVERSE: typing.Any
""" 
"""

GL_ANY_SAMPLES_PASSED: typing.Any
""" 
"""

GL_ARRAY_BUFFER: typing.Any
""" 
"""

GL_ARRAY_BUFFER_BINDING: typing.Any
""" 
"""

GL_ATTACHED_SHADERS: typing.Any
""" 
"""

GL_BACK: typing.Any
""" 
"""

GL_BACK_LEFT: typing.Any
""" 
"""

GL_BACK_RIGHT: typing.Any
""" 
"""

GL_BGR: typing.Any
""" 
"""

GL_BGRA: typing.Any
""" 
"""

GL_BGRA_INTEGER: typing.Any
""" 
"""

GL_BGR_INTEGER: typing.Any
""" 
"""

GL_BLEND: typing.Any
""" 
"""

GL_BLEND_DST: typing.Any
""" 
"""

GL_BLEND_DST_ALPHA: typing.Any
""" 
"""

GL_BLEND_DST_RGB: typing.Any
""" 
"""

GL_BLEND_EQUATION_ALPHA: typing.Any
""" 
"""

GL_BLEND_EQUATION_RGB: typing.Any
""" 
"""

GL_BLEND_SRC: typing.Any
""" 
"""

GL_BLEND_SRC_ALPHA: typing.Any
""" 
"""

GL_BLEND_SRC_RGB: typing.Any
""" 
"""

GL_BLUE: typing.Any
""" 
"""

GL_BLUE_INTEGER: typing.Any
""" 
"""

GL_BOOL: typing.Any
""" 
"""

GL_BOOL_VEC2: typing.Any
""" 
"""

GL_BOOL_VEC3: typing.Any
""" 
"""

GL_BOOL_VEC4: typing.Any
""" 
"""

GL_BUFFER_ACCESS: typing.Any
""" 
"""

GL_BUFFER_ACCESS_FLAGS: typing.Any
""" 
"""

GL_BUFFER_MAPPED: typing.Any
""" 
"""

GL_BUFFER_MAP_LENGTH: typing.Any
""" 
"""

GL_BUFFER_MAP_OFFSET: typing.Any
""" 
"""

GL_BUFFER_MAP_POINTER: typing.Any
""" 
"""

GL_BUFFER_SIZE: typing.Any
""" 
"""

GL_BUFFER_USAGE: typing.Any
""" 
"""

GL_BYTE: typing.Any
""" 
"""

GL_CCW: typing.Any
""" 
"""

GL_CLAMP_READ_COLOR: typing.Any
""" 
"""

GL_CLAMP_TO_BORDER: typing.Any
""" 
"""

GL_CLAMP_TO_EDGE: typing.Any
""" 
"""

GL_CLEAR: typing.Any
""" 
"""

GL_CLIP_DISTANCE0: typing.Any
""" 
"""

GL_CLIP_DISTANCE1: typing.Any
""" 
"""

GL_CLIP_DISTANCE2: typing.Any
""" 
"""

GL_CLIP_DISTANCE3: typing.Any
""" 
"""

GL_CLIP_DISTANCE4: typing.Any
""" 
"""

GL_CLIP_DISTANCE5: typing.Any
""" 
"""

GL_CLIP_DISTANCE6: typing.Any
""" 
"""

GL_CLIP_DISTANCE7: typing.Any
""" 
"""

GL_COLOR: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT0: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT1: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT10: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT11: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT12: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT13: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT14: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT15: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT16: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT17: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT18: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT19: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT2: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT20: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT21: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT22: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT23: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT24: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT25: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT26: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT27: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT28: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT29: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT3: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT30: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT31: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT4: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT5: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT6: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT7: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT8: typing.Any
""" 
"""

GL_COLOR_ATTACHMENT9: typing.Any
""" 
"""

GL_COLOR_BUFFER_BIT: typing.Any
""" 
"""

GL_COLOR_CLEAR_VALUE: typing.Any
""" 
"""

GL_COLOR_LOGIC_OP: typing.Any
""" 
"""

GL_COLOR_WRITEMASK: typing.Any
""" 
"""

GL_COMPARE_REF_TO_TEXTURE: typing.Any
""" 
"""

GL_COMPILE_STATUS: typing.Any
""" 
"""

GL_COMPRESSED_RED: typing.Any
""" 
"""

GL_COMPRESSED_RED_RGTC1: typing.Any
""" 
"""

GL_COMPRESSED_RG: typing.Any
""" 
"""

GL_COMPRESSED_RGB: typing.Any
""" 
"""

GL_COMPRESSED_RGBA: typing.Any
""" 
"""

GL_COMPRESSED_RG_RGTC2: typing.Any
""" 
"""

GL_COMPRESSED_SIGNED_RED_RGTC1: typing.Any
""" 
"""

GL_COMPRESSED_SIGNED_RG_RGTC2: typing.Any
""" 
"""

GL_COMPRESSED_SRGB: typing.Any
""" 
"""

GL_COMPRESSED_SRGB_ALPHA: typing.Any
""" 
"""

GL_COMPRESSED_TEXTURE_FORMATS: typing.Any
""" 
"""

GL_CONDITION_SATISFIED: typing.Any
""" 
"""

GL_CONSTANT_ALPHA: typing.Any
""" 
"""

GL_CONSTANT_COLOR: typing.Any
""" 
"""

GL_CONTEXT_COMPATIBILITY_PROFILE_BIT: typing.Any
""" 
"""

GL_CONTEXT_CORE_PROFILE_BIT: typing.Any
""" 
"""

GL_CONTEXT_FLAGS: typing.Any
""" 
"""

GL_CONTEXT_FLAG_FORWARD_COMPATIBLE_BIT: typing.Any
""" 
"""

GL_CONTEXT_PROFILE_MASK: typing.Any
""" 
"""

GL_COPY: typing.Any
""" 
"""

GL_COPY_INVERTED: typing.Any
""" 
"""

GL_COPY_READ_BUFFER: typing.Any
""" 
"""

GL_COPY_WRITE_BUFFER: typing.Any
""" 
"""

GL_CULL_FACE: typing.Any
""" 
"""

GL_CULL_FACE_MODE: typing.Any
""" 
"""

GL_CURRENT_PROGRAM: typing.Any
""" 
"""

GL_CURRENT_QUERY: typing.Any
""" 
"""

GL_CURRENT_VERTEX_ATTRIB: typing.Any
""" 
"""

GL_CW: typing.Any
""" 
"""

GL_DECR: typing.Any
""" 
"""

GL_DECR_WRAP: typing.Any
""" 
"""

GL_DELETE_STATUS: typing.Any
""" 
"""

GL_DEPTH: typing.Any
""" 
"""

GL_DEPTH24_STENCIL8: typing.Any
""" 
"""

GL_DEPTH32F_STENCIL8: typing.Any
""" 
"""

GL_DEPTH_ATTACHMENT: typing.Any
""" 
"""

GL_DEPTH_BUFFER_BIT: typing.Any
""" 
"""

GL_DEPTH_CLAMP: typing.Any
""" 
"""

GL_DEPTH_CLEAR_VALUE: typing.Any
""" 
"""

GL_DEPTH_COMPONENT: typing.Any
""" 
"""

GL_DEPTH_COMPONENT16: typing.Any
""" 
"""

GL_DEPTH_COMPONENT24: typing.Any
""" 
"""

GL_DEPTH_COMPONENT32: typing.Any
""" 
"""

GL_DEPTH_COMPONENT32F: typing.Any
""" 
"""

GL_DEPTH_FUNC: typing.Any
""" 
"""

GL_DEPTH_RANGE: typing.Any
""" 
"""

GL_DEPTH_STENCIL: typing.Any
""" 
"""

GL_DEPTH_STENCIL_ATTACHMENT: typing.Any
""" 
"""

GL_DEPTH_TEST: typing.Any
""" 
"""

GL_DEPTH_WRITEMASK: typing.Any
""" 
"""

GL_DITHER: typing.Any
""" 
"""

GL_DONT_CARE: typing.Any
""" 
"""

GL_DOUBLE: typing.Any
""" 
"""

GL_DOUBLEBUFFER: typing.Any
""" 
"""

GL_DRAW_BUFFER: typing.Any
""" 
"""

GL_DRAW_BUFFER0: typing.Any
""" 
"""

GL_DRAW_BUFFER1: typing.Any
""" 
"""

GL_DRAW_BUFFER10: typing.Any
""" 
"""

GL_DRAW_BUFFER11: typing.Any
""" 
"""

GL_DRAW_BUFFER12: typing.Any
""" 
"""

GL_DRAW_BUFFER13: typing.Any
""" 
"""

GL_DRAW_BUFFER14: typing.Any
""" 
"""

GL_DRAW_BUFFER15: typing.Any
""" 
"""

GL_DRAW_BUFFER2: typing.Any
""" 
"""

GL_DRAW_BUFFER3: typing.Any
""" 
"""

GL_DRAW_BUFFER4: typing.Any
""" 
"""

GL_DRAW_BUFFER5: typing.Any
""" 
"""

GL_DRAW_BUFFER6: typing.Any
""" 
"""

GL_DRAW_BUFFER7: typing.Any
""" 
"""

GL_DRAW_BUFFER8: typing.Any
""" 
"""

GL_DRAW_BUFFER9: typing.Any
""" 
"""

GL_DRAW_FRAMEBUFFER: typing.Any
""" 
"""

GL_DRAW_FRAMEBUFFER_BINDING: typing.Any
""" 
"""

GL_DST_ALPHA: typing.Any
""" 
"""

GL_DST_COLOR: typing.Any
""" 
"""

GL_DYNAMIC_COPY: typing.Any
""" 
"""

GL_DYNAMIC_DRAW: typing.Any
""" 
"""

GL_DYNAMIC_READ: typing.Any
""" 
"""

GL_ELEMENT_ARRAY_BUFFER: typing.Any
""" 
"""

GL_ELEMENT_ARRAY_BUFFER_BINDING: typing.Any
""" 
"""

GL_EQUAL: typing.Any
""" 
"""

GL_EQUIV: typing.Any
""" 
"""

GL_EXTENSIONS: typing.Any
""" 
"""

GL_FALSE: typing.Any
""" 
"""

GL_FASTEST: typing.Any
""" 
"""

GL_FILL: typing.Any
""" 
"""

GL_FIRST_VERTEX_CONVENTION: typing.Any
""" 
"""

GL_FIXED_ONLY: typing.Any
""" 
"""

GL_FLOAT: typing.Any
""" 
"""

GL_FLOAT_32_UNSIGNED_INT_24_8_REV: typing.Any
""" 
"""

GL_FLOAT_MAT2: typing.Any
""" 
"""

GL_FLOAT_MAT2x3: typing.Any
""" 
"""

GL_FLOAT_MAT2x4: typing.Any
""" 
"""

GL_FLOAT_MAT3: typing.Any
""" 
"""

GL_FLOAT_MAT3x2: typing.Any
""" 
"""

GL_FLOAT_MAT3x4: typing.Any
""" 
"""

GL_FLOAT_MAT4: typing.Any
""" 
"""

GL_FLOAT_MAT4x2: typing.Any
""" 
"""

GL_FLOAT_MAT4x3: typing.Any
""" 
"""

GL_FLOAT_VEC2: typing.Any
""" 
"""

GL_FLOAT_VEC3: typing.Any
""" 
"""

GL_FLOAT_VEC4: typing.Any
""" 
"""

GL_FRAGMENT_SHADER: typing.Any
""" 
"""

GL_FRAGMENT_SHADER_DERIVATIVE_HINT: typing.Any
""" 
"""

GL_FRAMEBUFFER: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_ALPHA_SIZE: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_BLUE_SIZE: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_COMPONENT_TYPE: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_DEPTH_SIZE: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_GREEN_SIZE: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_LAYERED: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_RED_SIZE: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_STENCIL_SIZE: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_CUBE_MAP_FACE: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LAYER: typing.Any
""" 
"""

GL_FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL: typing.Any
""" 
"""

GL_FRAMEBUFFER_BINDING: typing.Any
""" 
"""

GL_FRAMEBUFFER_COMPLETE: typing.Any
""" 
"""

GL_FRAMEBUFFER_DEFAULT: typing.Any
""" 
"""

GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT: typing.Any
""" 
"""

GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER: typing.Any
""" 
"""

GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS: typing.Any
""" 
"""

GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT: typing.Any
""" 
"""

GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE: typing.Any
""" 
"""

GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER: typing.Any
""" 
"""

GL_FRAMEBUFFER_SRGB: typing.Any
""" 
"""

GL_FRAMEBUFFER_UNDEFINED: typing.Any
""" 
"""

GL_FRAMEBUFFER_UNSUPPORTED: typing.Any
""" 
"""

GL_FRONT: typing.Any
""" 
"""

GL_FRONT_AND_BACK: typing.Any
""" 
"""

GL_FRONT_FACE: typing.Any
""" 
"""

GL_FRONT_LEFT: typing.Any
""" 
"""

GL_FRONT_RIGHT: typing.Any
""" 
"""

GL_FUNC_ADD: typing.Any
""" 
"""

GL_FUNC_REVERSE_SUBTRACT: typing.Any
""" 
"""

GL_FUNC_SUBTRACT: typing.Any
""" 
"""

GL_GEOMETRY_INPUT_TYPE: typing.Any
""" 
"""

GL_GEOMETRY_OUTPUT_TYPE: typing.Any
""" 
"""

GL_GEOMETRY_SHADER: typing.Any
""" 
"""

GL_GEOMETRY_VERTICES_OUT: typing.Any
""" 
"""

GL_GEQUAL: typing.Any
""" 
"""

GL_GREATER: typing.Any
""" 
"""

GL_GREEN: typing.Any
""" 
"""

GL_GREEN_INTEGER: typing.Any
""" 
"""

GL_HALF_FLOAT: typing.Any
""" 
"""

GL_INCR: typing.Any
""" 
"""

GL_INCR_WRAP: typing.Any
""" 
"""

GL_INDEX: typing.Any
""" 
"""

GL_INFO_LOG_LENGTH: typing.Any
""" 
"""

GL_INT: typing.Any
""" 
"""

GL_INTERLEAVED_ATTRIBS: typing.Any
""" 
"""

GL_INT_2_10_10_10_REV: typing.Any
""" 
"""

GL_INT_SAMPLER_1D: typing.Any
""" 
"""

GL_INT_SAMPLER_1D_ARRAY: typing.Any
""" 
"""

GL_INT_SAMPLER_2D: typing.Any
""" 
"""

GL_INT_SAMPLER_2D_ARRAY: typing.Any
""" 
"""

GL_INT_SAMPLER_2D_MULTISAMPLE: typing.Any
""" 
"""

GL_INT_SAMPLER_2D_MULTISAMPLE_ARRAY: typing.Any
""" 
"""

GL_INT_SAMPLER_2D_RECT: typing.Any
""" 
"""

GL_INT_SAMPLER_3D: typing.Any
""" 
"""

GL_INT_SAMPLER_BUFFER: typing.Any
""" 
"""

GL_INT_SAMPLER_CUBE: typing.Any
""" 
"""

GL_INT_VEC2: typing.Any
""" 
"""

GL_INT_VEC3: typing.Any
""" 
"""

GL_INT_VEC4: typing.Any
""" 
"""

GL_INVALID_ENUM: typing.Any
""" 
"""

GL_INVALID_FRAMEBUFFER_OPERATION: typing.Any
""" 
"""

GL_INVALID_INDEX: typing.Any
""" 
"""

GL_INVALID_OPERATION: typing.Any
""" 
"""

GL_INVALID_VALUE: typing.Any
""" 
"""

GL_INVERT: typing.Any
""" 
"""

GL_KEEP: typing.Any
""" 
"""

GL_LAST_VERTEX_CONVENTION: typing.Any
""" 
"""

GL_LEFT: typing.Any
""" 
"""

GL_LEQUAL: typing.Any
""" 
"""

GL_LESS: typing.Any
""" 
"""

GL_LINE: typing.Any
""" 
"""

GL_LINEAR: typing.Any
""" 
"""

GL_LINEAR_MIPMAP_LINEAR: typing.Any
""" 
"""

GL_LINEAR_MIPMAP_NEAREST: typing.Any
""" 
"""

GL_LINES: typing.Any
""" 
"""

GL_LINES_ADJACENCY: typing.Any
""" 
"""

GL_LINE_LOOP: typing.Any
""" 
"""

GL_LINE_SMOOTH: typing.Any
""" 
"""

GL_LINE_SMOOTH_HINT: typing.Any
""" 
"""

GL_LINE_STRIP: typing.Any
""" 
"""

GL_LINE_STRIP_ADJACENCY: typing.Any
""" 
"""

GL_LINE_WIDTH: typing.Any
""" 
"""

GL_LINE_WIDTH_GRANULARITY: typing.Any
""" 
"""

GL_LINE_WIDTH_RANGE: typing.Any
""" 
"""

GL_LINK_STATUS: typing.Any
""" 
"""

GL_LOGIC_OP_MODE: typing.Any
""" 
"""

GL_LOWER_LEFT: typing.Any
""" 
"""

GL_MAJOR_VERSION: typing.Any
""" 
"""

GL_MAP_FLUSH_EXPLICIT_BIT: typing.Any
""" 
"""

GL_MAP_INVALIDATE_BUFFER_BIT: typing.Any
""" 
"""

GL_MAP_INVALIDATE_RANGE_BIT: typing.Any
""" 
"""

GL_MAP_READ_BIT: typing.Any
""" 
"""

GL_MAP_UNSYNCHRONIZED_BIT: typing.Any
""" 
"""

GL_MAP_WRITE_BIT: typing.Any
""" 
"""

GL_MAX: typing.Any
""" 
"""

GL_MAX_3D_TEXTURE_SIZE: typing.Any
""" 
"""

GL_MAX_ARRAY_TEXTURE_LAYERS: typing.Any
""" 
"""

GL_MAX_CLIP_DISTANCES: typing.Any
""" 
"""

GL_MAX_COLOR_ATTACHMENTS: typing.Any
""" 
"""

GL_MAX_COLOR_TEXTURE_SAMPLES: typing.Any
""" 
"""

GL_MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS: typing.Any
""" 
"""

GL_MAX_COMBINED_GEOMETRY_UNIFORM_COMPONENTS: typing.Any
""" 
"""

GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS: typing.Any
""" 
"""

GL_MAX_COMBINED_UNIFORM_BLOCKS: typing.Any
""" 
"""

GL_MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS: typing.Any
""" 
"""

GL_MAX_CUBE_MAP_TEXTURE_SIZE: typing.Any
""" 
"""

GL_MAX_DEPTH_TEXTURE_SAMPLES: typing.Any
""" 
"""

GL_MAX_DRAW_BUFFERS: typing.Any
""" 
"""

GL_MAX_DUAL_SOURCE_DRAW_BUFFERS: typing.Any
""" 
"""

GL_MAX_ELEMENTS_INDICES: typing.Any
""" 
"""

GL_MAX_ELEMENTS_VERTICES: typing.Any
""" 
"""

GL_MAX_FRAGMENT_INPUT_COMPONENTS: typing.Any
""" 
"""

GL_MAX_FRAGMENT_UNIFORM_BLOCKS: typing.Any
""" 
"""

GL_MAX_FRAGMENT_UNIFORM_COMPONENTS: typing.Any
""" 
"""

GL_MAX_GEOMETRY_INPUT_COMPONENTS: typing.Any
""" 
"""

GL_MAX_GEOMETRY_OUTPUT_COMPONENTS: typing.Any
""" 
"""

GL_MAX_GEOMETRY_OUTPUT_VERTICES: typing.Any
""" 
"""

GL_MAX_GEOMETRY_TEXTURE_IMAGE_UNITS: typing.Any
""" 
"""

GL_MAX_GEOMETRY_TOTAL_OUTPUT_COMPONENTS: typing.Any
""" 
"""

GL_MAX_GEOMETRY_UNIFORM_BLOCKS: typing.Any
""" 
"""

GL_MAX_GEOMETRY_UNIFORM_COMPONENTS: typing.Any
""" 
"""

GL_MAX_INTEGER_SAMPLES: typing.Any
""" 
"""

GL_MAX_PROGRAM_TEXEL_OFFSET: typing.Any
""" 
"""

GL_MAX_RECTANGLE_TEXTURE_SIZE: typing.Any
""" 
"""

GL_MAX_RENDERBUFFER_SIZE: typing.Any
""" 
"""

GL_MAX_SAMPLES: typing.Any
""" 
"""

GL_MAX_SAMPLE_MASK_WORDS: typing.Any
""" 
"""

GL_MAX_SERVER_WAIT_TIMEOUT: typing.Any
""" 
"""

GL_MAX_TEXTURE_BUFFER_SIZE: typing.Any
""" 
"""

GL_MAX_TEXTURE_IMAGE_UNITS: typing.Any
""" 
"""

GL_MAX_TEXTURE_LOD_BIAS: typing.Any
""" 
"""

GL_MAX_TEXTURE_SIZE: typing.Any
""" 
"""

GL_MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS: typing.Any
""" 
"""

GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS: typing.Any
""" 
"""

GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS: typing.Any
""" 
"""

GL_MAX_UNIFORM_BLOCK_SIZE: typing.Any
""" 
"""

GL_MAX_UNIFORM_BUFFER_BINDINGS: typing.Any
""" 
"""

GL_MAX_VARYING_COMPONENTS: typing.Any
""" 
"""

GL_MAX_VARYING_FLOATS: typing.Any
""" 
"""

GL_MAX_VERTEX_ATTRIBS: typing.Any
""" 
"""

GL_MAX_VERTEX_OUTPUT_COMPONENTS: typing.Any
""" 
"""

GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS: typing.Any
""" 
"""

GL_MAX_VERTEX_UNIFORM_BLOCKS: typing.Any
""" 
"""

GL_MAX_VERTEX_UNIFORM_COMPONENTS: typing.Any
""" 
"""

GL_MAX_VIEWPORT_DIMS: typing.Any
""" 
"""

GL_MIN: typing.Any
""" 
"""

GL_MINOR_VERSION: typing.Any
""" 
"""

GL_MIN_PROGRAM_TEXEL_OFFSET: typing.Any
""" 
"""

GL_MIRRORED_REPEAT: typing.Any
""" 
"""

GL_MULTISAMPLE: typing.Any
""" 
"""

GL_NAND: typing.Any
""" 
"""

GL_NEAREST: typing.Any
""" 
"""

GL_NEAREST_MIPMAP_LINEAR: typing.Any
""" 
"""

GL_NEAREST_MIPMAP_NEAREST: typing.Any
""" 
"""

GL_NEVER: typing.Any
""" 
"""

GL_NICEST: typing.Any
""" 
"""

GL_NONE: typing.Any
""" 
"""

GL_NOOP: typing.Any
""" 
"""

GL_NOR: typing.Any
""" 
"""

GL_NOTEQUAL: typing.Any
""" 
"""

GL_NO_ERROR: typing.Any
""" 
"""

GL_NUM_COMPRESSED_TEXTURE_FORMATS: typing.Any
""" 
"""

GL_NUM_EXTENSIONS: typing.Any
""" 
"""

GL_OBJECT_TYPE: typing.Any
""" 
"""

GL_ONE: typing.Any
""" 
"""

GL_ONE_MINUS_CONSTANT_ALPHA: typing.Any
""" 
"""

GL_ONE_MINUS_CONSTANT_COLOR: typing.Any
""" 
"""

GL_ONE_MINUS_DST_ALPHA: typing.Any
""" 
"""

GL_ONE_MINUS_DST_COLOR: typing.Any
""" 
"""

GL_ONE_MINUS_SRC1_ALPHA: typing.Any
""" 
"""

GL_ONE_MINUS_SRC1_COLOR: typing.Any
""" 
"""

GL_ONE_MINUS_SRC_ALPHA: typing.Any
""" 
"""

GL_ONE_MINUS_SRC_COLOR: typing.Any
""" 
"""

GL_OR: typing.Any
""" 
"""

GL_OR_INVERTED: typing.Any
""" 
"""

GL_OR_REVERSE: typing.Any
""" 
"""

GL_OUT_OF_MEMORY: typing.Any
""" 
"""

GL_PACK_ALIGNMENT: typing.Any
""" 
"""

GL_PACK_IMAGE_HEIGHT: typing.Any
""" 
"""

GL_PACK_LSB_FIRST: typing.Any
""" 
"""

GL_PACK_ROW_LENGTH: typing.Any
""" 
"""

GL_PACK_SKIP_IMAGES: typing.Any
""" 
"""

GL_PACK_SKIP_PIXELS: typing.Any
""" 
"""

GL_PACK_SKIP_ROWS: typing.Any
""" 
"""

GL_PACK_SWAP_BYTES: typing.Any
""" 
"""

GL_PIXEL_PACK_BUFFER: typing.Any
""" 
"""

GL_PIXEL_PACK_BUFFER_BINDING: typing.Any
""" 
"""

GL_PIXEL_UNPACK_BUFFER: typing.Any
""" 
"""

GL_PIXEL_UNPACK_BUFFER_BINDING: typing.Any
""" 
"""

GL_POINT: typing.Any
""" 
"""

GL_POINTS: typing.Any
""" 
"""

GL_POINT_FADE_THRESHOLD_SIZE: typing.Any
""" 
"""

GL_POINT_SIZE: typing.Any
""" 
"""

GL_POINT_SPRITE_COORD_ORIGIN: typing.Any
""" 
"""

GL_POLYGON_MODE: typing.Any
""" 
"""

GL_POLYGON_OFFSET_FACTOR: typing.Any
""" 
"""

GL_POLYGON_OFFSET_FILL: typing.Any
""" 
"""

GL_POLYGON_OFFSET_LINE: typing.Any
""" 
"""

GL_POLYGON_OFFSET_POINT: typing.Any
""" 
"""

GL_POLYGON_OFFSET_UNITS: typing.Any
""" 
"""

GL_POLYGON_SMOOTH: typing.Any
""" 
"""

GL_POLYGON_SMOOTH_HINT: typing.Any
""" 
"""

GL_PRIMITIVES_GENERATED: typing.Any
""" 
"""

GL_PRIMITIVE_RESTART: typing.Any
""" 
"""

GL_PRIMITIVE_RESTART_INDEX: typing.Any
""" 
"""

GL_PROGRAM_POINT_SIZE: typing.Any
""" 
"""

GL_PROVOKING_VERTEX: typing.Any
""" 
"""

GL_PROXY_TEXTURE_1D: typing.Any
""" 
"""

GL_PROXY_TEXTURE_1D_ARRAY: typing.Any
""" 
"""

GL_PROXY_TEXTURE_2D: typing.Any
""" 
"""

GL_PROXY_TEXTURE_2D_ARRAY: typing.Any
""" 
"""

GL_PROXY_TEXTURE_2D_MULTISAMPLE: typing.Any
""" 
"""

GL_PROXY_TEXTURE_2D_MULTISAMPLE_ARRAY: typing.Any
""" 
"""

GL_PROXY_TEXTURE_3D: typing.Any
""" 
"""

GL_PROXY_TEXTURE_CUBE_MAP: typing.Any
""" 
"""

GL_PROXY_TEXTURE_RECTANGLE: typing.Any
""" 
"""

GL_QUADS_FOLLOW_PROVOKING_VERTEX_CONVENTION: typing.Any
""" 
"""

GL_QUERY_BY_REGION_NO_WAIT: typing.Any
""" 
"""

GL_QUERY_BY_REGION_WAIT: typing.Any
""" 
"""

GL_QUERY_COUNTER_BITS: typing.Any
""" 
"""

GL_QUERY_NO_WAIT: typing.Any
""" 
"""

GL_QUERY_RESULT: typing.Any
""" 
"""

GL_QUERY_RESULT_AVAILABLE: typing.Any
""" 
"""

GL_QUERY_WAIT: typing.Any
""" 
"""

GL_R11F_G11F_B10F: typing.Any
""" 
"""

GL_R16: typing.Any
""" 
"""

GL_R16F: typing.Any
""" 
"""

GL_R16I: typing.Any
""" 
"""

GL_R16UI: typing.Any
""" 
"""

GL_R16_SNORM: typing.Any
""" 
"""

GL_R32F: typing.Any
""" 
"""

GL_R32I: typing.Any
""" 
"""

GL_R32UI: typing.Any
""" 
"""

GL_R3_G3_B2: typing.Any
""" 
"""

GL_R8: typing.Any
""" 
"""

GL_R8I: typing.Any
""" 
"""

GL_R8UI: typing.Any
""" 
"""

GL_R8_SNORM: typing.Any
""" 
"""

GL_RASTERIZER_DISCARD: typing.Any
""" 
"""

GL_READ_BUFFER: typing.Any
""" 
"""

GL_READ_FRAMEBUFFER: typing.Any
""" 
"""

GL_READ_FRAMEBUFFER_BINDING: typing.Any
""" 
"""

GL_READ_ONLY: typing.Any
""" 
"""

GL_READ_WRITE: typing.Any
""" 
"""

GL_RED: typing.Any
""" 
"""

GL_RED_INTEGER: typing.Any
""" 
"""

GL_RENDERBUFFER: typing.Any
""" 
"""

GL_RENDERBUFFER_ALPHA_SIZE: typing.Any
""" 
"""

GL_RENDERBUFFER_BINDING: typing.Any
""" 
"""

GL_RENDERBUFFER_BLUE_SIZE: typing.Any
""" 
"""

GL_RENDERBUFFER_DEPTH_SIZE: typing.Any
""" 
"""

GL_RENDERBUFFER_GREEN_SIZE: typing.Any
""" 
"""

GL_RENDERBUFFER_HEIGHT: typing.Any
""" 
"""

GL_RENDERBUFFER_INTERNAL_FORMAT: typing.Any
""" 
"""

GL_RENDERBUFFER_RED_SIZE: typing.Any
""" 
"""

GL_RENDERBUFFER_SAMPLES: typing.Any
""" 
"""

GL_RENDERBUFFER_STENCIL_SIZE: typing.Any
""" 
"""

GL_RENDERBUFFER_WIDTH: typing.Any
""" 
"""

GL_RENDERER: typing.Any
""" 
"""

GL_REPEAT: typing.Any
""" 
"""

GL_REPLACE: typing.Any
""" 
"""

GL_RG: typing.Any
""" 
"""

GL_RG16: typing.Any
""" 
"""

GL_RG16F: typing.Any
""" 
"""

GL_RG16I: typing.Any
""" 
"""

GL_RG16UI: typing.Any
""" 
"""

GL_RG16_SNORM: typing.Any
""" 
"""

GL_RG32F: typing.Any
""" 
"""

GL_RG32I: typing.Any
""" 
"""

GL_RG32UI: typing.Any
""" 
"""

GL_RG8: typing.Any
""" 
"""

GL_RG8I: typing.Any
""" 
"""

GL_RG8UI: typing.Any
""" 
"""

GL_RG8_SNORM: typing.Any
""" 
"""

GL_RGB: typing.Any
""" 
"""

GL_RGB10: typing.Any
""" 
"""

GL_RGB10_A2: typing.Any
""" 
"""

GL_RGB10_A2UI: typing.Any
""" 
"""

GL_RGB12: typing.Any
""" 
"""

GL_RGB16: typing.Any
""" 
"""

GL_RGB16F: typing.Any
""" 
"""

GL_RGB16I: typing.Any
""" 
"""

GL_RGB16UI: typing.Any
""" 
"""

GL_RGB16_SNORM: typing.Any
""" 
"""

GL_RGB32F: typing.Any
""" 
"""

GL_RGB32I: typing.Any
""" 
"""

GL_RGB32UI: typing.Any
""" 
"""

GL_RGB4: typing.Any
""" 
"""

GL_RGB5: typing.Any
""" 
"""

GL_RGB5_A1: typing.Any
""" 
"""

GL_RGB8: typing.Any
""" 
"""

GL_RGB8I: typing.Any
""" 
"""

GL_RGB8UI: typing.Any
""" 
"""

GL_RGB8_SNORM: typing.Any
""" 
"""

GL_RGB9_E5: typing.Any
""" 
"""

GL_RGBA: typing.Any
""" 
"""

GL_RGBA12: typing.Any
""" 
"""

GL_RGBA16: typing.Any
""" 
"""

GL_RGBA16F: typing.Any
""" 
"""

GL_RGBA16I: typing.Any
""" 
"""

GL_RGBA16UI: typing.Any
""" 
"""

GL_RGBA16_SNORM: typing.Any
""" 
"""

GL_RGBA2: typing.Any
""" 
"""

GL_RGBA32F: typing.Any
""" 
"""

GL_RGBA32I: typing.Any
""" 
"""

GL_RGBA32UI: typing.Any
""" 
"""

GL_RGBA4: typing.Any
""" 
"""

GL_RGBA8: typing.Any
""" 
"""

GL_RGBA8I: typing.Any
""" 
"""

GL_RGBA8UI: typing.Any
""" 
"""

GL_RGBA8_SNORM: typing.Any
""" 
"""

GL_RGBA_INTEGER: typing.Any
""" 
"""

GL_RGB_INTEGER: typing.Any
""" 
"""

GL_RG_INTEGER: typing.Any
""" 
"""

GL_RIGHT: typing.Any
""" 
"""

GL_SAMPLER_1D: typing.Any
""" 
"""

GL_SAMPLER_1D_ARRAY: typing.Any
""" 
"""

GL_SAMPLER_1D_ARRAY_SHADOW: typing.Any
""" 
"""

GL_SAMPLER_1D_SHADOW: typing.Any
""" 
"""

GL_SAMPLER_2D: typing.Any
""" 
"""

GL_SAMPLER_2D_ARRAY: typing.Any
""" 
"""

GL_SAMPLER_2D_ARRAY_SHADOW: typing.Any
""" 
"""

GL_SAMPLER_2D_MULTISAMPLE: typing.Any
""" 
"""

GL_SAMPLER_2D_MULTISAMPLE_ARRAY: typing.Any
""" 
"""

GL_SAMPLER_2D_RECT: typing.Any
""" 
"""

GL_SAMPLER_2D_RECT_SHADOW: typing.Any
""" 
"""

GL_SAMPLER_2D_SHADOW: typing.Any
""" 
"""

GL_SAMPLER_3D: typing.Any
""" 
"""

GL_SAMPLER_BINDING: typing.Any
""" 
"""

GL_SAMPLER_BUFFER: typing.Any
""" 
"""

GL_SAMPLER_CUBE: typing.Any
""" 
"""

GL_SAMPLER_CUBE_SHADOW: typing.Any
""" 
"""

GL_SAMPLES: typing.Any
""" 
"""

GL_SAMPLES_PASSED: typing.Any
""" 
"""

GL_SAMPLE_ALPHA_TO_COVERAGE: typing.Any
""" 
"""

GL_SAMPLE_ALPHA_TO_ONE: typing.Any
""" 
"""

GL_SAMPLE_BUFFERS: typing.Any
""" 
"""

GL_SAMPLE_COVERAGE: typing.Any
""" 
"""

GL_SAMPLE_COVERAGE_INVERT: typing.Any
""" 
"""

GL_SAMPLE_COVERAGE_VALUE: typing.Any
""" 
"""

GL_SAMPLE_MASK: typing.Any
""" 
"""

GL_SAMPLE_MASK_VALUE: typing.Any
""" 
"""

GL_SAMPLE_POSITION: typing.Any
""" 
"""

GL_SCISSOR_BOX: typing.Any
""" 
"""

GL_SCISSOR_TEST: typing.Any
""" 
"""

GL_SEPARATE_ATTRIBS: typing.Any
""" 
"""

GL_SET: typing.Any
""" 
"""

GL_SHADER_SOURCE_LENGTH: typing.Any
""" 
"""

GL_SHADER_TYPE: typing.Any
""" 
"""

GL_SHADING_LANGUAGE_VERSION: typing.Any
""" 
"""

GL_SHORT: typing.Any
""" 
"""

GL_SIGNALED: typing.Any
""" 
"""

GL_SIGNED_NORMALIZED: typing.Any
""" 
"""

GL_SMOOTH_LINE_WIDTH_GRANULARITY: typing.Any
""" 
"""

GL_SMOOTH_LINE_WIDTH_RANGE: typing.Any
""" 
"""

GL_SMOOTH_POINT_SIZE_GRANULARITY: typing.Any
""" 
"""

GL_SMOOTH_POINT_SIZE_RANGE: typing.Any
""" 
"""

GL_SRC1_COLOR: typing.Any
""" 
"""

GL_SRC_ALPHA: typing.Any
""" 
"""

GL_SRC_ALPHA_SATURATE: typing.Any
""" 
"""

GL_SRC_COLOR: typing.Any
""" 
"""

GL_SRGB: typing.Any
""" 
"""

GL_SRGB8: typing.Any
""" 
"""

GL_SRGB8_ALPHA8: typing.Any
""" 
"""

GL_SRGB_ALPHA: typing.Any
""" 
"""

GL_STATIC_COPY: typing.Any
""" 
"""

GL_STATIC_DRAW: typing.Any
""" 
"""

GL_STATIC_READ: typing.Any
""" 
"""

GL_STENCIL: typing.Any
""" 
"""

GL_STENCIL_ATTACHMENT: typing.Any
""" 
"""

GL_STENCIL_BACK_FAIL: typing.Any
""" 
"""

GL_STENCIL_BACK_FUNC: typing.Any
""" 
"""

GL_STENCIL_BACK_PASS_DEPTH_FAIL: typing.Any
""" 
"""

GL_STENCIL_BACK_PASS_DEPTH_PASS: typing.Any
""" 
"""

GL_STENCIL_BACK_REF: typing.Any
""" 
"""

GL_STENCIL_BACK_VALUE_MASK: typing.Any
""" 
"""

GL_STENCIL_BACK_WRITEMASK: typing.Any
""" 
"""

GL_STENCIL_BUFFER_BIT: typing.Any
""" 
"""

GL_STENCIL_CLEAR_VALUE: typing.Any
""" 
"""

GL_STENCIL_FAIL: typing.Any
""" 
"""

GL_STENCIL_FUNC: typing.Any
""" 
"""

GL_STENCIL_INDEX: typing.Any
""" 
"""

GL_STENCIL_INDEX1: typing.Any
""" 
"""

GL_STENCIL_INDEX16: typing.Any
""" 
"""

GL_STENCIL_INDEX4: typing.Any
""" 
"""

GL_STENCIL_INDEX8: typing.Any
""" 
"""

GL_STENCIL_PASS_DEPTH_FAIL: typing.Any
""" 
"""

GL_STENCIL_PASS_DEPTH_PASS: typing.Any
""" 
"""

GL_STENCIL_REF: typing.Any
""" 
"""

GL_STENCIL_TEST: typing.Any
""" 
"""

GL_STENCIL_VALUE_MASK: typing.Any
""" 
"""

GL_STENCIL_WRITEMASK: typing.Any
""" 
"""

GL_STEREO: typing.Any
""" 
"""

GL_STREAM_COPY: typing.Any
""" 
"""

GL_STREAM_DRAW: typing.Any
""" 
"""

GL_STREAM_READ: typing.Any
""" 
"""

GL_SUBPIXEL_BITS: typing.Any
""" 
"""

GL_SYNC_CONDITION: typing.Any
""" 
"""

GL_SYNC_FENCE: typing.Any
""" 
"""

GL_SYNC_FLAGS: typing.Any
""" 
"""

GL_SYNC_FLUSH_COMMANDS_BIT: typing.Any
""" 
"""

GL_SYNC_GPU_COMMANDS_COMPLETE: typing.Any
""" 
"""

GL_SYNC_STATUS: typing.Any
""" 
"""

GL_TEXTURE: typing.Any
""" 
"""

GL_TEXTURE0: typing.Any
""" 
"""

GL_TEXTURE1: typing.Any
""" 
"""

GL_TEXTURE10: typing.Any
""" 
"""

GL_TEXTURE11: typing.Any
""" 
"""

GL_TEXTURE12: typing.Any
""" 
"""

GL_TEXTURE13: typing.Any
""" 
"""

GL_TEXTURE14: typing.Any
""" 
"""

GL_TEXTURE15: typing.Any
""" 
"""

GL_TEXTURE16: typing.Any
""" 
"""

GL_TEXTURE17: typing.Any
""" 
"""

GL_TEXTURE18: typing.Any
""" 
"""

GL_TEXTURE19: typing.Any
""" 
"""

GL_TEXTURE2: typing.Any
""" 
"""

GL_TEXTURE20: typing.Any
""" 
"""

GL_TEXTURE21: typing.Any
""" 
"""

GL_TEXTURE22: typing.Any
""" 
"""

GL_TEXTURE23: typing.Any
""" 
"""

GL_TEXTURE24: typing.Any
""" 
"""

GL_TEXTURE25: typing.Any
""" 
"""

GL_TEXTURE26: typing.Any
""" 
"""

GL_TEXTURE27: typing.Any
""" 
"""

GL_TEXTURE28: typing.Any
""" 
"""

GL_TEXTURE29: typing.Any
""" 
"""

GL_TEXTURE3: typing.Any
""" 
"""

GL_TEXTURE30: typing.Any
""" 
"""

GL_TEXTURE31: typing.Any
""" 
"""

GL_TEXTURE4: typing.Any
""" 
"""

GL_TEXTURE5: typing.Any
""" 
"""

GL_TEXTURE6: typing.Any
""" 
"""

GL_TEXTURE7: typing.Any
""" 
"""

GL_TEXTURE8: typing.Any
""" 
"""

GL_TEXTURE9: typing.Any
""" 
"""

GL_TEXTURE_1D: typing.Any
""" 
"""

GL_TEXTURE_1D_ARRAY: typing.Any
""" 
"""

GL_TEXTURE_2D: typing.Any
""" 
"""

GL_TEXTURE_2D_ARRAY: typing.Any
""" 
"""

GL_TEXTURE_2D_MULTISAMPLE: typing.Any
""" 
"""

GL_TEXTURE_2D_MULTISAMPLE_ARRAY: typing.Any
""" 
"""

GL_TEXTURE_3D: typing.Any
""" 
"""

GL_TEXTURE_ALPHA_SIZE: typing.Any
""" 
"""

GL_TEXTURE_ALPHA_TYPE: typing.Any
""" 
"""

GL_TEXTURE_BASE_LEVEL: typing.Any
""" 
"""

GL_TEXTURE_BINDING_1D: typing.Any
""" 
"""

GL_TEXTURE_BINDING_1D_ARRAY: typing.Any
""" 
"""

GL_TEXTURE_BINDING_2D: typing.Any
""" 
"""

GL_TEXTURE_BINDING_2D_ARRAY: typing.Any
""" 
"""

GL_TEXTURE_BINDING_2D_MULTISAMPLE: typing.Any
""" 
"""

GL_TEXTURE_BINDING_2D_MULTISAMPLE_ARRAY: typing.Any
""" 
"""

GL_TEXTURE_BINDING_3D: typing.Any
""" 
"""

GL_TEXTURE_BINDING_BUFFER: typing.Any
""" 
"""

GL_TEXTURE_BINDING_CUBE_MAP: typing.Any
""" 
"""

GL_TEXTURE_BINDING_RECTANGLE: typing.Any
""" 
"""

GL_TEXTURE_BLUE_SIZE: typing.Any
""" 
"""

GL_TEXTURE_BLUE_TYPE: typing.Any
""" 
"""

GL_TEXTURE_BORDER_COLOR: typing.Any
""" 
"""

GL_TEXTURE_BUFFER: typing.Any
""" 
"""

GL_TEXTURE_BUFFER_DATA_STORE_BINDING: typing.Any
""" 
"""

GL_TEXTURE_COMPARE_FUNC: typing.Any
""" 
"""

GL_TEXTURE_COMPARE_MODE: typing.Any
""" 
"""

GL_TEXTURE_COMPRESSED: typing.Any
""" 
"""

GL_TEXTURE_COMPRESSED_IMAGE_SIZE: typing.Any
""" 
"""

GL_TEXTURE_COMPRESSION_HINT: typing.Any
""" 
"""

GL_TEXTURE_CUBE_MAP: typing.Any
""" 
"""

GL_TEXTURE_CUBE_MAP_NEGATIVE_X: typing.Any
""" 
"""

GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: typing.Any
""" 
"""

GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: typing.Any
""" 
"""

GL_TEXTURE_CUBE_MAP_POSITIVE_X: typing.Any
""" 
"""

GL_TEXTURE_CUBE_MAP_POSITIVE_Y: typing.Any
""" 
"""

GL_TEXTURE_CUBE_MAP_POSITIVE_Z: typing.Any
""" 
"""

GL_TEXTURE_CUBE_MAP_SEAMLESS: typing.Any
""" 
"""

GL_TEXTURE_DEPTH: typing.Any
""" 
"""

GL_TEXTURE_DEPTH_SIZE: typing.Any
""" 
"""

GL_TEXTURE_DEPTH_TYPE: typing.Any
""" 
"""

GL_TEXTURE_FIXED_SAMPLE_LOCATIONS: typing.Any
""" 
"""

GL_TEXTURE_GREEN_SIZE: typing.Any
""" 
"""

GL_TEXTURE_GREEN_TYPE: typing.Any
""" 
"""

GL_TEXTURE_HEIGHT: typing.Any
""" 
"""

GL_TEXTURE_INTERNAL_FORMAT: typing.Any
""" 
"""

GL_TEXTURE_LOD_BIAS: typing.Any
""" 
"""

GL_TEXTURE_MAG_FILTER: typing.Any
""" 
"""

GL_TEXTURE_MAX_LEVEL: typing.Any
""" 
"""

GL_TEXTURE_MAX_LOD: typing.Any
""" 
"""

GL_TEXTURE_MIN_FILTER: typing.Any
""" 
"""

GL_TEXTURE_MIN_LOD: typing.Any
""" 
"""

GL_TEXTURE_RECTANGLE: typing.Any
""" 
"""

GL_TEXTURE_RED_SIZE: typing.Any
""" 
"""

GL_TEXTURE_RED_TYPE: typing.Any
""" 
"""

GL_TEXTURE_SAMPLES: typing.Any
""" 
"""

GL_TEXTURE_SHARED_SIZE: typing.Any
""" 
"""

GL_TEXTURE_STENCIL_SIZE: typing.Any
""" 
"""

GL_TEXTURE_SWIZZLE_A: typing.Any
""" 
"""

GL_TEXTURE_SWIZZLE_B: typing.Any
""" 
"""

GL_TEXTURE_SWIZZLE_G: typing.Any
""" 
"""

GL_TEXTURE_SWIZZLE_R: typing.Any
""" 
"""

GL_TEXTURE_SWIZZLE_RGBA: typing.Any
""" 
"""

GL_TEXTURE_WIDTH: typing.Any
""" 
"""

GL_TEXTURE_WRAP_R: typing.Any
""" 
"""

GL_TEXTURE_WRAP_S: typing.Any
""" 
"""

GL_TEXTURE_WRAP_T: typing.Any
""" 
"""

GL_TIMEOUT_EXPIRED: typing.Any
""" 
"""

GL_TIMEOUT_IGNORED: typing.Any
""" 
"""

GL_TIMESTAMP: typing.Any
""" 
"""

GL_TIME_ELAPSED: typing.Any
""" 
"""

GL_TRANSFORM_FEEDBACK_BUFFER: typing.Any
""" 
"""

GL_TRANSFORM_FEEDBACK_BUFFER_BINDING: typing.Any
""" 
"""

GL_TRANSFORM_FEEDBACK_BUFFER_MODE: typing.Any
""" 
"""

GL_TRANSFORM_FEEDBACK_BUFFER_SIZE: typing.Any
""" 
"""

GL_TRANSFORM_FEEDBACK_BUFFER_START: typing.Any
""" 
"""

GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN: typing.Any
""" 
"""

GL_TRANSFORM_FEEDBACK_VARYINGS: typing.Any
""" 
"""

GL_TRANSFORM_FEEDBACK_VARYING_MAX_LENGTH: typing.Any
""" 
"""

GL_TRIANGLES: typing.Any
""" 
"""

GL_TRIANGLES_ADJACENCY: typing.Any
""" 
"""

GL_TRIANGLE_FAN: typing.Any
""" 
"""

GL_TRIANGLE_STRIP: typing.Any
""" 
"""

GL_TRIANGLE_STRIP_ADJACENCY: typing.Any
""" 
"""

GL_TRUE: typing.Any
""" 
"""

GL_UNIFORM_ARRAY_STRIDE: typing.Any
""" 
"""

GL_UNIFORM_BLOCK_ACTIVE_UNIFORMS: typing.Any
""" 
"""

GL_UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES: typing.Any
""" 
"""

GL_UNIFORM_BLOCK_BINDING: typing.Any
""" 
"""

GL_UNIFORM_BLOCK_DATA_SIZE: typing.Any
""" 
"""

GL_UNIFORM_BLOCK_INDEX: typing.Any
""" 
"""

GL_UNIFORM_BLOCK_NAME_LENGTH: typing.Any
""" 
"""

GL_UNIFORM_BLOCK_REFERENCED_BY_FRAGMENT_SHADER: typing.Any
""" 
"""

GL_UNIFORM_BLOCK_REFERENCED_BY_GEOMETRY_SHADER: typing.Any
""" 
"""

GL_UNIFORM_BLOCK_REFERENCED_BY_VERTEX_SHADER: typing.Any
""" 
"""

GL_UNIFORM_BUFFER: typing.Any
""" 
"""

GL_UNIFORM_BUFFER_BINDING: typing.Any
""" 
"""

GL_UNIFORM_BUFFER_OFFSET_ALIGNMENT: typing.Any
""" 
"""

GL_UNIFORM_BUFFER_SIZE: typing.Any
""" 
"""

GL_UNIFORM_BUFFER_START: typing.Any
""" 
"""

GL_UNIFORM_IS_ROW_MAJOR: typing.Any
""" 
"""

GL_UNIFORM_MATRIX_STRIDE: typing.Any
""" 
"""

GL_UNIFORM_NAME_LENGTH: typing.Any
""" 
"""

GL_UNIFORM_OFFSET: typing.Any
""" 
"""

GL_UNIFORM_SIZE: typing.Any
""" 
"""

GL_UNIFORM_TYPE: typing.Any
""" 
"""

GL_UNPACK_ALIGNMENT: typing.Any
""" 
"""

GL_UNPACK_IMAGE_HEIGHT: typing.Any
""" 
"""

GL_UNPACK_LSB_FIRST: typing.Any
""" 
"""

GL_UNPACK_ROW_LENGTH: typing.Any
""" 
"""

GL_UNPACK_SKIP_IMAGES: typing.Any
""" 
"""

GL_UNPACK_SKIP_PIXELS: typing.Any
""" 
"""

GL_UNPACK_SKIP_ROWS: typing.Any
""" 
"""

GL_UNPACK_SWAP_BYTES: typing.Any
""" 
"""

GL_UNSIGNALED: typing.Any
""" 
"""

GL_UNSIGNED_BYTE: typing.Any
""" 
"""

GL_UNSIGNED_BYTE_2_3_3_REV: typing.Any
""" 
"""

GL_UNSIGNED_BYTE_3_3_2: typing.Any
""" 
"""

GL_UNSIGNED_INT: typing.Any
""" 
"""

GL_UNSIGNED_INT_10F_11F_11F_REV: typing.Any
""" 
"""

GL_UNSIGNED_INT_10_10_10_2: typing.Any
""" 
"""

GL_UNSIGNED_INT_24_8: typing.Any
""" 
"""

GL_UNSIGNED_INT_2_10_10_10_REV: typing.Any
""" 
"""

GL_UNSIGNED_INT_5_9_9_9_REV: typing.Any
""" 
"""

GL_UNSIGNED_INT_8_8_8_8: typing.Any
""" 
"""

GL_UNSIGNED_INT_8_8_8_8_REV: typing.Any
""" 
"""

GL_UNSIGNED_INT_SAMPLER_1D: typing.Any
""" 
"""

GL_UNSIGNED_INT_SAMPLER_1D_ARRAY: typing.Any
""" 
"""

GL_UNSIGNED_INT_SAMPLER_2D: typing.Any
""" 
"""

GL_UNSIGNED_INT_SAMPLER_2D_ARRAY: typing.Any
""" 
"""

GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE: typing.Any
""" 
"""

GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE_ARRAY: typing.Any
""" 
"""

GL_UNSIGNED_INT_SAMPLER_2D_RECT: typing.Any
""" 
"""

GL_UNSIGNED_INT_SAMPLER_3D: typing.Any
""" 
"""

GL_UNSIGNED_INT_SAMPLER_BUFFER: typing.Any
""" 
"""

GL_UNSIGNED_INT_SAMPLER_CUBE: typing.Any
""" 
"""

GL_UNSIGNED_INT_VEC2: typing.Any
""" 
"""

GL_UNSIGNED_INT_VEC3: typing.Any
""" 
"""

GL_UNSIGNED_INT_VEC4: typing.Any
""" 
"""

GL_UNSIGNED_NORMALIZED: typing.Any
""" 
"""

GL_UNSIGNED_SHORT: typing.Any
""" 
"""

GL_UNSIGNED_SHORT_1_5_5_5_REV: typing.Any
""" 
"""

GL_UNSIGNED_SHORT_4_4_4_4: typing.Any
""" 
"""

GL_UNSIGNED_SHORT_4_4_4_4_REV: typing.Any
""" 
"""

GL_UNSIGNED_SHORT_5_5_5_1: typing.Any
""" 
"""

GL_UNSIGNED_SHORT_5_6_5: typing.Any
""" 
"""

GL_UNSIGNED_SHORT_5_6_5_REV: typing.Any
""" 
"""

GL_UPPER_LEFT: typing.Any
""" 
"""

GL_VALIDATE_STATUS: typing.Any
""" 
"""

GL_VENDOR: typing.Any
""" 
"""

GL_VERSION: typing.Any
""" 
"""

GL_VERTEX_ARRAY_BINDING: typing.Any
""" 
"""

GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING: typing.Any
""" 
"""

GL_VERTEX_ATTRIB_ARRAY_DIVISOR: typing.Any
""" 
"""

GL_VERTEX_ATTRIB_ARRAY_ENABLED: typing.Any
""" 
"""

GL_VERTEX_ATTRIB_ARRAY_INTEGER: typing.Any
""" 
"""

GL_VERTEX_ATTRIB_ARRAY_NORMALIZED: typing.Any
""" 
"""

GL_VERTEX_ATTRIB_ARRAY_POINTER: typing.Any
""" 
"""

GL_VERTEX_ATTRIB_ARRAY_SIZE: typing.Any
""" 
"""

GL_VERTEX_ATTRIB_ARRAY_STRIDE: typing.Any
""" 
"""

GL_VERTEX_ATTRIB_ARRAY_TYPE: typing.Any
""" 
"""

GL_VERTEX_PROGRAM_POINT_SIZE: typing.Any
""" 
"""

GL_VERTEX_SHADER: typing.Any
""" 
"""

GL_VIEWPORT: typing.Any
""" 
"""

GL_WAIT_FAILED: typing.Any
""" 
"""

GL_WRITE_ONLY: typing.Any
""" 
"""

GL_XOR: typing.Any
""" 
"""

GL_ZERO: typing.Any
""" 
"""
