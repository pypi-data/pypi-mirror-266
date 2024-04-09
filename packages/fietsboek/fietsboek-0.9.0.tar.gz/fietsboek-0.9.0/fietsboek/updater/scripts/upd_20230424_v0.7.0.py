"""Revision upgrade script v0.7.0

Date created: 2023-04-24 20:26:12.399318
"""
from fietsboek.updater.script import UpdateScript

update_id = 'v0.7.0'
previous = [
    'v0.6.0',
]
alembic_revision = '3149aa2d0114'


class Up(UpdateScript):
    def pre_alembic(self, config):
        pass

    def post_alembic(self, config):
        pass


class Down(UpdateScript):
    def pre_alembic(self, config):
        pass

    def post_alembic(self, config):
        pass
