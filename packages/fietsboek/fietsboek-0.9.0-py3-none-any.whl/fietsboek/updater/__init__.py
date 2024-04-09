"""Updating (data migration) logic for fietsboek."""

import datetime
import enum
import importlib.resources
import importlib.util
import logging
import random
import string
from pathlib import Path
from typing import Optional

import alembic.command
import alembic.config
import alembic.runtime
import jinja2
import pyramid.paster
import sqlalchemy

LOGGER = logging.getLogger(__name__)

TEMPLATE = """\
\"\"\"Revision upgrade script {{ update_id }}

Date created: {{ date }}
\"\"\"
from fietsboek.updater.script import UpdateScript

update_id = {{ "{!r}".format(update_id) }}
previous = [
{%- for prev in previous %}
    {{ "{!r}".format(prev) }},
{% endfor -%}
]
alembic_revision = {{ "{!r}".format(alembic_revision) }}


class Up(UpdateScript):
    def pre_alembic(self, config):
        pass

    def post_alembic(self, config):
        pass


class Down(UpdateScript):
    def pre_alembic(self, config):
        pass

    def post_alembic(self, config):
        pass
"""


class UpdateState(enum.Enum):
    """State of the applied updates.

    This represents a "summary" of the output that ``fietsupdate status``
    produces.
    """

    OKAY = enum.auto()
    """Everything is good, the data is up to date."""

    OUTDATED = enum.auto()
    """The data is outdated, the update process should be run."""

    TOO_NEW = enum.auto()
    """The data contains revisions that are not known to Fietsboek yet."""

    UNKNOWN = enum.auto()
    """The data version could not be determined."""


