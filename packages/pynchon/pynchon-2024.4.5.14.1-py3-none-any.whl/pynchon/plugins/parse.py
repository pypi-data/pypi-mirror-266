""" pynchon.plugins.parse
"""

import shimport

from pynchon import abcs, events, models  # noqa
from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)
config = shimport.lazy("pynchon.config")


class Parse(models.NameSpace):
    """
    Misc tools for parsing
    """

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "parse"

    name = "parse"
    cli_name = "parse"
    cli_aliases = ["parser"]
