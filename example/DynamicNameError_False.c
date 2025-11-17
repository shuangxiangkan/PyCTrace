// DynamicNameError / incorrect
#include <Python.h>
#include <stdio.h>
#include <string.h>

static unsigned long g_counter = 0;
static const char *choose_suffix() { return "v1"; }
static int transform_label(int x) { return x + 42; }

static PyObject *py_tick(PyObject *s, PyObject *a) {
  long k = 0;
  if (!PyArg_ParseTuple(a, "l", &k))
    return NULL;
  g_counter += (unsigned long)k;
  Py_RETURN_NONE;
}
static PyMethodDef HostMethods[] = {{"tick", py_tick, METH_VARARGS, ""},
                                    {NULL, NULL, 0, NULL}};
static struct PyModuleDef HostModule = {PyModuleDef_HEAD_INIT, "host", NULL, -1,
                                        HostMethods};
PyMODINIT_FUNC PyInit_host(void) { return PyModule_Create(&HostModule); }

int main() {
  PyImport_AppendInittab("host", &PyInit_host);
  Py_Initialize();
  PyObject *g = PyModule_GetDict(PyImport_AddModule("__main__"));
  const char *py = "import host\n"
                   "def add_v2(a,b,k):\n"
                   "    print('P')\n"
                   "    host.tick(k)\n"
                   "    return a+b\n"
                   "def metrics_probe(): return 0\n";
  PyRun_String(py, Py_file_input, g, g);

  char fname[32];
  snprintf(fname, sizeof(fname), "add_%s", choose_suffix()); // -> add_v1
  PyObject *fn = PyDict_GetItemString(g, fname);
  PyObject *args = Py_BuildValue("(iii)", 10, 20, 3);
  PyObject *ret = PyObject_CallObject(fn, args);

  if (!ret) {
    PyErr_Clear();
    printf("ERR\n");
    Py_Finalize();
    return 0;
  }
  long v = PyLong_AsLong(ret);
  printf("OK:%ld COUNT:%lu\n", v, g_counter);
  Py_DECREF(ret);
  Py_Finalize();
  return 0;
}
