.. image:: https://img.shields.io/pypi/v/jaraco.zstd.svg
   :target: https://pypi.org/project/jaraco.zstd

.. image:: https://img.shields.io/pypi/pyversions/jaraco.zstd.svg

.. image:: https://github.com/jaraco/jaraco.zstd/actions/workflows/main.yml/badge.svg
   :target: https://github.com/jaraco/jaraco.zstd/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. .. image:: https://readthedocs.org/projects/PROJECT_RTD/badge/?version=latest
..    :target: https://PROJECT_RTD.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2024-informational
   :target: https://blog.jaraco.com/skeleton

Extract files from a ``.tar.zstd``::

    python -m jaraco.zstd --extract filename.tar.zstd

Usage::

    python -m jaraco.zstd --help
    usage: zstd.py [-h] -e SOURCE [--out-dir OUT_DIR]

    options:
      -h, --help            show this help message and exit
      -e SOURCE, --extract SOURCE
      --out-dir OUT_DIR

This project can be retired if
`indygreg/python-zstandard#186 <https://github.com/indygreg/python-zstandard/issues/186>`_
is fixed.
