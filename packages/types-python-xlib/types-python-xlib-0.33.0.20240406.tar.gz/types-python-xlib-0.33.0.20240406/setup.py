from setuptools import setup

name = "types-python-xlib"
description = "Typing stubs for python-xlib"
long_description = '''
## Typing stubs for python-xlib

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`python-xlib`](https://github.com/python-xlib/python-xlib) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`python-xlib`.

This version of `types-python-xlib` aims to provide accurate annotations
for `python-xlib==0.33.*`.
The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/python-xlib. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit `a9d644b3ffd9e9a8bb9a01393674972573cd256b` and was tested
with mypy 1.9.0, pyright 1.1.357, and
pytype 2024.3.19.
'''.lstrip()

setup(name=name,
      version="0.33.0.20240406",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/python-xlib.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['Xlib-stubs'],
      package_data={'Xlib-stubs': ['X.pyi', 'XK.pyi', 'Xatom.pyi', 'Xcursorfont.pyi', 'Xutil.pyi', '__init__.pyi', '_typing.pyi', 'display.pyi', 'error.pyi', 'ext/__init__.pyi', 'ext/composite.pyi', 'ext/damage.pyi', 'ext/dpms.pyi', 'ext/ge.pyi', 'ext/nvcontrol.pyi', 'ext/randr.pyi', 'ext/record.pyi', 'ext/res.pyi', 'ext/screensaver.pyi', 'ext/security.pyi', 'ext/shape.pyi', 'ext/xfixes.pyi', 'ext/xinerama.pyi', 'ext/xinput.pyi', 'ext/xtest.pyi', 'keysymdef/__init__.pyi', 'keysymdef/apl.pyi', 'keysymdef/arabic.pyi', 'keysymdef/cyrillic.pyi', 'keysymdef/greek.pyi', 'keysymdef/hebrew.pyi', 'keysymdef/katakana.pyi', 'keysymdef/korean.pyi', 'keysymdef/latin1.pyi', 'keysymdef/latin2.pyi', 'keysymdef/latin3.pyi', 'keysymdef/latin4.pyi', 'keysymdef/miscellany.pyi', 'keysymdef/publishing.pyi', 'keysymdef/special.pyi', 'keysymdef/technical.pyi', 'keysymdef/thai.pyi', 'keysymdef/xf86.pyi', 'keysymdef/xk3270.pyi', 'keysymdef/xkb.pyi', 'protocol/__init__.pyi', 'protocol/display.pyi', 'protocol/event.pyi', 'protocol/request.pyi', 'protocol/rq.pyi', 'protocol/structs.pyi', 'rdb.pyi', 'support/__init__.pyi', 'support/connect.pyi', 'support/lock.pyi', 'support/unix_connect.pyi', 'support/vms_connect.pyi', 'threaded.pyi', 'xauth.pyi', 'xobject/__init__.pyi', 'xobject/colormap.pyi', 'xobject/cursor.pyi', 'xobject/drawable.pyi', 'xobject/fontable.pyi', 'xobject/icccm.pyi', 'xobject/resource.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0 license",
      python_requires=">=3.8",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
