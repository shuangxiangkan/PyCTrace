#include <Python.h>

PyObject* func2(PyObject* self, PyObject* args) {
    return PyLong_FromLong(501);
}