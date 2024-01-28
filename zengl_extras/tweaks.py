try:
    from zengl_extras.extensions import cudart
except ImportError:
    pass

try:
    from zengl_extras.extensions import opencl
except ImportError:
    pass

from zengl_extras.glsl import enable_custom_shader_errors

enable_custom_shader_errors()

try:
    from zengl_extras.extensions.win import vsync
except ImportError:
    vsync = lambda: None
