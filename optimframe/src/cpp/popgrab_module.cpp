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

static PyObject *popgrab_get_neigh(PyObject *self, PyObject *args)
{
  int region;
  int ok = PyArg_ParseTuple(args, "i", &region);
  if (ok)
  {
    PyObject *my_list = PyList_New(0);
    for(auto &n : pg->get_neigh(region))
    {
      auto neighbour = Py_BuildValue("i", n);
      PyList_Append(my_list, neighbour);
    }

    return my_list;
  }
  Py_RETURN_NONE;
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

static PyObject *popgrab_remove(PyObject *self, PyObject *args)
{
  int region=-1;
  int ok = PyArg_ParseTuple(args, "i", &region);
  if (ok)
  {
    pg->remove(region);
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
    "Misc function";

static PyMethodDef module_methods[] = {
  {"set_pop", popgrab_set_pop, METH_VARARGS, one_docstring},
  {"read_pop", popgrab_read_pop, METH_VARARGS, one_docstring},
  {"read_reg", popgrab_read_reg, METH_VARARGS, one_docstring},
  {"put", popgrab_put, METH_VARARGS, one_docstring},
  {"run", popgrab_run, METH_VARARGS, one_docstring},
  {"get", popgrab_get, METH_VARARGS, one_docstring},
  {"remove", popgrab_remove, METH_VARARGS, one_docstring},
  {"get_neigh", popgrab_get_neigh, METH_VARARGS, one_docstring},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef popgrab_module_definition = {
    PyModuleDef_HEAD_INIT,
    "popgrab", module_docstring, -1, module_methods
};

// Second version of the API makes fillable objects

typedef struct {
    PyObject_HEAD
    PopulationGrabber *pg;
} PopGrab_Object;

static void
PopGrab_dealloc(PopGrab_Object *self)
{
  delete self -> pg;
  Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *
PopGrab_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  PopGrab_Object *self;
  self = (PopGrab_Object *) type->tp_alloc(type, 0);
  if (self != NULL) {
    self -> pg = new PopulationGrabber(700, 700);
  }
  return (PyObject *) self;
}

static int
PopGrab_init(PopGrab_Object *self, PyObject *args, PyObject *kwds)
{
  int x,y;
  int ok = PyArg_ParseTuple(args, "ii", &x, &y);
  if (ok)
  {
    self -> pg->setSize(x,y);
  }
  return 0;
}

static PyObject *PopGrab_get(PopGrab_Object *self, PyObject *args, PyObject *kwds)
{
  int region, p=-1;
  int ok = PyArg_ParseTuple(args, "i", &region);
  if (ok)
  {
    p = self -> pg->get(region);
  }
  PyObject *ret = Py_BuildValue("i", p);
  return ret;
}

static PyObject *PopGrab_set_pop(PopGrab_Object *self, PyObject *args, PyObject *kwds)
{
  int x,y,p;
  int ok = PyArg_ParseTuple(args, "iii", &x, &y, &p);
  if (ok)
  {
    self -> pg->set_pop(x,y,p);
  }
  Py_RETURN_NONE;
}

static PyObject *PopGrab_read_pop(PopGrab_Object *self, PyObject *args, PyObject *kwds)
{
  int x,y,p=-1;
  int ok = PyArg_ParseTuple(args, "ii", &x, &y);
  if (ok)
  {
    p = self -> pg->read_pop(x,y);
  }

  PyObject *ret = Py_BuildValue("i", p);
  return ret;
}

static PyObject *PopGrab_read_reg(PopGrab_Object *self, PyObject *args, PyObject *kwds)
{
  int x,y,p=-1;
  int ok = PyArg_ParseTuple(args, "ii", &x, &y);
  if (ok)
  {
    p = self -> pg->read_reg(x,y);
  }

  PyObject *ret = Py_BuildValue("i", p);
  return ret;
}

static PyObject *PopGrab_put(PopGrab_Object *self, PyObject *args, PyObject *kwds)
{
  int x,y,region=-1;
  int ok = PyArg_ParseTuple(args, "iii", &region, &x, &y);
  if (ok)
  {
    self -> pg->put(region,x,y);
  }

  Py_RETURN_NONE;
}

static PyObject *PopGrab_get_neigh(PopGrab_Object *self, PyObject *args, PyObject *kwds)
{
  int region;
  int ok = PyArg_ParseTuple(args, "i", &region);
  if (ok)
  {
    PyObject *my_list = PyList_New(0);
    for(auto &n : self->pg->get_neigh(region))
    {
      auto neighbour = Py_BuildValue("i", n);
      PyList_Append(my_list, neighbour);
    }

    return my_list;
  }
  Py_RETURN_NONE;
}
static PyObject *PopGrab_remove(PopGrab_Object *self, PyObject *args, PyObject *kwds)
{
  int region=-1;
  int ok = PyArg_ParseTuple(args, "i", &region);
  if (ok)
  {
    self -> pg->remove(region);
  }

  Py_RETURN_NONE;
}

static PyObject *PopGrab_run(PopGrab_Object *self, PyObject *args, PyObject *kwds)
{
  self -> pg->run();
  Py_RETURN_NONE;
}

static PyMethodDef PopGrab_methods[] = {
  {"read_reg", (PyCFunction) PopGrab_read_reg, METH_VARARGS, "Return region at coords."},
  {"set_pop",  (PyCFunction) PopGrab_set_pop, METH_VARARGS, one_docstring},
  {"read_pop",  (PyCFunction) PopGrab_read_pop, METH_VARARGS, one_docstring},
  {"put",  (PyCFunction) PopGrab_put, METH_VARARGS, one_docstring},
  {"run",  (PyCFunction) PopGrab_run, METH_VARARGS, one_docstring},
  {"get",  (PyCFunction) PopGrab_get, METH_VARARGS, one_docstring},
  {"remove",  (PyCFunction) PopGrab_remove, METH_VARARGS, one_docstring},
  {"get_neigh", (PyCFunction) PopGrab_get_neigh, METH_VARARGS, one_docstring},
  {NULL}  /* Sentinel */
};

static PyTypeObject PopGrab_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "custom.PopGrab",
    .tp_doc = "PopGrab objects",
    .tp_basicsize = sizeof(PopGrab_Object),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PopGrab_new,
    .tp_init = (initproc) PopGrab_init,
    .tp_dealloc = (destructor) PopGrab_dealloc,
    .tp_methods = PopGrab_methods,
};

PyMODINIT_FUNC PyInit_popgrab(void)
{
   Py_Initialize();

   if (PyType_Ready(&PopGrab_Type) < 0)
        return NULL;
   
   pg = new PopulationGrabber(700,700);
   PyObject *m = PyModule_Create(&popgrab_module_definition);

   if (m == NULL)
   {
     return NULL;
   }

   Py_INCREF(&PopGrab_Type);
   PyModule_AddObject(m, "PopGrab", (PyObject *) &PopGrab_Type);

   return m;
}

