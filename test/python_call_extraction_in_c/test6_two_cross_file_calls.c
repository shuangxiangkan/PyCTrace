#include <Python.h>
#include <stdio.h>
#include "test6_helpers_json.h"
#include "test6_helpers_base64.h"

int main() {
    Py_Initialize();
    
    const char *json_module = get_json_module_name();
    PyObject *pJsonModule = PyImport_ImportModule(json_module);
    const char *loads_func = get_json_loads_name();
    PyObject *pLoadsFunc = PyObject_GetAttrString(pJsonModule, loads_func);
    PyObject *pJsonArgs = create_json_string();
    PyObject *pJsonResult = PyObject_CallObject(pLoadsFunc, pJsonArgs);
    
    if (pJsonResult) {
        PyObject *pStr1 = PyObject_Str(pJsonResult);
        const char *json_str = PyUnicode_AsUTF8(pStr1);
        printf("Parsed JSON: %s\n", json_str);
        Py_DECREF(pStr1);
    }
    
    const char *base64_module = get_base64_module_name();
    PyObject *pBase64Module = PyImport_ImportModule(base64_module);
    const char *encode_func = get_base64_encode_name();
    PyObject *pEncodeFunc = PyObject_GetAttrString(pBase64Module, encode_func);
    PyObject *pBase64Args = create_bytes_to_encode();
    PyObject *pBase64Result = PyObject_CallObject(pEncodeFunc, pBase64Args);
    
    if (pBase64Result) {
        PyObject *pStr2 = PyObject_Str(pBase64Result);
        const char *base64_str = PyUnicode_AsUTF8(pStr2);
        printf("Base64 encoded: %s\n", base64_str);
        Py_DECREF(pStr2);
    }
    
    Py_XDECREF(pBase64Result);
    Py_DECREF(pBase64Args);
    Py_DECREF(pEncodeFunc);
    Py_DECREF(pBase64Module);
    
    Py_XDECREF(pJsonResult);
    Py_DECREF(pJsonArgs);
    Py_DECREF(pLoadsFunc);
    Py_DECREF(pJsonModule);
    
    Py_Finalize();
    return 0;
}