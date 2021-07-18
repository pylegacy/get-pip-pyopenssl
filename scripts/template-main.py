#! /usr/bin/env python
# -*- coding: utf8 -*-
#
# Copyright (c) 2021 Víctor Molina García
#
# This file is part of get-pip-pyopenssl.
#
# get-pip-pyopenssl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# get-pip-pyopenssl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with get-pip-pyopenssl. If not, see <https://www.gnu.org/licenses/>.
#
"""Script to install a functional `pip` package that uses `pyOpenSSL`.

This is a helper script that downloads the appropriate `get-pip-pyopenssl`
script based on the Python installation used to run it.

The `get-pip-pyopenssl` script will install a functional `pip` package
for Python versions without Server Name Identification (SNI) support by
forcing the use of `pyOpenSSL` inside `pip`, which solves PyPI issues
#974 and #978 that left `pip` unusable for the Python versions without
SNI support:
    https://github.com/pypa/pypi-support/issues/974
    https://github.com/pypa/pypi-support/issues/978
"""


def get_arch():
    """Return the platform name."""

    import sys
    import distutils.util

    value = distutils.util.get_platform().replace("-", "_")
    if value.startswith("macosx"):
        raise NotImplementedError
    if value == "linux_x86_64" and sys.maxsize == 2147483647:
        value = "linux_i686"
    return value.replace("linux", "manylinux1")


def get_abi():
    """Return the ABI for the current Python installation."""

    import sys
    import platform
    from distutils import sysconfig

    # Get ABI flags.
    abid = ("d" if sysconfig.get_config_var("WITH_PYDEBUG") == 1 or
            hasattr(sys, "gettotalrefcount")
            else "")
    abim = ("m" if sys.version_info < (3, 8) and
            sysconfig.get_config_var("WITH_PYMALLOC") == 1 or
            platform.python_implementation() == "CPython"
            else "")
    abiu = ("u" if sys.version_info < (3, 3) and
            sysconfig.get_config_var("Py_UNICODE_SIZE") == 4 or
            sys.maxunicode == 0x10FFFF
            else "")

    # Create ABI string.
    pyver = "cp{0}{1}".format(*sys.version_info[:2])
    pyabi = "{0}{1}{2}{3}".format(*[pyver, abid, abim, abiu])

    return pyabi


def main():

    import os
    import re
    import sys
    import shutil
    import tempfile
    import subprocess

    try:
        from urllib.request import urlopen
    except ImportError:
        from urllib2 import urlopen

    arch = get_arch()
    pyabi = get_abi()
    pyver = re.match("(cp\d+)m?u?", pyabi).groups(1)[0]
    version = "{0}.{1}".format(*sys.version_info[:2])

    scriptroot = os.path.dirname(os.path.abspath(__file__))
    scriptname = "get-pip-pyopenssl-{0}-{1}-{2}.py".format(pyver, pyabi, arch)
    if re.match("https?://.*", scriptroot):
        # Script root is an URL.
        scriptpath = "/".join([scriptroot.strip("/"), version, scriptname])
        try:
            tmpdir = tempfile.mkdtemp(prefix="tmp-get-pip-pyopenssl-")
            tmppath = os.path.join(tmpdir, scriptname)
            conn = urlopen(scriptpath)
            try:
                with open(tmppath, "wb") as fd:
                    fd.write(conn.read())
            finally:
                conn.close()
            subprocess.call([sys.executable, "-u", tmppath])
        finally:
            if tmpdir:
                shutil.rmtree(tmpdir, ignore_errors=True)
    else:
        # Script root is a folder.
        scriptpath = os.path.join(scriptroot, version, scriptname)
        subprocess.call([sys.executable, "-u", scriptpath])


if __name__ == "__main__":
    main()
