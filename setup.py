from setuptools import Extension, setup
from wheel.bdist_wheel import bdist_wheel


class bdist_wheel_abi3(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()

        if python.startswith('cp'):
            return 'cp36', 'abi3', plat

        return python, abi, plat


cudart = Extension(
    name='zengl_extras.cudart',
    sources=['zengl_extras/cudart.c'],
    define_macros=[('Py_LIMITED_API', 0x03060000)],
    py_limited_api=True,
    optional=True,
)

opencl = Extension(
    name='zengl_extras.opencl',
    sources=['zengl_extras/opencl.c'],
    define_macros=[('Py_LIMITED_API', 0x03060000)],
    py_limited_api=True,
    optional=True,
)

setup(
    name='zengl-extras',
    version='0.6.0',
    packages=['zengl_extras'],
    ext_modules=[cudart, opencl],
    install_requires=['zengl', 'requests', 'progress', 'colorama'],
    cmdclass={'bdist_wheel': bdist_wheel_abi3},
)
