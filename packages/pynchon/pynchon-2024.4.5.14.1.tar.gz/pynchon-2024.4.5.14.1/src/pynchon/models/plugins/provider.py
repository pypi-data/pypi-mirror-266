""" pynchon.models.plugins.provider """

from fleks import tagging

from . import validators

from pynchon import api, cli, events  # noqa
from pynchon.util import lme, typing  # noqa

from .cli import CliPlugin  # noqa

LOGGER = lme.get_logger(__name__)


@tagging.tags(cli_label="Provider")
class Provider(CliPlugin):
    """A wrapper for context that other plugins can use"""

    cli_label = "Provider"
    cli_description = __doc__

    contribute_plan_apply = False
    priority = 2
    __class_validators__ = [
        validators.require_conf_key,
        # validators.warn_config_kls,
    ]
