"""Data manager for fietsboek.

Data are objects that belong to a track (such as images), but are not stored in
the database itself. This module makes access to such data objects easier.
"""

# We don't have onexc yet in all supported versions, so let's ignore the
# deprecation for now and stick with onerror:
# pylint: disable=deprecated-argument
import datetime
import logging
import os
import random
import shutil
import string
import uuid
from pathlib import Path
from typing import BinaryIO, List, Literal, Optional

import brotli
import gpxpy
from filelock import FileLock

from . import util

LOGGER = logging.getLogger(__name__)


def generate_filename(filename: Optional[str]) -> str:
    """Generates a safe-to-use filename for uploads.

    If possible, tries to keep parts of the original filename intact, such as
    the extension.

    :param filename: The original filename.
    :return: The generated filename.
    """
    if filename:
        good_name = util.secure_filename(filename)
        if good_name:
            random_prefix = "".join(random.choice(string.ascii_lowercase) for _ in range(5))
            return f"{random_prefix}_{good_name}"

    return str(uuid.uuid4())


class DataManager:
    """Data manager.

    The data manager is usually provided as ``request.data_manager`` and can be
    used to access track's images and other on-disk data.

    :ivar data_dir: Path to the data folder.
    """

    def __init__(self, data_dir: Path):
        self.data_dir: Path = data_dir

    def _track_data_dir(self, track_id):
        return self.data_dir / "tracks" / str(track_id)

    def _user_data_dir(self, user_id):
        return self.data_dir / "users" / str(user_id)

    def maintenance_mode(self) -> Optional[str]:
        """Checks whether the maintenance mode is enabled.

        If maintenance mode is enabled, returns the reason given.

        If maintenance mode is disabled, returns ``None``.

        :return: The maintenance mode state.
        """
        try:
            return (self.data_dir / "MAINTENANCE").read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

    def initialize(self, track_id: int) -> "TrackDataDir":
        """Creates the data directory for a track.

        :raises FileExistsError: If the directory already exists.
        :param track_id: ID of the track.
        :return: The manager that can be used to manage this track's data.
        """
        path = self._track_data_dir(track_id)
        path.mkdir(parents=True)
        return TrackDataDir(track_id, path, journal=True, is_fresh=True)

    def initialize_user(self, user_id: int) -> "UserDataDir":
        """Creates the data directory for a user.

        :raises FileExistsError: If the directory already exists.
        :param user_id: ID of the user.
        :return: The manager that can be used to manage this user's data.
        """
        path = self._user_data_dir(user_id)
        path.mkdir(parents=True)
        return UserDataDir(user_id, path)

    def purge(self, track_id: int):
        """Forcefully purges all data from the given track.

        This function logs errors but raises no exception, as such it can
        always be used to clean up after a track.
        """
        TrackDataDir(track_id, self._track_data_dir(track_id)).purge()

    def open(self, track_id: int) -> "TrackDataDir":
        """Opens a track's data directory.

        :raises FileNotFoundError: If the track directory does not exist.
        :param track_id: ID of the track.
        :return: The manager that can be used to manage this track's data.
        """
        path = self._track_data_dir(track_id)
        if not path.is_dir():
            raise FileNotFoundError(f"The path {path} is not a directory") from None
        return TrackDataDir(track_id, path)

    def open_user(self, user_id: int) -> "UserDataDir":
        """Opens a user's data directory.

        :raises FileNotFoundError: If the user directory does not exist.
        :param user_id: ID of the user.
        :return: The manager that can be used to manage this user's data.
        """
        path = self._user_data_dir(user_id)
        if not path.is_dir():
            raise FileNotFoundError(f"The path {path} is not a directory") from None
        return UserDataDir(user_id, path)


