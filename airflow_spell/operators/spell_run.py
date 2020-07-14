import typing
from typing import Dict, List, Optional

from airflow.models.baseoperator import BaseOperator, AirflowException
from airflow.utils.decorators import apply_defaults

from airflow_spell import SpellClient


""" https://spell.run/docs/runs/
"""


class SpellRunOperator(BaseOperator, SpellClient):
    """
    Execute a run on Spell Run (same args as spell.client.runs.RunService

    Args:
        command (str): the command to run
        machine_type (str, optional): the machine type for the run (default: CPU)
        workspace_id (int, optional): the workspace ID for code to include in the run (default: None)
        commit_hash (str, optional): a specific commit hash in the workspace corresponding to :obj:`workspace_id`
            for code to include in the run (default: None)
        commit_label (str, optional): a commit label for code to include in the run. Only applicable
            if this is a workflow run (i.e., the :py:attr:`~spell.client.SpellClient.active_workflow` of the
            client is set or a :obj:`workflow_id` is provided) (default: None). The value must correspond
            to one of the commit labels specified upon workflow creation using the ``--repo`` option.
            Only applicable if a workspace is specified.
        github_url (str, optional): a GitHub URL to a repository for code to include in the run. Not applicable
            when :obj:`workspace_id` or :obj:`commit_label` is specified.
        github_ref (str, optional): a reference to a commit, branch, or tag in the repository corresponding to
            :obj:`github_url` for code to include in the run (default: master)
        pip_packages (:obj:`list` of :obj:`str`, optional): pip dependencies (default: None).
            For example: ``["moviepy", "scikit-image"]``
        apt_packages (:obj:`list` of :obj:`str`, optional): apt dependencies (default: None).
            For example: ``["python-tk", "ffmpeg"]``
        requirements_file (str, optional): a path to a requirements file
        envvars (:obj:`dict` of :obj:`str` -> :obj:`str`, optional): name to value mapping of
            environment variables for the run (default: None).
            For example: ``{"VARIABLE" : "VALUE", "LANG" : "C.UTF-8"}``
        cwd (str, optional): the working directory within the repository in which to execute the command
            (default: None). Only applicable if a workspace is specified.
        tensorboard_directory(str, optional): the path where tensorboard files will be read from.
        distributed(int, optional): execute a distributed run using N machines of the specified machine type.
        conda_file (str, optional): the path to a conda specification file or YAML environment file (default: None).
        docker_image (str, optional): the name of docker image to use as base (default: None)
        framework (str, optional): the framework to use for the run (default: None). For example: ``pytorch``
        framework_version (str, optional): the framework version to use for the run (default: None).
            For example: ``0.2.0``
        attached_resources (:obj:`dict` of :obj:`str` -> :obj:`str`, optional): resource name to
            mountpoint mapping of attached resouces for the run (default: None).
            For example: ``{"runs/42" : "/mnt/data"}``
        description (str, optional): a description for the run (default: None)
        idempotent (bool, optional): use an existing identical run if available in lieu of re-running
            (default: false)
        workflow_id (int, optional): the id of the workflow to which this run will be associated (default: None).
            This argument is unnecessary if the :py:attr:`~spell.client.SpellClient.active_workflow` of
            the client is set and this argument will take precedence if they differ.
    """
    ui_color = "#f2f0f6"
    ui_fgcolor = "#3c1fd1"

    @apply_defaults
    def __init__(self, **kwargs) -> None:
        BaseOperator.__init__(self, **kwargs)
        spell_conn_id = kwargs.pop("spell_conn_id")
        self.task_id = kwargs.pop("task_id")
        SpellClient.__init__(self, spell_conn_id=spell_conn_id)
        self.params = kwargs.pop("params")
        self.kwargs = kwargs

    def execute(self, context: typing.Dict):
        """
        Submit and monitor a Spell run
        :raises: AirflowException
        """
        self.submit_run(context)
        self.monitor_run(context)
        return "Spell run execute completed."

    def submit_run(self, context: typing.Dict):  # pylint: disable=unused-argument
        self.log.info("Running Spell run")

        try:
            run = self.client.runs.new(**self.kwargs)
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
