"""Interface to the hittekaart_ application to generate heatmaps.

.. _hittekaart: https://gitlab.com/dunj3/hittekaart
"""

import enum
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import aliased
from sqlalchemy.orm.session import Session

from . import models
from .data import DataManager
from .models.track import TrackType

LOGGER = logging.getLogger(__name__)


class Mode(enum.Enum):
    """Heatmap generation mode.

    This enum represents the different types of overlay maps that
    ``hittekaart`` can generate.
    """

    HEATMAP = "heatmap"
    TILEHUNTER = "tilehunter"


def generate(
    output: Path,
    mode: Mode,
    input_files: list[Path],
    *,
    exe_path: Optional[Path] = None,
    threads: int = 0,
):
    """Calls hittekaart with the given arguments.

    :param output: Output filename. Note that this function always uses the
        sqlite output mode.
    :param mode: What to generate.
    :param input_files: List of paths to the input files.
    :param exe_path: Path to the hittekaart binary. If not given,
        ``hittekaart`` is searched in the path.
    :param threads: Number of threads that ``hittekaart`` should use. Defaults
        to 0, which uses all available cores.
    """
    if not input_files:
        return
    # There are two reasons why we do the tempfile dance:
    # 1. hittekaart refuses to overwrite existing files
    # 2. This way we can (hope for?) an atomic move (at least if temporary file
    #    is on the same filesystem). In the future, we might want to enforce
    #    this, but for now, it's alright.
    with tempfile.TemporaryDirectory() as tempdir:
        tmpfile = Path(tempdir) / "hittekaart.sqlite"
        binary = str(exe_path) if exe_path else "hittekaart"
        cmdline = [
            binary,
            "--sqlite",
            "-o",
            str(tmpfile),
            "-m",
            mode.value,
            "-t",
            str(threads),
            "--",
        ]
        cmdline.extend(map(str, input_files))
        LOGGER.debug("Running %r", cmdline)
        subprocess.run(cmdline, check=True, stdout=subprocess.DEVNULL)

        LOGGER.debug("Moving temporary file")
        shutil.move(tmpfile, output)


def generate_for(
    user: models.User,
    dbsession: Session,
    data_manager: DataManager,
    mode: Mode,
    *,
    exe_path: Optional[Path] = None,
    threads: int = 0,
):
    """Uses :meth:`generate` to generate a heatmap for the given user.

    This function automatically retrieves the user's tracks from the database
    and passes them to ``hittekaart``.

    The output is saved in the user's data directory using the
    ``data_manager``.

    :raises ValueError: If the user does not have an ID and thus the map cannot
        be saved.
    :param user: The user for which to generate the map.
    :param dbsession: The database session.
    :param data_manager: The data manager.
    :param mode: The mode of the heatmap.
    :param exe_path: See :meth:`generate`.
    :param threads: See :meth:`generate`.
    """
    # pylint: disable=too-many-arguments
    if user.id is None:
        raise ValueError("User has no ID, cannot generate a heatmap yet")

    query = user.all_tracks_query()
    query = select(aliased(models.Track, query)).where(query.c.type == TrackType.ORGANIC)
    input_paths = []
    for track in dbsession.execute(query).scalars():
        if track.id is None:
            continue
        path = data_manager.open(track.id).gpx_path()
        input_paths.append(path)

    if not input_paths:
        return

    try:
        user_dir = data_manager.initialize_user(user.id)
    except FileExistsError:
        user_dir = data_manager.open_user(user.id)

    output_paths = {
        Mode.HEATMAP: user_dir.heatmap_path(),
        Mode.TILEHUNTER: user_dir.tilehunt_path(),
    }

    generate(output_paths[mode], mode, input_paths, exe_path=exe_path, threads=threads)


__all__ = ["Mode", "generate", "generate_for"]
