"""Endpoints for the user profile pages."""

import datetime
import logging
import sqlite3
import urllib.parse
from dataclasses import dataclass
from typing import Optional

from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import select
from sqlalchemy.orm import aliased

from .. import models, util
from ..data import UserDataDir
from ..models.track import TrackType, TrackWithMetadata
from ..summaries import Summary

# A well-made transparent tile is actually pretty small (only 116 bytes), which
# is even smaller than our HTTP 404 page. So not only is it more efficient
# (bandwidth-wise) to transfer the transparent PNG, it also means that we can
# set cache headers, which the client will honor.
#
# Since the tile is so small, we've embedded it right here in the source.
#
# The tile is taken and adapted from hittekaart, which in turn took inspiration
# from https://www.mjt.me.uk/posts/smallest-png/ and
# http://www.libpng.org/pub/png/spec/1.2/PNG-Contents.html
# fmt: off
EMPTY_TILE = bytes([
    0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
    0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,
    0x01, 0x03, 0x00, 0x00, 0x00, 0x66, 0xbc, 0x3a, 0x25, 0x00, 0x00, 0x00,
    0x03, 0x50, 0x4c, 0x54, 0x45, 0x00, 0xff, 0x00, 0x34, 0x5e, 0xc0, 0xa8,
    0x00, 0x00, 0x00, 0x01, 0x74, 0x52, 0x4e, 0x53, 0x00, 0x40, 0xe6, 0xd8,
    0x66, 0x00, 0x00, 0x00, 0x1f, 0x49, 0x44, 0x41, 0x54, 0x68, 0x81, 0xed,
    0xc1, 0x01, 0x0d, 0x00, 0x00, 0x00, 0xc2, 0xa0, 0xf7, 0x4f, 0x6d, 0x0e,
    0x37, 0xa0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xbe, 0x0d,
    0x21, 0x00, 0x00, 0x01, 0x9a, 0x60, 0xe1, 0xd5, 0x00, 0x00, 0x00, 0x00,
    0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
])
# fmt: on

LOGGER = logging.getLogger(__name__)


@dataclass
class CumulativeStats:
    """Cumulative user stats.

    The values start out with default values, and tracks can be merged in via
    :meth:`add`.
    """

    # pylint: disable=too-many-instance-attributes

    count: int = 0
    """Number of tracks added."""

    length: float = 0.0
    """Total length, in meters."""

    uphill: float = 0.0
    """Total uphill, in meters."""

    downhill: float = 0.0
    """Total downhill, in meters."""

    moving_time: datetime.timedelta = datetime.timedelta(0)
    """Total time spent moving."""

    stopped_time: datetime.timedelta = datetime.timedelta(0)
    """Total time standing still."""

    max_speed: float = 0.0
    """Overall maximum speed, in m/s."""

    longest_distance_track: Optional[TrackWithMetadata] = None
    """The track with the longest distance."""

    shortest_distance_track: Optional[TrackWithMetadata] = None
    """The track with the shortest distance."""

    longest_duration_track: Optional[TrackWithMetadata] = None
    """The track with the longest time."""

    shortest_duration_track: Optional[TrackWithMetadata] = None
    """The track with the shortest time."""

    def add(self, track: TrackWithMetadata):
        """Adds a track to this stats collection.

        :param track: The track to add, with accompanying metadata.
        """
        self.count += 1
        self.length += track.length
        self.uphill += track.uphill
        self.downhill += track.downhill
        self.moving_time += track.moving_time
        self.stopped_time += track.stopped_time
        self.max_speed = max(self.max_speed, track.max_speed)

        if self.longest_distance_track is None or self.longest_distance_track.length < track.length:
            self.longest_distance_track = track

        if (
            self.shortest_distance_track is None
            or self.shortest_distance_track.length > track.length
        ):
            self.shortest_distance_track = track

        if (
            self.longest_duration_track is None
            or self.longest_duration_track.duration < track.duration
        ):
            self.longest_duration_track = track

        if (
            self.shortest_duration_track is None
            or self.shortest_duration_track.duration > track.duration
        ):
            self.shortest_duration_track = track

    @property
    def avg_speed(self) -> float:
        """Average speed, in m/s."""
        if not self.moving_time:
            return 0.0
        return self.length / self.moving_time.total_seconds()

    @property
    def avg_length(self) -> float:
        """Average length, in m."""
        if not self.count:
            return 0
        return self.length / self.count

    @property
    def avg_duration(self) -> datetime.timedelta:
        """Average duration of a track.

        Note that this property is automatically rounded to seconds.
        """
        if not self.count:
            return datetime.timedelta()
        return round_to_seconds((self.moving_time + self.stopped_time) / self.count)