class Updater:
    """A class that implements the updating logic.

    This class is responsible for holding all of the update scripts and running
    them in the right order.
    """

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.settings = pyramid.paster.get_appsettings(config_path)
        self.alembic_config = alembic.config.Config(config_path)
        self.scripts: dict[str, "UpdateScript"] = {}
        self.forward_dependencies: dict[str, list[str]] = {}
        self.backward_dependencies: dict[str, list[str]] = {}

    @property
    def version_file(self) -> Path:
        """Returns the path to the version file.

        :return: The path to the data's version file.
        """
        data_dir = Path(self.settings["fietsboek.data_dir"])
        return data_dir / "VERSION"

    def load(self):
        """Load all update scripts into memory."""
        scripts = _load_update_scripts()
        for script in scripts:
            self.scripts[script.id] = script
        self.forward_dependencies = {script.id: script.previous for script in self.scripts.values()}
        # Ensure that each script has an entry
        self.backward_dependencies = {script.id: [] for script in self.scripts.values()}
        for script in self.scripts.values():
            down_alembic = None
            for prev_id in script.previous:
                self.backward_dependencies[prev_id].append(script.id)
                possible_alembic = self.scripts[prev_id].alembic_version
                if down_alembic is None:
                    down_alembic = possible_alembic
                elif down_alembic != possible_alembic:
                    LOGGER.error(
                        "Invalid update graph - two different down alembics for script %s",
                        script.id,
                    )
                    raise ValueError(f"Two alembic downgrades for {script.id}")
                down_alembic = possible_alembic
            script.down_alembic = down_alembic

    def exists(self, revision_id: str) -> bool:
        """Checks if the revision with the given ID exists.

        :param revision_id: ID of the revision to check.
        :return: True if the revision exists.
        """
        return revision_id in self.scripts

    def current_versions(self) -> list[str]:
        """Reads the current version of the data.

        :return: The versions, or an empty list if no versions are found.
        """
        try:
            versions = self.version_file.read_text(encoding="utf-8").split("\n")
            return [version.strip() for version in versions if version.strip()]
        except FileNotFoundError:
            return []

    def _transitive_versions(self) -> set[str]:
        versions = set()
        queue = self.current_versions()
        while queue:
            current = queue.pop()
            versions.add(current)
            if current in self.scripts:
                queue.extend(self.scripts[current].previous)
        return versions

    def _reverse_versions(self) -> set[str]:
        all_versions = set(script.id for script in self.scripts.values())
        return all_versions - self._transitive_versions()

    def stamp(self, versions: list[str]):
        """Stampts the given version into the version file.

        This does not run any updates, it simply updates the version information.

        :param version: The versions to stamp.
        """
        self.version_file.write_text("\n".join(versions), encoding="utf-8")

    def _pick_updates(
        self,
        wanted: str,
        applied: set[str],
        dependencies: dict[str, list[str]],
    ) -> set[str]:
        to_apply = set()
        queue = [wanted]
        while queue:
            current = queue.pop(0)
            if current in applied or current in to_apply:
                continue
            to_apply.add(current)
            queue.extend(dependencies[current])
        return to_apply

    def _make_schedule(self, wanted: set[str], dependencies: dict[str, list[str]]) -> list[str]:
        wanted = set(wanted)
        queue: list[str] = []
        while wanted:
            next_updates = {
                update
                for update in wanted
                if all(previous not in wanted for previous in dependencies[update])
            }
            queue.extend(next_updates)
            wanted -= next_updates
        return queue

    def _stamp_versions(self, old: list[str], new: list[str]):
        versions = self.current_versions()
        versions = [version for version in versions if version not in old]
        versions.extend(new)
        self.stamp(versions)

    def upgrade(self, target: str):
        """Run the tasks to upgrade to the given target.

        This ensures that all previous migrations are also run.

        :param target: The target revision.
        """
        # First, we figure out which tasks we have already applied and which
        # still need applying. This is pretty much a BFS over the current
        # version and its dependencies.
        applied_versions = self._transitive_versions()
        to_apply = self._pick_updates(target, applied_versions, self.forward_dependencies)
        # Second, we need to ensure that the tasks are applied in the right
        # order (topological sort)
        application_queue = self._make_schedule(to_apply, self.forward_dependencies)
        # Finally, we can run the updates
        LOGGER.debug("Planned update: %s", application_queue)
        for update in application_queue:
            script = self.scripts[update]
            script.upgrade(self.settings, self.alembic_config)
            self._stamp_versions(script.previous, [script.id])

    def downgrade(self, target: str):
        """Run the tasks to downgrade to the given target.

        This ensures that all succeeding down-migrations are also run.

        :param target: The target revision.
        """
        # This is basically the same as upgrade() but with the reverse
        # dependencies instead.
        applied_versions = self._reverse_versions()
        to_apply = self._pick_updates(target, applied_versions, self.backward_dependencies)
        to_apply -= {target}
        application_queue = self._make_schedule(to_apply, self.backward_dependencies)
        LOGGER.debug("Planned downgrade: %s", application_queue)
        for downgrade in application_queue:
            script = self.scripts[downgrade]
            script.downgrade(self.settings, self.alembic_config)
            self._stamp_versions([script.id], script.previous)

    def new_revision(self, revision_id: Optional[str] = None) -> str:
        """Creates a new revision with the current versions as dependencies and
        the current alembic version.

        :param revision_id: The revision ID to use. By default, a random string
            will be generated.
        :return: The filename of the revision file in the ``updater/``
            directory.
        """
        if not revision_id:
            revision_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=16))

        current_versions = self.current_versions()

        engine = sqlalchemy.create_engine(self.settings["sqlalchemy.url"])
        with engine.connect() as conn:
            context = alembic.runtime.migration.MigrationContext.configure(conn)
            current_alembic = context.get_current_heads()
        LOGGER.debug("Found alembic versions: %s", current_alembic)
        assert len(current_alembic) == 1
        current_alembic = current_alembic[0]  # type: ignore

        loader = jinja2.DictLoader({"revision.py": TEMPLATE})
        env = jinja2.Environment(loader=loader, autoescape=False)
        template = env.get_template("revision.py")
        date = datetime.datetime.now()
        revision = template.render(
            update_id=revision_id,
            previous=current_versions,
            alembic_revision=current_alembic,
            date=date,
        )

        filename = f"upd_{date:%Y%m%d}_{revision_id}.py"
        filepath = Path(__file__).parent / "scripts" / filename
        LOGGER.info("Writing new revision (%s) to %r", revision_id, filepath)
        with open(filepath, "x", encoding="utf-8") as fobj:
            fobj.write(revision)
        return filename

    def heads(self) -> list[str]:
        """Returns all "heads", that are the latest revisions.

        :return: The heads.
        """
        return [rev_id for (rev_id, deps) in self.backward_dependencies.items() if not deps]

    def has_applied(self, revision_id: str, backward: bool = False) -> bool:
        """Checks whether the given revision is applied.

        By default, this checks if a given update is applied, i.e. the current
        version is greater-or-equal to the given revision ID. If ``backward``
        is ``True``, we instead check if the current version is lower-or-equal
        to the given revision ID.

        Note that this function does not raise an error if the given revision
        ID cannot be found and instead simply returns ``False``. Use
        :meth:`exists` to check whether the revision actually exists.

        :param revision_id: The revision to check.
        :param backward: Whether to switch the comparison direction.
        :return: ``True`` if the current version at least matches the asked
            revision ID.
        """
        if not backward:
            return revision_id in self._transitive_versions()
        return revision_id in self._reverse_versions() | set(self.current_versions())

    def state(self) -> UpdateState:
        """Checks the update state of the instance.

        This returns a condensed version of what ``fietsupdate status``
        outputs.

        :return: The update state of the data.
        """
        state = UpdateState.OKAY
        current = self.current_versions()
        heads = self.heads()
        if current:
            for i in current:
                if not self.exists(i):
                    state = UpdateState.TOO_NEW
        else:
            return UpdateState.UNKNOWN
        updates = set(heads) - set(current)
        if updates:
            if state != UpdateState.OKAY:
                # We are both too new and too old, so something is pretty wrong
                return UpdateState.UNKNOWN
            return UpdateState.OUTDATED
        return state


