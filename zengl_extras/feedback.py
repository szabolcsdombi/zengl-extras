import _zengl
import zengl


class _state:
    link_program_callback = None
    vertex_size = None
    varyings = None
    dtype = None


class Loader:
    def __init__(self, loader):
        import ctypes

        from OpenGL import GL

        self.loader = loader
        link_program_ptr = self.loader.load_opengl_function("glLinkProgram")
        link_program = ctypes.cast(link_program_ptr, ctypes.CFUNCTYPE(None, ctypes.c_int32))

        def link_program_hook(program):
            varyings_count = len(_state.varyings)
            varyings_strings = [ctypes.create_string_buffer(name.encode()) for name in _state.varyings]
            varyings_block = (ctypes.c_char_p * varyings_count)()
            for i in range(varyings_count):
                varyings_block[i] = ctypes.cast(varyings_strings[i], ctypes.c_char_p)
            varyings_ptr = ctypes.cast(varyings_block, ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
            if varyings_count:
                GL.glTransformFeedbackVaryings(program, varyings_count, varyings_ptr, GL.GL_INTERLEAVED_ATTRIBS)
            link_program(program)

        _state.link_program_hook = ctypes.CFUNCTYPE(None, ctypes.c_int32)(link_program_hook)
        self.link_program_callback = ctypes.cast(_state.link_program_hook, ctypes.c_void_p).value

    def load_opengl_function(self, name):
        if name == "glLinkProgram":
            return self.link_program_callback
        return self.loader.load_opengl_function(name)


def feedback(pipeline):
    import ctypes

    import numpy as np
    from OpenGL import GL

    total_vertex_count = pipeline.vertex_count * pipeline.instance_count
    buffer_size = total_vertex_count * _state.vertex_size
    buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, buffer_size, None, GL.GL_DYNAMIC_DRAW)
    GL.glBindBufferRange(GL.GL_TRANSFORM_FEEDBACK_BUFFER, 0, buffer, 0, buffer_size)
    GL.glEnable(GL.GL_RASTERIZER_DISCARD)
    instance_count = pipeline.instance_count
    pipeline.instance_count = 0
    pipeline.render()
    GL.glBeginTransformFeedback(GL.GL_TRIANGLES)
    pipeline.instance_count = instance_count
    pipeline.render()
    GL.glEndTransformFeedback()
    data = ctypes.create_string_buffer(buffer_size)
    GL.glGetBufferSubData(GL.GL_ARRAY_BUFFER, 0, buffer_size, data)
    GL.glDisable(GL.GL_RASTERIZER_DISCARD)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    GL.glBindBufferRange(GL.GL_TRANSFORM_FEEDBACK_BUFFER, 0, 0, 0, 0)
    buffers = (ctypes.c_int32 * 1)(buffer)
    GL.glDeleteBuffers(1, buffers)
    return np.frombuffer(bytes(data), dtype=_state.dtype)


def enable_transform_feedback(varyings=None, vertex_size=None, dtype="f4"):
    if _state.link_program_callback is None:
        zengl.init(Loader(_zengl.DefaultLoader()))

    if varyings is None:
        varyings = ["gl_Position"]
        vertex_size = 16

    if vertex_size is None:
        raise ValueError("invalid vertex_size")

    _state.varyings = [name for name in varyings]
    _state.vertex_size = vertex_size
    _state.dtype = dtype


def disable_transform_feedback():
    _state.varyings = []
