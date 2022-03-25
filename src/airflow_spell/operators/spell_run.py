from typing import Dict, Optional

from airflow import AirflowException
from airflow.models import BaseOperator

from airflow_spell import SpellClient


""" https://spell.run/docs/runs/
"""


class SpellRunOperator(BaseOperator, SpellClient):
    """
    Execute a run on Spell Run (same args as spell.client.runs.RunService

    Args:
        spell_conn_id (str): Airflow connection id for spell
        spell_owner (str, optional): Spell owner (if different from user account)
        task_id (str, optional):
        params (dict, optional):
        (all commands below passed to SpellClient)
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

    def __init__(
        self,
        *,
        task_id: str,
        spell_owner: Optional[str] = None,
        spell_conn_id: Optional[str] = None,
        **kwargs,
    ):
        BaseOperator.__init__(self, task_id=task_id)
        SpellClient.__init__(self, spell_conn_id=spell_conn_id, spell_owner=spell_owner)
        self.log.warning(kwargs)
        if "default_args" in kwargs:
            kwargs.pop("default_args")
        self.kwargs = kwargs

    def execute(self, context: Dict) -> int:
        """
        Submit and monitor a Spell run
        :raises: AirflowException
        """
        self.submit_run(context)
        self.monitor_run(context)

        # this return value gets pushed as XCom
        return self.spell_run_id

    def submit_run(self, context: Dict):  # pylint: disable=unused-argument
        self.log.info("Running Spell run")

        try:
            run = self.client.runs.new(**self.kwargs)
            self.spell_run_id = run.id

            self.log.info(
                "Spell run (spell_run_id: %s) started: %s"
                % (self.spell_run_id, str(run))
            )

        except Exception as e:
            self.log.info("Spell run (task_id: %s) failed submission" % self.task_id)
            raise AirflowException(e)

    def monitor_run(self, context: Dict):  # pylint: disable=unused-argument
        """
        Monitor a Spell run
        :raises: AirflowException
        """
        try:
            self.wait_for_run(self.spell_run_id)
            self.check_run_complete(self.spell_run_id)
            self.log.info("Spell run (%s) succeeded" % self.spell_run_id)

        except Exception as e:
            self.log.info("Spell run (%s) failed monitoring" % self.spell_run_id)
            raise AirflowException(e)
