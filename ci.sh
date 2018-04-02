#!/bin/bash
source ~/bash_ci

cd "$(this_dir)" || exit

ci_run python3.6 -m pylint -E kython
ci_run python3.6 -m mypy kython

ci_report_errors
