from setuptools import setup

name = "types-PyAutoGUI"
description = "Typing stubs for PyAutoGUI"
long_description = '''
## Typing stubs for PyAutoGUI

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`PyAutoGUI`](https://github.com/asweigart/pyautogui) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`PyAutoGUI`.

This version of `types-PyAutoGUI` aims to provide accurate annotations
for `PyAutoGUI==0.9.*`.
The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/PyAutoGUI. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit `a9d644b3ffd9e9a8bb9a01393674972573cd256b` and was tested
with mypy 1.9.0, pyright 1.1.357, and
pytype 2024.3.19.
'''.lstrip()

setup(name=name,
      version="0.9.3.20240406",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/PyAutoGUI.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['types-PyScreeze'],
      packages=['pyautogui-stubs'],
      package_data={'pyautogui-stubs': ['__init__.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0 license",
      python_requires=">=3.8",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
