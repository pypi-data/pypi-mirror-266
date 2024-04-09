"""Script to do maintenance actions for fietsboek."""

import datetime
import logging
import logging.config
from pathlib import Path

import click
import pyramid.paster
import redis as mod_redis
from redis import Redis
from sqlalchemy import create_engine, delete, exists, not_, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from .. import config as mod_config
from .. import hittekaart, models
from ..config import Config
from ..data import DataManager
from ..models.user import TOKEN_LIFETIME
from . import config_option

LOGGER = logging.getLogger(__name__)


@click.command()
@config_option
def cli(config):
    """Runs regular maintenance operations on the instance.

    This does the following:

    \b
    * Deletes pending uploads that are older than 24 hours.
    * Rebuilds the cache for missing tracks.
    * (optional) Runs ``hittekaart`` to generate heatmaps
    """
    logging.config.fileConfig(config)
    settings = pyramid.paster.get_appsettings(config)

    config = mod_config.parse(settings)
    # Do this early to reduce the chances of "accidentally" hitting the
    # database when maintenance mode is turned on.
    data_manager = DataManager(config.data_dir)
    if data_manager.maintenance_mode() is not None:
        LOGGER.info("Skipping cronjob tasks due to maintenance mode")
        return

    engine = create_engine(config.sqlalchemy_url)

    LOGGER.debug("Starting maintenance tasks")
    remove_old_uploads(engine)
    remove_old_tokens(engine)
    rebuild_cache(engine, data_manager)

    if config.hittekaart_autogenerate:
        redis = mod_redis.from_url(config.redis_url)
        run_hittekaart(engine, data_manager, redis, config)


def remove_old_uploads(engine: Engine):
    """Removes old uploads from the database."""
    LOGGER.info("Deleting old uploads")
    limit = datetime.datetime.now() - datetime.timedelta(hours=24)
    session = Session(engine)
    stmt = delete(models.Upload).where(models.Upload.uploaded_at < limit)
    session.execute(stmt)
    session.commit()


def remove_old_tokens(engine: Engine):
    """Removes old tokens from the database."""
    LOGGER.info("Deleting old tokens")
    limit = datetime.datetime.utcnow() - TOKEN_LIFETIME
    session = Session(engine)
    stmt = delete(models.Token).where(models.Token.date < limit)
    session.execute(stmt)
    session.commit()


def rebuild_cache(engine: Engine, data_manager: DataManager):
    """Rebuilds the cache entries that are currently missing."""
    LOGGER.debug("Rebuilding caches")
    session = Session(engine)
    needed_rebuilds = select(models.Track).where(
        not_(exists(select(models.TrackCache).where(models.TrackCache.track_id == models.Track.id)))
    )
    with session:
        for track in session.execute(needed_rebuilds).scalars():
            assert track.id is not None
            LOGGER.info("Rebuilding cache for track %d", track.id)
            gpx_data = data_manager.open(track.id).decompress_gpx()
            track.ensure_cache(gpx_data)
            session.add(track)
        session.commit()


def run_hittekaart(engine: Engine, data_manager: DataManager, redis: Redis, config: Config):
    """Run outstanding hittekaart requests."""
    # The logic here is as follows:
    # We keep two lists: a high-priority one and a low-priority one
    # If there are high priority entries, we run all of them.
    # They are refilled when users upload tracks.
    # If there are no high priority entries, we run a single low priority one.
    # If there are no low priority entries, we re-fill the queue by adding all tracks.
    # This way, we ensure that we "catch" modifications fast, but we also
    # re-generate all maps over time (e.g. if the hittekaart version changes or
    # we miss an update).
    modes = [hittekaart.Mode(mode) for mode in config.hittekaart_autogenerate]
    exe_path = Path(config.hittekaart_bin) if config.hittekaart_bin else None
    session = Session(engine)
    had_hq_item = False

    while True:
        # High-priority queue
        item = redis.spop("hittekaart:queue:high")
        if item is None:
            break
        had_hq_item = True
        user = session.execute(select(models.User).filter_by(id=int(item))).scalar()
        if user is None:
            LOGGER.debug("User %d had a high-priority queue entry but was not found", item)
            continue

        for mode in modes:
            LOGGER.info("Generating %s for user %d (high-priority)", mode.value, user.id)
            hittekaart.generate_for(
                user,
                session,
                data_manager,
                mode,
                exe_path=exe_path,
                threads=config.hittekaart_threads,
            )

    if had_hq_item:
        return

    # Low-priority queue
    item = redis.spop("hittekaart:queue:low")
    if item is None:
        refill_queue(session, redis)
        item = redis.spop("hittekaart:queue:low")
        if item is None:
            LOGGER.debug("No users, no hittekaarts")
            return

    user = session.execute(select(models.User).filter_by(id=int(item))).scalar()
    if user is None:
        LOGGER.debug("User %d had a low-priority queue entry but was not found", item)
        return

    for mode in modes:
        LOGGER.info("Generating %s for user %d (low-priority)", mode.value, user.id)
        hittekaart.generate_for(
            user, session, data_manager, mode, exe_path=exe_path, threads=config.hittekaart_threads
        )


def refill_queue(session: Session, redis: Redis):
    """Refills the low-priority hittekaart queue by adding all users to it."""
    LOGGER.debug("Refilling low-priority queue")
    for user in session.execute(select(models.User)).scalars():
        assert user.id is not None
        redis.sadd("hittekaart:queue:low", user.id)


__all__ = ["cli"]
