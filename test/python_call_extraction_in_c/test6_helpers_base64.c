#include <Python.h>

const char* get_base64_module_name() {
    return "base64";
}

const char* get_base64_encode_name() {
    return "b64encode";
}

PyObject* create_bytes_to_encode() {
    return Py_BuildValue("(y)", "Hello World");
}