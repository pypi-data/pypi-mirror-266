""" pynchon.plugins.fixme
"""

from fnmatch import fnmatch

from pynchon import abcs, models
from pynchon.util import lme, typing
from pynchon.util.os import invoke

from fleks.cli import click, options  # noqa


LOGGER = lme.get_logger(__name__)


class FixMeConfig(abcs.Config):
    config_key: typing.ClassVar[str] = "fixme"
    exclude_patterns: typing.List[str] = typing.Field()

    # @tagging.tagged_property(conflict_strategy="override")
    @property
    def exclude_patterns(self):
        from pynchon.config import globals

        global_ex = globals.exclude_patterns
        my_ex = self.__dict__.get("exclude_patterns", [])
        return list(set(global_ex + my_ex))


class FixMe(models.Planner):
    """Generates {docs_root}/FIXME.md from source"""

    name = "fixme"
    config_class = FixMeConfig
    cli_label = "Docs Tools"

    def plan(self, config: dict = None) -> typing.List:
        """ """
        config = config or self.__class__.get_current_config()
        plan = super(self.__class__, self).plan(config)
        target = abcs.Path(self.project_config["docs"]["root"]) / "FIXME.md"
        plan.append(
            self.goal(
                type="gen",
                resource=target,
                command=f"pynchon fixme gen --output {target}",
            )
        )
        return plan

    @click.option(
        "--output",
        "-o",
        default="docs/FIXME.md",
        help=("output file to write.  (optional)"),
    )
    @options.should_print
    @options.header
    def gen(
        self,
        output,
        should_print: bool,
        header,
    ):
        """
        Generate FIXME.md files, aggregating references to all FIXME's in code-base
        """
        from pynchon import api

        config = self.__class__.project_config
        src_root = config.src["root"]
        exclude_patterns = self["exclude_patterns"]
        cmd = invoke(f"grep --line-number -R FIXME {src_root}")
        assert cmd.succeeded
        items = []
        skipped = {}
        for line in cmd.stdout.split("\n"):
            line = line.strip()
            if not line or line.startswith("Binary file"):
                continue
            bits = line.split(":")
            file = bits.pop(0)
            path = abcs.Path(file)
            for g in exclude_patterns:
                if fnmatch(file, g):
                    skipped[g] = skipped.get(g, []) + [file]
                    break
            else:
                line_no = bits.pop(0)
                items.append(
                    dict(
                        file=abcs.Path(file).relative_to(
                            abcs.Path(config["git"]["root"]).absolute()
                        ),
                        line=":".join(bits),
                        line_no=line_no,
                    )
                )
        for g in skipped:
            msg = f"exclude_pattern @ `{g}` skipped {len(skipped[g])} matches"
            LOGGER.info(msg)
        result = api.render.get_template(
            "pynchon/plugins/fixme/FIXME.md.j2",
        ).render(**dict(items=items))
        msg = result
        print(msg, file=open(output, "w"))
        if should_print and output != "/dev/stdout":
            print(msg)

    #
    # @classmethod
    # def asdasdinit_cli(kls):
    #     """
    #     """
    #     parent = kls.click_group
    #     T_FIXME = constants.ENV.get_template(
    #         "pynchon/plugins/plugins/fixme/FIXME.md.j2"
    #     )
