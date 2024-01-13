#!/bin/bash

find ./ -name '*.pyc' -exec rm -f {} \; 2>/dev/null
find ./ -name '__pycache__' -exec rm -rf {} \; 2>/dev/null
find ./ -name 'Thumbs.db' -exec rm -f {} \; 2>/dev/null
find ./ -name '*~' -exec rm -f {} \; 2>/dev/null
rm -rf .cache .pytest_cache .mypy_cache build dist *.egg-info htmlcov .tox/ docs/_build 2>/dev/null
