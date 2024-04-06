""" pynchon.plugins.plugins
"""

from fleks import tagging

from pynchon import abcs, cli, models
from pynchon.api import render
from pynchon.util.os import invoke
from pynchon.util.text import dumps

from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


class PluginsMan(models.Provider):
    """Meta-plugin for managing plugins"""

    name = "plugins"
    cli_name = "plugins"

    @cli.click.argument("plugin_name")
    @cli.click.option("--json-schema", "-s", is_flag=True, default=False)
    @cli.click.option("--markdown", "-m", is_flag=True, default=False)
    def schema(
        self, plugin_name, markdown: bool = False, json_schema: bool = True
    ) -> str:
        """Retrieves the configuration schema for the given plugin"""
        if not any([markdown, json_schema]):
            json_schema = True
        plugin = self.siblings[plugin_name]
        cfg = plugin.config
        model = cfg.__class__
        schema = cfg.schema()
        if json_schema:
            print(dumps.json(schema, indent=2))
        elif markdown:
            template_name = f"via {__file__}"
            t = render.get_template(
                from_string="""{% include 'pynchon/pydantic-model.md.j2' %}""",
                template_name=template_name,
            )
            fields = model.__fields__
            for dprop_name in model.get_properties():
                dprop = getattr(model, dprop_name, None)
                # import IPython; IPython.embed()
                if dprop:
                    fields[dprop_name] = dict(
                        is_dynamic=True,
                        annotation=str(dprop.fget.__annotations__.get("return", "")),
                        default=None,
                        required=False,
                        description=dprop.__doc__ or "(Missing docstring for property)",
                    )

            print(
                t.render(
                    plugin_name=plugin_name, model=model, fields=fields, schema=schema
                )
            )
        else:
            raise SystemExit(1)

    @cli.click.option("--name")
    @cli.click.option("--template-skeleton", "-t", is_flag=True, default=False)
    def new(self, name: str = None, template_skeleton: bool = False) -> None:
        """
        Create new plugin from template (for devs)
        """
        # FIXME: use pattern?
        plugins_d = abcs.Path(__file__).parents[0]
        template_plugin_f = plugins_d / "__template__.py"
        new_plugin_file = plugins_d / f"{name}.py"
        cmd = f"ls {new_plugin_file} || cp {template_plugin_f} {new_plugin_file} && git status"
        result = invoke(cmd, system=True)
        if template_skeleton:
            raise NotImplementedError()
        return result.succeeded

    @tagging.tags(click_aliases=["ls"])
    def list(self, **kwargs):
        """List all plugins"""
        return list(self.status()["plugins"].keys())

    @tagging.tags(click_aliases=["st", "stat"])
    def status(self) -> typing.Dict:
        """Returns details about all known plugins"""
        result = typing.OrderedDict()
        for name, p in self.siblings.items():
            result[name] = dict(priority=p.priority, key=p.get_config_key())
        return dict(plugins=result)
