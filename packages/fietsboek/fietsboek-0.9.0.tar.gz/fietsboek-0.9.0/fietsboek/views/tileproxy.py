"""Tile proxying layer.

While this might slow down the initial load (as we now load everything through
fietsboek), we can cache the OSM tiles per instance, and we can provide better
access control for services like thunderforest.com.

Additionally, this protects the users' IP, as only fietsboek can see it.
"""

import datetime
import logging
import threading
from itertools import chain
from typing import List, Optional
from urllib.parse import quote

import requests
from pydantic import AnyUrl, TypeAdapter
from pyramid.httpexceptions import HTTPBadRequest, HTTPGatewayTimeout
from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config
from requests.exceptions import ReadTimeout
from zope.interface import Interface, implementer

from .. import __VERSION__
from ..config import Config, LayerAccess, LayerType, TileLayerConfig

LOGGER = logging.getLogger(__name__)


def _href(url, text):
    return f'<a href="{url}" target="_blank">{text}</a>'


_jb_copy = _href("https://www.j-berkemeier.de/GPXViewer", "GPXViewer")


def _url(value: str) -> AnyUrl:
    return TypeAdapter(AnyUrl).validate_python(value)


DEFAULT_TILE_LAYERS = [
    # Main base layers
    TileLayerConfig(
        layer_id="osm",
        name="OSM",
        url=_url("https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
        type=LayerType.BASE,
        zoom=19,
        access=LayerAccess.PUBLIC,
        attribution="".join(
            [
                _jb_copy,
                " | Map data &copy; ",
                _href("https://www.openstreetmap.org/", "OpenStreetMap"),
                " and contributors ",
                _href("https://creativecommons.org/licenses/by-sa/2.0/", "CC-BY-SA"),
            ]
        ),
    ),
    TileLayerConfig(
        layer_id="satellite",
        name="Satellit",
        url=_url(
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ),
        type=LayerType.BASE,
        zoom=21,
        access=LayerAccess.PUBLIC,
        attribution="".join(
            [
                _jb_copy,
                " | Map data &copy; ",
                _href("https://www.esri.com", "Esri"),
                ", i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, ",
                "IGP, UPR-EGP, and the GIS User Community",
            ]
        ),
    ),
    TileLayerConfig(
        layer_id="osmde",
        name="OSMDE",
        url=_url("https://tile.openstreetmap.de/tiles/osmde/{z}/{x}/{y}.png"),
        type=LayerType.BASE,
        zoom=19,
        access=LayerAccess.PUBLIC,
        attribution="".join(
            [
                _jb_copy,
                " | Map data &copy; ",
                _href("https://www.openstreetmap.org/", "OpenStreetMap"),
                " and contributors ",
                _href("https://creativecommons.org/licenses/by-sa/2.0/", "CC-BY-SA"),
            ]
        ),
    ),
    TileLayerConfig(
        layer_id="opentopo",
        name="Open Topo",
        url=_url("https://tile.opentopomap.org/{z}/{x}/{y}.png"),
        type=LayerType.BASE,
        zoom=17,
        access=LayerAccess.PUBLIC,
        attribution="".join(
            [
                _jb_copy,
                " | Kartendaten: © OpenStreetMap-Mitwirkende, SRTM | Kartendarstellung: © ",
                _href("https://opentopomap.org/about", "OpenTopoMap"),
                " (CC-BY-SA)",
            ]
        ),
    ),
    TileLayerConfig(
        layer_id="topplusopen",
        name="TopPlusOpen",
        url=_url(
            "https://sgx.geodatenzentrum.de/wmts_topplus_open/tile/"
            "1.0.0/web/default/WEBMERCATOR/{z}/{y}/{x}.png"
        ),
        type=LayerType.BASE,
        zoom=18,
        access=LayerAccess.PUBLIC,
        attribution="".join(
            [
                _jb_copy,
                " | Kartendaten: © ",
                _href(
                    "https://www.bkg.bund.de/SharedDocs/Produktinformationen"
                    "/BKG/DE/P-2017/170922-TopPlus-Web-Open.html",
                    "Bundesamt für Kartographie und Geodäsie",
                ),
            ]
        ),
    ),
    # Overlay layers
    TileLayerConfig(
        layer_id="opensea",
        name="OpenSea",
        url=_url("https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"),
        type=LayerType.OVERLAY,
        zoom=None,
        access=LayerAccess.PUBLIC,
        attribution=(
            'Kartendaten: © <a href="http://www.openseamap.org">OpenSeaMap</a> contributors'
        ),
    ),
    TileLayerConfig(
        layer_id="hiking",
        name="Hiking",
        url=_url("https://tile.waymarkedtrails.org/hiking/{z}/{x}/{y}.png"),
        type=LayerType.OVERLAY,
        zoom=None,
        access=LayerAccess.PUBLIC,
        attribution=(
            f'&copy; {_href("http://waymarkedtrails.org", "Sarah Hoffmann")} '
            f'({_href("https://creativecommons.org/licenses/by-sa/3.0/", "CC-BY-SA")})'
        ),
    ),
    TileLayerConfig(
        layer_id="cycling",
        name="Cycling",
        url=_url("https://tile.waymarkedtrails.org/cycling/{z}/{x}/{y}.png"),
        type=LayerType.OVERLAY,
        zoom=None,
        access=LayerAccess.PUBLIC,
        attribution=(
            f'&copy; {_href("http://waymarkedtrails.org", "Sarah Hoffmann")} '
            f'({_href("https://creativecommons.org/licenses/by-sa/3.0/", "CC-BY-SA")})'
        ),
    ),
]

STAMEN_LAYERS = [
    TileLayerConfig(
        layer_id="stamen-toner",
        name="Stamen Toner",
        url=_url("https://stamen-tiles.a.ssl.fastly.net/toner/{z}/{x}/{y}.png"),
        type=LayerType.BASE,
        zoom=17,
        access=LayerAccess.PUBLIC,
        attribution=(
            f'{_jb_copy} | Map tiles by <a href="http://stamen.com">Stamen Design</a>, '
            'under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
            'Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under '
            '<a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
        ),
    ),
    TileLayerConfig(
        layer_id="stamen-terrain",
        name="Stamen Terrain",
        url=_url("https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png"),
        type=LayerType.BASE,
        zoom=15,
        access=LayerAccess.PUBLIC,
        attribution=(
            f'{_jb_copy} | Map tiles by <a href="http://stamen.com">Stamen Design</a>, '
            'under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
            'Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under '
            '<a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
        ),
    ),
    TileLayerConfig(
        layer_id="stamen-watercolor",
        name="Stamen Watercolor",
        url=_url("https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.png"),
        type=LayerType.BASE,
        zoom=17,
        access=LayerAccess.PUBLIC,
        attribution=(
            f'{_jb_copy} | Map tiles by <a href="http://stamen.com">Stamen Design</a>, '
            'under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
            'Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under '
            '<a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.'
        ),
    ),
]

TTL = datetime.timedelta(days=7)
"""Time to live of cached tiles."""

TIMEOUT = datetime.timedelta(seconds=1.5)
"""Timeout when requesting new tiles from a source server."""

PUNISHMENT_TTL = datetime.timedelta(minutes=10)
"""Block-out period after too many requests of a server have timed out."""

PUNISHMENT_THRESHOLD = 10
"""Block a provider after that many requests have timed out."""

MAX_CONCURRENT_CONNECTIONS = 2
"""Maximum TCP connections per tile host."""

CONNECTION_CLOSE_TIMEOUT = datetime.timedelta(seconds=2)
"""Timeout after which keep-alive connections are killed.

Note that new requests reset the timeout.
"""


class ITileRequester(Interface):  # pylint: disable=inherit-non-class
    """An interface to define the tile requester."""

    def load_tile(self, url: str, headers: Optional[dict[str, str]] = None) -> requests.Response:
        """Loads a tile at the given URL.

        :param url: The URL of the tile to load.
        :param headers: Additional headers to send.
        :return: The response.
        """
        raise NotImplementedError()


@implementer(ITileRequester)
class TileRequester:  # pylint: disable=too-few-public-methods
    """Implementation of the tile requester using requests sessions.

    The benefit of this over doing ``requests.get`` is that we can re-use
    connections, and we ensure that we comply with the use policy of the tile
    servers by not hammering them with too many connections.
    """

    def __init__(self):
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_maxsize=MAX_CONCURRENT_CONNECTIONS,
            pool_block=True,
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.lock = threading.Lock()
        self.closer = None

    def load_tile(self, url: str, headers: Optional[dict[str, str]] = None) -> requests.Response:
        """Implementation of :meth:`ITileRequester.load_tile`."""
        response = self.session.get(url, headers=headers, timeout=TIMEOUT.total_seconds())
        response.raise_for_status()
        self._schedule_session_close()
        return response

    def _schedule_session_close(self):
        with self.lock:
            if self.closer:
                self.closer.cancel()
            self.closer = threading.Timer(
                CONNECTION_CLOSE_TIMEOUT.total_seconds(),
                self._close_session,
            )
            self.closer.start()

    def _close_session(self):
        with self.lock:
            self.closer = None
            self.session.close()


@view_config(route_name="tile-proxy", http_cache=3600)
def tile_proxy(request):
    """Requests the given tile from the proxy.

    :param request: The Pyramid request.
    :type request: pyramid.request.Request
    :return: The HTTP response.
    :rtype: pyramid.response.Response
    """
    # pylint: disable=too-many-locals
    if request.config.disable_tile_proxy:
        raise HTTPBadRequest("Tile proxying is disabled")

    provider = request.matchdict["provider"]
    tile_sources = {source.layer_id: source for source in sources_for(request)}
    if provider not in tile_sources:
        raise HTTPBadRequest("Invalid provider")

    x, y, z = (
        int(request.matchdict["x"]),
        int(request.matchdict["y"]),
        int(request.matchdict["z"]),
    )
    cache_key = f"tile:{provider}-{x}-{y}-{z}"
    content_type = "image/png"

    cached = request.redis.get(cache_key)
    if cached is not None:
        return Response(cached, content_type=content_type)

    timeout_tracker = f"provider-timeout:{provider}"
    if int(request.redis.get(timeout_tracker) or "0") > PUNISHMENT_THRESHOLD:
        # We've gotten too many timeouts from this provider recently, so avoid
        # contacting it in the first place.
        LOGGER.debug("Aborted attempt to contact %s due to previous timeouts", provider)
        raise HTTPGatewayTimeout(f"Avoiding request to {provider}")

    url = (
        tile_sources[provider]
        .url.unicode_string()
        .replace(quote("{x}"), str(x))
        .replace(quote("{y}"), str(y))
        .replace(quote("{z}"), str(z))
    )
    # Avoid doing actual requests during tests
    if url.startswith("http://localhost:0"):
        LOGGER.debug("Skipping tile proxy request for testing URL")
        return Response(b"", content_type="image/png")
    headers = {
        "user-agent": f"Fietsboek-Tile-Proxy/{__VERSION__}",
    }
    from_mail = request.config.email_from
    if from_mail:
        headers["from"] = from_mail

    loader: ITileRequester = request.registry.getUtility(ITileRequester)
    try:
        resp = loader.load_tile(url, headers=headers)
    except ReadTimeout:
        LOGGER.debug("Proxy timeout when accessing %r", url)
        request.redis.incr(timeout_tracker)
        request.redis.expire(timeout_tracker, PUNISHMENT_TTL)
        raise HTTPGatewayTimeout(f"No response in time from {provider}") from None
    except requests.HTTPError as exc:
        LOGGER.info("Proxy request failed for %s: %s", provider, exc)
        status_code = 400
        if exc.response:
            status_code = exc.response.status_code
        return Response(f"Failed to get tile from {provider}", status_code=status_code)
    else:
        request.redis.set(cache_key, resp.content, ex=TTL)
        return Response(resp.content, content_type=resp.headers.get("Content-type", content_type))


def sources_for(request: Request) -> List[TileLayerConfig]:
    """Returns all eligible tile sources for the given request.

    :param request: The Pyramid request.
    :return: A list of tile sources.
    """
    return [
        source
        for source in chain(
            (
                default_layer
                for default_layer in DEFAULT_TILE_LAYERS
                if default_layer.layer_id in request.config.default_tile_layers
            ),
            extract_tile_layers(request.config),
        )
        if source.access == LayerAccess.PUBLIC or request.identity is not None
    ]


def extract_tile_layers(config: Config) -> List[TileLayerConfig]:
    """Extract all defined tile layers from the settings.

    :param config: The fietsboek config.
    :return: A list of extracted tile sources.
    """
    layers = []
    layers.extend(_extract_thunderforest(config))
    layers.extend(_extract_stamen(config))
    layers.extend(config.tile_layers)
    return layers


def _extract_thunderforest(config):
    # Thunderforest Shortcut!
    tf_api_key = config.thunderforest_key.get_secret_value()
    if tf_api_key:
        tf_access = config.thunderforest_access
        tf_attribution = " | ".join(
            [
                _jb_copy,
                _href("https://www.thunderforest.com/", "Thunderforest"),
                _href("https://www.openstreetmap.org/", "OpenStreetMap"),
            ]
        )
        for tf_map in config.thunderforest_maps:
            url = (
                f"https://tile.thunderforest.com/{tf_map}/"
                f"{{z}}/{{x}}/{{y}}.png?apikey={tf_api_key}"
            )
            yield TileLayerConfig(
                layer_id=f"tf-{tf_map}",
                name=f"TF {tf_map.title()}",
                url=_url(url),
                type=LayerType.BASE,
                zoom=22,
                access=tf_access,
                attribution=tf_attribution,
            )


def _extract_stamen(config):
    layers = {layer.layer_id: layer for layer in STAMEN_LAYERS}
    for name in config.stamen_maps:
        yield layers[f"stamen-{name}"]
