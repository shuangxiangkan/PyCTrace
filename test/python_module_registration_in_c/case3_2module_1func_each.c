#include <Python.h>

static PyObject* func1(PyObject* self, PyObject* args) {
    return PyLong_FromLong(300);
}

static PyObject* func2(PyObject* self, PyObject* args) {
    return PyLong_FromLong(301);
}

static PyMethodDef module3a_methods[] = {
    {"func1", func1, METH_VARARGS, "Function 1"},
    {NULL, NULL, 0, NULL}
};

static PyMethodDef module3b_methods[] = {
    {"func2", func2, METH_VARARGS, "Function 2"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module3adef = {
    PyModuleDef_HEAD_INIT,
    "module3a",
    "Module 3a documentation",
    -1,
    module3a_methods
};

static struct PyModuleDef module3bdef = {
    PyModuleDef_HEAD_INIT,
    "module3b",
    "Module 3b documentation",
    -1,
    module3b_methods
};

PyMODINIT_FUNC PyInit_module3a(void) {
    return PyModule_Create(&module3adef);
}

PyMODINIT_FUNC PyInit_module3b(void) {
    return PyModule_Create(&module3bdef);
}