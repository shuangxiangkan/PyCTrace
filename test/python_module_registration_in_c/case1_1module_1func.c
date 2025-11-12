#include <Python.h>

static PyObject* func1(PyObject* self, PyObject* args) {
    return PyLong_FromLong(100);
}

static PyMethodDef module1_methods[] = {
    {"func1", func1, METH_VARARGS, "Function 1"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module1def = {
    PyModuleDef_HEAD_INIT,
    "module1",
    "Module 1 documentation",
    -1,
    module1_methods
};

PyMODINIT_FUNC PyInit_module1(void) {
    return PyModule_Create(&module1def);
}