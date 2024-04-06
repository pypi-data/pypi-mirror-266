""" pynchon.config.util
"""

import functools
import collections

from pynchon import abcs
from pynchon import config as config_module
from pynchon import constants, events
from pynchon.util import lme, typing
from pynchon.util.text import loadf, loads
from pynchon.plugins.util import PluginNotRegistered, get_plugin

LOGGER = lme.get_logger(__name__)

from pydantic import create_model


@functools.lru_cache(maxsize=100, typed=False)
def finalize():
    """ """
    from pynchon import abcs
    from pynchon.plugins import registry as plugins_registry

    plugins = []
    top = dict(
        __base__=abcs.Config,
        pynchon=config_module.RAW,
        git=config_module.GIT,
    )

    # NB: already sorted by priority
    for pname in plugins_registry.keys():
        try:
            tmp = get_plugin(pname)
        except (PluginNotRegistered,) as exc:
            LOGGER.critical(f"PluginNotRegistered: {exc}")
            continue
        else:
            plugins.append(tmp)

    for plugin_kls in plugins:
        pconf_kls = getattr(plugin_kls, "config_class", None)
        conf_key = plugin_kls.get_config_key()
        if pconf_kls is None:
            plugin_config = abcs.Config()
        else:
            # user_defaults = (
            #     config_module.PYNCHON_CORE
            #     if plugin_kls.name == "base"
            #     else config_module.USER_DEFAULTS.get(plugin_kls.name, {})
            # )
            # user_defaults = config_module.USER_DEFAULTS.get(plugin_kls.name, {})
            user_defaults = config_module.MERGED_CONFIG_FILES.get(conf_key, {})
            ctx = {
                **config_module.MERGED_CONFIG_FILES,
                **dict(pynchon=config_module.PYNCHON),
            }
            # if conf_key=='globals':
            #     import IPython; IPython.embed()
            from pynchon.api import render

            user_defaults = render.dictionary(user_defaults, ctx)

            if plugin_kls.name == "core":
                # special case: this is already bootstrapped
                from pynchon.config import PYNCHON_CORE

                plugin_config = PYNCHON_CORE
            else:
                plugin_config = pconf_kls(
                    **{
                        # **plugin_defaults,
                        **user_defaults,
                    }
                )
        setattr(config_module, conf_key, plugin_config)
        # result.update({conf_key: plugin_config})
        if conf_key not in ["json"]:
            top[conf_key] = plugin_config
        else:
            top[f"{conf_key}_"] = typing.Field(alias=conf_key, default=plugin_config)
        events.lifecycle.send(
            __name__, config=f"plugin-config@`{plugin_config}` was finalized"
        )

        plugin_obj = plugin_kls(final=plugin_config)
        # plugins_registry.register(plugin_obj)
        plugins_registry[plugin_kls.name]["obj"] = plugin_obj
        events.lifecycle.send(
            plugin_obj, plugin=f"plugin@`{plugin_kls.__name__}` was finalized"
        )
    result = create_model("Top", **top)
    result = result()
    # import IPython; IPython.embed()
    return result


def config_folders():
    import os

    from pynchon import config

    folders = list(
        set(
            filter(
                None,
                [
                    os.getcwd(),
                    constants.PYNCHON_ROOT,
                    config.GIT["root"],
                ],
            )
        )
    )
    return [abcs.Path(f) for f in folders]


def get_config_files():
    """ """
    if constants.PYNCHON_CONFIG:
        return [abcs.Path(constants.PYNCHON_CONFIG)]
    result = []
    folders = config_folders()
    for folder in folders:
        for file in constants.CONF_FILE_SEARCH_ORDER:
            candidate = folder / file
            result.append(candidate)
    return result


def load_config_from_files() -> typing.Dict[str, str]:
    """ """
    contents = collections.OrderedDict()
    candidates = get_config_files()
    for config_file in candidates:
        if not config_file.exists():
            LOGGER.info(f"config_file@`{config_file}` doesn't exist, skipping it")
            continue
        elif config_file.name.endswith("pyproject.toml"):
            LOGGER.info(f"Loading from toml: {config_file}")
            tmp = loadf.toml(config_file)
            tmp = tmp.get("tool", {})
            tmp = tmp.get("pynchon", {})
            contents[config_file] = tmp
        elif config_file.name.endswith(".json5"):
            LOGGER.info(f"Loading from json5: {config_file}")
            with open(config_file.absolute()) as fhandle:
                raw_contents = fhandle.read()
            try:
                contents[config_file] = loads.json5(raw_contents)
            except (Exception,) as exc:
                LOGGER.critical(exc)
                contents[config_file] = {}

        else:
            err = f"don't know how to load config from {config_file}"
            raise NotImplementedError(err)
    return contents
