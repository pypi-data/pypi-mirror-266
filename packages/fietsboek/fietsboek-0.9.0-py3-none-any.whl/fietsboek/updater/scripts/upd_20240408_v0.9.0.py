"""Revision upgrade script v0.9.0

Date created: 2024-04-08 20:29:49.521943
"""
from fietsboek.updater.script import UpdateScript

update_id = 'v0.9.0'
previous = [
    'v0.8.0',
]
alembic_revision = '4566843039d6'


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
