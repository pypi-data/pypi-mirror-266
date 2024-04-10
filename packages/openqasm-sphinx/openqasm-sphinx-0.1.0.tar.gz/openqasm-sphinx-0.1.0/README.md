# Sphinx tools for OpenQASM

[![License](https://img.shields.io/github/license/openqasm/openqasm-sphinx.svg?style=popout-square)](https://opensource.org/licenses/Apache-2.0)[![Release](https://img.shields.io/github/release/openqasm/openqasm-sphinx.svg?style=popout-square)](https://github.com/openqasm/openqasm-sphinx/releases)[![Downloads](https://img.shields.io/pypi/dm/openqasm-sphinx.svg?style=popout-square)](https://pypi.org/project/openqasm-sphinx/)

This repository provides the Python package `openqasm-sphinx`, which provides a [Sphinx extension](https://www.sphinx-doc.org) for documentation OpenQASM 2 and 3 code.


## Installation and use

Install the latest release of `openqasm-sphinx` package from pip:

```bash
pip install openqasm-sphinx
```

This will automatically install all the dependencies as well (Sphinx, for example) if they are not already installed.

To activate the extension add `openqasm_sphinx` to your `extensions` list in your Sphinx `conf.py` file, such as:

```python
project = "My Project"
author = "Me"
version = "1.0"

extensions = [
    "openqasm_sphinx",
]
```

There is no need to import the extension; Sphinx will ahndle this automatically.


## Developing

If you're looking to contribute to this project, please first read [our contributing guidelines](CONTRIBUTING.md).

Set up your development environment by installing the development requirements with pip:

```bash
pip install -r requirements-dev.txt tox
```

This installs a few more packages than the dependencies of the package at runtime.

After the development requirements are installed, you can install an editable version of the package with

```bash
pip install -e .
```

After this, any changes you make to the library code will immediately be present when you open a new Python interpreter session, or build a Sphinx project that depends on this project.


## License

This project is licensed under [version 2.0 of the Apache License](LICENSE).
This is a Qiskit project.
