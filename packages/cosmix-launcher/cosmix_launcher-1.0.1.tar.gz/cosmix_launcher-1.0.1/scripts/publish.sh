#!/usr/bin/env sh
rm -rf dist
python3 -m pip install --upgrade pip build twine
python3 -m build && python3 -m twine upload dist/*
