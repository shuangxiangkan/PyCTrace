#ifndef TEST6_HELPERS_BASE64_H
#define TEST6_HELPERS_BASE64_H

#include <Python.h>

const char* get_base64_module_name();
const char* get_base64_encode_name();
PyObject* create_bytes_to_encode();

#endif