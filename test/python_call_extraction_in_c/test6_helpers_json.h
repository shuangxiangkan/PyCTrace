#ifndef TEST6_HELPERS_JSON_H
#define TEST6_HELPERS_JSON_H

#include <Python.h>

const char* get_json_module_name();
const char* get_json_loads_name();
PyObject* create_json_string();

#endif