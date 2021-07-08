#! /usr/bin/env python


class Package(object):
    """Wrapper class for Python packages coming from PyPI."""

    REMOTE = "https://files.pythonhosted.org/packages"

    def __init__(self, filename):
        """Create a new instance from a Python package filename."""

        self.filename = filename
        self.data = None

    @property
    def name(self):
        """Python package name."""

        nsuffixes = 1 + int(self.filename.endswith(".tar.gz"))
        base = self.filename.rsplit(".", nsuffixes)[0]
        return self.filename.split("-")[0]

    @property
    def version(self):
        """Python package version in string format."""

        nsuffixes = 1 + int(self.filename.endswith(".tar.gz"))
        base = self.filename.rsplit(".", nsuffixes)[0]
        return base.split("-")[1]

    @property
    def url(self):
        """Python package remote url from the PyPI repository."""

        import re
        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        # Define some patterns.
        urlpattern = "https://pypi.org/project/{0}/{1}/#files"
        rowpattern = ".*<a href=\"(.*{0}.*)\">".format(
            self.filename.replace(".", "\\."))

        # Parse the download page from PyPI to get the package url.
        conn = urlopen(urlpattern.format(self.name, self.version))
        try:
            htmlpage = conn.read().decode("utf-8").splitlines()
        finally:
            conn.close()

        for htmlrow in htmlpage:
            match = re.match(rowpattern, htmlrow)
            if match:
                return match.group(1)
        msg = "no url found for package {0}".format(self.filename)
        raise ValueError(msg)

    def download(self):
        """Get the Python package as a :class:`bytes` object."""

        try:
            from urllib.request import urlopen
        except ImportError:
            from urllib2 import urlopen

        conn = urlopen(self.url)
        try:
            self.data = conn.read()
        finally:
            conn.close()

    def textify(self):
        """Return the Python package data as plain encoded text."""

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
        """Return data string from a data stream using base64."""

        spaces = " " * pad
        if nchars is None:
            nchars = 79 - pad

        from base64 import b64encode
        raw = b64encode(data).decode("utf-8")
        lines = [raw[i:i + nchars] for i in range(0, len(raw), nchars)]
        return "\n".join(["{0}{1}".format(spaces, line) for line in lines])

    @staticmethod
    def pkgdecode(text):
        """Return data stream from a data string using base64."""

        from base64 import b64decode
        return b64decode("".join(line.strip() for line in text.split("\n")))


def main():

    PACKAGES = [
        # Essential packages (`pip`, `wheel` and `setuptools`).
        Package("pip-9.0.3-py2.py3-none-any.whl"),
        Package("argparse-1.4.0-py2.py3-none-any.whl"),
        Package("wheel-0.29.0-py2.py3-none-any.whl"),
        Package("setuptools-36.8.0-py2.py3-none-any.whl"),
        # `cffi` and dependencies (for `cryptography`).
        Package("pycparser-2.18.tar.gz"),
        Package("cffi-1.11.2-cp26-cp26mu-manylinux1_x86_64.whl"),
        # `enum34` and dependencies (for `cryptography`).
        Package("ordereddict-1.1.tar.gz"),
        Package("enum34-1.1.10.tar.gz"),
        # `cryptography` and its remaining dependencies.
        Package("asn1crypto-1.4.0-py2.py3-none-any.whl"),
        Package("idna-2.7-py2.py3-none-any.whl"),
        Package("ipaddress-1.0.23-py2.py3-none-any.whl"),
        Package("cryptography-2.1.1-cp26-cp26mu-manylinux1_x86_64.whl"),
        # `pyOpenSSL` and its remaining dependencies.
        Package("six-1.13.0-py2.py3-none-any.whl"),
        Package("pyOpenSSL-16.2.0-py2.py3-none-any.whl"),
    ]

    pkgtext = []
    for pkg in PACKAGES:
        pkgtext.append(pkg.textify())
    injection = "\n".join(pkgtext)

    import os.path
    scripts_dir = os.path.dirname(__file__)
    template_file = os.path.join(scripts_dir, "get-pip-template.py")
    with open("get-pip-py2.6.py", "w") as fd1:
        with open(template_file, "r") as fd2:
            for line2 in fd2:
                if line2 != "PACKAGES = {}\n":
                    fd1.write(line2)
                else:
                    fd1.write("PACKAGES = {{\n\n{0}\n\n}}\n".format(injection))


if __name__ == "__main__":
    main()
