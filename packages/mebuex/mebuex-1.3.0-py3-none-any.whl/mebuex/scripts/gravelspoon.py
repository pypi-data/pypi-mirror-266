# Breaking out of the setuptools build isolation to use the system's
# NumPy includes.
#
# Author: Malte J. Ziebarth (mjz.science@fmvkb.de)
#
# Copyright 2023, Malte J. Ziebarth
# SPDX-License-Identifier: MIT


def numpy_get_include():
    """
    This function tries to find the NumPy include directory,
    potentially within a build isolation, and prints the include
    path to standard out.
    """
    try:
        # In case things work out of the box:
        import numpy
        print(numpy.get_include())

    except ImportError:
        import subprocess
        import sys
        from pathlib import Path
        from os import rename, symlink
        np_incl_byte = subprocess.check_output(
            [sys.executable,'-c','import os;os.chdir("..");import numpy;'
                                 'print(numpy.get_include())'],
            env={}
        )

        np_include = np_incl_byte.decode().strip()

        # Make numpy available in the isolated environment this code is running
        # in. Do this by symlinking the previously discovered system NumPy
        # package into a site-package directory found in the isolated
        # environment Python path.
        found_site_packages = False
        success = False
        for path in sys.path[::-1]:
            p = Path(path)
            if 'site-packages' in path:
                found_site_packages = True
                p = Path(path)
                if not p.exists():
                    continue
                is_dir = (p / "numpy").is_dir()
                if is_dir:
                    rename((p / "numpy").resolve(), (p / "numpyold").resolve())
                symlink(Path(np_include).parent.parent.resolve(),
                        (p / "numpy").resolve())
                success = True
                break

        if not success:
            msg = "Could not link the NumPy package to the isolated " \
                  "site-packages."
            if found_site_packages:
                msg += " Found site-packages but did not exist."
            else:
                msg += " Found no site-pacakges."
            raise RuntimeError(msg)

        print(np_include)
