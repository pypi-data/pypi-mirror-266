# digitalmarketplace-test-utils

![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)

Utility functions and scripts for testing Digital Marketplace code

This library's dependencies are deliberately kept minimal - see comment in `setup.py` before
adding any more!

## Versioning

Releases of this project follow [semantic versioning](http://semver.org/), ie
> Given a version number MAJOR.MINOR.PATCH, increment the:
>
> - MAJOR version when you make incompatible API changes,
> - MINOR version when you add functionality in a backwards-compatible manner, and
> - PATCH version when you make backwards-compatible bug fixes.

To make a new version:
- update the version in the `dmutils/__init__.py` file
- if you are making a major change, also update the change log;

When the pull request is merged a GitHub Action will tag the new version.

## Licence

Unless stated otherwise, the codebase is released under [the MIT License][mit].
This covers both the codebase and any sample code in the documentation.

The documentation is [&copy; Crown copyright][copyright] and available under the terms
of the [Open Government 3.0][ogl] licence.

[mit]: LICENCE
[copyright]: http://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/
[ogl]: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
