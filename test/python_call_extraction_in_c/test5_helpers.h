#ifndef TEST5_HELPERS_H
#define TEST5_HELPERS_H

#include <Python.h>

const char* get_datetime_module_name();
const char* get_datetime_class_name();
PyObject* create_datetime_args();

#endif