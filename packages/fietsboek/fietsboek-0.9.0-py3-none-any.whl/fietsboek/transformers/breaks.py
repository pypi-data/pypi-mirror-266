"""Transformers that deal with breaks in the track."""

import datetime

from gpxpy.gpx import GPX, GPXTrack
from pyramid.i18n import TranslationString

from . import Parameters, Transformer

_ = TranslationString

# 1km/h is the default limit of gpxpy. We convert this into m/s to make our
# live easier.
STOPPED_SPEED_LIMIT: float = 1 * 1000 / (60 * 60)
"""Speed limit (in m/s) at which the track is considered to be stopped."""

# We don't want to remove "breaks" at traffic lights or similar, so 5 minutes
# should be a good default.
MIN_BREAK_TO_REMOVE: datetime.timedelta = datetime.timedelta(minutes=5)
"""Minimum length of the break to trigger the removal."""


class RemoveBreaks(Transformer):
    """A transformer that fixes points with zero elevation."""

    @classmethod
    def identifier(cls) -> str:
        return "remove-breaks"

    @classmethod
    def name(cls) -> TranslationString:
        return _("transformers.remove-breaks.title")

    @classmethod
    def description(cls) -> TranslationString:
        return _("transformers.remove-breaks.description")

    @classmethod
    def parameter_model(cls) -> type[Parameters]:
        return Parameters

    @property
    def parameters(self) -> Parameters:
        return Parameters()

    @parameters.setter
    def parameters(self, value):
        pass

    def execute(self, gpx: GPX):
        for track in gpx.tracks:
            self._clean(track)

    def _clean(self, track: GPXTrack):
        if not track.get_points_no():
            return

        i = 0
        while i < track.get_points_no():
            segment_idx, point_idx = index(track, i)
            point = track.segments[segment_idx].points[point_idx]

            # We check if the following points constitute a break, and if yes,
            # how many of them
            count = 0
            current_length = 0.0
            last_point = point
            while True:
                try:
                    j_segment, j_point = index(track, i + count + 1)
                except IndexError:
                    break
                current_point = track.segments[j_segment].points[j_point]
                current_length += last_point.distance_3d(current_point) or 0.0
                last_point = current_point

                delta_t = datetime.timedelta(seconds=point.time_difference(last_point) or 0.0)
                if not delta_t or current_length / delta_t.total_seconds() > STOPPED_SPEED_LIMIT:
                    break
                count += 1

            # No break, carry on!
            if not count:
                i += 1
                continue

            # At this point, check if the break is long enough to be removed
            delta_t = datetime.timedelta(seconds=point.time_difference(last_point) or 0.0)
            if delta_t < MIN_BREAK_TO_REMOVE:
                i += 1
                continue

            # Here, we have a proper break to remove
            # Delete the points belonging to the break ...
            for _ in range(count):
                j_segment, j_point = index(track, i + 1)
                del track.segments[j_segment].points[j_point]

            # ... and shift the time of the following points
            j = i + 1
            while j < track.get_points_no():
                j_segment, j_point = index(track, j)
                track.segments[j_segment].points[j_point].adjust_time(-delta_t)
                j += 1


def index(track: GPXTrack, idx: int) -> tuple[int, int]:
    """Takes a one-dimensional index (the point index) and returns an index
    into the segment/segment points.

    :raises IndexError: When the given index is out of bounds.
    :param track: The track for which to get the index.
    :param idx: The "1D" index.
    :return: A tuple with the segment index, and the index of the point within
    the segment.
    """
    for segment_idx, segment in enumerate(track.segments):
        if idx < len(segment.points):
            return (segment_idx, idx)
        idx -= len(segment.points)
    raise IndexError


__all__ = ["RemoveBreaks"]
