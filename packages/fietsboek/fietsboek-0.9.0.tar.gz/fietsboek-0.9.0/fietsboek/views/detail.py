"""Track detail views."""

import datetime
import gzip
import logging

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPInternalServerError,
    HTTPNotAcceptable,
    HTTPNotFound,
)
from pyramid.i18n import TranslationString as _
from pyramid.response import FileResponse, Response
from pyramid.view import view_config
from sqlalchemy import select

from .. import models, util
from ..models.track import Track, TrackWithMetadata

LOGGER = logging.getLogger(__name__)


def _sort_key(image_name: str) -> str:
    """Returns the "key" by which the image should be sorted.

    :param image_name: Name of the image (on disk).
    :return: The value that should be used to sort the image.
    """
    if "_" not in image_name:
        return image_name
    return image_name.split("_", 1)[1]


@view_config(
    route_name="details", renderer="fietsboek:templates/details.jinja2", permission="track.view"
)
def details(request):
    """Renders the detail page for a given track.

    :param request: The Pyramid request.
    :type request: pyramid.request.Request
    :return: The HTTP response.
    :rtype: pyramid.response.Response
    """
    track = request.context
    description = util.safe_markdown(track.description)
    show_edit_link = track.owner == request.identity

    on_disk_images = []
    try:
        manager = request.data_manager.open(track.id)
        on_disk_images.extend(manager.images())
    except FileNotFoundError:
        pass

    images = []
    for image_name in on_disk_images:
        query = []
        if "secret" in request.GET:
            query.append(("secret", request.GET["secret"]))
        img_src = request.route_url("image", track_id=track.id, image_name=image_name, _query=query)
        query = select(models.ImageMetadata).filter_by(track=track, image_name=image_name)
        image_metadata = request.dbsession.execute(query).scalar_one_or_none()
        if image_metadata:
            images.append((_sort_key(image_name), img_src, image_metadata.description))
        else:
            images.append((_sort_key(image_name), img_src, ""))

    images.sort(key=lambda element: element[0])
    # Strip off the sort key again
    images = [(image[1], image[2]) for image in images]

    with_meta = TrackWithMetadata(track, request.data_manager)
    return {
        "track": with_meta,
        "show_organic": track.show_organic_data(),
        "show_edit_link": show_edit_link,
        "mps_to_kph": util.mps_to_kph,
        "comment_md_to_html": util.safe_markdown,
        "description": description,
        "images": images,
    }


@view_config(route_name="gpx", http_cache=3600, permission="track.view")
def gpx(request):
    """Returns the actual GPX data from the stored track.

    :param request: The Pyramid request.
    :type request: pyramid.request.Request
    :return: The HTTP response.
    :rtype: pyramid.response.Response
    """
    track: Track = request.context
    try:
        manager = request.data_manager.open(track.id)
    except FileNotFoundError:
        LOGGER.error("Track exists in database, but not on disk: %d", track.id)
        return HTTPInternalServerError()
    if track.title:
        wanted_filename = f"{track.id} - {util.secure_filename(track.title)}.gpx"
    else:
        wanted_filename = f"{track.id}.gpx"
    content_disposition = f'attachment; filename="{wanted_filename}"'
    # We can be nice to the client if they support it, and deliver the gzipped
    # data straight. This saves decompression time on the server and saves a
    # lot of bandwidth.
    accepted = request.accept_encoding.acceptable_offers(["br", "gzip", "identity"])
    for encoding, _qvalue in accepted:
        if encoding == "br":
            response = FileResponse(
                str(manager.gpx_path()),
                request,
                content_type="application/gpx+xml",
                content_encoding="br",
            )
            break
        if encoding == "gzip":
            # gzip'ed GPX files are so much smaller than uncompressed ones, it
            # is worth re-compressing them for the client
            data = gzip.compress(manager.decompress_gpx())
            response = Response(data, content_type="application/gpx+xml", content_encoding="gzip")
            break
        if encoding == "identity":
            response = Response(manager.decompress_gpx(), content_type="application/gpx+xml")
            break
    else:
        return HTTPNotAcceptable("No data with acceptable encoding found")
    response.md5_etag()
    response.content_disposition = content_disposition
    return response


@view_config(route_name="invalidate-share", request_method="POST", permission="track.unshare")
def invalidate_share(request):
    """Endpoint to invalidate the share link.

    :param request: The Pyramid request.
    :type request: pyramid.request.Request
    :return: The HTTP response.
    :rtype: pyramid.response.Response
    """
    track = request.context
    track.link_secret = util.random_link_secret()
    return HTTPFound(request.route_url("details", track_id=track.id))


@view_config(route_name="delete-track", request_method="POST", permission="track.delete")
def delete_track(request):
    """Endpoint to delete the track.

    :param request: The Pyramid request.
    :type request: pyramid.request.Request
    :return: The HTTP response.
    :rtype: pyramid.response.Response
    """
    track = request.context
    track_id = track.id
    request.dbsession.delete(track)
    request.data_manager.purge(track_id)
    request.session.flash(request.localizer.translate(_("flash.track_deleted")))

    if request.config.hittekaart_autogenerate:
        request.redis.sadd("hittekaart:queue:high", request.identity.id)

    return HTTPFound(request.route_url("home"))


@view_config(route_name="badge", http_cache=3600)
def badge(request):
    """Returns the image data associated with a badge.

    :param request: The Pyramid request.
    :type request: pyramid.request.Request
    :return: The HTTP response.
    :rtype: pyramid.response.Response
    """
    response = Response(request.context.image)
    response.md5_etag()
    return response


@view_config(route_name="image", http_cache=3600, permission="track.view")
def image(request):
    """Returns the image data for the requested image.

    This ensures that the image is sent efficiently, by delegating to the WSGI
    file wrapper if possible.

    :param request: The Pyramid request.
    :type request: pyramid.request.Request
    :return: The HTTP response.
    :rtype: pyramid.response.Response
    """
    track = request.context
    try:
        image_path = request.data_manager.open(track.id).image_path(request.matchdict["image_name"])
    except FileNotFoundError:
        return HTTPNotFound()
    return FileResponse(str(image_path), request)


@view_config(route_name="add-comment", request_method="POST", permission="track.comment")
def add_comment(request):
    """Endpoint to add a comment to a track.

    :param request: The Pyramid request.
    :type request: pyramid.request.Request
    :return: The HTTP response.
    :rtype: pyramid.response.Response
    """
    track = request.context
    comment = models.Comment(
        track=track,
        author=request.identity,
        date=datetime.datetime.utcnow(),
        title=request.params["title"],
        text=request.params["comment"],
    )
    request.dbsession.add(comment)
    return HTTPFound(request.route_url("details", track_id=track.id))
