from precisely import assert_that, has_attrs
from airflow_spell import SpellUploadOperator


def test_upload_operator_can_be_created():
    upload_operator = SpellUploadOperator(
        spell_conn_id="testing-spell-upload-operator",
        task_id="testing-task-id",
        local_path="test.path",
    )

    assert_that(
        upload_operator,
        has_attrs(
            spell_conn_id="testing-spell-upload-operator",
            task_id="testing-task-id",
            local_path="test.path",
        ),
    )


def test_upload_operator_can_be_executed(monkeypatch):
    upload_operator = SpellUploadOperator(
        spell_conn_id="testing-spell-upload-operator",
        task_id="testing-task-id",
        local_path="test.path",
    )

    upload_operator.execute({}, client=object)

    assert_that(
        upload_operator,
        has_attrs(
            spell_conn_id="testing-spell-upload-operator",
            task_id="testing-task-id",
            local_path="test.path",
        ),
    )