class TrackDataDir:
    """Manager for a single track's data.

    If initialized with ``journal = True``, then you can use :meth:`rollback`
    to roll back the changes in case of an error. In case of no error, use
    :meth:`commit` to commit the changes. If you don't want the "journalling"
    semantics, use ``journal = False``.
    """

    def __init__(self, track_id: int, path: Path, *, journal: bool = False, is_fresh: bool = False):
        self.track_id: int = track_id
        self.path: Path = path
        self.journal: Optional[list] = [] if journal else None
        self.is_fresh = is_fresh

    def __enter__(self) -> "TrackDataDir":
        if self.journal is None:
            self.journal = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> Literal[False]:
        if exc_type is None and exc_val is None and exc_tb is None:
            self.commit()
        else:
            self.rollback()
        return False

    def rollback(self):
        """Rolls back the journal, e.g. in case of error.

        :raises ValueError: If the data directory was opened without the
            journal, this raises :exc:`ValueError`.
        """
        LOGGER.debug("Rolling back state of %s", self.path)

        if self.journal is None:
            raise ValueError("Rollback on a non-journalling data directory")

        if self.is_fresh:
            # Shortcut if the directory is fresh, simply remove everything
            self.journal = None
            self.purge()
            return

        for action, *rest in reversed(self.journal):
            if action == "purge":
                (new_name,) = rest
                shutil.move(new_name, self.path)
            elif action == "compress_gpx":
                (old_data,) = rest
                if old_data is None:
                    self.gpx_path().unlink()
                else:
                    self.gpx_path().write_bytes(old_data)
            elif action == "add_image":
                (image_path,) = rest
                image_path.unlink()
            elif action == "delete_image":
                path, data = rest
                path.write_bytes(data)

        self.journal = None

    def commit(self):
        """Commits all changed and deletes the journal.

        Note that this function will do nothing if the journal is disabled,
        meaning it can always be called.
        """
        LOGGER.debug("Committing journal for %s", self.path)

        if self.journal is None:
            return

        for action, *rest in reversed(self.journal):
            if action == "purge":
                (new_name,) = rest
                shutil.rmtree(new_name, ignore_errors=False, onerror=self._log_deletion_error)
            elif action == "compress_gpx":
                # Nothing to do here, the new data is already on the disk
                pass
            elif action == "add_image":
                # Nothing to do here, the image is already saved
                pass
            elif action == "delete_image":
                # Again, nothing to do here, we simply discard the in-memory image data
                pass

        self.journal = None

    def lock(self) -> FileLock:
        """Returns a FileLock that can be used to lock access to the track's
        data.

        :return: The lock responsible for locking this data directory.
        """
        return FileLock(self.path / "lock")

    @staticmethod
    def _log_deletion_error(_, path, exc_info):
        LOGGER.warning("Failed to remove %s", path, exc_info=exc_info)

    def purge(self):
        """Purge all data pertaining to the track.

        This function logs errors but raises no exception, as such it can
        always be used to clean up after a track.
        """
        if self.journal is None:
            if self.path.is_dir():
                shutil.rmtree(self.path, ignore_errors=False, onerror=self._log_deletion_error)
        else:
            new_name = self.path.with_name("trash-" + self.path.name)
            shutil.move(self.path, new_name)
            self.journal.append(("purge", new_name))

    def size(self) -> int:
        """Returns the size of the data that this track entails.

        :return: The size of bytes that this track consumes.
        """
        size = 0
        for root, _, files in os.walk(self.path):
            size += sum(os.path.getsize(os.path.join(root, fname)) for fname in files)
        return size

    def gpx_path(self) -> Path:
        """Returns the path of the GPX file.

        This file contains the (brotli) compressed GPX data.

        :return: The path where the GPX is supposed to be.
        """
        return self.path / "track.gpx.br"

    def compress_gpx(self, data: bytes, quality: int = 4):
        """Set the GPX content to the compressed form of data.

        If you want to write compressed data directly, use :meth:`gpx_path` to
        get the path of the GPX file.

        :param data: The GPX data (uncompressed).
        :param quality: Compression quality, from 0 to 11 - 11 is highest
            quality but slowest compression speed.
        """
        if self.journal is not None:
            # First, we check if we already saved an old state of the GPX data
            for action, *_ in self.journal:
                if action == "compress_gpx":
                    break
            else:
                # We did not save a state yet
                old_data = None if not self.gpx_path().is_file() else self.gpx_path().read_bytes()
                self.journal.append(("compress_gpx", old_data))

        compressed = brotli.compress(data, quality=quality)
        self.gpx_path().write_bytes(compressed)

    def decompress_gpx(self) -> bytes:
        """Returns the GPX bytes decompressed.

        :return: The saved GPX file, decompressed.
        """
        return brotli.decompress(self.gpx_path().read_bytes())

    def engrave_metadata(
        self,
        title: Optional[str],
        description: Optional[str],
        author_name: Optional[str],
        time: Optional[datetime.datetime],
        *,
        gpx: Optional[gpxpy.gpx.GPX] = None,
    ):
        """Engrave the given metadata into the GPX file.

        Note that this will overwrite all existing metadata in the given
        fields.

        If ``None`` is given, it will erase that specific part of the metadata.

        :param title: The title of the track.
        :param description: The description of the track.
        :param creator: Name of the track's creator.
        :param time: Time of the track.
        :param gpx: The pre-parsed GPX track, to save time if it is already parsed.
        """
        # pylint: disable=too-many-arguments
        if gpx is None:
            gpx = gpxpy.parse(self.decompress_gpx())
        # First we delete the existing metadata
        for track in gpx.tracks:
            track.name = None
            track.description = None

        # Now we add the new metadata
        gpx.author_name = author_name
        gpx.name = title
        gpx.description = description
        gpx.time = time

        self.compress_gpx(util.encode_gpx(gpx))

    def backup(self):
        """Create a backup of the GPX file."""
        shutil.copy(self.gpx_path(), self.backup_path())

    def backup_path(self) -> Path:
        """Path of the GPX backup file.

        :return: The path of the backup file.
        """
        return self.path / "track.bck.gpx.br"

    def images(self) -> List[str]:
        """Returns a list of images that belong to the track.

        :param track_id: Numerical ID of the track.
        :return: A list of image IDs.
        """
        image_dir = self.path / "images"
        if not image_dir.exists():
            return []
        images = [image.name for image in image_dir.iterdir()]
        return images

    def image_path(self, image_id: str) -> Path:
        """Returns a path to a saved image.

        :raises FileNotFoundError: If the given image could not be found.
        :param image_id: ID of the image.
        :return: A path pointing to the requested image.
        """
        image = self.path / "images" / util.secure_filename(image_id)
        if not image.exists():
            raise FileNotFoundError("The requested image does not exist")
        return image

    def add_image(self, image: BinaryIO, filename: Optional[str] = None) -> str:
        """Saves an image to a track.

        :param image: The image, as a file-like object to read from.
        :param filename: The image's original filename.
        :return: The ID of the saved image.
        """
        image_dir = self.path / "images"
        image_dir.mkdir(parents=True, exist_ok=True)

        filename = generate_filename(filename)
        path = image_dir / filename
        with open(path, "wb") as fobj:
            shutil.copyfileobj(image, fobj)

        if self.journal is not None:
            self.journal.append(("add_image", path))

        return filename

    def delete_image(self, image_id: str):
        """Deletes an image from a track.

        :raises FileNotFoundError: If the given image could not be found.
        :param image_id: ID of the image.
        """
        # Be sure to not delete anything else than the image file
        image_id = util.secure_filename(image_id)
        if "/" in image_id or "\\" in image_id:
            return
        path = self.image_path(image_id)

        if self.journal is not None:
            self.journal.append(("delete_image", path, path.read_bytes()))

        path.unlink()


class UserDataDir:
    """Manager for a single user's data."""

    def __init__(self, user_id: int, path: Path):
        self.user_id = user_id
        self.path = path

    def heatmap_path(self) -> Path:
        """Returns the path for the heatmap tile file.

        :return: The path of the heatmap SQLite databse.
        """
        return self.path / "heatmap.sqlite"

    def tilehunt_path(self) -> Path:
        """Returns the path for the tilehunt tile file.

        :return: The path of the tilehunt SQLite database.
        """
        return self.path / "tilehunt.sqlite"
