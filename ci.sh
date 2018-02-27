#!/bin/bash

cd "$(this_dir)" || exit

source ~/bash_ci


ci_run python3.6 -m pylint -E kython
ci_run python3.6 -m mypy kython

ci_report_errors
