#!/usr/bin/env bash
cd "$(dirname "$0")" || exit

if [[ ! -a venv/bin/activate ]]; then
    ./create_test_virtualenv.sh
fi
source venv/bin/activate

./venv/bin/airflow "$@"
