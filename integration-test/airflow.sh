#!/usr/bin/env bash
cd "$(dirname "$0")" || exit

if [[ ! -a venv/bin/activate ]]; then
    ./create_test_virtualenv.sh
fi
source venv/bin/activate

export AIRFLOW_HOME=${PWD}
export ENABLE_AIRFLOW_AUTH=1
export AIRFLOW_VERSION=1.10.4

./venv/bin/airflow "$@"
