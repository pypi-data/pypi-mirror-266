"""High-level actions.

This module implements the basic logic for high level intents such as "add a
track", "delete a track", ... It combines the low-level APIs of the ORM and the
data manager, and provides functions that can be used by the views, the API and
the test functions.
"""

import datetime
import logging
import re
from typing import List, Optional

import brotli
import gpxpy
from pyramid.i18n import TranslationString as _
from pyramid.request import Request
from sqlalchemy import select
from sqlalchemy.orm.session import Session

from . import email, models
from . import transformers as mod_transformers
from . import util
from .data import DataManager, TrackDataDir
from .models.track import TrackType, Visibility
from .models.user import TokenType

LOGGER = logging.getLogger(__name__)


def add_track(
    dbsession: Session,
    data_manager: DataManager,
    owner: models.User,
    title: str,
    date: datetime.datetime,
    visibility: Visibility,
    track_type: TrackType,
    description: str,
    badges: List[models.Badge],
    tagged_people: List[models.User],
    tags: List[str],
    transformers: list[mod_transformers.Transformer],
    gpx_data: bytes,
) -> models.Track:
    """Adds a track to the database.

    Note that this function does not do any authorization checking, and as
    such, expects the caller to ensure that everything is in order.

    Most of the parameters correspond to the attributes of
    :class:`~fietsboek.models.track.Track` objects.

    :param dbsession: The database session.
    :param data_manager: The data manager.
    :param owner: The owner of the track.
    :param title: Title of the track.
    :param date: Date of the track, should be timezone-aware.
    :param visibility: Track visibility.
    :param track_type: Type of the track.
    :param description: Track description.
    :param badges: Badges to attach to the track.
    :param tagged_people: List of people to tag.
    :param tags: List of text tags for the track.
    :param transformers: List of :class:`~fietsboek.transformers.Transformer` to apply.
    :param gpx_data: Actual GPX data (uncompressed, straight from the source).
    :return: The track object that has been inserted into the database. Useful
        for its ``id`` attribute.
    """
    # pylint: disable=too-many-arguments,too-many-locals
    LOGGER.debug("Inserting new track...")
    track = models.Track(
        owner=owner,
        title=title,
        visibility=visibility,
        type=track_type,
        description=description,
        badges=badges,
        link_secret=util.random_link_secret(),
        tagged_people=tagged_people,
    )
    track.date = date
    track.sync_tags(tags)
    dbsession.add(track)
    dbsession.flush()

    # Save the GPX data
    LOGGER.debug("Creating a new data folder for %d", track.id)
    assert track.id is not None
    with data_manager.initialize(track.id) as manager:
        LOGGER.debug("Saving GPX to %s", manager.gpx_path())
        manager.compress_gpx(gpx_data)
        manager.backup()

        gpx = gpxpy.parse(gpx_data)
        for transformer in transformers:
            LOGGER.debug("Running %s with %r", transformer, transformer.parameters)
            transformer.execute(gpx)
        track.transformers = [
            [tfm.identifier(), tfm.parameters.model_dump()] for tfm in transformers
        ]

        # Best time to build the cache is right after the upload, but *after* the
        # transformers have been applied!
        track.ensure_cache(gpx)
        dbsession.add(track.cache)

        manager.engrave_metadata(
            title=track.title,
            description=track.description,
            author_name=track.owner.name,
            time=track.date,
            gpx=gpx,
        )

    return track


