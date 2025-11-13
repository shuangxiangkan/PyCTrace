#include <Python.h>
#include <stdio.h>
#include "test5_helpers.h"

int main() {
    Py_Initialize();
    
    const char *module_name = get_datetime_module_name();
    PyObject *pModule = PyImport_ImportModule(module_name);
    
    const char *class_name = get_datetime_class_name();
    PyObject *pClass = PyObject_GetAttrString(pModule, class_name);
    
    PyObject *pArgs = create_datetime_args();
    PyObject *pDatetime = PyObject_CallObject(pClass, pArgs);
    
    if (pDatetime) {
        PyObject *pStr = PyObject_Str(pDatetime);
        const char *datetime_str = PyUnicode_AsUTF8(pStr);
        printf("Created datetime: %s\n", datetime_str);
        Py_DECREF(pStr);
    }
    
    Py_XDECREF(pDatetime);
    Py_DECREF(pArgs);
    Py_DECREF(pClass);
    Py_DECREF(pModule);
    
    Py_Finalize();
    return 0;
}