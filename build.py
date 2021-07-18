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

if __name__ == "__main__":

    import os
    import re
    import sys
    import itertools
    import subprocess

    here = os.path.dirname(__file__)
    dest = os.path.join("build")

    targets = ("Linux", "Windows")
    archs = ("32bit", "64bit")
    abis = ("cp26m", "cp26mu", "cp27m", "cp27mu")

    for target, arch, abi in itertools.product(targets, archs, abis):

        # Do not build 'mu' ABI for Windows.
        if target == "Windows" and abi.endswith("u"):
            continue

        # Get Python version from ABI.
        version = re.match("cp(\d+)m?u?", abi).groups(1)[0]
        version = ".".join([version[0], version[1:]])

        # Call the generate script.
        print("- Building {0} for {1} {2}...".format(abi, target, arch))
        subprocess.call([
            sys.executable, "-u",
            os.path.join(here, "scripts", "generate.py"),
            "--target", target,
            "--arch", arch,
            "--abi", abi,
            "--dest", os.path.join(dest, version),
        ])
