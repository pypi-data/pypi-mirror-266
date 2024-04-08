#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import glob
from sys import argv
import pathlib



from setuptools import setup, Extension, find_packages
from os import listdir
from os.path import isfile, join
import platform
import pip
import sys

from setuptools.command.build_ext import build_ext as build_ext_orig


version = "0.0.9"
libName = "pyfdmss"

file_dir_path = os.path.dirname(os.path.realpath(__file__))


def import_lib(name):
    try:
        return __import__(name) # пытаемся импортировать
    except ImportError:
        pip.main(['install', name]) # ставим библиотеку если её нет
    return __import__(name) # возвращаем библиотеку

def package_files(directory):
    return [
        os.path.join(p, f)
        for p, d, files in os.walk(directory)
        for f in files
        if ".cpp" in f
    ]

pybind11 = import_lib('pybind11')

extra_compile_args = ["-O3", "-w", "-std=c++11", "-fopenmp"]
installRequiresList = ["pybind11"]
entry_points_Command = {"main_library": ["run = pyfdmss:run"]}

pyfdmss_module = Extension(
    libName,
    sources=package_files("./src/"),
    language="c++",
    extra_compile_args=extra_compile_args,
    extra_link_args=["-fopenmp"],
    include_dirs=[file_dir_path + "/src", pybind11.get_include()],
)

setup(
    name=libName,
    version=version,
    author="Kirill M. Gerke, Marina V. Karsanina, Andrey A. Ananev, Andrey Zubov",
    author_email="andrey.ananev@phystech.edu",
    license="GPLv3",
    packages=["fdmsslib"],
    package_dir={"fdmsslib": "./src/"},
    package_data={"fdmsslib": ["*.cpp", "*.h"]},
    ext_modules=[pyfdmss_module],
    setup_requires=installRequiresList,
    install_requires=installRequiresList,
    requires=installRequiresList,
    entry_points=entry_points_Command,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: C++",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
