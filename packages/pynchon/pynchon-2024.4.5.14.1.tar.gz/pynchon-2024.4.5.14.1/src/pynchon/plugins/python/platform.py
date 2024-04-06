""" pynchon.plugins.python.platform:
"""

import platform as stdlib_platform

from fleks import tagging

from pynchon import abcs, cli
from pynchon.util import lme, python, typing
from pynchon.util.os import invoke

from .common import PythonPlanner

LOGGER = lme.get_logger(__name__)


@tagging.tags(click_aliases=["py"])
class PythonPlatform(PythonPlanner):
    """
    Tools and info for Python projects and platforms
    """

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "python"
        libcst: typing.Dict[str, typing.Any] = typing.Field(default={})

        @property
        def version(self):
            return stdlib_platform.python_version()

        @property
        def is_package(self) -> bool:
            return python.is_package(".")

        @property
        def package(self) -> typing.Dict:
            """ """
            if self.is_package:
                return PackageConfig()
            else:
                return {}

    cli_name = "python"

    priority = 2
    name = "python"

    @cli.click.group
    def bootstrap(self):
        """helpers for bootstrapping python projects"""

    @bootstrap.command("libcst")
    def bootstrap_libcst(self):
        """bootstrap .libcst.codemod.yaml"""
        # @cli.click.option('--libcst',help='bootstrap .libcst.codemod.yaml', default=False, is_flag=True)

    # @bootstrap.command("new")
    # @cli.click.argument("name")
    # def bootstrap_new(self):
    #     """shortcut for `pynchon cut new py/NAME`"""

    # def plan(self):
    #     plan = super(self.__class__, self).plan()
    #     libcst_config = self["libcst"]
    #     if libcst_config:
    #         plan.append(self._goal_libcst_refresh(libcst_config))
    #     return plan

    # @cli.click.group("src")
    # def src(self):
    #     """Generates code for python modules, packages, etc"""

    # @src.command
    @tagging.tags(click_aliases=["src.sorted"])
    def sorted(self):
        """Sorts code-ordering with `ssort`"""
        plan = super(self.__class__, self).plan()
        src_root = self[:"src.root":]
        plan.append(
            self.goal(
                type="code-gen",
                resource=src_root,
                command=f"pip install ssort==0.11.6 && ssort {src_root}",
            )
        )
        return self.apply(plan)


class PackageConfig(abcs.Config):
    """WARNING: `parent` below prevents moving this class elsewhere"""

    parent = PythonPlatform.config_class
    config_key: typing.ClassVar[str] = "package"

    @property
    def name(self) -> str:
        """ """
        from pynchon.util import python

        result = python.load_setupcfg().get("metadata", {}).get("name")
        return result

    @property
    def console_scripts(self) -> str:
        """ """
        from pynchon.util import python

        return python.load_entrypoints(python.load_setupcfg())

    @property
    def version(self) -> str:
        """ """
        if "version" not in self.__dict__:
            cmd = invoke("python setup.py --version 2>/dev/null", log_command=False)
            self.__dict__.update(version=cmd.succeeded and cmd.stdout.strip())
        return self.__dict__["version"]
