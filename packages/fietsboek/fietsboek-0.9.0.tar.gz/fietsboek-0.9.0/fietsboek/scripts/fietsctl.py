"""Script to do maintenance work on a Fietsboek instance."""

# pylint: disable=too-many-arguments
import logging
from typing import Optional

import click
from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup
from pyramid.paster import bootstrap, setup_logging
from pyramid.scripting import AppEnvironment
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from .. import __VERSION__, hittekaart, models, util
from ..data import DataManager
from . import config_option

LOGGER = logging.getLogger("fietsctl")

EXIT_OKAY = 0
EXIT_FAILURE = 1

FG_USER_NAME = "yellow"
FG_USER_EMAIL = "yellow"
FG_USER_TAG = "red"
FG_SIZE = "cyan"
FG_TRACK_TITLE = "green"
FG_TRACK_SIZE = "bright_red"


def human_bool(value: bool) -> str:
    """Formats a boolean for CLI output.

    :param value: The value to format.
    :return: The string representing the bool.
    """
    return "yes" if value else "no"


def setup(config_path: str) -> AppEnvironment:
    """Sets up the logging and app environment for the scripts.

    This - for example - sets up a transaction manager in
    ``setup(...)["request"]``.

    :param config_path: Path to the configuration file.
    :return: The prepared environment.
    """
    setup_logging(config_path)
    return bootstrap(config_path)


