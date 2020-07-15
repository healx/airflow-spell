#!/usr/bin/env python
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow_spell import SpellRunOperator


default_args = {
    'depends_on_past': False,
    'start_date': datetime(2019, 10, 13),
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
    'schedule_interval': "@never",
    'catchup': False,
}


with DAG("Airflow-Spell-Testing", default_args=default_args, catchup=False) as dag:
    first_task = BashOperator(task_id="first_task", bash_command="echo 'hello 1'")
    hello_task = SpellRunOperator(
        task_id="spell-task",
        command='python -c "import sys; sys.stderr.write(sys.version)"',
        spell_conn_id="spell_conn_id",
        # spell_owner="organisation",  # for example, if different to username, default is username
        # machine_type="GPU-V100",  # for example, default os "CPU"
    )
    final_task = BashOperator(task_id="final_task", bash_command="echo 'hello world'")

    first_task >> hello_task >> final_task
