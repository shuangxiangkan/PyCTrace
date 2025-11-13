#include <Python.h>

const char* get_json_module_name() {
    return "json";
}

const char* get_json_loads_name() {
    return "loads";
}

PyObject* create_json_string() {
    return Py_BuildValue("(s)", "{\"name\": \"test\", \"value\": 42}");
}