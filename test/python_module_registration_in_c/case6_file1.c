#include <Python.h>

extern PyObject* func1(PyObject* self, PyObject* args);

static PyMethodDef module6a_methods[] = {
    {"func1", func1, METH_VARARGS, "Function 1"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module6adef = {
    PyModuleDef_HEAD_INIT,
    "module6a",
    "Module 6a documentation",
    -1,
    module6a_methods
};

PyMODINIT_FUNC PyInit_module6a(void) {
    return PyModule_Create(&module6adef);
}

PyObject* func2(PyObject* self, PyObject* args) {
    return PyLong_FromLong(601);
}