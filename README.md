# get-pip-pyopenssl

This script generates working `get-pip.py` scripts for Python versions
without Server Name Identification (SNI) support by forcing the use
of `pyOpenSSL` inside `pip`.

Because it is not possible to install packages until having a `pip`
that actually works, all the required dependencies are appended to
the end of the script, as the usual `get-pip.py` does with `pip`.

The resulting `get-pip.py` script solves PyPI issues
[#974](https://github.com/pypa/pypi-support/issues/974) and
[#978](https://github.com/pypa/pypi-support/issues/978) that left `pip`
unusable for the Python versions without SNI support:

## Usage

At the moment, there is one specific `get-pip.py` script for every
platform, architecture and Python ABI, because the bundled dependencies
`cffi` and `cryptography` are pre-compiled binaries.

For example, to use this script under GNU/Linux 64-bit with Python 2.6
(ABI `cp26mu`), download the appropriate file from the
[Releases](../../releases) section and simply run it as:
```
python get-pip-cp26-cp26mu-manylinux1_x86_64.py
```

The project is currently in active development and future releases will
try to reduce the number of `get-pip.py` scripts to just have one per
Python version (major plus minor).

## License

```
Copyright (c) 2021 Víctor Molina García

get-pip-pyopenssl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

get-pip-pyopenssl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with get-pip-pyopenssl. If not, see <https://www.gnu.org/licenses/>.
```
