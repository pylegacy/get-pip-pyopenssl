#! /usr/bin/env python
# -*- coding: utf8 -*-
#
# Copyright (c) 2021 Víctor Molina García
# MIT License
#
# Script to install a functional `pip` under Python 2.6 by forcing to
# use `pyOpenSSL`.
#
# Because it is not possible to install packages until having a `pip`
# that actually works, all the required dependencies are appended to
# the end of the file, as the usual `get-pip.py` does with `pip`.
#
# This script solves PyPI issues #974 and #978 that left Python 2.6
# unsupported due to the SNI requirement that the Python 2.6 `ssl`
# module cannot provide:
#     https://github.com/pypa/pypi-support/issues/974
#     https://github.com/pypa/pypi-support/issues/978
#
# The script currently supports `cp26mu` under `manylinux1_x86_64`.
#
from __future__ import print_function


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

    import pip
    rc = pip.main(["install"] + [pkgname] + list(args))
    if rc != 0:
        raise RuntimeError("pip failed with exit code {0}".format(rc))


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
    pip_file = os.path.join(pip_fold, "__init__.py")
    ssl_file = os.path.join(pip_fold, "_vendor", "urllib3",
                            "contrib", "pyopenssl.py")

    # Force `pip` to use `pyOpenSSL`.
    lines = []
    with open(pip_file, "r") as fd:
        found_try = False
        for line in fd:
            if "try:" in line:
                found_try = True
            elif found_try and "import ssl" in line:
                indent = line[:len(line) - len(line.lstrip())]
                injection = [
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
    with open(pip_file, "w") as fd:
        fd.writelines(lines)

    # Patch issue with unicode/bytes mix in `pyopenssl`.
    lines = []
    with open(ssl_file, "r") as fd:
        text = "return self.connection.send(data)"
        for line in fd:
            lines.append(line.replace("data", "data.encode()")
                         if text in line else line)
    with open(ssl_file, "w") as fd:
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
