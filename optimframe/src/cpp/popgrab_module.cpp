#include "Python.h"
#include <iostream>

#include "PopulationGrabber.hpp"

using std::cout;
using std::cerr;

static PopulationGrabber *pg;

static PyObject *popgrab_get(PyObject *self, PyObject *args)
{
  int region, p=-1;
  int ok = PyArg_ParseTuple(args, "i", &region);
  if (ok)
  {
    p = pg->get(region);
  }
  PyObject *ret = Py_BuildValue("i", p);
  return ret;
}

static PyObject *popgrab_set_pop(PyObject *self, PyObject *args)
{
  int x,y,p;
  int ok = PyArg_ParseTuple(args, "iii", &x, &y, &p);
  if (ok)
  {
    pg->set_pop(x,y,p);
  }
  Py_RETURN_NONE;
}

static PyObject *popgrab_read_pop(PyObject *self, PyObject *args)
{
  int x,y,p=-1;
  int ok = PyArg_ParseTuple(args, "ii", &x, &y);
  if (ok)
  {
    p = pg->read_pop(x,y);
  }

  PyObject *ret = Py_BuildValue("i", p);
  return ret;
}

static PyObject *popgrab_read_reg(PyObject *self, PyObject *args)
{
  int x,y,p=-1;
  int ok = PyArg_ParseTuple(args, "ii", &x, &y);
  if (ok)
  {
    p = pg->read_reg(x,y);
  }

  PyObject *ret = Py_BuildValue("i", p);
  return ret;
}

static PyObject *popgrab_put(PyObject *self, PyObject *args)
{
  int x,y,region=-1;
  int ok = PyArg_ParseTuple(args, "iii", &region, &x, &y);
  if (ok)
  {
    pg->put(region,x,y);
  }

  Py_RETURN_NONE;
}

static PyObject *popgrab_run(PyObject *self, PyObject *args)
{
  pg->run();
  Py_RETURN_NONE;
}


static char module_docstring[] =
  "A Python module that computes population allocations based on distance.";

static char one_docstring[] =
    "Get a one back.";

static PyMethodDef module_methods[] = {
  {"set_pop", popgrab_set_pop, METH_VARARGS, one_docstring},
  {"read_pop", popgrab_read_pop, METH_VARARGS, one_docstring},
  {"read_reg", popgrab_read_reg, METH_VARARGS, one_docstring},
  {"put", popgrab_put, METH_VARARGS, one_docstring},
  {"run", popgrab_run, METH_VARARGS, one_docstring},
  {"get", popgrab_get, METH_VARARGS, one_docstring},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef popgrab_module_definition = {
    PyModuleDef_HEAD_INIT, "popgrab", module_docstring, -1, module_methods
};

PyMODINIT_FUNC PyInit_popgrab(void)
{
   Py_Initialize();
   pg = new PopulationGrabber(700,700);
   return PyModule_Create(&popgrab_module_definition);
}
