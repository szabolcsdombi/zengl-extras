from setuptools import Extension, setup

cudart = Extension(
    name="zengl_extras.extensions.cudart",
    sources=["zengl_extras/extensions/cudart.c"],
    define_macros=[("Py_LIMITED_API", 0x03060000)],
    py_limited_api=True,
    optional=True,
)

opencl = Extension(
    name="zengl_extras.extensions.opencl",
    sources=["zengl_extras/extensions/opencl.c"],
    define_macros=[("Py_LIMITED_API", 0x03060000)],
    py_limited_api=True,
    optional=True,
)

win = Extension(
    name="zengl_extras.extensions.win",
    sources=["zengl_extras/extensions/win.c"],
    libraries=["user32", "dwmapi", "powrprof"],
    define_macros=[("Py_LIMITED_API", 0x03060000)],
    py_limited_api=True,
    optional=True,
)

setup(
    name="zengl-extras",
    version="0.1.0",
    packages=["zengl_extras", "zengl_extras.extensions"],
    ext_modules=[cudart, opencl, win],
    install_requires=["zengl", "requests", "progress", "colorama"],
    package_data={"zengl_extras": ["tweaks.pyi"]},
    include_package_data=True,
)
