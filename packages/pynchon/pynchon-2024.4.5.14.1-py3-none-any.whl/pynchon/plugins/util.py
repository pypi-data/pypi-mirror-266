""" pynchon.plugins.util
"""

from pynchon.util import lme, typing  # noqa

# , importing

# from .exceptions import * # noqa
LOGGER = lme.get_logger(__name__)


# importing.module_builder(__name__, ...)
class PluginNotInitialized(RuntimeError):
    pass


class PluginNotRegistered(RuntimeError):
    pass


class PluginNotConfigured(RuntimeError):
    pass


def get_plugin_meta(plugin_name: str, strict: bool = True) -> typing.Dict:
    """ """
    from pynchon.plugins import registry

    try:
        return registry[plugin_name]
    except KeyError:
        if strict:
            raise PluginNotRegistered(plugin_name)
        else:
            return None


def get_plugin_class(plugin_name: str, strict: bool = True) -> typing.Type:
    """ """
    meta = get_plugin_meta(plugin_name, strict=strict)
    if meta is None:
        return meta
    try:
        return meta["kls"]
    except KeyError:
        if strict:
            raise PluginNotRegistered(plugin_name)
        else:
            return None


get_plugin = get_plugin_class


def get_plugin_obj(plugin_name: str) -> object:
    """

    :param plugin_name: str:
    :param plugin_name: str:

    """
    meta = get_plugin_meta(plugin_name)
    try:
        return meta["obj"]
    except KeyError:
        err = f"cannot retrieve ['obj'] for `{plugin_name}` from registry; is config finalized?"
        LOGGER.critical(err)
        raise PluginNotInitialized(plugin_name)
