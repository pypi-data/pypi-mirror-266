from setuptools import setup

name = "types-capturer"
description = "Typing stubs for capturer"
long_description = '''
## Typing stubs for capturer

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`capturer`](https://github.com/xolox/python-capturer) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`capturer`.

This version of `types-capturer` aims to provide accurate annotations
for `capturer==3.0.*`.
The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/capturer. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit `1d33abb91749cfa070fbc1482f186ff6b2ecbbbb` and was tested
with mypy 1.9.0, pyright 1.1.357, and
pytype 2024.3.19.
'''.lstrip()

setup(name=name,
      version="3.0.0.20240408",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/capturer.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['capturer-stubs'],
      package_data={'capturer-stubs': ['__init__.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0 license",
      python_requires=">=3.8",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
