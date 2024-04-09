from setuptools import setup

name = "types-icalendar"
description = "Typing stubs for icalendar"
long_description = '''
## Typing stubs for icalendar

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`icalendar`](https://github.com/collective/icalendar) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`icalendar`.

This version of `types-icalendar` aims to provide accurate annotations
for `icalendar==5.0.*`.
The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/icalendar. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit `09ff220e098da389aa68116d6374546633e4a928` and was tested
with mypy 1.9.0, pyright 1.1.357, and
pytype 2024.3.19.
'''.lstrip()

setup(name=name,
      version="5.0.0.20240409",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/icalendar.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['types-pytz'],
      packages=['icalendar-stubs'],
      package_data={'icalendar-stubs': ['__init__.pyi', 'cal.pyi', 'caselessdict.pyi', 'parser.pyi', 'parser_tools.pyi', 'prop.pyi', 'timezone_cache.pyi', 'tools.pyi', 'windows_to_olson.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0 license",
      python_requires=">=3.8",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
