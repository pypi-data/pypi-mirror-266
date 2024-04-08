# FeynModel

FeynModel is a project to develop an XML dialect for describing Feynman Models.
It is in design very close to the UFO format, but not as restrictive (-> less complete).

[![PyPI version][pypi image]][pypi link] [![PyPI version][pypi versions]][pypi link]  ![downloads](https://img.shields.io/pypi/dm/feynml.svg)


[![test][a t image]][a t link]     [![Coverage Status][c t i]][c t l] [![Codacy Badge][cc c i]][cc c l]  [![Codacy Badge][cc q i]][cc q l]  [![Documentation][rtd t i]][rtd t l]

## Installation
```sh
pip install [--user] feynmodel
```

or from cloned source:

```sh
poerty install --with docs --with dev
poetry shell
```

## Documentation

*   <https://pyfeyn2.readthedocs.io/en/stable/feynml/>
*   <https://apn-pucky.github.io/pyfeyn2/feynml/index.html>

## Related:

*   <https://github.com/APN-Pucky/feynml>
*   <https://github.com/APN-Pucky/pyfeyn2>


## Development


### package/python structure:

*   <https://mathspp.com/blog/how-to-create-a-python-package-in-2022>
*   <https://www.brainsorting.com/posts/publish-a-package-on-pypi-using-poetry/>

[doc stable]: https://apn-pucky.github.io/feynmodel/index.html
[doc test]: https://apn-pucky.github.io/feynmodel/test/index.html

[pypi image]: https://badge.fury.io/py/feynmodel.svg
[pypi link]: https://pypi.org/project/feynmodel/
[pypi versions]: https://img.shields.io/pypi/pyversions/feynmodel.svg

[a t link]: https://github.com/APN-Pucky/feynmodel/actions/workflows/test.yml
[a t image]: https://github.com/APN-Pucky/feynmodel/actions/workflows/test.yml/badge.svg

[cc q i]: https://app.codacy.com/project/badge/Grade/6604fe515a7e4ebf927b44f8f5f79dc0
[cc q l]: https://www.codacy.com/gh/APN-Pucky/feynmodel/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=APN-Pucky/feynmodel&amp;utm_campaign=Badge_Grade
[cc c i]: https://app.codacy.com/project/badge/Coverage/6604fe515a7e4ebf927b44f8f5f79dc0
[cc c l]: https://www.codacy.com/gh/APN-Pucky/feynmodel/dashboard?utm_source=github.com&utm_medium=referral&utm_content=APN-Pucky/feynmodel&utm_campaign=Badge_Coverage

[c t l]: https://coveralls.io/github/APN-Pucky/feynmodel?branch=master
[c t i]: https://coveralls.io/repos/github/APN-Pucky/feynmodel/badge.svg?branch=master

[rtd t i]: https://readthedocs.org/projects/pyfeyn2/badge/?version=latest
[rtd t l]: https://pyfeyn2.readthedocs.io/en/latest/?badge=latest
