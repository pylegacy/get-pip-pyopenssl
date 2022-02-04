#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021-2022 Víctor Molina García
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

This script installs a functional `pip` package for Python versions
without Server Name Identification (SNI) support by forcing the use
of `pyOpenSSL` inside `pip`.

Because it is not possible to install packages until having a `pip`
that actually works, all the required dependencies are appended to
the end of the script, as the usual `get-pip.py` does with `pip`.

The resulting `get-pip.py` script solves PyPI issues #974 and #978
that left `pip` unusable for the Python versions without SNI support:
    https://github.com/pypa/pypi-support/issues/974
    https://github.com/pypa/pypi-support/issues/978
"""
from __future__ import print_function

__version__ = None


def unpack(path, dest=None):

    import os
    from contextlib import closing
    from zipfile import ZipFile

    pkgname = os.path.basename(path).split("-")[0]
    if dest is None:
        dest = os.getcwd()
    with closing(ZipFile(path, "r")) as archive:
        for file in archive.namelist():
            if file.startswith("{0}/".format(pkgname)):
                archive.extract(file, dest)


def pkgdecode(text):

    from base64 import b64decode
    return b64decode("".join(line.strip() for line in text.split("\n")))


def pip_extract(pkgname, dest=None):

    import os
    import shutil
    import tempfile

    pkg = PACKAGES[pkgname]
    tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp(prefix="tmp-get-pip-extract-")
        pkgpath = os.path.join(tmpdir, pkg["filename"])
        pkgdata = pkgdecode(pkg["filedata"])
        with open(pkgpath, "wb") as fd:
            fd.write(pkgdata)
        unpack(pkgpath, dest=dest)
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


def pip_install(pkgname, *args):

    import os
    import sys
    import warnings
    import subprocess
    import pip
    from pip._vendor.urllib3.exceptions import SNIMissingWarning
    from pip._vendor.urllib3.exceptions import InsecurePlatformWarning
    pip_parent_dir = os.path.dirname(os.path.dirname(pip.__file__))

    def pip_main(*args):
        # pip main call for pip >= 10.
        if hasattr(pip, "_internal"):
            env = os.environ.copy()
            env["PYTHONPATH"] = "{0}{1}{2}".format(
                pip_parent_dir, ";" if os.name == "nt" else ":",
                os.environ.get("PYTHONPATH", ""))
            wflags = ["-W ignore::{0}.{1}".format(x.__module__, x.__name__)
                      for x in [SNIMissingWarning, InsecurePlatformWarning]]
            return subprocess.call(
                [sys.executable] + wflags + ["-m", "pip"] + list(args),
                env=env)
        # pip main call for pip < 10.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=SNIMissingWarning)
            warnings.simplefilter("ignore", category=InsecurePlatformWarning)
            return pip.main(list(args))

    retcode = pip_main("install", pkgname, *args)
    if retcode != 0:
        raise RuntimeError("pip failed with exit code {0}".format(retcode))


def pip_autoinstall(pkgname, *args):

    import os
    import shutil
    import tempfile

    pkg = PACKAGES[pkgname]
    tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp(prefix="tmp-get-pip-autoinstall-")
        pkgpath = os.path.join(tmpdir, pkg["filename"])
        pkgdata = pkgdecode(pkg["filedata"])
        with open(pkgpath, "wb") as fd:
            fd.write(pkgdata)
        pip_install(pkgpath, *args)
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


def pip_autopatch():

    import os
    import pip

    # Define files to patch.
    pip_fold = os.path.dirname(pip.__file__)
    pyopenssl_file = os.path.join(pip_fold, "_vendor", "urllib3",
                                  "contrib", "pyopenssl.py")

    pip_file = os.path.join(pip_fold, "__init__.py")
    compat_file = os.path.join(pip_fold, "_vendor", "distlib", "compat.py")
    sslimport_file = compat_file if os.path.exists(compat_file) else pip_file

    # Force `pip` to use `pyOpenSSL`.
    lines = []
    with open(sslimport_file, "r") as fd:
        found_try = False
        for line in fd:
            if "try:" in line:
                found_try = True
            elif found_try and "import ssl" in line:
                indent = line[:len(line) - len(line.lstrip())]
                injection = [
                    "import warnings",
                    "with warnings.catch_warnings():",
                    "    warnings.simplefilter(\"ignore\", category=DeprecationWarning)",
                    "    from pip._vendor.urllib3.contrib import pyopenssl",
                    "    pyopenssl.inject_into_urllib3()",
                    "    del pyopenssl",
                ]
                lines.extend(["{0}{1}\n".format(indent, item)
                              for item in injection])
                found_try = False
            else:
                found_try = False
            lines.append(line)
    with open(sslimport_file, "w") as fd:
        fd.writelines(lines)

    # Patch issue with unicode/bytes mix in `pyopenssl`.
    lines = []
    with open(pyopenssl_file, "r") as fd:
        text = "return self.connection.send(data)"
        for line in fd:
            lines.append(line.replace("data", "data.encode()")
                         if text in line else line)
    with open(pyopenssl_file, "w") as fd:
        fd.writelines(lines)


def main():

    import os
    import sys
    import imp
    import shutil
    import tempfile

    tmpdir = None
    curdir = os.getcwd()
    force_args = ["-I", "--no-deps"]

    try:

        tmpdir = tempfile.mkdtemp(prefix="tmp-get-pip-")
        os.chdir(tmpdir)

        # Unpack `pip` and `wheel` temporarily.
        for pkg in ("pip", "wheel"):
            pip_extract(pkg)
        sys.path.insert(0, tmpdir)

        # Install `pip`, `wheel` and `setuptools`.
        for pkg in ("pip", "argparse", "wheel", "setuptools"):
            pip_autoinstall(pkg, *force_args)

        # Delete temporary `pip` and `wheel` and reload the installed ones.
        sys.path.pop(0)
        for pkg in ("pip", "wheel"):
            shutil.rmtree(pkg, ignore_errors=True)
            imp.reload(imp.load_module(pkg, *imp.find_module(pkg)))

        # Install `cffi` and its dependencies.
        for pkg in ("pycparser", "cffi"):
            pip_autoinstall(pkg)

        # Install `enum34` and its dependencies.
        for pkg in ("ordereddict", "enum34"):
            if pkg in PACKAGES:
                pip_autoinstall(pkg, *force_args)

        # Install `cryptography` dependencies.
        for pkg in ("six", "asn1crypto", "idna", "ipaddress"):
            pip_autoinstall(pkg)

        # Install `cryptography` and `pyOpenSSL`.
        for pkg in ("cryptography", "pyOpenSSL"):
            pip_autoinstall(pkg)

        # Reload `pip` again and patch it.
        imp.reload(imp.load_module("pip", *imp.find_module("pip")))
        pip_autopatch()
        print("Successfully patched pip")

    finally:

        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)
        os.chdir(curdir)


PACKAGES = {}


if __name__ == "__main__":
    main()
