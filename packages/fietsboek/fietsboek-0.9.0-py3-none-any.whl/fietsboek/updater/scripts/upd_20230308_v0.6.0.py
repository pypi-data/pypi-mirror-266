"""Revision upgrade script v0.6.0

Date created: 2023-03-08 18:34:02.074102
"""
from fietsboek.updater.script import UpdateScript

update_id = 'v0.6.0'
previous = [
    'v0.5.0',
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
