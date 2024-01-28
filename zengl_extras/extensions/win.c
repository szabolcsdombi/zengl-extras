#include <Python.h>
#include <PowerSetting.h>
#include <Shlwapi.h>

extern _declspec(dllexport) DWORD NvOptimusEnablement = 0x00000001;
extern _declspec(dllexport) int AmdPowerXpressRequestHighPerformance = 0x00000001;

static PyObject * meth_vsync(PyObject * self, PyObject * args) {
    DwmFlush();
    Py_RETURN_NONE;
}

static PyMethodDef module_methods[] = {
    {"vsync", (PyCFunction)meth_vsync, METH_NOARGS, NULL},
    {0},
};

static PyModuleDef module_def = {PyModuleDef_HEAD_INIT, "win", NULL, -1, module_methods};

extern PyObject * PyInit_win() {
    PowerSetActiveScheme(NULL, &GUID_MIN_POWER_SAVINGS);
    SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
    SetPriorityClass(GetCurrentProcess(), HIGH_PRIORITY_CLASS);
    return PyModule_Create(&module_def);
}
