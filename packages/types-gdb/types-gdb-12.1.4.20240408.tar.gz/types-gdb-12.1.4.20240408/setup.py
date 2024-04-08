from setuptools import setup

name = "types-gdb"
description = "Typing stubs for gdb"
long_description = '''
## Typing stubs for gdb

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`gdb`](https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;a=tree) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`gdb`.

This version of `types-gdb` aims to provide accurate annotations
for `gdb==12.1.*`.
The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/gdb. All fixes for
types and metadata should be contributed there.

Type hints for GDB's [Python API](https://sourceware.org/gdb/onlinedocs/gdb/Python-API.html). Note that this API is available only when running Python scripts under GDB: it is not possible to install the `gdb` package separately, for instance using `pip`.

See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit `1d33abb91749cfa070fbc1482f186ff6b2ecbbbb` and was tested
with mypy 1.9.0, pyright 1.1.357, and
pytype 2024.3.19.
'''.lstrip()

setup(name=name,
      version="12.1.4.20240408",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/gdb.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['gdb-stubs'],
      package_data={'gdb-stubs': ['FrameDecorator.pyi', 'FrameIterator.pyi', '__init__.pyi', 'events.pyi', 'printing.pyi', 'prompt.pyi', 'types.pyi', 'unwinder.pyi', 'xmethod.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0 license",
      python_requires=">=3.8",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
