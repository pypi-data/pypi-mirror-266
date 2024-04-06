""" pynchon.plugins.drawio

    A Wrapper for docker-containers that
    provide the "drawio" diagramming utility

    Live Cloud Version:
        https://app.diagrams.net/
    Local Server:
        https://hub.docker.com/r/jgraph/drawio
        https://www.drawio.com/blog/diagrams-docker-app
    CLI Tools:
        https://github.com/rlespinasse/docker-drawio-desktop-headless
"""

import webbrowser

from fleks import tagging

from pynchon import abcs, api, cli, events, models  # noqa
from pynchon.util import files, lme, text, typing  # noqa

LOGGER = lme.get_logger(__name__)

ElementList = typing.List[typing.Dict]
DEFAULT_HTTP_PORT = 8080
DEFAULT_DOCKER_NAME = "drawio-server"


@tagging.tags(click_aliases=["draw"])
class DrawIO(models.DiagramTool, models.Planner):
    """
    Wrapper for docker-containers that
    provide the "drawio" diagramming utility
    """

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "drawio"
        file_glob: str = typing.Field(
            default="*.drawio", description="Where to find jinja templates"
        )

        docker_image: str = typing.Field(
            default="jgraph/drawio", help="Docker image to use"
        )
        http_port: str = typing.Field(help="Port to use", default=DEFAULT_HTTP_PORT)
        docker_args: typing.List = typing.Field(
            default=[f"-it --rm --name={DEFAULT_DOCKER_NAME}"],
            help="Docker args to use",
        )
        export_docker_image: str = typing.Field(
            default="rlespinasse/drawio-desktop-headless"
        )
        export_width: int = typing.Field(help="", default=800)
        export_args: typing.List = typing.Field(
            help="",
            default=[
                "--export",
                "--embed-svg-images",
                "--embed-diagram",
                "--svg-theme light",
            ],
        )

    name = "drawio"
    cli_name = "drawio"
    priority = 0

    @tagging.tags(click_aliases=["ls"])
    def list(self, changes=False, **kwargs):
        """
        Lists affected resources (*.drawio files) for this project
        """
        return self._list(changes=changes, **kwargs)

    @cli.click.argument("output", required=False)
    @cli.click.argument("input")
    def export(self, input, output=None, format="svg"):
        """
        Exports a given .drawio file to some
        output file/format (default format is SVG)
        """
        assert input.endswith(".drawio") or input.endswith(
            ".xml"
        ), "Expected an xml or drawio file as input"
        output = output or ".".join(
            list(filter(None, input.split(".")[:-1])) + [format]
        )
        export_args = " ".join(self.config.export_args)
        export_args += f" --width {self.config.export_width}"
        export_docker_args = "-w /workspace -v `pwd`:/workspace"
        result = self._run_docker(
            (
                f"docker run {export_docker_args} {self.config.export_docker_image} "
                f"{export_args} --output {output} {input}"
            ),
            strict=True,
        )
        print(result.stdout if result.succeeded else result)
        raise SystemExit(0 if result.succeeded else 1)

    def serve(self):
        """
        Runs the drawio-UI in a docker-container
        """
        port = self.config.http_port
        dargs = self.config.docker_args
        dimg = self.config.docker_image
        cmd_t = f"docker run {dargs} -p {port}:{port} {dimg}"
        return self._run_docker(cmd_t, strict=True, interactive=True)

    def open(self, *args, **kwargs):
        """
        Opens a browser for the container started by `serve`
        """
        return webbrowser.open(
            f"http://localhost:{self.config.http_port}/?offline=1&https=0"
        )
