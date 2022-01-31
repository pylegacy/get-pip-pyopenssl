# get-pip-pyopenssl

This tool generates working `get-pip` scripts that force the use of
`pyOpenSSL` inside `pip`. Because it is not possible to install packages
until having a `pip` that actually works, all the required dependencies
are appended to the end of the scripts, as the usual `get-pip` does with
`pip`.

The resulting `get-pip` scripts solve PyPI issues
[#974](https://github.com/pypa/pypi-support/issues/974) and
[#978](https://github.com/pypa/pypi-support/issues/978) that left `pip`
unusable for the Python versions without SNI support.

The project is currently in active development. At the moment, the tool
provides support for Python 2.6 and Python 2.7 under GNU/Linux and
Windows. Future releases will try to add support for more Python
versions.

## Usage

There is one specific script for every platform, architecture and Python
ABI, because the bundled dependencies `cffi` and `cryptography` are
pre-compiled binaries.

The helper script `get-pip-pyopenssl.py` takes care of downloading the
appropriate script under the hood and it is the recommended way of using
the tool.

* For GNU/Linux systems, run:
```sh
wget http://pylegacy.org/hub/get-pip-pyopenssl.py
python get-pip-pyopenssl.py
```

* For Windows, run (in PowerShell):
```sh
Invoke-WebRequest http://pylegacy.org/hub/get-pip-pyopenssl.py -OutFile get-pip-pyopenssl.py
python get-pip-pyopenssl.py
```

## License

```
Copyright (c) 2021-2022 Víctor Molina García

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
