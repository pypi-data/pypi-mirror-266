""" pynchon.models.plugins.docker
"""

from pynchon import abcs
from pynchon.cli import click

from .tool import ToolPlugin

from pynchon.util import lme, typing  # noqa

from . import validators  # noqa

LOGGER = lme.get_logger("DOCKER")


class DockerWrapper(ToolPlugin):
    """
    Wrappers for dockerized tools
    """

    class BaseConfig(abcs.Config):
        docker_image: str = typing.Field(default="docker/hello-world")
        docker_args: typing.List = typing.Field(default=[])

    cli_label = "Docker Wrappers"
    cli_description = "Plugins that wrap invocations on containers"
    contribute_plan_apply = False
    priority = 2
    __class_validators__ = [
        validators.require_conf_key,
    ]

    @property
    def command_extra(self):
        import sys

        command = sys.argv[sys.argv.index(self.click_group.name) + 2 :]
        return " ".join(command)

    def _get_docker_command_base(self, *args, **kwargs):
        docker_image = kwargs.pop("docker_image", self["docker_image"])
        docker_args = kwargs.pop("docker_args", "")
        docker_args = (
            docker_args + " " + " ".join(f'--{k}="{v}"' for k, v in kwargs.items())
        )
        return (
            "docker run -v `pwd`:/workspace -w /workspace "
            f"{docker_args} {docker_image} {' '.join(args)}"
        )

    def _get_docker_command(self, *args, **kwargs):
        """ """
        cmd_t = self._get_docker_command_base(" ".join(args))
        docker_args = " ".join(self["docker_args"])
        zip_kws = " ".join(["{k}={v}" for k, v in kwargs.items()])
        cmd_t += f" {docker_args} {zip_kws}"
        return cmd_t

    @click.command(
        context_settings=dict(
            ignore_unknown_options=True,
            allow_extra_args=True,
        )
    )
    def run(self, *args, **kwargs):
        """Passes given command through to docker-image this plugin wraps"""
        command = self._get_docker_command(self.command_extra)
        LOGGER.warning(command)
        plan = super().plan(
            goals=[
                self.goal(
                    type="render",
                    resource=kwargs.get("output", kwargs.get("o", "")),
                    command=command,
                )
            ]
        )
        result = self.apply(plan=plan)
        if result.ok:
            raise SystemExit(0)
        else:
            LOGGER.critical(f"Action failed: {result.actions[0].error}")
            raise SystemExit(1)

    def _run_docker(self, cmd, **kwargs):
        """ """
        from pynchon.util.os import invoke

        LOGGER.critical(cmd)
        result = invoke(cmd, **kwargs)
        LOGGER.warning(result.stdout)
        return result


class DiagramTool(DockerWrapper):
    cli_label = "Diagramming Tools"
    cli_description = "View and render technical diagrams from source, in several formats.  (Usually these require docker, but no other system dependencies.)"
