"""Module for a yearly/monthly track summary."""

from typing import Dict, List

from fietsboek.models.track import TrackWithMetadata


class Summary:
    """A summary of a user's tracks.

    :ivar years: Mapping of year to :class:`YearSummary`.
    :vartype years: dict[int, YearSummary]
    :ivar ascending: If ``True``, years will be sorted from old-to-new,
        otherwise they will be sorted new-to-old.
    :vartype ascending: bool
    """

    def __init__(self, ascending: bool = True):
        self.years: Dict[int, YearSummary] = {}
        self.ascending = ascending

    def __iter__(self):
        items = list(self.years.values())
        items.sort(key=lambda y: y.year, reverse=not self.ascending)
        return iter(items)

    def __len__(self) -> int:
        return len(self.all_tracks())

    def all_tracks(self) -> List[TrackWithMetadata]:
        """Returns all tracks of the summary.

        :return: All tracks.
        """
        return [track for year in self for month in year for track in month.all_tracks()]

    def add(self, track: TrackWithMetadata):
        """Add a track to the summary.

        This automatically inserts the track into the right yearly summary.

        :raises ValueError: If the given track has no date set.
        :param track: The track to insert.
        :type track: fietsboek.model.track.Track
        """
        if track.date is None:
            raise ValueError("Cannot add a track without date")
        year = track.date.year
        self.years.setdefault(year, YearSummary(year, self.ascending)).add(track)

    @property
    def total_length(self) -> float:
        """Returns the total length of all tracks in this summary.

        :return: The total length in meters.
        """
        return sum(track.length for track in self.all_tracks())


class YearSummary:
    """A summary over a single year.

    :ivar year: Year number.
    :ivar months: Mapping of month to :class:`MonthSummary`.
    :ivar ascending: If ``True``, months will be sorted from old-to-new,
        otherwise they will be sorted new-to-old.
    :vartype ascending: bool
    """

    def __init__(self, year: int, ascending: bool = True):
        self.year: int = year
        self.months: Dict[int, MonthSummary] = {}
        self.ascending = ascending

    def __iter__(self):
        items = list(self.months.values())
        items.sort(key=lambda x: x.month, reverse=not self.ascending)
        return iter(items)

    def __len__(self) -> int:
        return len(self.all_tracks())

    def all_tracks(self) -> List[TrackWithMetadata]:
        """Returns all tracks of the summary.

        :return: All tracks.
        """
        return [track for month in self for track in month]

    def add(self, track: TrackWithMetadata):
        """Add a track to the summary.

        This automatically inserts the track into the right monthly summary.

        :raises ValueError: If the given track has no date set.
        :param track: The track to insert.
        """
        if track.date is None:
            raise ValueError("Cannot add a track without date")
        month = track.date.month
        self.months.setdefault(month, MonthSummary(month)).add(track)

    @property
    def total_length(self) -> float:
        """Returns the total length of all tracks in this summary.

        :return: The total length in meters.
        """
        return sum(track.length for track in self.all_tracks())


class MonthSummary:
    """A summary over a single month.

    :ivar month: Month number (1-12).
    :ivar tracks: List of tracks in this month.
    """

    def __init__(self, month):
        self.month: int = month
        self.tracks: List[TrackWithMetadata] = []

    def __iter__(self):
        items = self.tracks[:]
        # We know that sorting by date works, we even assert that all tracks
        # have a date set.
        items.sort(key=lambda t: t.date)  # type: ignore
        return iter(items)

    def __len__(self) -> int:
        return len(self.all_tracks())

    def all_tracks(self) -> List[TrackWithMetadata]:
        """Returns all tracks of the summary.

        :return: All tracks.
        """
        return self.tracks[:]

    def add(self, track: TrackWithMetadata):
        """Add a track to the summary.

        :raises ValueError: If the given track has no date set.
        :param track: The track to insert.
        """
        if track.date is None:
            raise ValueError("Cannot add a track without date")
        self.tracks.append(track)

    @property
    def total_length(self) -> float:
        """Returns the total length of all tracks in this summary.

        :return: The total length in meters.
        """
        return sum(track.length for track in self.all_tracks())
