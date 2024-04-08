#!/usr/bin/env python3

import os
import sys
from setuptools import setup

SCRIPTDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(SCRIPTDIR, "src")))

import liteexpr

with open(os.path.join(SCRIPTDIR, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
                             name = "liteexpr",
                      description = "A light, expression language.",
                          version = liteexpr.__version__,
                          license = liteexpr.__license__,
                           author = liteexpr.__author__,
                     author_email = "markuskimius+py@gmail.com",
                              url = "https://github.com/markuskimius/liteexpr",
                         keywords = [ "expression", "language", "antlr4" ],
                 long_description = long_description,
    long_description_content_type = "text/markdown",
                         packages = [ "liteexpr" ],
                      package_dir = { "" : "src" },
                 install_requires = [ "antlr4-python3-runtime" ],
                   extras_require = {
                        "compile" : [
                            "antlr4-tools",
                        ]
                   },
             include_package_data = True,
)

