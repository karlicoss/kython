#!/bin/bash
set -e
pylint -E kython
mypy kython
