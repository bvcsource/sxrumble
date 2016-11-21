#!/usr/bin/env bash

set -e


_log () {
    echo -e "\n\e[${1}m$2\e[0m"
}

info () { _log 34 "$@"; }
success () { _log 32 "$@"; }


info 'Linting'
flake8 .

info 'Type checking'
MYPYPATH='./stubs' mypy sxrumble

info 'Running tests'
py.test -x --ff

success '✓ All checks passed'
