import typing

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from click import Context
from spell.api.client import APIClient
from spell.cli.commands.upload import upload

from airflow_spell import SpellClient


""" https://spell.ml/docs/reference/#spell-upload
"""


class SpellUploadOperator(BaseOperator, SpellClient):
    ui_color = "#f2f0f6"
    ui_fgcolor = "#3c1fd1"

    @apply_defaults
    def __init__(self, **kwargs) -> None:
        BaseOperator.__init__(self, **kwargs)
        spell_conn_id = kwargs.pop("spell_conn_id")
        spell_owner = kwargs.pop("spell_owner", None)
        SpellClient.__init__(self, spell_conn_id=spell_conn_id, spell_owner=spell_owner)
        self.task_id = kwargs.pop("task_id")
        self.local_path = kwargs.pop("local_path")

    def execute(self, context: typing.Dict, client: typing.Optional[APIClient] = None):
        if client is not None:
            api_client = client
        else:
            api_client = self.client.api
        wrap_upload(client=api_client, local_path=self.local_path)
        return "Spell upload execute completed."


def wrap_upload(client: APIClient, local_path: str):
    with Context(upload, obj=dict(client=client)):
        upload.callback(
            path=local_path, name=local_path, cluster_name=None, compress=False,
        )
