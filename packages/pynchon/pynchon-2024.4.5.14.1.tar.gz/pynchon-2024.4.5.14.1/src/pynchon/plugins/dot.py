""" pynchon.plugins.dot
"""

from fleks import cli

from pynchon.util.os import invoke

from pynchon import abcs, api, models  # noqa
from pynchon.util import files, lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


class Dot(models.DiagramTool, models.Planner):
    """Finds / Renders (graphviz) dot files for this project"""

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "dot"
        exclude_patterns: typing.List[str] = typing.Field(default=[])

    name = "dot"

    def list(self) -> typing.List[str]:
        """ """
        # config = config or self.project_config
        search = [
            abcs.Path(self.project_root).joinpath("**/*.dot"),
        ]
        self.logger.debug(f"search pattern is {search}")
        result = files.find_globs(search)
        self.logger.debug(f"found {len(result)} files (pre-filter)")
        excludes = self["exclude_patterns" :: self[:"globals.exclude_patterns":]]
        self.logger.debug(f"filtering search with {len(excludes)} excludes")
        result = [p for p in result if not p.match_any_glob(excludes)]
        self.logger.debug(f"found {len(result)} files (post-filter)")
        if not result:
            err = f"{self.name} plugin is included in this config, but found no .dot files!"
            self.logger.critical(err)
        return result

    @cli.options.output
    @cli.click.option("--img", default="nshine/dot")
    @cli.click.option("--output-mode")
    @cli.click.argument("file", nargs=1)
    def render(
        self,
        img: str = "??",
        file: str = "",
        output_mode: str = "png",
        output: str = "",
    ):
        cmd = f"cat {file} | docker run --rm --entrypoint dot -i {img} -T{output_mode} > {output}"
        result = invoke(cmd, strict=True)
        # assert result.succeeded
        return result.succeeded

    def plan(
        self,
        config=None,
    ) -> models.Plan:
        plan = super(self.__class__, self).plan(config=config)
        self.logger.debug("planning for rendering for .dot graph files..")
        cmd_t = "pynchon dot render {rsrc} --output {output} --output-mode png"
        for rsrc in self.list():
            plan.append(
                self.goal(
                    resource=rsrc,
                    command=cmd_t.format(
                        rsrc=rsrc, output=str(rsrc)[: str(rsrc).rfind(".")] + ".png"
                    ),
                    type="render",
                )
            )
        return plan
