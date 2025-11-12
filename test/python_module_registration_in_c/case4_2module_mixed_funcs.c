#include <Python.h>

static PyObject* func1(PyObject* self, PyObject* args) {
    return PyLong_FromLong(400);
}

static PyObject* func2(PyObject* self, PyObject* args) {
    return PyLong_FromLong(401);
}

static PyObject* func3(PyObject* self, PyObject* args) {
    return PyLong_FromLong(402);
}

static PyMethodDef module4a_methods[] = {
    {"func1", func1, METH_VARARGS, "Function 1"},
    {NULL, NULL, 0, NULL}
};

static PyMethodDef module4b_methods[] = {
    {"func2", func2, METH_VARARGS, "Function 2"},
    {"func3", func3, METH_VARARGS, "Function 3"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module4adef = {
    PyModuleDef_HEAD_INIT,
    "module4a",
    "Module 4a documentation",
    -1,
    module4a_methods
};

static struct PyModuleDef module4bdef = {
    PyModuleDef_HEAD_INIT,
    "module4b",
    "Module 4b documentation",
    -1,
    module4b_methods
};

PyMODINIT_FUNC PyInit_module4a(void) {
    return PyModule_Create(&module4adef);
}

PyMODINIT_FUNC PyInit_module4b(void) {
    return PyModule_Create(&module4bdef);
}