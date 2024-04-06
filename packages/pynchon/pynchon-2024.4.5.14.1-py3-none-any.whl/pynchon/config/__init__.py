""" pynchon.config
"""

# from pynchon import abcs
from fleks.plugin import Meta

from pynchon.api import render
from pynchon.app import app
from pynchon.core import Config as CoreConfig
from pynchon.util import lme  # typing

from pynchon.plugins.git import GitConfig  # noqa

from .util import config_folders  # noqa
from .util import finalize  # noqa
from .util import get_config_files  # noqa
from .util import load_config_from_files  # noqa

LOGGER = lme.get_logger(__name__)
events = app.events

# FIXME: abstract into phases inside pynchon.app
msg = "Loading raw-config from OS.."
events.lifecycle.send(__name__, stage=msg)
git = GIT = GitConfig()
# import IPython; IPython.embed()
msg = "Building raw-config from files.."
events.lifecycle.send(
    __name__,
    msg=msg,
    stage=msg,
)
CONFIG_FILES = []
MERGED_CONFIG_FILES = {}
for cfg_src, config in load_config_from_files().items():
    MERGED_CONFIG_FILES = {**MERGED_CONFIG_FILES, **config}
    config and CONFIG_FILES.append(cfg_src)

# NB: this content is potentially templated
msg = "Building plugins-list.."
events.lifecycle.send(
    __name__,
    msg=msg,
    stage=msg,
)

pynchon = PYNCHON = CoreConfig(
    skip_instance_validation=True,  # still bootstrapping..
    config_files=CONFIG_FILES,
    **MERGED_CONFIG_FILES,
)
RAW = PYNCHON.copy()
# from pynchon.constants import CLI_SETTERS
PLUGINS = PYNCHON["plugins"]
LOGGER.warning(f"plugins: {PLUGINS}")
# FIXME: get from registry or mcls
_all_names = PLUGINS + Meta.NAMES

msg = "Splitting core config.."
events.lifecycle.send(
    __name__,
    msg=msg,
    stage=msg,
)
PYNCHON_CORE = {x: PYNCHON[x] for x in PYNCHON.__fields__.keys() if x not in _all_names}
PYNCHON_CORE = CoreConfig(**PYNCHON_CORE)

msg = "Interpolating config.."
events.lifecycle.send(
    __name__,
    msg=msg,
    stage=msg,
)

USER_DEFAULTS = render.dictionary(input=RAW.copy(), context=dict(pynchon=RAW))
