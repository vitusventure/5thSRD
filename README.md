# 5thSRD
This is a markdown version of the 5th Edition System Reference Document.

Documents are in the docs/ directory.

Published as a website built via mkdocs on https://5thsrd.org

# How to Build
Various indexes are built using build_indexes.py.

Install dependencies with [poetry](https://python-poetry.org/docs/#installation):
```bash
poetry install
poetry shell
```

For pdf dependencies follow these instructions: https://github.com/orzih/mkdocs-with-pdf#requirements (https://doc.courtbouillon.org/weasyprint/latest/first_steps.html#installation)

Build the full site using mkdocs (http://www.mkdocs.org/): mkdocs build --clean

You can also serve locally by running mkdocs serve
