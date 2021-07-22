# Changelog

All notable changes to this project will be documented in this file. The format
is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and the
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2021-07-23

### Fixed
- Silence expected warnings `SNIMissingWarning` and `InsecurePlatformWarning`
  while still patching `pip`.

## [0.1.0] - 2021-07-18

### Added
- Initial Python 2.6 and Python 2.7 support for the following platforms:
  - GNU/Linux: archs i686 and x86_64, ABIs cp26m, cp26mu, cp27m, cp27mu.
  - Windows: archs win32 and win_amd64, ABIs cp26m, cp27m.
- Helper script `get-pip-pyopenssl.py` that finds the specific script based
  on the system information provided by the Python environment.


[Unreleased]:
https://github.com/molinav/get-pip-pyopenssl/compare/v0.2.0...master
[0.2.0]:
https://github.com/molinav/get-pip-pyopenssl/compare/v0.1.0...v0.2.0
[0.1.0]:
https://github.com/molinav/get-pip-pyopenssl/releases/tag/v0.1.0