def round_to_seconds(value: datetime.timedelta) -> datetime.timedelta:
    """Round a timedelta to full seconds.

    :param value: The input value.
    :return: The rounded value.
    """
    return util.round_timedelta_to_multiple(value, datetime.timedelta(seconds=1))


@view_config(
    route_name="profile",
    renderer="fietsboek:templates/profile.jinja2",
    request_method="GET",
    permission="profile.view",
)
def profile(request: Request) -> dict:
    """Shows the profile page.

    :param request: The pyramid request.
    :return: The template parameters.
    """
    total = CumulativeStats()

    query = request.context.all_tracks_query()
    query = select(aliased(models.Track, query)).where(query.c.type == TrackType.ORGANIC)
    track: models.Track
    for track in request.dbsession.execute(query).scalars():
        meta = TrackWithMetadata(track, request.data_manager)
        total.add(meta)

    total.moving_time = round_to_seconds(total.moving_time)
    total.stopped_time = round_to_seconds(total.stopped_time)

    user_id = request.context.id
    heatmap_url = None
    tilehunt_url = None
    try:
        user_dir: UserDataDir = request.data_manager.open_user(request.context.id)
    except FileNotFoundError:
        pass
    else:
        if user_dir.heatmap_path().is_file():
            heatmap_url = util.tile_url(request, "user-tile", user_id=user_id, map="heatmap")
        if user_dir.tilehunt_path().is_file():
            tilehunt_url = util.tile_url(request, "user-tile", user_id=user_id, map="tilehunt")

    return {
        "user": request.context,
        "total": total,
        "mps_to_kph": util.mps_to_kph,
        "heatmap_url": heatmap_url,
        "tilehunt_url": tilehunt_url,
    }


@view_config(
    route_name="user-tile",
    request_method="GET",
    permission="profile.view",
    http_cache=datetime.timedelta(hours=1),
)
def user_tile(request: Request) -> Response:
    """Returns a single tile from the user's own overlay maps.

    :param request: The pyramid request.
    :return: The response, with the tile content (or an error).
    """
    try:
        user_dir: UserDataDir = request.data_manager.open_user(request.context.id)
    except FileNotFoundError:
        return HTTPNotFound()

    paths = {
        "heatmap": user_dir.heatmap_path(),
        "tilehunt": user_dir.tilehunt_path(),
    }
    path = paths.get(request.matchdict["map"])
    if path is None:
        return HTTPNotFound()

    # See
    # https://docs.python.org/3/library/sqlite3.html#how-to-work-with-sqlite-uris
    # https://stackoverflow.com/questions/10205744/opening-sqlite3-database-from-python-in-read-only-mode
    # https://stackoverflow.com/questions/17170202/dont-want-to-create-a-new-database-if-it-doesnt-already-exists
    sqlite_uri = urllib.parse.urlunparse(("file", "", str(path), "", "mode=ro", ""))
    try:
        connection = sqlite3.connect(sqlite_uri, uri=True)
    except sqlite3.OperationalError:
        return HTTPNotFound()

    cursor = connection.cursor()
    result = cursor.execute(
        "SELECT data FROM tiles WHERE zoom = ? AND x = ? AND y = ?;",
        (int(request.matchdict["z"]), int(request.matchdict["x"]), int(request.matchdict["y"])),
    )
    result = result.fetchone()
    if result is None:
        return Response(EMPTY_TILE, content_type="image/png")

    return Response(result[0], content_type="image/png")


@view_config(
    route_name="json-summary", request_method="GET", permission="profile.view", renderer="json"
)
def json_summary(request: Request) -> Response:
    """Returns the per-month summary as JSON.

    :param request: The pyramid request.
    :return: The response, rendered as JSON.
    """
    query = request.identity.all_tracks_query()
    query = select(aliased(models.Track, query)).where(query.c.type == TrackType.ORGANIC)
    summary = Summary()

    for track in request.dbsession.execute(query).scalars():
        if track.cache is None:
            LOGGER.debug("Skipping track %d as it has no cached metadata", track.id)
            continue
        summary.add(TrackWithMetadata(track, request.data_manager))

    return {y.year: {m.month: m.total_length for m in y} for y in summary}


__all__ = ["profile", "user_tile", "json_summary"]
