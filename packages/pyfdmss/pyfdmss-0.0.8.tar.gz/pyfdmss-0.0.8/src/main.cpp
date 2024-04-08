#include <pybind11/pybind11.h>
#include <Python.h>
#include <iostream>


#include "wrapper.h"
#include "testmodule.h"

namespace py = pybind11;



PYBIND11_MODULE(pyfdmss, m) {
    m.def("run", &run, "Function to run FDMSS solver",
            py::arg("config_path") = "config.xml", 
            py::arg("image_path") = "image3d.raw",
            py::arg("summary_path") = "output.txt",
            py::arg("velx_path") = "/dev/null", 
            py::arg("vely_path") = "/dev/null", 
            py::arg("velz_path") = "/dev/null",
            py::arg("pressure_path") = "/dev/null",
            py::arg("full_vel_path") = "/dev/null", 
            py::arg("comp_vel_path") = "/dev/null",
            py::arg("log_path") = "/dev/null"); // добавили функцию в модуль
    m.def("mrun", &mrun); // добавили функцию в модуль
};