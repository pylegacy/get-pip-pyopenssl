#! /usr/bin/env python


class Package(object):

    REMOTE = "https://files.pythonhosted.org/packages"

    def __init__(self, filename, dir1, dir2, dir3):

        self.filename = filename
        self.dir1 = dir1
        self.dir2 = dir2
        self.dir3 = dir3
        self.data = None

    @property
    def name(self):
        return self.filename.split("-")[0]

    @property
    def version(self):
        return self.filename.split("-")[1]

    @property
    def url(self):
        return "{0}/{1}/{2}/{3}/{4}".format(
            self.REMOTE, self.dir1, self.dir2, self.dir3, self.filename)

    def download(self):
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen
        conn = urlopen(self.url)
        self.data = conn.read()

    def textify(self):

        if self.data is None:
            self.download()

        return "\n".join([
            "\"{name}\": {{",
            "    \"filename\":",
            "        \"{filename}\",",
            "    \"filedata\": \"\"\"",
            "{filedata}",
            "    \"\"\",",
            "}},"
        ]).format(name=self.name,
                  filename=self.filename,
                  filedata=self.pkgencode(self.data))

    @staticmethod
    def pkgencode(data, pad=0, nchars=None):

        spaces = " " * pad
        if nchars is None:
            nchars = 79 - pad

        from base64 import b64encode
        raw = b64encode(data).decode("utf-8")
        lines = [raw[i:i + nchars] for i in range(0, len(raw), nchars)]
        return "\n".join(["{0}{1}".format(spaces, line) for line in lines])

    @staticmethod
    def pkgdecode(text):

        from base64 import b64decode
        return b64decode("".join(line.strip() for line in text.split("\n")))


def main():

    PACKAGES = [
        # Essential packages (`pip`, `wheel` and `setuptools`).
        Package(
            "pip-9.0.3-py2.py3-none-any.whl",
            dir1="ac", dir2="95",
            dir3="a05b56bb975efa78d3557efa36acaf9cf5d2fd0ee0062060493687432e03"
        ),
        Package(
            "argparse-1.4.0-py2.py3-none-any.whl",
            dir1="f2", dir2="94",
            dir3="3af39d34be01a24a6e65433d19e107099374224905f1e0cc6bbe1fd22a2f"
        ),
        Package(
            "wheel-0.29.0-py2.py3-none-any.whl",
            dir1="8a", dir2="e9",
            dir3="8468cd68b582b06ef554be0b96b59f59779627131aad48f8a5bce4b13450"
        ),
        Package(
            "setuptools-36.8.0-py2.py3-none-any.whl",
            dir1="27", dir2="f6",
            dir3="fabfc9c71c9b1b99d2ec4768a6e1f73b2e924f51c89d436302b8c2a25459"
        ),
        # `cffi` and dependencies (for `cryptography`).
        Package(
            "pycparser-2.18.tar.gz",
            dir1="8c", dir2="2d",
            dir3="aad7f16146f4197a11f8e91fb81df177adcc2073d36a17b1491fd09df6ed"
        ),
        Package(
            "cffi-1.11.2-cp26-cp26mu-manylinux1_x86_64.whl",
            dir1="60", dir2="3f",
            dir3="ed4937422ef943ec6db2c3ddf3b8e1dc1621e0903d1c9fba1d834f7a16dc"
        ),
        # `enum34` and dependencies (for `cryptography`).
        Package(
            "ordereddict-1.1.tar.gz",
            dir1="53", dir2="25",
            dir3="ef88e8e45db141faa9598fbf7ad0062df8f50f881a36ed6a0073e1572126"
        ),
        Package(
            "enum34-1.1.10.tar.gz",
            dir1="11", dir2="c4",
            dir3="2da1f4952ba476677a42f25cd32ab8aaf0e1c0d0e00b89822b835c7e654c"
        ),
        # `cryptography` and its remaining dependencies.
        Package(
            "asn1crypto-1.4.0-py2.py3-none-any.whl",
            dir1="b5", dir2="a8",
            dir3="56be92dcd4a5bf1998705a9b4028249fe7c9a035b955fe93b6a3e5b829f8"
        ),
        Package(
            "idna-2.7-py2.py3-none-any.whl",
            dir1="4b", dir2="2a",
            dir3="0276479a4b3caeb8a8c1af2f8e4355746a97fab05a372e4a2c6a6b876165"
        ),
        Package(
            "ipaddress-1.0.23-py2.py3-none-any.whl",
            dir1="c2", dir2="f8",
            dir3="49697181b1651d8347d24c095ce46c7346c37335ddc7d255833e7cde674d"
        ),
        Package(
            "cryptography-2.1.1-cp26-cp26mu-manylinux1_x86_64.whl",
            dir1="12", dir2="8b",
            dir3="fc515561ebe9cea1eb1d48b09b5cdff4164966b68c13fa6c04aec205f9eb"
        ),
        # `pyOpenSSL` and its remaining dependencies.
        Package(
            "six-1.13.0-py2.py3-none-any.whl",
            dir1="65", dir2="26",
            dir3="32b8464df2a97e6dd1b656ed26b2c194606c16fe163c695a992b36c11cdf"
        ),
        Package(
            "pyOpenSSL-16.2.0-py2.py3-none-any.whl",
            dir1="ac", dir2="93",
            dir3="b4cd538d31adacd07f83013860db6b88d78755af1f3fefe68ec22d397e7b"
        ),
    ]

    pkgtext = []
    for pkg in PACKAGES:
        pkgtext.append(pkg.textify())
    injection = "\n".join(pkgtext)

    with open("get-pip-py26.py", "w") as fd1:
        with open("get-pip-template.py", "r") as fd2:
            for line2 in fd2:
                if line2 != "PACKAGES = {}\n":
                    fd1.write(line2)
                else:
                    fd1.write("PACKAGES = {{\n\n{0}\n\n}}\n".format(injection))


if __name__ == "__main__":
    main()
