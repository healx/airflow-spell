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
if [ `python -c 'import sys; print("{}{}".format(*sys.version_info[:2]))'` -lt "37" ]; then
    echo "This script requires python 3.7 or greater"
    exit 1
fi

python -m venv venv

source venv/bin/activate
# Currently (21/01/2020) failing with a "ImportError: cannot import name 'SourceDistribution'" error
# https://github.com/pypa/pip/issues/7217
# python -m pip install --upgrade pip
python -m pip install pendulum==1.4.4

export AIRFLOW_HOME=${PWD}
export ENABLE_AIRFLOW_AUTH=1
export AIRFLOW_VERSION=1.10.4


function WEBSERVER_AUTH() {
    if [[ $ENABLE_AIRFLOW_AUTH == 1 ]]; then
        echo "authenticate = True"
        echo "rbac = True"
        echo "auth_backend = airflow.contrib.auth.backends.password_auth"
    else
        echo "authenticate = False"
        echo "rbac = False"
    fi
}


echo "export AIRFLOW_HOME=${AIRFLOW_HOME}" >> bin/activate

AIRFLOW_GPL_UNIDECODE=true python -m pip install apache-airflow[crypto,password,s3]==${AIRFLOW_VERSION} fastparquet


rm -rf plugins
mkdir -p plugins
ln -sf "${PWD}/../airflow_spell" plugins/airflow_spell

mo -u < airflow.cfg.tmpl > airflow.cfg
airflow initdb

if [[ $ENABLE_AIRFLOW_AUTH == 1 ]]; then
    # Create user 'admin' with password 'admin'
    airflow create_user -r Admin -u admin -e admin@example.com -f admin -l admin -p admin
fi
