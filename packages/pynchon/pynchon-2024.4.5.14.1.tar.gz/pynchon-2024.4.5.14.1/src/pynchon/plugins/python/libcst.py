""" pynchon.plugins.python.libcst
"""

from fleks import cli, tagging

from pynchon.util.os import invoke

from pynchon import abcs, events, models  # noqa
from pynchon.util import lme, python, typing  # noqa

LOGGER = lme.get_logger(__name__)
F_CODEMOD_YAML = ".libcst.codemod.yaml"

from .common import PythonPlanner


class LibCST(PythonPlanner):
    """
    Code-transforms via libcst[1]
    """

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "python-libcst"

    name = "python-libcst"
    cli_name = "python-libcst"

    @cli.click.group("gen")
    def gen(self):
        """Generates code for python modules, packages, etc"""

    @tagging.tags(click_aliases=["src.transform"])
    @cli.click.argument("transform_name", nargs=1)
    @cli.click.argument("src_root", default="", nargs=1)
    def run_transform(self, transform_name="docstrings.simple.module", src_root=""):
        """Runs the given libcst transform on {src.root}"""
        src_root = src_root or self[:"src.root":]
        return invoke(
            f"python -m libcst.tool codemod {transform_name} {src_root}", system=True
        )

    @tagging.tags(click_aliases=["src.list-transforms"])
    def list_transforms(self):
        """Lists known libcst transforms"""
        out = invoke("python -mlibcst.tool list", strict=True)
        out = out.stdout
        print(f"\n{out}")

    def _goal_libcst_refresh(self, libcst_config):
        """ """
        from pynchon.util import text

        min = text.to_json(libcst_config, minified=True)
        rsrc = F_CODEMOD_YAML
        cmd = f"printf '{min}' | python -mpynchon.util.text.dumpf yaml > {rsrc}"
        return self.goal(
            type="render",
            label="refresh libcst-config",
            resource=rsrc,
            command=cmd,
        )

    def plan(self):
        """Run plan for this plugin"""
        plan = super(self.__class__, self).plan()
        libcst_config = self[F_CODEMOD_YAML::{}]
        if libcst_config:
            plan.append(self._goal_libcst_refresh(libcst_config))
        [plan.append(g) for g in self.docstrings(should_plan=True).goals]
        return plan

    @gen.command
    @cli.options.ignore_private
    @cli.options.ignore_missing
    @cli.options.plan
    @cli.click.argument("SRC_ROOT", required=False, default=None)
    @cli.click.option(
        "--modules", help="create docstrings for modules", default=False, is_flag=True
    )
    @cli.click.option(
        "--functions",
        help="create docstrings for functions",
        default=False,
        is_flag=True,
    )
    @cli.click.option(
        "--methods", help="create docstrings for methods", default=False, is_flag=True
    )
    def docstrings(
        self,
        src_root=None,
        should_plan: bool = False,
        ignore_missing: bool = False,
        ignore_private: bool = True,
        modules: bool = True,
        functions: bool = True,
        methods: bool = True,  # noqa
        classes: bool = True,
    ):
        """Generates python docstrings"""
        src_root = src_root or self[:"src.root":]
        cmd = "docstrings.simple.function"
        plan = self.Plan()
        plan.append(
            self.goal(
                command=f"python -mlibcst.tool codemod {cmd} {src_root}",
                resource=src_root,
                type="codemod",
            )
        )
        if should_plan:
            LOGGER.critical(plan)
            return plan
        else:
            return self.apply(plan)
