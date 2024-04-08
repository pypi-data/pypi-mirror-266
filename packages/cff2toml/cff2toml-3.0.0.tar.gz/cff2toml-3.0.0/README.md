# cff2toml

A module to synchronize metadata between TOML and CFF files, including between pyproject.toml and CITATION.cff files.

[![PyPI - Version](https://img.shields.io/pypi/v/cff2toml.svg)](https://pypi.org/project/cff2toml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cff2toml.svg)](https://pypi.org/project/cff2toml)

---

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [Limitations](#limitations)
- [Roadmap](#roadmap)
- [License](#license)

## Installation

```console
pip install cff2toml
```

## Usage

```console
cff2toml --help
```

This package offers a CLI and classes to manipulate metadata in CFF and TOML files.

One common use case is to synchronize metadata between pyproject.toml and CITATION.cff files in a Python project.

### Viewing metadata in CITATION.cff and pyproject.toml

Here is how you change the version in both CITATION.cff and pyproject.toml,
assuming they are in the same directory

```
cff2toml view version
```

You can also change other common metadata. See the help.

### Changing metadata in both CITATION.cff and pyproject.toml

Here is how you change the version in both CITATION.cff and pyproject.toml,
assuming they are in the same directory

```
cff2toml change version 2.30.1
```

You can also change other common metadata. See the help.

## Limitations

The tool is in early and active development, so it should not be used yet for production systems. The CLI only supports version and license at the moment, but the underlying libraries support more.

## Roadmap

1. Improve CLI tool to view and change other metadata fields.
2. Improve documentation of the underlying classes.
3. Fix the output order so that it creates a more useful semantic ordering of propreties (not alphabetical).

## License

`cff2toml` is distributed under the terms of the [Apache 2.0](https://spdx.org/licenses/Apache-2.0.html) license
