#!/usr/bin/env bash
cd "$(dirname "$0")" || exit

# https://github.com/tests-always-included/mo
MO=mo
if [[ ! -f "$MO" ]]; then
  curl -sSL https://git.io/get-mo -o mo
fi
# shellcheck source=mo
source ./$MO

# setup python env
if [ `python3 -c 'import sys; print("{}{}".format(*sys.version_info[:2]))'` -lt "37" ]; then
    echo "This script requires python 3.7 or greater"
    exit 1
fi

export VENV="venv"
if [[ ! -d $VENV ]]; then
    python3 -m venv $VENV
    # Currently (21/01/2020) failing with a "ImportError: cannot import name 'SourceDistribution'" error
    # https://github.com/pypa/pip/issues/7217
    # python -m pip install --upgrade pip
    $VENV/bin/python -m pip install apache-airflow
    $VENV/bin/python -m pip install -e ../
    echo "export AIRFLOW_HOME=${AIRFLOW_HOME}" >> $VENV/bin/activate
fi

source $VENV/bin/activate
export AIRFLOW_HOME=${PWD}
export ENABLE_AIRFLOW_AUTH=0
export AIRFLOW_VERSION=1.10.4

mo -u < airflow.cfg.tmpl > airflow.cfg

airflow initdb
