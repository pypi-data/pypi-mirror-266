from setuptools import setup

name = "types-docutils"
description = "Typing stubs for docutils"
long_description = '''
## Typing stubs for docutils

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`docutils`](https://sourceforge.net/p/docutils/code) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`docutils`.

This version of `types-docutils` aims to provide accurate annotations
for `docutils==0.20.*`.
The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/docutils. All fixes for
types and metadata should be contributed there.

This stub package is marked as [partial](https://peps.python.org/pep-0561/#partial-stub-packages).
If you find that annotations are missing, feel free to contribute and help complete them.


See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit `a9d644b3ffd9e9a8bb9a01393674972573cd256b` and was tested
with mypy 1.9.0, pyright 1.1.357, and
pytype 2024.3.19.
'''.lstrip()

setup(name=name,
      version="0.20.0.20240406",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/docutils.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['docutils-stubs'],
      package_data={'docutils-stubs': ['__init__.pyi', 'core.pyi', 'examples.pyi', 'frontend.pyi', 'io.pyi', 'languages/__init__.pyi', 'nodes.pyi', 'parsers/__init__.pyi', 'parsers/null.pyi', 'parsers/recommonmark_wrapper.pyi', 'parsers/rst/__init__.pyi', 'parsers/rst/directives/__init__.pyi', 'parsers/rst/directives/admonitions.pyi', 'parsers/rst/directives/body.pyi', 'parsers/rst/directives/html.pyi', 'parsers/rst/directives/images.pyi', 'parsers/rst/directives/misc.pyi', 'parsers/rst/directives/parts.pyi', 'parsers/rst/directives/references.pyi', 'parsers/rst/directives/tables.pyi', 'parsers/rst/roles.pyi', 'parsers/rst/states.pyi', 'parsers/rst/tableparser.pyi', 'readers/__init__.pyi', 'readers/doctree.pyi', 'readers/pep.pyi', 'readers/standalone.pyi', 'statemachine.pyi', 'transforms/__init__.pyi', 'utils/__init__.pyi', 'writers/__init__.pyi', 'writers/docutils_xml.pyi', 'writers/html4css1.pyi', 'writers/html5_polyglot.pyi', 'writers/latex2e.pyi', 'writers/manpage.pyi', 'writers/null.pyi', 'writers/odf_odt.pyi', 'writers/pep_html.pyi', 'writers/pseudoxml.pyi', 'writers/s5_html.pyi', 'writers/xetex.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0 license",
      python_requires=">=3.8",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
