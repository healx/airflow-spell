#!/usr/bin/env python
from datetime import datetime, timedelta

from airflow import DAG
from airflow_spell import HelloOperator


default_args = {
    'depends_on_past': False,
    'start_date': datetime(2019, 10, 13),
    'retries': 1,
    'retry_delay': timedelta(minutes=10)
}


with DAG("Airflow-Spell-Testing", default_args=default_args):
    hello_task = HelloOperator(task_id='sample-task', name='foo_bar')

