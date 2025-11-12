#include <Python.h>

static PyObject* func1(PyObject* self, PyObject* args) {
    return PyLong_FromLong(500);
}

extern PyObject* func2(PyObject* self, PyObject* args);

static PyMethodDef module5_methods[] = {
    {"func1", func1, METH_VARARGS, "Function 1"},
    {"func2", func2, METH_VARARGS, "Function 2"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module5def = {
    PyModuleDef_HEAD_INIT,
    "module5",
    "Module 5 documentation",
    -1,
    module5_methods
};

PyMODINIT_FUNC PyInit_module5(void) {
    return PyModule_Create(&module5def);
}