def edit_images(request: Request, track: models.Track, *, manager: Optional[TrackDataDir] = None):
    """Edit the images according to the given request.

    This deletes and adds images and image descriptions as needed, based on the
    ``image[...]`` and ``image-description[...]`` fields.

    :param request: The request.
    :param track: The track to edit.
    :param manager: The track's data manager. If not given, it will
        automatically be opened from the request.
    """
    LOGGER.debug("Editing images for %d", track.id)
    manager = manager if manager else request.data_manager.open(track.id)

    # Delete requested images
    for image in request.params.getall("delete-image[]"):
        manager.delete_image(image)
        image_meta = request.dbsession.execute(
            select(models.ImageMetadata).filter_by(track_id=track.id, image_name=image)
        ).scalar_one_or_none()
        LOGGER.debug("Deleted image %s %s (metadata: %s)", track.id, image, image_meta)
        if image_meta:
            request.dbsession.delete(image_meta)

    # Add new images, but only if the setting allows for it
    set_descriptions = set()
    for param_name, image in request.params.items():
        match = re.match("image\\[(\\d+)\\]$", param_name)
        if not match:
            continue
        # Sent for the multi input
        if image == b"":
            continue

        upload_id = match.group(1)

        # If the uploads are disabled, we still add the image to
        # set_descriptions so that later down below we don't try to set the
        # description for it.
        if not request.config.enable_image_uploads:
            set_descriptions.add(upload_id)
            LOGGER.debug("Tried to upload image but uploads are disabled (track %s)", track.id)
            continue

        image_name = manager.add_image(image.file, image.filename)
        image_meta = models.ImageMetadata(track=track, image_name=image_name)
        image_meta.description = request.params.get(f"image-description[{upload_id}]", "")
        request.dbsession.add(image_meta)
        LOGGER.debug("Uploaded image %s %s", track.id, image_name)
        set_descriptions.add(upload_id)

    images = manager.images()
    # Set image descriptions
    for param_name, description in request.params.items():
        match = re.match("image-description\\[(.+)\\]$", param_name)
        if not match:
            continue
        image_id = match.group(1)
        # Descriptions that we already set while adding new images can be
        # ignored
        if image_id in set_descriptions:
            continue
        # Did someone give us a wrong ID?!
        if image_id not in images:
            LOGGER.info("Got a ghost image description for track %s: %s", track.id, image_id)
            continue
        image_meta = models.ImageMetadata.get_or_create(request.dbsession, track, image_id)
        image_meta.description = description
        request.dbsession.add(image_meta)


def execute_transformers(request: Request, track: models.Track) -> Optional[gpxpy.gpx.GPX]:
    """Execute the transformers for the given track.

    Note that this function "short circuits" if the saved transformer settings
    already match the settings given in the request.

    This function saves the modified data, but does also return it in case you
    need to do further processing (unless no transformations have taken place).

    :param request: The request.
    :param track: The track.
    :return: The transformed track.
    """
    # pylint: disable=too-many-locals
    LOGGER.debug("Executing transformers for %d", track.id)

    settings = mod_transformers.extract_from_request(request)

    serialized = [[tfm.identifier(), tfm.parameters.model_dump()] for tfm in settings]
    if serialized == track.transformers:
        LOGGER.debug("Applied transformations match on %d, skipping", track.id)
        return None

    # We always start with the backup, that way we don't get "deepfried GPX"
    # files by having the same filters run multiple times on the same input.
    # They are not idempotent after all.
    manager = request.data_manager.open(track.id)
    gpx_bytes = manager.backup_path().read_bytes()
    gpx_bytes = brotli.decompress(gpx_bytes)
    gpx = gpxpy.parse(gpx_bytes)

    for transformer in settings:
        LOGGER.debug("Running %s with %r", transformer, transformer.parameters)
        transformer.execute(gpx)

    LOGGER.debug("Saving transformed file for %d", track.id)
    manager.compress_gpx(util.encode_gpx(gpx))

    LOGGER.debug("Saving new transformers on %d", track.id)
    track.transformers = serialized

    LOGGER.debug("Rebuilding cache for %d", track.id)
    request.dbsession.delete(track.cache)
    track.cache = None
    track.ensure_cache(gpx)
    request.dbsession.add(track.cache)
    return gpx


def send_verification_token(request: Request, user: models.User):
    """Creates a verification token and sends it to the user.

    If no verification token exists yet, a fresh one is created.

    If a token already exists, a fresh one is still created. The old token
    stays valid until its expiry date.

    Note that this function does not provide the user with feedback other than
    the email. You may want to show a flash message or similar to show that
    something has happened.

    :param request: The request.
    :param user: The user who to generate a verification token for.
    """
    # Some of this code appears in the password reset form as well, but that's
    # fine for now.
    # pylint: disable=duplicate-code
    token = models.Token.generate(user, TokenType.VERIFY_EMAIL)
    request.dbsession.add(token)

    if user.email is None:
        LOGGER.error("Trying to send an email to %r (id=%d), but no email is set", user, user.id)
        return

    message = email.prepare_message(
        request.config.email_from,
        user.email,
        request.localizer.translate(_("email.verify_mail.subject")),
    )
    message.set_content(
        request.localizer.translate(_("email.verify.text")).format(
            request.route_url("use-token", uuid=token.uuid)
        )
    )
    email.send_message(
        request.config.email_smtp_url,
        request.config.email_username,
        request.config.email_password.get_secret_value(),
        message,
    )
