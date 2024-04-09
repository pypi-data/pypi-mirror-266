"""Custom filters for Jinja2."""

import datetime
import json

import jinja2
from babel.dates import format_datetime
from babel.numbers import format_decimal
from jinja2.runtime import Context
from markupsafe import Markup
from pyramid.request import Request

from . import util


@jinja2.pass_context
def filter_format_decimal(ctx: Context, value: float) -> str:
    """Format a decimal number according to the locale.

    This uses the right thousands grouping and the right decimal separator.

    :param ctx: The jinja context, passed automatically.
    :param value: The value to format.
    :return: The formatted decimal.
    """
    request = ctx.get("request")
    locale = request.localizer.locale_name
    return format_decimal(value, locale=locale)


@jinja2.pass_context
def filter_format_datetime(ctx: Context, value: datetime.datetime) -> str:
    """Format a datetime according to the locale.

    :param ctx: The jinja context, passed automatically.
    :param value: The value to format.
    :return: The formatted date.
    """
    request = ctx.get("request")
    locale = request.localizer.locale_name
    return format_datetime(value, locale=locale)


@jinja2.pass_context
def filter_local_datetime(ctx: Context, value: datetime.datetime) -> Markup:
    """Format a UTC datetime to show in the user's local timezone.

    This is done by embedding the UTC timestamp in the page, such that we can
    do some client-side magic and replace it with the time in the user's local
    timezone. As a fallback value, we do apply the locale's standard
    formatting, in case JavaScript is disabled - however, that will not
    represent the time in the user's timezone, but in UTC.

    :param ctx: The jinja context, passed automatically.
    :param value: The value to format.
    :return: The formatted date.
    """
    # If we get a naive object in, we assume that we got it from the database
    # and we have to treat it like a UTC-aware object. This happens when we
    # access object's DateTime columns directly, as SQLAlchemy only returns
    # naive datetimes.
    if value.tzinfo is None:
        value = value.replace(tzinfo=datetime.timezone.utc)
    else:
        value = value.astimezone(datetime.timezone.utc)

    request = ctx.get("request")
    locale = request.localizer.locale_name
    fallback = Markup.escape(format_datetime(value, locale=locale))

    # Forget about the fractional seconds
    timestamp = int(value.timestamp())
    return Markup(
        f'<span class="fietsboek-local-datetime" data-utc-timestamp="{timestamp}">{fallback}</span>'
    )


def global_embed_tile_layers(request: Request) -> Markup:
    """Renders the available tile servers for the current user, as a JSON object.

    The returned value is wrapped as a :class:`~markupsafe.Markup` so that it
    won't get escaped by jinja.

    :param request: The Pyramid request.
    :return: The available tile servers.
    """
    # pylint: disable=import-outside-toplevel,cyclic-import
    from .views import tileproxy

    tile_sources = tileproxy.sources_for(request)

    if request.config.disable_tile_proxy:

        def _url(source):
            return source.url

    else:

        def _url(source):
            return util.tile_url(request, "tile-proxy", provider=source.layer_id)

    return Markup(
        json.dumps(
            [
                {
                    "name": source.name,
                    "url": _url(source),
                    "attribution": source.attribution,
                    "type": source.layer_type.value,
                    "zoom": source.zoom,
                }
                for source in tile_sources
            ]
        )
    )


def global_list_languages(request: Request) -> list[tuple[str, str]]:
    """Returns a list of available languages.

    The first element of each tuple is the (technical) locale name, the second
    element is the display name.

    :param request: The Pyramid request.
    :return: The available languages.
    """
    return util.list_locales(request)
