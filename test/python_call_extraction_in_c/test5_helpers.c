#include <Python.h>

const char* get_datetime_module_name() {
    return "datetime";
}

const char* get_datetime_class_name() {
    return "datetime";
}

PyObject* create_datetime_args() {
    return Py_BuildValue("(iiiiii)", 2024, 11, 13, 10, 30, 0);
}