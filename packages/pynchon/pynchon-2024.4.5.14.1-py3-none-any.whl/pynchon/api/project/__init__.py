""" pynchon.api.project
"""

from pynchon.util import lme, text, typing

LOGGER = lme.get_logger(__name__)


def get_config() -> dict:
    """ """
    from pynchon.config.util import finalize

    return finalize()


def plan(config: dict = {}) -> dict:
    """
    :param config: dict:  (Default value = {})
    """
    plan = []
    config = config or get_config()
    project = config["project"]
    from pynchon.plugins.util import get_plugin_obj

    for plugin_name in config["pynchon"]["plugins"]:
        plugin = get_plugin_obj(plugin_name)
        if not plugin.contribute_plan_apply:
            continue
        fxn = getattr(plugin, "plan", None)
        if fxn is None:
            continue
        plugin.logger.debug("Planning..")
        result = plugin.plan(config)
        msg = "Done planning.  "
        if result:
            msg = msg + "result={}"
            plugin.logger.debug(msg.format(text.to_json(result)))
        else:
            plugin.logger.critical(msg + "But plugin produced an empty plan!")
        assert isinstance(
            result, typing.List
        ), f"plugin @ {plugin_name} generates bad plan {result}"
        plan += result

    return config, plan
