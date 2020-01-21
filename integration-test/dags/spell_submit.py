#!/usr/bin/env python
from datetime import datetime, timedelta

from airflow import DAG
from airflow_spell import HelloOperator


default_args = {
    'owner': 'Airflow',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


with DAG("Airflow-Spell-Testing", default_args=default_args) as dag:
    hello_task = HelloOperator(task_id='sample-task', name='foo_bar')
