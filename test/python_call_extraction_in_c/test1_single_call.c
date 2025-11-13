#include <Python.h>

int main() {
    Py_Initialize();
    
    PyObject *pModule = PyImport_ImportModule("sys");
    PyObject *pFunc = PyObject_GetAttrString(pModule, "exit");
    PyObject *pArgs = Py_BuildValue("(i)", 0);
    PyObject *pResult = PyObject_CallObject(pFunc, pArgs);
    
    Py_XDECREF(pResult);
    Py_DECREF(pArgs);
    Py_DECREF(pFunc);
    Py_DECREF(pModule);
    
    Py_Finalize();
    return 0;
}