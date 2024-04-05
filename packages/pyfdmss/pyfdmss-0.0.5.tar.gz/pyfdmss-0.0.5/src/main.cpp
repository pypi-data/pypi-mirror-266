#include <pybind11/pybind11.h>
#include <Python.h>
#include <iostream>


#include "wrapper.h"
#include "testmodule.h"

namespace py = pybind11;

PYBIND11_MODULE(pyfdmss, m) {
    m.def("run", &run); // добавили функцию в модуль
    m.def("mrun", &mrun); // добавили функцию в модуль
};