import typing

from airflow.models.baseoperator import BaseOperator, AirflowException
from airflow.utils.decorators import apply_defaults

from airflow_spell import SpellClientHook


""" https://spell.run/docs/runs/
"""


class SpellRunOperator(BaseOperator, SpellClientHook):
    # ui_color = "#c3dae0"
    # template_fields = (
    #     "job_name",
    #     "overrides",
    #     "parameters",
    # )

    @apply_defaults
    def __init__(self, spell_conn_id: str, command: str, **kwargs):  # pylint: disable=too-many-arguments
        BaseOperator.__init__(self, **kwargs)
        SpellClientHook.__init__(self, spell_conn_id=spell_conn_id)
        self.command = command

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
            run = self.client.new(command=self.command)
            self.run_id = run.id

            self.log.info(f"Spell run ({self.run_id}) started: {run}")

        except Exception as e:
            self.log.info(f"Spell run ({self.run_id}) failed submission")
            raise AirflowException(e)

    def monitor_run(self, context: typing.Dict):  # pylint: disable=unused-argument
        """
        Monitor a Spell run
        :raises: AirflowException
        """
        try:
            if self.waiters:
                self.waiters.wait_for_run(self.run_id)
            else:
                self.wait_for_run(self.run_id)

            self.check_run_success(self.run_id)
            self.log.info(f"Spell run ({self.run_id}) succeeded")

        except Exception as e:
            self.log.info(f"Spell run ({self.run_id}) failed monitoring")
            raise AirflowException(e)