@click.group(
    help=__doc__,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(package_name="fietsboek")
def cli():
    """CLI main entry point."""


@cli.group("user")
def cmd_user():
    """Management functions for user accounts."""


@cmd_user.command("add")
@config_option
@click.option("--email", help="Email address of the user.", prompt=True)
@click.option("--name", help="Name of the user.", prompt=True)
@click.option(
    "--password",
    help="password of the user",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
)
@click.option("--admin", help="Make the new user an admin.", is_flag=True)
@click.pass_context
def cmd_user_add(
    ctx: click.Context,
    config: str,
    email: str,
    name: str,
    password: str,
    admin: bool,
):
    """Create a new user.

    This user creation bypasses the "enable_account_registration" setting. It
    also immediately sets the new user's account to being verified.

    If email, name or password are not given as command line arguments, they
    will be asked for interactively.

    On success, the created user's unique ID will be printed.

    Note that this function does less input validation and should therefore be used with care!
    """
    env = setup(config)

    # The UNIQUE constraint only prevents identical emails from being inserted,
    # but does not take into account the case insensitivity. The least we
    # should do here to not brick log ins for the user is to check if the email
    # already exists.
    query = models.User.query_by_email(email)
    with env["request"].tm:
        result = env["request"].dbsession.execute(query).scalar_one_or_none()
        if result is not None:
            click.echo("Error: The given email already exists!", err=True)
            ctx.exit(EXIT_FAILURE)

    user = models.User(name=name, email=email, is_verified=True, is_admin=admin)
    user.set_password(password)
    user.roll_session_secret()

    with env["request"].tm:
        dbsession = env["request"].dbsession
        dbsession.add(user)
        dbsession.flush()
        user_id = user.id

    click.echo(user_id)


@cmd_user.command("del")
@config_option
@click.option("--force", "-f", help="Override the safety check.", is_flag=True)
@optgroup.group("User selection", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option("--id", "-i", "id_", help="Database ID of the user.", type=int)
@optgroup.option("--email", "-e", help="Email address of the user.")
@click.pass_context
def user_del(
    ctx: click.Context,
    config: str,
    force: bool,
    id_: Optional[int],
    email: Optional[str],
):
    """Delete a user.

    This command deletes the user's account as well as any tracks associated
    with it.

    This command is destructive and irreversibly deletes data.
    """
    env = setup(config)
    if id_ is not None:
        query = select(models.User).filter_by(id=id_)
    else:
        query = models.User.query_by_email(email)
    with env["request"].tm:
        dbsession = env["request"].dbsession
        user = dbsession.execute(query).scalar_one_or_none()
        if user is None:
            click.echo("Error: No such user found.", err=True)
            ctx.exit(EXIT_FAILURE)
        click.secho(user.name, fg=FG_USER_NAME)
        click.echo(user.email)
        if not force:
            if not click.confirm("Really delete this user?"):
                click.echo("Aborted by user.")
                ctx.exit(EXIT_FAILURE)
        dbsession.delete(user)
        click.echo("User deleted")


@cmd_user.command("list")
@config_option
def cmd_user_list(config: str):
    """Prints a listing of all user accounts.

    The format is:

        [av] {ID} - {email} - {name}

    with one line per user. The 'a' is added for admin accounts, the 'v' is added
    for verified users.
    """
    env = setup(config)
    with env["request"].tm:
        dbsession = env["request"].dbsession
        users = dbsession.execute(select(models.User).order_by(models.User.id)).scalars()
        for user in users:
            # pylint: disable=consider-using-f-string
            tag = "[{}{}]".format(
                "a" if user.is_admin else "-",
                "v" if user.is_verified else "-",
            )
            tag = click.style(tag, fg=FG_USER_TAG)
            user_email = click.style(user.email, fg=FG_USER_EMAIL)
            user_name = click.style(user.name, fg=FG_USER_NAME)
            click.echo(f"{tag} {user.id} - {user_email} - {user_name}")


@cmd_user.command("passwd")
@config_option
@click.option("--password", help="Password of the user.")
@optgroup.group("User selection", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option("--id", "-i", "id_", help="Database ID of the user,", type=int)
@optgroup.option("--email", "-e", help="Email address of the user.")
@click.pass_context
def cms_user_passwd(
    ctx: click.Context,
    config: str,
    password: Optional[str],
    id_: Optional[int],
    email: Optional[str],
):
    """Change the password of a user."""
    env = setup(config)
    if id_ is not None:
        query = select(models.User).filter_by(id=id_)
    else:
        query = models.User.query_by_email(email)
    with env["request"].tm:
        dbsession = env["request"].dbsession
        user = dbsession.execute(query).scalar_one_or_none()
        if user is None:
            click.echo("Error: No such user found.", err=True)
            ctx.exit(EXIT_FAILURE)
        if not password:
            password = click.prompt("Password", hide_input=True, confirmation_prompt=True)

        user.set_password(password)
        user_name = click.style(user.name, fg=FG_USER_NAME)
        user_email = click.style(user.email, fg=FG_USER_EMAIL)
        click.echo(f"Changed password of {user_name} ({user_email})")


@cmd_user.command("modify")
@config_option
@click.option("--admin/--no-admin", help="Make the user an admin.", default=None)
@click.option("--verified/--no-verified", help="Set the user verification status.", default=None)
@click.option("--set-email", help="Set the user's email address")
@optgroup.group("User selection", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option("--id", "-i", "id_", help="Database ID of the user.", type=int)
@optgroup.option("--email", "-e", help="Email address of the user.")
@click.pass_context
def cms_user_modify(
    ctx: click.Context,
    config: str,
    admin: Optional[bool],
    verified: Optional[bool],
    id_: Optional[int],
    email: Optional[str],
    set_email: Optional[str],
):
    """Modify a user."""
    env = setup(config)
    if id_ is not None:
        query = select(models.User).filter_by(id=id_)
    else:
        query = models.User.query_by_email(email)
    with env["request"].tm:
        dbsession = env["request"].dbsession
        user = dbsession.execute(query).scalar_one_or_none()
        if user is None:
            click.echo("Error: No such user found.", err=True)
            ctx.exit(EXIT_FAILURE)

        if admin is not None:
            user.is_admin = admin
        if verified is not None:
            user.is_verified = verified
        if set_email is not None:
            # Try to ensure that the email is unique. We do have the constraint
            # for that, but capitalization might screw us here.
            try:
                dbsession.execute(models.User.query_by_email(set_email)).scalar_one()
            except NoResultFound:
                user.email = set_email
            else:
                click.echo("Error: E-Mail already exists", err=True)
                ctx.exit(EXIT_FAILURE)

        user_name = click.style(user.name, fg=FG_USER_NAME)
        user_email = click.style(user.email, fg=FG_USER_EMAIL)
        click.echo(f"{user_name} - {user_email}")
        click.echo(f"Is admin: {human_bool(user.is_admin)}")
        click.echo(f"Is verified: {human_bool(user.is_verified)}")


@cmd_user.command("hittekaart")
@config_option
@click.option(
    "--mode",
    "modes",
    help="Heatmap type to generate.",
    type=click.Choice([mode.value for mode in hittekaart.Mode]),
    multiple=True,
    default=["heatmap"],
)
@click.option("--delete", help="Delete the specified heatmap.", is_flag=True)
@optgroup.group("User selection", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option("--id", "-i", "id_", help="Database ID of the user.", type=int)
@optgroup.option("--email", "-e", help="Email address of the user.")
@click.pass_context
def cmd_user_hittekaart(
    ctx: click.Context,
    config: str,
    modes: list[str],
    delete: bool,
    id_: Optional[int],
    email: Optional[str],
):
    """Generate heatmap for a user."""
    env = setup(config)
    modes = [hittekaart.Mode(mode) for mode in modes]

    if id_ is not None:
        query = select(models.User).filter_by(id=id_)
    else:
        query = models.User.query_by_email(email)

    exe_path = env["request"].config.hittekaart_bin
    threads = env["request"].config.hittekaart_threads
    with env["request"].tm:
        dbsession = env["request"].dbsession
        data_manager: DataManager = env["request"].data_manager
        user = dbsession.execute(query).scalar_one_or_none()
        if user is None:
            click.echo("Error: No such user found.", err=True)
            ctx.exit(EXIT_FAILURE)

        if delete:
            try:
                user_manager = data_manager.open_user(user.id)
            except FileNotFoundError:
                return
            if hittekaart.Mode.HEATMAP in modes:
                user_manager.heatmap_path().unlink(missing_ok=True)
            if hittekaart.Mode.TILEHUNTER in modes:
                user_manager.tilehunt_path().unlink(missing_ok=True)
            return

        click.echo(f"Generating overlay maps for {click.style(user.name, fg=FG_USER_NAME)}...")

        for mode in modes:
            hittekaart.generate_for(
                user, dbsession, data_manager, mode, exe_path=exe_path, threads=threads
            )
            click.echo(f"Generated {mode.value}")


@cli.group("track")
def cmd_track():
    """Management functions for tracks."""


@cmd_track.command("list")
@config_option
def cmd_track_list(config: str):
    """List all tracks that are present in the system."""
    env = setup(config)
    total_size = 0
    total_tracks = 0
    with env["request"].tm:
        dbsession = env["request"].dbsession
        data_manager: DataManager = env["request"].data_manager
        tracks = dbsession.execute(select(models.Track)).scalars()
        for track in tracks:
            total_tracks += 1
            try:
                track_size = data_manager.open(track.id).size()
            except FileNotFoundError:
                size = "---"
            else:
                total_size += track_size
                size = util.human_size(track_size)
            size = click.style(f"{size:>10}", fg=FG_TRACK_SIZE)
            owner_name = click.style(track.owner.name, fg=FG_USER_NAME)
            owner_email = click.style(track.owner.email, fg=FG_USER_EMAIL)
            track_title = click.style(track.title, fg=FG_TRACK_TITLE)
            click.echo(f"{track.id:>4} - {size} - {owner_name} <{owner_email}> - {track_title}")
    click.echo("-" * 80)
    click.echo(
        f"Total: {total_tracks} - {click.style(util.human_size(total_size), fg=FG_TRACK_SIZE)}"
    )


@cmd_track.command("del")
@config_option
@click.option("--force", "-f", help="Override the safety check.", is_flag=True)
@click.option("--id", "-i", "id_", help="Database ID of the track.", type=int, required=True)
@click.pass_context
def cmd_track_del(
    ctx: click.Context,
    config: str,
    force: bool,
    id_: Optional[int],
):
    """Delete a track.

    This command deletes the track as well as any images and comments
    associated with it.

    This command is destructive and irreversibly deletes data.
    """
    env = setup(config)
    query = select(models.Track).filter_by(id=id_)
    with env["request"].tm:
        dbsession = env["request"].dbsession
        track = dbsession.execute(query).scalar_one_or_none()
        if track is None:
            click.echo("Error: No such track found.", err=True)
            ctx.exit(EXIT_FAILURE)
        click.secho(track.title, fg=FG_TRACK_TITLE)
        if not force:
            if not click.confirm("Really delete this track?"):
                click.echo("Aborted by user.")
                ctx.exit(EXIT_FAILURE)
        try:
            data = env["request"].data_manager.open(track.id)
        except FileNotFoundError:
            LOGGER.warning("Data directory not found for track - ignoring")
        else:
            data.purge()
        dbsession.delete(track)
        click.echo("Track deleted")


@cli.command("maintenance-mode")
@config_option
@click.option("--disable", help="Disable the maintenance mode.", is_flag=True)
@click.argument("reason", required=False)
@click.pass_context
def cmd_maintenance_mode(ctx: click.Context, config: str, disable: bool, reason: Optional[str]):
    """Controls the maintenance mode.

    When REASON is given, enables the maintenance mode with the given text as
    reason.

    With neither --disable nor REASON given, just checks the state of the
    maintenance mode.
    """
    env = setup(config)
    data_manager = env["request"].data_manager
    if disable and reason:
        click.echo("Cannot enable and disable maintenance mode at the same time", err=True)
        ctx.exit(EXIT_FAILURE)
    elif not disable and not reason:
        maintenance = data_manager.maintenance_mode()
        if maintenance is None:
            click.echo("Maintenance mode is disabled")
        else:
            click.echo(f"Maintenance mode is enabled: {maintenance}")
    elif disable:
        (data_manager.data_dir / "MAINTENANCE").unlink()
    else:
        (data_manager.data_dir / "MAINTENANCE").write_text(reason, encoding="utf-8")


@cli.command("version")
def cmd_version():
    """Show the installed fietsboek version."""
    name = __name__.split(".", 1)[0]
    print(f"{name} {__VERSION__}")


__all__ = ["cli"]
