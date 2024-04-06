""" pynchon.util.text.render CLI
"""

from fleks.cli import click, options  # noqa
from fleks.util.tagging import tags

from pynchon.cli import common

from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)

import shimport

entry = common.entry_for(__name__)


tmp = (
    shimport.wrapper("pynchon.util.text.render")
    .prune(
        filter_instances=typing.FunctionType,
        filter_module_origin="pynchon.util.text.render",
    )
    .map_ns(
        lambda _name, fxn: [fxn, tags[fxn].get("click_aliases", []) + [fxn.__name__]]
    )
    .starmap(
        lambda fxn, aliases: [
            entry.command(
                name=alias.replace("_", "-"),
                help=(
                    fxn.__doc__
                    if alias == fxn.__name__
                    else f"Alias for `{fxn.__name__}`"
                ),
            )(fxn)
            for alias in aliases
        ]
    )
)

if __name__ == "__main__":
    entry()
