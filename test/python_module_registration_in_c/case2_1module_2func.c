#include <Python.h>

static PyObject* func1(PyObject* self, PyObject* args) {
    return PyLong_FromLong(200);
}

static PyObject* func2(PyObject* self, PyObject* args) {
    return PyLong_FromLong(201);
}

static PyMethodDef module2_methods[] = {
    {"func1", func1, METH_VARARGS, "Function 1"},
    {"func2", func2, METH_VARARGS, "Function 2"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module2def = {
    PyModuleDef_HEAD_INIT,
    "module2",
    "Module 2 documentation",
    -1,
    module2_methods
};

PyMODINIT_FUNC PyInit_module2(void) {
    return PyModule_Create(&module2def);
}