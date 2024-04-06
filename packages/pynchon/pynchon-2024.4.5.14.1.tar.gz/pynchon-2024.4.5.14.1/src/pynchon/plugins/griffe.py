""" pynchon.plugins.griffe
"""

from fleks import tagging

from pynchon import abcs, cli, events, models  # noqa
from pynchon.util import lme, os, typing  # noqa

LOGGER = lme.get_logger(__name__)

from pynchon.plugins.python.common import PythonPlanner


@tagging.tags(click_aliases=["g", "gr"])
class Griffe(PythonPlanner):
    """Tools for working with Python ASTs"""

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "griffe"

    name = "griffe"
    cli_name = "griffe"

    @tagging.tags(click_aliases=["dump"])
    @cli.click.option(
        "--package", "-p", "pkg", help="dotpath for a python package to use", default=""
    )
    def list(self, pkg: str = ""):
        """dump package signature from griffe"""
        pkg = pkg or self[:"python.package.name":]
        # return invoke(f'griffe {pkg}',load_json=True,log_command=True)
        # invoke(f"griffe {pkg} > .tmp.griffe")
        # from pynchon.util.text import loadf
        # return loadf.json(".tmp.griffe")
        return os.slurp_json(
            f"griffe {pkg}",
        )

    @cli.click.option(
        "--classes", "-c", is_flag=True, default=False, help="return classes"
    )
    @cli.click.option(
        "--functions", "-f", is_flag=True, default=False, help="return classes"
    )
    @cli.click.option(
        "--modules", "-m", is_flag=True, default=False, help="return classes"
    )
    def grep(
        self, classes: bool = False, functions: bool = False, modules: bool = False
    ):
        """grep for types"""
        result = self.list()
        print(result)
        raise NotImplementedError()
        # return result
