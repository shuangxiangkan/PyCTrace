#include <Python.h>
#include <stdio.h>

static const char* get_first_function_name() {
    return "len";
}

static const char* get_second_function_name() {
    return "sum";
}

static PyObject* create_list() {
    return Py_BuildValue("[i,i,i]", 1, 2, 3);
}

static PyObject* create_tuple() {
    return Py_BuildValue("(i,i,i,i)", 10, 20, 30, 40);
}

int main() {
    Py_Initialize();
    
    PyObject *pBuiltins = PyImport_ImportModule("builtins");
    
    const char *func_name1 = get_first_function_name();
    PyObject *pLenFunc = PyObject_GetAttrString(pBuiltins, func_name1);
    PyObject *pList = create_list();
    PyObject *pArgs1 = Py_BuildValue("(O)", pList);
    PyObject *pResult1 = PyObject_CallObject(pLenFunc, pArgs1);
    long list_len = PyLong_AsLong(pResult1);
    printf("List length: %ld\n", list_len);
    
    const char *func_name2 = get_second_function_name();
    PyObject *pSumFunc = PyObject_GetAttrString(pBuiltins, func_name2);
    PyObject *pTuple = create_tuple();
    PyObject *pArgs2 = Py_BuildValue("(O)", pTuple);
    PyObject *pResult2 = PyObject_CallObject(pSumFunc, pArgs2);
    long sum_result = PyLong_AsLong(pResult2);
    printf("Sum: %ld\n", sum_result);
    
    Py_XDECREF(pResult2);
    Py_DECREF(pArgs2);
    Py_DECREF(pTuple);
    Py_DECREF(pSumFunc);
    Py_XDECREF(pResult1);
    Py_DECREF(pArgs1);
    Py_DECREF(pList);
    Py_DECREF(pLenFunc);
    Py_DECREF(pBuiltins);
    
    Py_Finalize();
    return 0;
}