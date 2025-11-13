#include <Python.h>

int main() {
    Py_Initialize();
    
    PyObject *pModule = PyImport_ImportModule("math");
    
    PyObject *pSqrtFunc = PyObject_GetAttrString(pModule, "sqrt");
    PyObject *pArgs1 = Py_BuildValue("(d)", 16.0);
    PyObject *pResult1 = PyObject_CallObject(pSqrtFunc, pArgs1);
    double sqrt_result = PyFloat_AsDouble(pResult1);
    
    PyObject *pPowFunc = PyObject_GetAttrString(pModule, "pow");
    PyObject *pArgs2 = Py_BuildValue("(dd)", 2.0, 3.0);
    PyObject *pResult2 = PyObject_CallObject(pPowFunc, pArgs2);
    double pow_result = PyFloat_AsDouble(pResult2);
    
    Py_XDECREF(pResult2);
    Py_DECREF(pArgs2);
    Py_DECREF(pPowFunc);
    Py_XDECREF(pResult1);
    Py_DECREF(pArgs1);
    Py_DECREF(pSqrtFunc);
    Py_DECREF(pModule);
    
    Py_Finalize();
    return 0;
}