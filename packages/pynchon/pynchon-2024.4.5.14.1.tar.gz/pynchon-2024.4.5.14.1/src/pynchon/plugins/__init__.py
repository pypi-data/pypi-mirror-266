""" pynchon.plugins
"""

import collections

import fleks
import shimport

from pynchon import config, constants, events  # noqa
from pynchon.util import lme, typing  # noqa

from .util import get_plugin, get_plugin_obj  # noqa

LOGGER = lme.get_logger(__name__)
mod_wrap = shimport.wrap(__name__, import_children="**/*.py")
registry = {
    **mod_wrap.prune(
        exclude_names="git".split(),  # FIXME: hack
        types_in=[fleks.Plugin],
        filter_vals=[
            lambda val: val.name in config.PLUGINS + constants.PLUGINS,
        ],
    ).namespace
}
registry = registry.items()
registry = collections.OrderedDict(sorted(registry, key=lambda x: x[1].priority))
registry = collections.OrderedDict(
    [
        [plugin_kls.name, dict(obj=None, kls=plugin_kls)]
        for k, plugin_kls in registry.items()
    ]
)
registry["core"]["obj"] = registry["core"]["kls"]()
# registry = collections.OrderedDict(sorted(registry.items(), key=lambda x: x[1]['kls'].priority))
events.lifecycle.send(__name__, msg="Finished creating plugin registry")
