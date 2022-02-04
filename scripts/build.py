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
"""Script to build `get-pip-pyopenssl` distributables."""
from __future__ import print_function


def main():
    """Main script function."""

    import io
    import os
    import re
    import sys
    import argparse
    import itertools
    import subprocess
    from generate import __version__

    # Define arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dest",
        type=str, help="Destination build folder", required=False,
        default="build")
    parser.add_argument(
        "--remote",
        type=str, help="Expected remote root location", required=False,
        default=None)

    # Parse arguments.
    args = parser.parse_args()

    here = os.path.dirname(__file__)
    targets = ("Linux", "Windows")
    archs = ("32bit", "64bit")
    abis = ("cp26m", "cp26mu", "cp27m", "cp27mu")

    for target, arch, abi in itertools.product(targets, archs, abis):

        # Do not build 'mu' ABI for Windows.
        if target == "Windows" and abi.endswith("u"):
            continue

        # Get Python version from ABI.
        version = re.match(r"cp(\d+)m?u?", abi).groups(1)[0]
        version = ".".join([version[0], version[1:]])

        # Call the generate script.
        print("- Building {0} for {1} {2}...".format(abi, target, arch))
        subprocess.call([
            sys.executable, "-u",
            os.path.join(here, "generate.py"),
            "--target", target,
            "--arch", arch,
            "--abi", abi,
            "--dest", os.path.join(args.dest, "pip", version),
        ])

    # Write out the helper script.
    template = os.path.join(here, "template-main.py")
    outfile = os.path.join(args.dest, "get-pip-pyopenssl.py")
    with io.open(outfile, "wb") as fd1:
        with io.open(template, "r", encoding="utf-8") as fd2:
            for line2 in fd2:
                if line2 == "__version__ = None\n":
                    line2 = "__version__ = \"{0}\"\n".format(__version__)
                if line2.startswith("    scriptroot =") and args.remote:
                    line2 = "    scriptroot = \"{0}\"\n".format(args.remote)
                fd1.write(line2.encode())


if __name__ == "__main__":
    main()
