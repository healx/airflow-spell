from random import uniform
from time import sleep
from typing import List, Optional, Union

from airflow import LoggingMixin, AirflowException
from airflow.hooks.base_hook import BaseHook
from spell.client import SpellClient as ExternalSpellClient
from spell.client.runs import Run as ExternalSpellRun
from spell.client.runs import RunsService as ExternalSpellRunsService


class SpellHook(BaseHook):
    def __init__(self, spell_conn_id="spell_default", owner: Optional[str] = None):
        super().__init__(source=__file__)
        self.spell_conn_id = spell_conn_id
        self.owner = owner

    def get_client(self):
        if self.owner is not None:
            owner = self.owner
        else:
            owner = self._get_owner()

        return ExternalSpellClient(token=self._get_token(), owner=owner)

    def _get_token(self):
        # get_connection is on BaseHook
        connection_object = self.get_connection(self.spell_conn_id)
        return connection_object.password

    def _get_owner(self):
        connection_object = self.get_connection(self.spell_conn_id)
        return connection_object.host


class SpellClient(LoggingMixin):
    MAX_RETRIES = 4200
    STATUS_RETRIES = 10

    # delays are in seconds
    DEFAULT_DELAY_MIN = 1
    DEFAULT_DELAY_MAX = 10

    def __init__(self, spell_conn_id: Optional[str] = None):
        super().__init__()
        self.spell_conn_id = spell_conn_id
        self._hook: Optional[SpellHook] = None
        self._client: Optional[ExternalSpellClient] = None

    @property
    def hook(self) -> SpellHook:
        if self._hook is None:
            self._hook = SpellHook(spell_conn_id=self.spell_conn_id)
        return self._hook

    @property
    def client(self) -> ExternalSpellClient:
        if self._client is None:
            self._client = self.hook.get_client()
        return self._client

    def get_run(self, run_id: str) -> ExternalSpellRun:
        return ExternalSpellRun(self.client.api, self.client.api.get_run(run_id))

    def wait_for_run(self, run_id: str, delay: Optional[Union[int, float]] = None):
        """
        Wait for spell run to complete

        :param run_id: a spell run ID
        :type run_id: str

        :param delay: a delay before polling for run status
        :type delay: Optional[Union[int, float]]

        :raises: AirflowException
        """
        _delay(delay)
        self.poll_for_run_running(run_id, delay)
        self.poll_for_run_complete(run_id, delay)
        self.log.info(f"Spell run ({run_id}) has completed")

    def check_run_success(self, run_id: str) -> bool:
        """
        Check the final status of the spell run; return True if the run
        'COMPLETE', else raise an AirflowException

        :param run_id: a spell run ID
        :type run_id: str

        :rtype: bool

        :raises: AirflowException
        """
        run = self.get_run(run_id)
        run_status = run.status

        if run_status == ExternalSpellRunsService.COMPLETE:
            self.log.info(f"Spell run ({run_id}) completed: {run}")
            return True

        if run_status == ExternalSpellRunsService.FAILED:
            raise AirflowException(f"Spell run ({run_id}) failed: {run}")

        STILL_RUNNING = [
            ExternalSpellRunsService.BUILDING,
            ExternalSpellRunsService.PUSHING,
            ExternalSpellRunsService.RUNNING,
            ExternalSpellRunsService.SAVING
        ]
        if run_status in STILL_RUNNING:
            raise AirflowException(f"Spell ({run_id}) is not complete: {run}")

        raise AirflowException(f"Spell ({run_id}) has unknown status ({run_status}): {run}")

    def poll_for_run_running(self, run_id: str, delay: Union[int, float, None] = None):
        """
        Poll for job running. The status that indicates a job is running or
        already complete are: 'RUNNING'|'SUCCEEDED'|'FAILED'.

        So the status options that this will wait for are the transitions from:
        'SUBMITTED'>'PENDING'>'RUNNABLE'>'STARTING'>'RUNNING'|'SUCCEEDED'|'FAILED'

        The completed status options are included for cases where the status
        changes too quickly for polling to detect a RUNNING status that moves
        quickly from STARTING to RUNNING to completed (often a failure).

        :param job_id: a batch job ID
        :type job_id: str

        :param delay: a delay before polling for job status
        :type delay: Optional[Union[int, float]]

        :raises: AirflowException
        """
        _delay(delay)
        running_status = [
            ExternalSpellRunsService.BUILDING,
            ExternalSpellRunsService.RUNNING,
            ExternalSpellRunsService.SAVING,
            ExternalSpellRunsService.PUSHING,
        ]
        self.poll_run_status(run_id, running_status)

    def poll_for_run_complete(self, run_id: str, delay: Union[int, float, None] = None):
        """
        Poll for job completion. The status that indicates job completion
        are: 'SUCCEEDED'|'FAILED'.

        So the status options that this will wait for are the transitions from:
        'SUBMITTED'>'PENDING'>'RUNNABLE'>'STARTING'>'RUNNING'>'SUCCEEDED'|'FAILED'

        :param job_id: a batch job ID
        :type job_id: str

        :param delay: a delay before polling for job status
        :type delay: Optional[Union[int, float]]

        :raises: AirflowException
        """
        _delay(delay)
        complete_status = ExternalSpellRunsService.FINAL
        self.poll_run_status(run_id, complete_status)

    def poll_run_status(self, run_id: str, match_status: List[str]) -> bool:
        """
        Poll for job status using an exponential back-off strategy (with max_retries).

        :param job_id: a batch job ID
        :type job_id: str

        :param match_status: a list of job status to match; the batch job status are:
            'SUBMITTED'|'PENDING'|'RUNNABLE'|'STARTING'|'RUNNING'|'SUCCEEDED'|'FAILED'
        :type match_status: List[str]

        :rtype: bool

        :raises: AirflowException
        """
        retries = 0
        while True:

            run = self.get_run(run_id)
            run_status = run.status

            self.log.info(f"Spell run ({run_id}) check status ({run_status}) in {match_status}")

            if run_status in match_status:
                return True

            if retries >= self.MAX_RETRIES:
                raise AirflowException(f"Spell run ({run_id}) status checks exceed max_retries")

            retries += 1
            pause = _exponential_delay(retries)
            self.log.info(
                f"Spell run ({run_id}) status check ({retries} of {self.MAX_RETRIES})"
                f" in the next {pause:.2f} seconds"
            )

            _delay(pause)


