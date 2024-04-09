"""Various command line scripts to interact with the fietsboek installation."""

from typing import Any, Optional

import click
from click.core import ParameterSource


class ConfigOption(click.Path):
    """Special :class:`~click.Path` subclass to print a more helpful error
    message.

    This class recognizes if the config option is not given and prints a hint
    if the file does not exist in this case.
    """

    def __init__(self):
        super().__init__(exists=True, dir_okay=False)

    def convert(
        self,
        value: Any,
        param: Optional[click.Parameter],
        ctx: Optional[click.Context],
    ) -> Any:
        try:
            return super().convert(value, param, ctx)
        except click.BadParameter as exc:
            if param is not None and param.name is not None and ctx is not None:
                source = ctx.get_parameter_source(param.name)
                if source == ParameterSource.DEFAULT:
                    exc.message += (
                        f"\n\nHint: {value!r} is the default, "
                        "try specifying a configuration file explicitely."
                    )
            raise exc


# We keep this as a separate option that is added to each subcommand as Click
# (unlike argparse) cannot handle "--help" without the required arguments of
# the parent (so "fietsupdate update --help" would error out)
# See also
# https://github.com/pallets/click/issues/295
# https://github.com/pallets/click/issues/814
config_option = click.option(
    "-c",
    "--config",
    type=ConfigOption(),
    required=True,
    default="fietsboek.ini",
    help="Path to the Fietsboek configuration file",
)


__all__ = ["config_option"]
