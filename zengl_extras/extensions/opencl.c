#include <Python.h>

static PyModuleDef module_def = {PyModuleDef_HEAD_INIT, "opencl", NULL, -1, NULL};

extern PyObject * PyInit_opencl() {
    return PyModule_Create(&module_def);
}
