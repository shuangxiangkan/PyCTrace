#include <Python.h>

extern PyObject* func2(PyObject* self, PyObject* args);

static PyMethodDef module6b_methods[] = {
    {"func2", func2, METH_VARARGS, "Function 2"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module6bdef = {
    PyModuleDef_HEAD_INIT,
    "module6b",
    "Module 6b documentation",
    -1,
    module6b_methods
};

PyMODINIT_FUNC PyInit_module6b(void) {
    return PyModule_Create(&module6bdef);
}

PyObject* func1(PyObject* self, PyObject* args) {
    return PyLong_FromLong(600);
}