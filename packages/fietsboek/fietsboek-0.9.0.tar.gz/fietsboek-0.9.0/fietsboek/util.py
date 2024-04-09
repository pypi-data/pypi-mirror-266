"""Various utility functions."""

import datetime
import html
import importlib.resources
import os
import re
import secrets
import unicodedata
from typing import List, Optional, TypeVar, Union

import babel
import gpxpy
import markdown
import nh3
import sqlalchemy
import webob
from markupsafe import Markup
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.i18n import TranslationString as _
from pyramid.request import Request
from sqlalchemy import select

T = TypeVar("T")

ALLOWED_TAGS = (
    # Those were the bleach defaults, they worked fine
    {"a", "abbr", "acronym", "b", "blockquote", "code", "em", "i", "li", "ol", "strong", "ul"}
    # Allow headings
    .union({"h1", "h2", "h3", "h4", "h5", "h6"})
    .union({"p"})
    .union({"img"})
)

ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "abbr": {"title"},
    "acronym": {"title"},
    "img": {"alt", "src"},
}

# Arbitrarily chosen, just make sure they are representable
DEFAULT_START_TIME = datetime.datetime(1977, 5, 25, 8, 0)
DEFAULT_END_TIME = datetime.datetime(1985, 7, 3, 8, 0)

DISPLAY_NAME_PATH = "DISPLAY_NAME"
"""Path of the file in a locale resource folder which contains the display name."""


_filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
_windows_device_files = (
    "CON",
    "AUX",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "LPT1",
    "LPT2",
    "LPT3",
    "PRN",
    "NUL",
)


