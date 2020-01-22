import typing
from typing import Optional

from airflow.models.baseoperator import BaseOperator, AirflowException
from airflow.utils.decorators import apply_defaults

from airflow_spell import SpellClient


""" https://spell.run/docs/runs/
"""


class SpellRunOperator(BaseOperator, SpellClient):
    """
    Execute a run on Spell Run

    :param command: the command to run
    :type command: str

    :param machine_type: the machine type for the run (default: CPU)
    :type machine_type: Optional[str]
    """
    ui_color = "#f2f0f6"
    ui_fgcolor = "#3c1fd1"

    @apply_defaults
    def __init__(
            self,
            spell_conn_id: str,
            command: str,
            machine_type: Optional[str] = "CPU",
            **kwargs
    ) -> None:
        BaseOperator.__init__(self, **kwargs)
        SpellClient.__init__(self, spell_conn_id=spell_conn_id)
        self.command = command
        self.machine_type = machine_type

    def execute(self, context: typing.Dict):
        """
        Submit and monitor a Spell run
        :raises: AirflowException
        """
        self.submit_run(context)
        self.monitor_run(context)

    def submit_run(self, context: typing.Dict):  # pylint: disable=unused-argument
        self.log.info("Running Spell run")

        try:
            run = self.client.runs.new(
                command=self.command,
                machine_type=self.machine_type
            )
            self.run_id = run.id

            self.log.info(f"Spell run ({self.run_id}) started: {run}")

        except Exception as e:
            self.log.info(f"Spell run (task_id: {self.task_id}) failed submission")
            raise AirflowException(e)

    def monitor_run(self, context: typing.Dict):  # pylint: disable=unused-argument
        """
        Monitor a Spell run
        :raises: AirflowException
        """
        try:
            self.wait_for_run(self.run_id)
            self.check_run_success(self.run_id)
            self.log.info(f"Spell run ({self.run_id}) succeeded")

        except Exception as e:
            self.log.info(f"Spell run ({self.run_id}) failed monitoring")
            raise AirflowException(e)
