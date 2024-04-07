# Mebuex
A setuptools `Extension` and `build_ext` wrapper for builds based on Meson.

## Usage
Mebuex assumes that the structure of a package is as follows:
```
root
 | - builddir
 | ... some source layout to be compiled with Meson ...
 | - *packagename*
 |    | ... Python package layout handled by setup.py ...
 | - setup.py
 | - meson.build
```
That is, the root directory of the package contains the `setup.py` file,
the `meson.build` file, a Meson build directory (here `builddir`, but can be
configured), directories covering the sources to be built by Meson, and the
Python package source tree.

The relevant part of this layout is that `setup.py` and `meson.build` are
contained in the root directory, and that a designated build directory is
specified (need not exist before building). The Meson build file should contain
all relevant configuration to build a Python extension within the build
directory (here `builddir`). The `setup.py` file should be based on setuptools
and contain all relevant configuration for the Python part of the package.

Within the `setup.py` file, the Python extension built by Meson can then be
included using the `MesonExtension` and `build_ext` commands supplied by Mebuex.
An example code would look like this (suppose that the Meson build would yield
an extension `mypackage.backend`):
```python
from setuptools import setup
from mebuex import MesonExtension, build_ext

ext = MesonExtension('mypackage.backend', builddir='builddir')

setup(name='mypackage',
      version='1.0.0',
      author='Me',
      description='Or is it yours?',
      ext_modules=[ext],
      cmdclass={'build_ext' : build_ext}
)
```

### Finding the NumPy include directory
Mebuex ships with a Python script to discover the system NumPy includes when
building in the isolated build environment. The `gravelspoon` command that
helps break out of the build prison can be used in a `meson.build` file as
follows:
```python
incpath_np = run_command(
  gravelspoon
)

incdir_np = include_directories([incpath_np])
```


## Install
Mebuex can be installed with Pip locally
```bash
pip install .
```
or from PyPI:
```bash
pip install mebuex
```

## License
Mebuex is licensed under the MIT license (see the LICENSE file).

## Changelog
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


### [1.3.0] - 2024-04-07
#### Added
- Add the `mebuex_destpath` and `mebuex_destname` attributes to the
  `MebuexExtension` class. This can be used from install scripts, after
  performing the `build_ext` command, to retrieve the destination path
  where the extension file was copied to.

### [1.2.0] - 2023-12-29
#### Added
- Add the `gravelspoon` command to break out of the setuptools build isolation
  and find the system NumPy includes.

### [1.1.7] - 2023-08-20
#### Added
- Print error message stderr when re-raising assumed compilation error.

### [1.1.6] - 2023-08-20
#### Added
- Print error message when re-raising assumed compilation error.

### [1.1.5] - 2023-06-02
#### Changed
 - Try wiping the build directory if compilation within a previously setup
   build directory fails.

### [1.1.4] - 2023-05-04
#### Changed
 - Be more verbose on `destpath` error in `build_ext.build_extension`.

### [1.1.3] - 2023-04-14
#### Added
 - Add example project in `example/` subfolder.

### [1.1.2] - 2023-04-13
#### Changed
 - Change to `pyproject.toml` install workflow.

### [1.1.1] - 2022-10-05
#### Changed
 - Add a more informative error message if the directory to copy the built
   extension to does not exist.

### [1.1.0] - 2022-07-13
#### Changed
 - Fixed empty lib being copied to wheel directory instead of Meson-compiled
   lib.
 - Fix handling of dots in compiled names (likely irrelevant).

### [1.0.0] - 2022-07-13
#### Added
 - First version
