#include <Python.h>
#include <stdio.h>
#include <string.h>

static const char* get_module_name() {
    return "os";
}

static PyObject* build_args(int count) {
    return Py_BuildValue("(i)", count);
}

int main() {
    Py_Initialize();
    
    const char *module_name = get_module_name();
    PyObject *pModule = PyImport_ImportModule(module_name);
    
    PyObject *pFunc = PyObject_GetAttrString(pModule, "getcwd");
    PyObject *pArgs = build_args(0);
    PyObject *pResult = PyObject_CallObject(pFunc, pArgs);
    
    if (pResult) {
        const char *cwd = PyUnicode_AsUTF8(pResult);
        printf("Current directory: %s\n", cwd);
    }
    
    Py_XDECREF(pResult);
    Py_DECREF(pArgs);
    Py_DECREF(pFunc);
    Py_DECREF(pModule);
    
    Py_Finalize();
    return 0;
}