#include <Python.h>

static PyModuleDef module_def = {PyModuleDef_HEAD_INIT, "cudart", NULL, -1, NULL};

extern PyObject * PyInit_cudart() {
    return PyModule_Create(&module_def);
}
