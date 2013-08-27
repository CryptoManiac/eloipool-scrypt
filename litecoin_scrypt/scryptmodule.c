#include <Python.h>

//#include "scrypt.h"

/*
static PyObject *scrypt_getpowhash(PyObject *self, PyObject *args)
{
    char *output;
    PyObject *value;
    PyStringObject *input;
    if (!PyArg_ParseTuple(args, "S", &input))
        return NULL;
    Py_INCREF(input);
    output = PyMem_Malloc(32);

    scrypt_1024_1_1_256((char *)PyString_AsString((PyObject*) input), output);
    Py_DECREF(input);
    value = Py_BuildValue("s#", output, 32);
    PyMem_Free(output);
    return value;
}
*/

static PyObject *scrypt_getpowhash(PyObject *self, PyObject *args, PyObject* kwargs) {
    char *input;
    int      inputlen;

    char *outbuf;
    size_t   outbuflen;

    static char *g2_kwlist[] = {"input", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y#", g2_kwlist,
                                     &input, &inputlen)) {
        return NULL;
    }

    outbuf = PyMem_Malloc(32);
    outbuflen = 32;

    Py_BEGIN_ALLOW_THREADS;
    
    scrypt_1024_1_1_256(input, outbuf);

    Py_END_ALLOW_THREADS;

    PyObject *value = NULL;
    
    value = Py_BuildValue("y#", outbuf, 32);
    
    PyMem_Free(outbuf);
    return value;
}


static PyMethodDef ScryptMethods[] = {
    { "getPoWHash", (PyCFunction) scrypt_getpowhash, METH_VARARGS | METH_KEYWORDS, "Returns the proof of work hash using scrypt" },
    { NULL, NULL, 0, NULL }
};

static struct PyModuleDef scryptmodule = {
    PyModuleDef_HEAD_INIT,
    "ltc_scrypt",
    NULL,
    -1,
    ScryptMethods
};

PyMODINIT_FUNC PyInit_ltc_scrypt(void) {
    PyObject *m = PyModule_Create(&scryptmodule);

    if (m == NULL) {
        return NULL;
    }

    return m;
}