class UpdateScript:
    """Represents an update script."""

    def __init__(self, source: str, name: str):
        self.name = name
        spec = importlib.util.spec_from_loader(f"{__name__}.{name}", None)
        self.module = importlib.util.module_from_spec(spec)  # type: ignore
        assert self.module
        exec(source, self.module.__dict__)  # pylint: disable=exec-used
        self.down_alembic: Optional[str] = None

    def __repr__(self):
        return f"<{__name__}.{self.__class__.__name__} name={self.name!r} id={self.id!r}>"

    @property
    def id(self) -> str:
        """Returns the ID of the update.

        :return: The id of the update
        """
        return self.module.update_id

    @property
    def previous(self) -> list[str]:
        """Returns all dependencies of the update.

        :return: The IDs of all dependencies of the update.
        """
        return getattr(self.module, "previous", [])

    @property
    def alembic_version(self) -> str:
        """Returns the alembic revisions of the update.

        :return: The needed alembic revisions.
        """
        return self.module.alembic_revision

    def upgrade(self, config: dict, alembic_config: alembic.config.Config):
        """Runs the upgrade migrations of this update script.

        This first runs the pre_alembic task, then the alembic migration, and
        finally the post_alembic task.

        Note that this does not ensure that all previous scripts have also been
        executed.

        :param config: The app configuration.
        :param alembic_config: The alembic config to use.
        """
        LOGGER.info("[up] Running pre-alembic task for %s", self.id)
        self.module.Up().pre_alembic(config)
        LOGGER.info("[up] Running alembic upgrade for %s to %s", self.id, self.alembic_version)
        alembic.command.upgrade(alembic_config, self.alembic_version)
        LOGGER.info("[up] Running post-alembic task for %s", self.id)
        self.module.Up().post_alembic(config)

    def downgrade(self, config: dict, alembic_config: alembic.config.Config):
        """Runs the downgrade migrations of this update script.

        See also :meth:`upgrade`.

        :param config: The app configuration.
        :param alembic_config: The alembic config to use.
        """
        LOGGER.info("[down] Running pre-alembic task for %s", self.id)
        self.module.Down().pre_alembic(config)
        if self.down_alembic:
            LOGGER.info("[down] Running alembic downgrade for %s to %s", self.id, self.down_alembic)
            alembic.command.downgrade(alembic_config, self.down_alembic)
            LOGGER.info("[down] Running post-alembic task for %s", self.id)
            self.module.Down().post_alembic(config)


def _filename_to_modname(name):
    if name.endswith(".py"):
        name = name[:-3]
    name = name.replace(".", "_")
    return name


def _load_update_scripts():
    """Loads all available import scripts."""
    files = importlib.resources.files(__name__) / "scripts"
    return [
        UpdateScript(file.read_text(encoding="utf-8"), _filename_to_modname(file.name))
        for file in files.iterdir()
        if file.name.startswith("upd_")
    ]
