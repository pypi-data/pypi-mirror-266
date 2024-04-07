# An extension using the Meson build system.
#
# Author: Malte J. Ziebarth (mjz.science@fmvkb.de)
#
# Copyright 2022, Malte J. Ziebarth
# SPDX-License-Identifier: MIT

from pathlib import Path
from setuptools import Extension

class MesonExtension(Extension):
    """
    An extension to be built using the Meson build system.
    This class assumes that a `meson.build` file resides in
    the root directory of the Python package sources.
    """
    mebuex_destpath: Path | None
    mebuex_destname: Path | None

    def __init__(self, name, builddir='builddir', compiledname=None):
        self.name = name
        self.builddir = builddir
        self.sourcepath = Path().resolve()
        self.mebuex_destname = None
        self.mebuex_destpath = None
        if compiledname is None:
            self.compiledname = name.split('.')[-1]
        else:
            self.compiledname = compiledname
        super().__init__(name, [])
