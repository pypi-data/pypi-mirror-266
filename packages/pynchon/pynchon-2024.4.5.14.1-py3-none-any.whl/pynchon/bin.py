"""
pynchon: a utility for docs generation and template-rendering
"""

import fleks
import shimport
from trogon import tui

from pynchon import cli

from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)

click = cli.click
plugins = shimport.lazy("pynchon.plugins")


class RootGroup(fleks.cli.RootGroup):
    @fleks.classproperty
    def default(kls):  # noqa
        from pynchon import bin

        return bin.default


@tui()
@click.version_option()
@click.option("--plugins", help="shortcut for `--set plugins=...`")
@click.option("--set", "set_config", help="config overrides")
@click.option("--get", "get_config", help="config retrieval")
@click.group(
    "pynchon",
    cls=RootGroup,
)
def entry(
    plugins: str = "",
    set_config: str = "",  # noqa
    get_config: str = "",
):
    """ """


def bootstrap(plugins: list = []):
    """ """
    from pynchon import constants
    from pynchon.app import app

    constants.PLUGINS = plugins
    from pynchon.plugins import registry as plugin_registry

    from pynchon import config  # isort: skip

    events = app.events
    events.lifecycle.send(__name__, stage="Building CLIs from plugins..")
    registry = click_registry = {}
    loop = plugin_registry.items()
    for name, plugin_meta in loop:
        if name not in config.PLUGINS + constants.PLUGINS:
            LOGGER.warning(f"skipping `{name}`")
            continue
        plugin_kls = plugin_meta["kls"]
        init_fxn = plugin_kls.init_cli
        # LOGGER.critical(f'\t{name}.init_cli: {init_fxn}')
        try:
            p_entry = init_fxn()
        except (Exception,) as exc:
            LOGGER.critical(f"  failed to initialize cli for {plugin_kls.__name__}:")
            LOGGER.critical(f"    {exc}")
            raise
        else:
            registry[name] = dict(plugin=plugin_kls, entry=p_entry)


@entry.command(
    "default",
    hidden=True,
    context_settings=dict(
        ignore_unknown_options=True,
    ),
)
@click.option("--plugins", help="shortcut for `--set plugins=...`")
@click.option("--set", "set_config", help="config overrides")
@click.option("--get", "get_config", help="config retrieval")
@click.argument("extra", nargs=-1)
@click.pass_context
def default(
    ctx, plugins: str = "", set_config: str = "", get_config: str = "", **kwargs  # noqa
):
    """this is always executed, regardless of subcommands and before them"""
    # LOGGER.critical('top-level')
    setters = ctx.params.get("set_config", []) or []
    plugins = ctx.params.get("plugins", "")
    # plugins and setters.append(f'pynchon.plugins+={}')
    setters and LOGGER.critical(f"--set: {setters}")
    bootstrap(plugins=plugins.split(",") if plugins else [])
