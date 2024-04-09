"""Transformers that deal with elevation changes in the track."""

from collections.abc import Callable, Iterable
from itertools import islice, zip_longest

from gpxpy.gpx import GPX, GPXTrackPoint
from pyramid.i18n import TranslationString

from . import Parameters, Transformer

_ = TranslationString

MAX_ORGANIC_SLOPE: float = 1.0


def slope(point_a: GPXTrackPoint, point_b: GPXTrackPoint) -> float:
    """Returns the slope between two GPX points.

    This is defined as delta_h / euclid_distance.

    :param point_a: First point.
    :param point_b: Second point.
    :return: The slope, as percentage.
    """
    if point_a.elevation is None or point_b.elevation is None:
        return 0.0
    delta_h = abs(point_a.elevation - point_b.elevation)
    dist = point_a.distance_2d(point_b)
    if dist == 0.0 or dist is None:
        return 0.0
    return delta_h / dist


class FixNullElevation(Transformer):
    """A transformer that fixes points with zero elevation."""

    @classmethod
    def identifier(cls) -> str:
        return "fix-null-elevation"

    @classmethod
    def name(cls) -> TranslationString:
        return _("transformers.fix-null-elevation.title")

    @classmethod
    def description(cls) -> TranslationString:
        return _("transformers.fix-null-elevation.description")

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
        def all_points():
            return gpx.walk(only_points=True)

        def rev_points():
            # We cannot use reversed(gpx.walk(...)) since that is not a
            # generator, so we do it manually.
            return (
                point
                for track in reversed(gpx.tracks)
                for segment in reversed(track.segments)
                for point in reversed(segment.points)
            )

        # First, from the front
        self.fixup(all_points)
        # Then, from the back
        self.fixup(rev_points)

    @classmethod
    def fixup(cls, points: Callable[[], Iterable[GPXTrackPoint]]):
        """Fixes the given GPX points.

        This iterates over the points and checks for the first point that has a
        non-zero elevation, and a slope that doesn't exceed 100%. All previous
        points will have their elevation adjusted to match this first "good
        point".

        :param points: A function that generates the iterable of points.
        """
        bad_until = 0
        final_elevation = 0.0
        for i, (point, next_point) in enumerate(zip(points(), islice(points(), 1, None))):
            if (
                point.elevation is not None
                and point.elevation != 0.0
                and slope(point, next_point) < MAX_ORGANIC_SLOPE
            ):
                bad_until = i
                final_elevation = point.elevation
                break

        for point in islice(points(), None, bad_until):
            point.elevation = final_elevation


class FixElevationJumps(Transformer):
    """A transformer that fixes big jumps in the elevation."""

    @classmethod
    def identifier(cls) -> str:
        return "fix-elevation-jumps"

    @classmethod
    def name(cls) -> TranslationString:
        return _("transformers.fix-elevation-jumps")

    @classmethod
    def description(cls) -> TranslationString:
        return _("transformers.fix-elevation-jumps.description")

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
        current_adjustment = 0.0

        points = gpx.walk(only_points=True)
        next_points = gpx.walk(only_points=True)

        for current_point, next_point in zip_longest(points, islice(next_points, 1, None)):
            point_adjustment = current_adjustment
            if next_point and slope(current_point, next_point) > MAX_ORGANIC_SLOPE:
                current_adjustment += current_point.elevation - next_point.elevation
                print(f"{current_adjustment=}")
            current_point.elevation += point_adjustment


__all__ = ["FixNullElevation", "FixElevationJumps"]
