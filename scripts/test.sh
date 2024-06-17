#!/usr/bin/env bash

set -e
poetry run coverage run -m pytest -s --doctest-glob="utils.py"
poetry run coverage report --omit="tests/*" -m
