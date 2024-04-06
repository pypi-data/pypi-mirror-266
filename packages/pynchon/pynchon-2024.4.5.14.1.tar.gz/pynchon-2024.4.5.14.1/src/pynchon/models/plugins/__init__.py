""" pynchon.models.plugins
"""

import typing

import fleks
from fleks import tagging

from pynchon import abcs, api, cli, events  # noqa
from pynchon.util import lme, typing  # noqa

from . import validators  # noqa
from .cli import CliPlugin  # noqa
from .docker import DiagramTool, DockerWrapper  # noqa
from .provider import Provider  # noqa
from .pynchon import PynchonPlugin  # noqa
from .tool import AutomationTool, ToolPlugin  # noqa

LOGGER = lme.get_logger(__name__)
classproperty = fleks.util.typing.classproperty


class BasePlugin(CliPlugin):
    """The default plugin-type most new plugins will use"""

    priority = 10

    @property
    def working_dir(self):
        """ """
        return abcs.Path(".").absolute()

    @property
    def exclude_patterns(self):
        """
        ensures that `exclude_patterns` for any plugin should honor the global-excludes
        """
        from pynchon.plugins import util as plugin_util

        globals = plugin_util.get_plugin("globals").get_current_config()
        global_ex = globals["exclude_patterns"]
        my_ex = self.get("exclude_patterns", [])
        return list(set(global_ex + my_ex + ["**/pynchon/templates/includes/**"]))


@tagging.tags(cli_label="NameSpaces")
class NameSpace(CliPlugin):
    """Collects functionality from other plugins under a single namespace"""

    cli_label = "NameSpace"
    contribute_plan_apply = False
    cli_description = __doc__
    priority = 1
