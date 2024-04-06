""" pynchon.plugins.render
"""

from pynchon import models

from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


class Renderers(models.NameSpace):
    """Collects `render` commands from other plugins"""

    name = cli_name = "render"
    config_class = None
    # cli_subsumes: typing.List[str] = [
    #     'pynchon.util.text.render.__main__',
    # ]


#
#
# @kommand(
#     name="dot",
#     parent=PARENT,
#     options=[
#         options.output,
#         click.option(
#             "--open",
#             "open_after",
#             is_flag=True,
#             default=False,
#             help=(f"if true, opens the created file using {DEFAULT_OPENER}"),
#         ),
#     ],
#     arguments=[files_arg],
# )
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
