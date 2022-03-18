import inspect
from timeit import default_timer
from typing import Callable
from unittest.mock import MagicMock, PropertyMock, patch

from airflow.exceptions import AirflowException
from precisely import assert_that, has_attr, is_instance, less_than, raises
import pytest
from spell.client.runs import RunsService

from airflow_spell import SpellClient
from airflow_spell.hooks.spell_client import _delay


def test_client_can_be_created():
    client = SpellClient(spell_conn_id="testing-spell-client")
    assert_that(client, has_attr("spell_conn_id", "testing-spell-client"))


def test_delay_delays_for_duration_within_bounds():
    start = default_timer()
    for _ in range(10):
        _delay(delay=0.1)  # .1 second
    average_duration = (default_timer() - start) / 10

    assert_that(average_duration, less_than(1))


@pytest.fixture
def spell_client() -> SpellClient:
    return SpellClient()


def mock_get_run(status, user_exit_code: int = 0) -> Callable:
    def mock_func(_, __):
        return MagicMock(status=status, user_exit_code=user_exit_code)

    return mock_func


POSSIBLE_INCOMPLETE_SPELL_STATUS = [
    member[1]
    for member in inspect.getmembers(RunsService, lambda value: isinstance(value, str))
    if "." not in member[1] and member[1] is not "complete"
]


class TestRunComplete:
    def test_run_complete_does_not_raise_exception(self, monkeypatch, spell_client):
        monkeypatch.setattr(
            SpellClient, "_get_run", mock_get_run(status=RunsService.COMPLETE)
        )
        spell_client.check_run_complete(run_id="test1")

    @pytest.mark.parametrize("status", POSSIBLE_INCOMPLETE_SPELL_STATUS)
    def test_run_not_complete_raises_exception(self, status, monkeypatch, spell_client):
        monkeypatch.setattr(SpellClient, "_get_run", mock_get_run(status=status))
        assert_that(
            lambda: spell_client.check_run_complete(run_id="test1"),
            raises(is_instance(AirflowException)),
        )

    def test_run_complete_with_non_zero_exit_code_raises_exception(
        self, monkeypatch, spell_client
    ):
        monkeypatch.setattr(
            SpellClient,
            "_get_run",
            mock_get_run(status=RunsService.COMPLETE, user_exit_code=1),
        )
        assert_that(
            lambda: spell_client.check_run_complete(run_id="test1"),
            raises(is_instance(AirflowException)),
        )


def mock_changing_get_run(status) -> Callable:
    def mock_func(_, __):
        return MagicMock(status=status())

    return mock_func


class TestWaitForRun:
    def test_complete_status_ends_run(self, monkeypatch, spell_client):
        with patch(
            "spell.client.runs.RunsService", new_callable=PropertyMock
        ) as mocked_get_run_status:
            mocked_get_run_status.side_effect = [
                RunsService.RUNNING,
                RunsService.COMPLETE,
            ]

            monkeypatch.setattr(
                SpellClient,
                "_get_run",
                mock_changing_get_run(status=mocked_get_run_status),
            )

            # Act - if this process completes, we don't see an exception
            # (it waits and then exits)
            spell_client.wait_for_run(run_id="test1", delay=0)

    def test_failed_status_ends_run(self, monkeypatch, spell_client):
        with patch(
            "spell.client.runs.RunsService", new_callable=PropertyMock
        ) as mocked_get_run_status:
            mocked_get_run_status.side_effect = [
                RunsService.RUNNING,
                RunsService.FAILED,
            ]

            monkeypatch.setattr(
                SpellClient,
                "_get_run",
                mock_changing_get_run(status=mocked_get_run_status),
            )

            # Act - if this process completes, we don't see an exception
            # (it waits and then exits)
            spell_client.wait_for_run(run_id="test1", delay=0)

    def test_fast_jobs_end(self, monkeypatch, spell_client):
        # Catch issue where jobs that go straight from "machine_requested" to "COMPLETE"
        # don't report as COMPLETE
        with patch(
            "spell.client.runs.RunsService", new_callable=PropertyMock
        ) as mocked_get_run_status:
            mocked_get_run_status.side_effect = [
                "machine_requested",
                RunsService.COMPLETE,
            ]

            monkeypatch.setattr(
                SpellClient,
                "_get_run",
                mock_changing_get_run(status=mocked_get_run_status),
            )

            # Act - if this process completes, we don't see an exception
            # (it waits and then exits)
            spell_client.wait_for_run(run_id="test1", delay=0)
