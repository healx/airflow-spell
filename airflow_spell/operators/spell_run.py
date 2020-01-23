import typing
from typing import Dict, List, Optional

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

    :param workspace_id: the workspace ID for code to include in the run (default: None)
    :type workspace_id: Optional[int]

    :param commit_hash: a specific commit hash in the workspace corresponding to :obj:`workspace_id`
        for code to include in the run (default: None)
    :type commit_hash: Optional[str]

    :param commit_label: a commit label for code to include in the run. Only applicable
        if this is a workflow run (i.e., the :py:attr:`~spell.client.SpellClient.active_workflow` of the
        client is set or a :obj:`workflow_id` is provided) (default: None). The value must correspond
        to one of the commit labels specified upon workflow creation using the ``--repo`` option.
        Only applicable if a workspace is specified.
    :type commit_label: Optional[str]

    :param github_url: a GitHub URL to a repository for code to include in the run. Not applicable
        when :obj:`workspace_id` or :obj:`commit_label` is specified.
    :type github_url: Optional[str]

    :param github_ref: a reference to a commit, branch, or tag in the repository corresponding to
        :obj:`github_url` for code to include in the run (default: master)
    :type github_ref: Optional[str]

    :param pip_packages: pip dependencies (default: None).
        For example: ``["moviepy", "scikit-image"]``
    :type pip_packages: Optional[List[str]]

    :param apt_packages: apt dependencies (default: None).
        For example: ``["python-tk", "ffmpeg"]``
    :type apt_packages: Optional[List[str]]

    :param envvars: name to value mapping of environment variables for the run (default: None).
        For example: ``{"VARIABLE" : "VALUE", "LANG" : "C.UTF-8"}``
    :type envvars: Optional[Dict[str, str]]

    :param cwd: the working directory within the repository in which to execute the command (default: None).
        Only applicable if a workspace is specified.
    :type cwd: Optional[str]

    :param tensorboard_directory: the path where tensorboard files will be read from.
    :type tensorboard_directory: Optional[str]

    :param distributed: execute a distributed run using N machines of the specified machine type.
    :type distributed: Optional[int]

    :param python2: set the python version to python 2 (default: false)
    :type python2: Optional[bool]

    :param conda_file: the path to a conda specification file or YAML environment file (default: None).
    :type conda_file: Optional[str]

    :param docker_image: the name of docker image to use as base (default: None)
    :type docker_image: Optional[str]

    :param framework: the framework to use for the run (default: None). For example: ``pytorch``
    :type framework: Optional[str]

    :param framework_version: the framework version to use for the run (default: None).
        For example: ``0.2.0``
    :type framework_version: Optional[str]:

    :param attached_resources: resource name to mountpoint mapping of attached resources for the run (default: None).
        For example: ``{"runs/42" : "/mnt/data"}``
    :type attached_resources: Optional[Dict[str, str]]

    :param description: a description for the run (default: None)
    :type description: Optional[str]

    :param idempotent: use an existing identical run if available in lieu of re-running (default: false)
    :type idempotent: Optional[bool]

    :param workflow_id: the id of the workflow to which this run will be associated (default: None).
        This argument is unnecessary if the :py:attr:`~spell.client.SpellClient.active_workflow` of
        the client is set and this argument will take precedence if they differ.
    :type workflow_id: Optional[int]
    """
    ui_color = "#f2f0f6"
    ui_fgcolor = "#3c1fd1"

    @apply_defaults
    def __init__(
            self,
            spell_conn_id: str,
            command: str,
            machine_type: str = "CPU",
            workspace_id: Optional[int] = None,
            commit_hash: Optional[str] = None,
            commit_label: Optional[str] = None,
            github_url: Optional[str] = None,
            github_ref: str = "master",
            pip_packages: Optional[List[str]] = None,
            apt_packages: Optional[List[str]] = None,
            envvars: Optional[Dict[str, str]] = None,
            cwd: Optional[str] = None,
            tensorboard_directory: Optional[str] = None,
            distributed: Optional[int] = None,
            python2: bool = False,
            conda_file: Optional[str] = None,
            docker_image: Optional[str] = None,
            framework: Optional[str] = None,
            framework_version: Optional[str] = None,
            attached_resources: Optional[Dict[str, str]] = None,
            description: Optional[str] = None,
            idempotent: bool = False,
            # workflow_id: Optional[int] = None,
            **kwargs
    ) -> None:
        BaseOperator.__init__(self, **kwargs)
        SpellClient.__init__(self, spell_conn_id=spell_conn_id)
        self.command = command
        self.machine_type = machine_type
        self.workspace_id = workspace_id
        self.commit_hash = commit_hash
        self.commit_label = commit_label
        self.github_url = github_url
        self.github_ref = github_ref
        self.pip_packages = pip_packages
        self.apt_packages = apt_packages
        self.envvars = envvars
        self.cwd = cwd
        self.tensorboard_directory = tensorboard_directory
        self.distributed = distributed
        self.python2 = python2
        self.conda_file = conda_file
        self.docker_image = docker_image
        self.framework = framework
        self.framework_version = framework_version
        self.attached_resources = attached_resources
        self.description = description
        self.idempotent = idempotent
        # setting workflow_id as None causes trouble for spell 0.33.0
        # self.workflow_id = workflow_id

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
            run = self.client.runs.new(
                command=self.command,
                machine_type=self.machine_type,
                workspace_id=self.workspace_id,
                commit_hash=self.commit_hash,
                commit_label=self.commit_label,
                github_url=self.github_url,
                github_ref=self.github_ref,
                pip_packages=self.pip_packages,
                apt_packages=self.apt_packages,
                envvars=self.envvars,
                cwd=self.cwd,
                tensorboard_directory=self.tensorboard_directory,
                distributed=self.distributed,
                python2=self.python2,
                conda_file=self.conda_file,
                docker_image=self.docker_image,
                framework=self.framework,
                framework_version=self.framework_version,
                attached_resources=self.attached_resources,
                description=self.description,
                idempotent=self.idempotent,
                # workflow_id=self.workflow_id,
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
