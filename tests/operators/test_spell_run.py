from precisely import assert_that, has_attrs
from airflow_spell import SpellRunOperator


def test_run_operator_can_be_created():
    run_operator = SpellRunOperator(
        spell_conn_id="testing-spell-run-operator",
        command="DO IT NOW!",
        task_id="testing-task-id",
    )

    assert_that(run_operator, has_attrs(
        spell_conn_id="testing-spell-run-operator",
        command="DO IT NOW!",
        task_id="testing-task-id",
    ))
