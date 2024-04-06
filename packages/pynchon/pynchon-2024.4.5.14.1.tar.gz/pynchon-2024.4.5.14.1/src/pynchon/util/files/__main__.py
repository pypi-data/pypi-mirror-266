""" pynchon.util.files CLI
"""

import shimport
from fleks.util.tagging import tags

from pynchon.cli import common

from fleks.cli import click, options  # noqa

from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


entry = common.entry_for(__name__)


(
    shimport.wrapper("pynchon.util.files")
    .prune(
        filter_instances=typing.FunctionType,
        filter_module_origin="pynchon.util.files",
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
