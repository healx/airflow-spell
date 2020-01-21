from typing import Optional, Union

from airflow import LoggingMixin
from airflow.hooks.base_hook import BaseHook
from spell.client import SpellClient


class SpellHook(BaseHook):
    def __init__(self, spell_conn_id="spell_default"):
        super().__init__(source=__file__)
        self.spell_conn_id = spell_conn_id

    def get_client(self):
        return SpellClient(token=self._get_token())

    def _get_token(self):
        # get_connection is on BaseHook
        connection_object = self.get_connection(self.spell_conn_id)
        return connection_object.password


class SpellClientHook(LoggingMixin):
    def __init__(self, spell_conn_id: Optional[str] = None):
        super().__init__()
        self.spell_conn_id = spell_conn_id
        self._hook = None  # type: Union[SpellHook, None]
        self._client = None  # type: Union[SpellClient, None]

    @property
    def hook(self) -> SpellHook:
        if self._hook is None:
            self._hook = SpellHook(spell_conn_id=self.spell_conn_id)
        return self._hook

    @property
    def client(self) -> SpellClient:
        if self._client is None:
            self._client = self.hook.get_client()
        return self._client
