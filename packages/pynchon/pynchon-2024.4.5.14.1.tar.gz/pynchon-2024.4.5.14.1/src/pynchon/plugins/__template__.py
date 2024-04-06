""" pynchon.plugins.__template__
"""

from pynchon import abcs, cli, events, models  # noqa
from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


class PluginTemplate(models.Provider):
    """PluginTemplate"""

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "template"

    name = "template"
    cli_name = "template"
    cli_label = "Meta"
