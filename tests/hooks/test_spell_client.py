from timeit import default_timer
from precisely import assert_that, has_attr, less_than
from airflow_spell import SpellClient
from airflow_spell.hooks.spell_client import _delay


def test_client_can_be_created():
    client = SpellClient(spell_conn_id="testing-spell-client")
    assert_that(client, has_attr("spell_conn_id", "testing-spell-client"))


def test_delay_delays_for_duration_within_bounds():
    start = default_timer()
    for _ in range(10):
        _delay(delay=.1)  # .1 second
    average_duration = (default_timer() - start) / 10

    assert_that(average_duration, less_than(1))