def safe_markdown(md_source: str) -> Markup:
    """Transform a markdown document into a safe HTML document.

    This uses ``markdown`` to first parse the markdown source into HTML, and
    then ``bleach`` to strip any disallowed HTML tags.

    :param md_source: The markdown source.
    :return: The safe HTML transformed version.
    """
    converted = markdown.markdown(md_source, output_format="html")
    converted = nh3.clean(converted, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    return Markup(converted)


def fix_iso_timestamp(timestamp: str) -> str:
    """Fixes an ISO timestamp to make it parseable by
    :meth:`datetime.datetime.fromisoformat`.

    This removes an 'Z' if it exists at the end of the timestamp, and replaces
    it with '+00:00'.

    :param timestamp: The timestamp to fix.
    :return: The fixed timestamp.
    """
    if timestamp.endswith("Z"):
        return timestamp[:-1] + "+00:00"
    return timestamp


def round_timedelta_to_multiple(
    value: datetime.timedelta, multiples: datetime.timedelta
) -> datetime.timedelta:
    """Round the timedelta `value` to be a multiple of `multiples`.

    :param value: The value to be rounded.
    :param multiples: The size of each multiple.
    :return: The rounded value.
    """
    lower = value.total_seconds() // multiples.total_seconds() * multiples.total_seconds()
    second_offset = value.total_seconds() - lower
    if second_offset <= multiples.total_seconds() // 2:
        # Round down
        return datetime.timedelta(seconds=lower)
    # Round up
    return datetime.timedelta(seconds=lower) + multiples


def guess_gpx_timezone(gpx: gpxpy.gpx.GPX) -> datetime.tzinfo:
    """Guess which timezone the GPX file was recorded in.

    This looks at a few timestamps to see if they have timezone information
    attached, including some known GPX extensions.

    :param gpx: The parsed GPX file to analyse.
    :return: The timezone information.
    """
    time_bounds = gpx.get_time_bounds()
    times = [
        gpx.time,
        time_bounds.start_time,
        time_bounds.end_time,
    ]
    times = [time for time in times if time]
    # First, we check if any of the timestamps has a timezone attached. Note
    # that some devices save their times in UTC, so we need to look for a
    # timestamp different than UTC.
    for time in times:
        if time.tzinfo and time.tzinfo.utcoffset(time):
            return time.tzinfo

    # Next, we look if there's a "localTime" extension on the track, so we can
    # compare the local time to the time.
    if times:
        for track in gpx.tracks:
            time = times[0]
            local_time = None
            for extension in track.extensions:
                if extension.tag.lower() == "localtime":
                    local_time = datetime.datetime.fromisoformat(
                        fix_iso_timestamp(extension.text)
                    ).replace(tzinfo=None)
                elif extension.tag.lower() == "time":
                    time = datetime.datetime.fromisoformat(
                        fix_iso_timestamp(extension.text)
                    ).replace(tzinfo=None)
            if local_time is not None:
                # We found a pair that we can use!
                offset = local_time - time
                # With all the time madness, luckily most time zones seem to stick
                # to an offset that is a multiple of 15 minutes (see
                # https://en.wikipedia.org/wiki/List_of_UTC_offsets). We try to
                # round the value to the nearest of 15 minutes, to prevent any
                # funky offsets from happening due to slight clock desyncs.
                offset = round_timedelta_to_multiple(offset, datetime.timedelta(minutes=15))
                return datetime.timezone(offset)

    # If all else fails, we assume that we are UTC+00:00
    return datetime.timezone.utc


def tour_metadata(gpx_data: Union[str, bytes, gpxpy.gpx.GPX]) -> dict:
    """Calculate the metadata of the tour.

    Returns a dict with ``length``, ``uphill``, ``downhill``, ``moving_time``,
    ``stopped_time``, ``max_speed``, ``avg_speed``, ``start_time`` and
    ``end_time``.

    :param gpx_data: The GPX data of the tour. Can be pre-parsed to save time.
    :return: A dictionary with the computed values.
    """
    if isinstance(gpx_data, bytes):
        gpx_data = gpx_data.decode("utf-8")
    if isinstance(gpx_data, gpxpy.gpx.GPX):
        gpx = gpx_data
    else:
        gpx = gpxpy.parse(gpx_data)
    timezone = guess_gpx_timezone(gpx)
    uphill, downhill = gpx.get_uphill_downhill()
    moving_data = gpx.get_moving_data()
    time_bounds = gpx.get_time_bounds()
    try:
        avg_speed = moving_data.moving_distance / moving_data.moving_time
    except ZeroDivisionError:
        avg_speed = 0.0
    return {
        "length": gpx.length_3d(),
        "uphill": uphill,
        "downhill": downhill,
        "moving_time": moving_data.moving_time,
        "stopped_time": moving_data.stopped_time,
        "max_speed": moving_data.max_speed,
        "avg_speed": avg_speed,
        "start_time": (time_bounds.start_time or DEFAULT_START_TIME).astimezone(timezone),
        "end_time": (time_bounds.end_time or DEFAULT_END_TIME).astimezone(timezone),
    }


def mps_to_kph(mps: float) -> float:
    """Converts meters/second to kilometers/hour.

    :param mps: Input meters/second.
    :return: The converted km/h value.
    """
    return mps / 1000 * 60 * 60


def human_size(num_bytes: int) -> str:
    """Formats the amount of bytes for human consumption.

    :param num_bytes: The amount of bytes.
    :return: The formatted amount.
    """
    num_bytes = float(num_bytes)
    suffixes = ["B", "KiB", "MiB", "GiB"]
    prefix = ""
    if num_bytes < 0:
        prefix = "-"
        num_bytes = -num_bytes
    for suffix in suffixes:
        if num_bytes < 1024 or suffix == suffixes[-1]:
            if suffix == "B":
                # Don't do the decimal point for bytes
                return f"{prefix}{int(num_bytes)} {suffix}"
            return f"{prefix}{num_bytes:.1f} {suffix}"
        num_bytes /= 1024
    # Unreachable:
    return ""


def month_name(request: Request, month: int) -> str:
    """Returns the localized name for the month with the given number.

    :param request: The pyramid request.
    :param month: Number of the month, 1 = January.
    :return: The localized month name.
    """
    assert 1 <= month <= 12
    locale = babel.Locale.parse(request.localizer.locale_name)
    return locale.months["stand-alone"]["wide"][month]


def random_link_secret(nbytes: int = 20) -> str:
    """Safely generates a secret suitable for the link share.

    The returned string consists of characters that are safe to use in a URL.

    :param nbytes: Number of random bytes to use.
    :return: A randomly drawn string.
    """
    return secrets.token_urlsafe(nbytes)


def retrieve_multiple(
    dbsession: "sqlalchemy.orm.session.Session",
    model: type[T],
    params: "webob.multidict.NestedMultiDict",
    name: str,
) -> list[T]:
    """Parses a reply to retrieve multiple database objects.

    This is usable for arrays sent by HTML forms, for example to retrieve all
    badges or all tagged friends.

    If an object could not be found, this raises a
    :class:`~pyramid.httpexceptions.HTTPBadRequest`.

    :raises pyramid.httpexceptions.HTTPBadRequest: If an object could not be
        found.
    :param dbsession: The database session.
    :param model: The model class to retrieve.
    :param params: The form parameters.
    :param name: Name of the parameter to look for.
    :return: A list of elements found.
    """
    objects = []
    for obj_id in params.getall(name):
        if not obj_id:
            continue
        query = select(model).filter_by(id=obj_id)
        obj = dbsession.execute(query).scalar_one_or_none()
        if obj is None:
            raise HTTPBadRequest()
        objects.append(obj)
    return objects


def check_password_constraints(password: str, repeat_password: Optional[str] = None):
    """Verifies that the password constraints match for the given password.

    This is usually also verified client-side, but for people that bypass the
    client side verification and the API, this is re-implemented here.

    If ``repeat_password`` is given, this also verifies that the two passwords
    match.

    :raises ValueError: If the verification of the constraints failed. The
        first arg of the error will be a
        :class:`~pyramid.i18n.TranslationString` with the message of why the
        verification failed.
    :param password: The password which to verify.
    :param repeat_password: The password repeat.
    """
    if repeat_password is not None:
        if repeat_password != password:
            raise ValueError(_("password_constraint.mismatch"))
    if len(password) < 8:
        raise ValueError(_("password_constraint.length"))


def _locale_packages(locale_packages: Optional[list[str]] = None) -> list[str]:
    # We expect this to be "fietsboek", but we are open to forks.
    my_package = __name__.split(".", 1)[0]
    packages = [my_package]
    if locale_packages:
        packages.extend(locale_packages)
    return packages


def read_localized_resource(
    locale_name: str,
    path: str,
    locale_packages: Optional[List[str]] = None,
    raise_on_error: bool = False,
) -> str:
    """Reads a localized resource.

    Localized resources are located in the ``fietsboek/locale/**`` directory.
    Note that ``path`` may contain slashes.

    If the resource could not be found, a placeholder string is returned instead.

    :param locale_name: Name of the locale.
    :param path: Path of the resource.
    :param locale_packages: Names of packages in which locale data is searched.
        By default, only built-in locales are searched.
    :param raise_on_error: Raise an error instead of returning a placeholder.
    :raises FileNotFoundError: If the path could not be found and
        ``raise_on_error`` is ``True``.
    :return: The text content of the resource.
    """
    locales = [locale_name]
    # Second chance: If the locale is a specific form of a more general
    # locale, try the general locale as well.
    if "_" in locale_name:
        locales.append(locale_name.split("_", 1)[0])

    locale_packages = _locale_packages(locale_packages)

    for locale in locales:
        for package in locale_packages:
            locale_dir = importlib.resources.files(package) / "locale" / locale
            resource_path = locale_dir / path
            try:
                return resource_path.read_text(encoding="utf-8")
            except (FileNotFoundError, ModuleNotFoundError, NotADirectoryError):
                pass
    if raise_on_error:
        raise FileNotFoundError(f"Resource {path!r} not found")
    return f"{locale_name}:{path}"


def locale_display_name(locale_name: str, locale_packages: Optional[list[str]] = None) -> str:
    """Reads the display name for the given locale.

    If the name cannot be found, simply returns ``locale_name``.

    :param locale_name: Name of the locale.
    :param locale_packages: Names of packages in which locale data is searched.
    """
    try:
        return read_localized_resource(locale_name, DISPLAY_NAME_PATH, locale_packages, True)
    except FileNotFoundError:
        return locale_name


def list_locales(request: Request) -> list[tuple[str, str]]:
    """Lists all available locales.

    Returns a list of locale name and display name tuples.

    :param request: The Pyramid request for which to list the locales.
    """
    locales = []
    for locale_name in request.config.available_locales:
        display_name = locale_display_name(locale_name, request.config.language_packs)
        locales.append((locale_name, display_name))
    return locales


def tile_url(request: Request, route_name: str, **kwargs: str) -> str:
    """Generates a URL for tiles.

    This is basically :meth:`request.route_url`, but it keeps the
    ``{x}``/``{y}``/``{z}`` placeholders intact for consumption by Leaflet.

    Expects that the URL takes a ``x``, ``y`` and ``z`` parameter.

    :param request: The Pyramid request.
    :param route_name: The name of the route.
    :param kwargs: Remaining route parameters. Will be passed to ``route_url``.
    :return: The route URL, with intact placeholders.
    """
    # This feels hacky (because it is), but I don't see a better way. The route
    # generation is basically a closure that fills the placeholders
    # all-or-none, and there is no way to get a "structured" representation of
    # the URL without re-parsing it.
    # Using {x} triggers the urlquoting, so we need to do some .replace() calls
    # in the end anyway. Might as well use something that looks a bit better,
    # and not %7Bx%7D.
    kwargs["x"] = "__x__"
    kwargs["y"] = "__y__"
    kwargs["z"] = "__z__"
    route = request.route_url(route_name, **kwargs)
    return route.replace("__x__", "{x}").replace("__y__", "{y}").replace("__z__", "{z}")


def encode_gpx(gpx: gpxpy.gpx.GPX) -> bytes:
    """Encodes a GPX in-memory representation to the XML representation.

    This ensures that the resulting XML file is valid.

    Returns the contents of the XML as bytes, ready to be written to disk.

    :param gpx: The GPX file to encode. Might be modified!
    :return: The encoded GPX content.
    """
    for track in gpx.tracks:
        if track.link:
            track.link = html.escape(track.link)
    return gpx.to_xml().encode("utf-8")


def secure_filename(filename: str) -> str:
    r"""Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.  The filename returned is an ASCII only string
    for maximum portability.
    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename('i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you abort or
    generate a random filename if the function returned an empty one.

    :param filename: the filename to secure
    :return: The secure filename.
    """
    # Taken from
    # https://github.com/pallets/werkzeug/blob/main/src/werkzeug/utils.py

    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip("._")

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if (
        os.name == "nt"
        and filename
        and filename.split(".", maxsplit=1)[0].upper() in _windows_device_files
    ):
        filename = f"_{filename}"

    return filename