def _delay(delay: Union[int, float, None] = None):
    """
    Pause execution for ``delay`` seconds.

    :param delay: a delay to pause execution using ``time.sleep(delay)``;
        a small 1 second jitter is applied to the delay.
    :type delay: Optional[Union[int, float]]

    .. note::
        This method uses a default random delay, i.e.
        ``random.uniform(DEFAULT_DELAY_MIN, DEFAULT_DELAY_MAX)``;
        using a random interval helps to avoid AWS API throttle limits
        when many concurrent tasks request job-descriptions.
    """
    if delay is None:
        delay = uniform(SpellClient.DEFAULT_DELAY_MIN, SpellClient.DEFAULT_DELAY_MAX)
    else:
        delay = _add_jitter(delay)
    sleep(delay)


def _exponential_delay(tries: int) -> float:
    max_interval = 600.0  # results in 3 to 10 minute delay
    delay = 1 + pow(tries * 0.6, 2)
    delay = min(max_interval, delay)
    return uniform(delay / 3, delay)


def _add_jitter(
    delay: Union[int, float], width: Union[int, float] = 1, minima: Union[int, float] = 0
) -> float:
    """
    Use delay +/- width for random jitter

    Adding jitter to status polling can help to avoid
    Spell API limits for monitoring spell jobs with
    a high concurrency in Airflow tasks.

    :param delay: number of seconds to pause;
        delay is assumed to be a positive number
    :type delay: Union[int, float]

    :param width: delay +/- width for random jitter;
        width is assumed to be a positive number
    :type width: Union[int, float]

    :param minima: minimum delay allowed;
        minima is assumed to be a non-negative number
    :type minima: Union[int, float]

    :return: uniform(delay - width, delay + width) jitter
        and it is a non-negative number
    :rtype: float
    """
    delay = abs(delay)
    width = abs(width)
    minima = abs(minima)
    lower = max(minima, delay - width)
    upper = delay + width
    return uniform(lower, upper)
