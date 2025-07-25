# KiUtils

This project is a fork/continuation of https://github.com/mvnmgrx/kiutils.
> All credits go to the original author. Please note that some documentation might be outdated and not in sync with this project.

Simple and SCM-friendly KiCad file parser based on Python dataclasses for KiCad 9.0
and up. The following KiCad-related files are currently supported:
- `.kicad_pcb` - Board layouts
- `.kicad_sch` - Schematics
- `.kicad_mod` - Footprints
- `.kicad_sym` - Symbols and symbol libraries
- `.kicad_wks` - Worksheets
- `.kicad_dru` - Custom design rules
- `fp-lib-table` & `sym-lib-table` - Library tables

KiUtils implements a "pythonic" abstraction of the documentation found at the
[KiCad Developer Reference](https://dev-docs.kicad.org/en/file-formats/) and is
intended to work with an SCM like Git or SVN without breaking the layout of the
files when the Python script ran.

Parsing of the files is based on the S-Expression parser found in this library:
[GitLab: KiCad Library utilities](https://gitlab.com/kicad/libraries/kicad-library-utils)

## Prerequisites
The following is required to use `kiutils`:
- Python 3.8 or higher

## Installation
Use Python's `pip` to install it:
```
pip install git+https://github.com/Wittmann-MEE/kiutils.git
```

If ``kiutils`` is already installed, upgrade it to the latest version using:
```
pip install git+https://github.com/Wittmann-MEE/kiutils.git --upgrade
```

## Documentation
Visit the [kiutils documentation](https://kiutils.readthedocs.io/) for more information on how to 
install, use and develop `kiutils`, as well as examples and general module documentation.
