""" pynchon.plugins.json
"""

from pynchon import abcs, models  # noqa
from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)

from pynchon.models.planner import RenderingPlugin  # noqa


class Json(RenderingPlugin):
    """Tools for working with JSON & JSON5"""

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "json"

    # cli_subsumes: typing.List[typing.Callable] = [
    #     loadf_main.json5,
    #     loadf_main.json,
    #     loadf_main.j5,
    #     # loadf_main.json,
    # ]

    # @tags(click_aliases=['loads',])
    # def json_loads(self):
    #     """ loads JSON from string-input (strict) """

    # @tags(click_aliases=['loadf',])
    # def json_loadf(self):
    #     """ loads JSON from file-input (strict) """
    #     pass

    # def load_json5(self):
    #     """ loads JSON-5 from string-input """
    #     pass
    #
    # def loadf_json5(self):
    #     """ loads JSON-5 from file-input """
    #     pass
    # DEFAULT_OPENER = "open"
    #
    #
    # @kommand(
    #     name="any",
    #     parent=PARENT,
    #     formatters=dict(
    #         # markdown=pynchon.T_TOC_CLI,
    #     ),
    #     options=[
    #         # options.file,
    #         options.format,
    #         # options.stdout,
    #         options.output,
    #     ],
    # )
    # def render_any(format, file, stdout, output):
    #     """
    #     Render files with given renderer
    #     """
    #     raise NotImplementedError()

    name = "json"
    priority = 1
    cli_name = name
