""" pynchon.plugins.python.api
"""

from fleks import cli, tagging

from pynchon import abcs
from pynchon.api import render
from pynchon.util import complexity, lme, typing

from .common import PythonPlanner

LOGGER = lme.get_logger(__name__)


@tagging.tags(click_aliases=["pa"])
class PythonAPI(PythonPlanner):
    """Generators for Python API docs"""

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "python-api"
        skip_private_methods: bool = typing.Field(default=True)
        skip_patterns: typing.List[str] = typing.Field(default=[])
        apply_hooks: typing.List[str] = typing.Field(default=["diff-after"])

    name = "python-api"

    @cli.click.group("gen")
    def gen(self):
        """Generates API docs from python modules, packages, etc"""

    # FIXME: not bound correctly: missing 1 req pos arg 'self'
    @gen.command("toc")
    @cli.options.file
    @cli.options.header
    @cli.options.should_print
    @cli.options.package
    @cli.click.option(
        "--output",
        "-o",
        default="docs/api/README.md",
        help=("output file to write.  (optional)"),
    )
    @cli.click.option(
        "--exclude",
        default="",
        help=("comma-separated list of modules to exclude (optional)"),
    )
    def toc(
        self,
        package=None,
        should_print=None,
        file=None,
        exclude=None,
        output=None,
        stdout=None,
        header=None,
    ):
        """Generate table-of-contents"""
        T_TOC_API = render.get_template("pynchon/plugins/python/api/TOC.md.j2")
        module = complexity.get_module(package=package, file=file)
        result = complexity.visit_module(
            module=module,
            module_name=module.name,
            template=T_TOC_API,
            exclude=exclude.split(","),
        )
        header = f"{header}\n\n" if header else ""
        result = dict(
            header=f"## API for '{package}' package\n\n{header}" + "-" * 80,
            blocks=result,
        )
        result = result["header"] + "\n".join(result["blocks"])
        print(result, file=open(output, "w"))
        if should_print and output != "/dev/stdout":
            print(result)

    def plan(self, config=None) -> typing.List:
        """
        Runs a plan for this plugin
        """
        config = config or self.project_config
        plan = super(self.__class__, self).plan(config)
        docs_root = self[:"docs.root":]
        api_docs_root = f"{docs_root}/api"
        if not abcs.Path(api_docs_root).exists():
            plan.append(
                self.goal(
                    command=f"mkdir -p {api_docs_root}",
                    resource=api_docs_root,
                    type="mkdir",
                )
            )
        pkg = self[:"python.package.name":None]
        pkg_arg = pkg and f"--package {pkg}"
        src_root = self[:"src.root":]
        src_arg = src_root and f"--file {src_root}"
        input = f"{pkg_arg or src_arg}"
        outputf = f"{api_docs_root}/README.md"
        output = f"--output {outputf}"
        cmd_t = "pynchon python-api gen toc"
        plan.append(
            self.goal(
                resource=outputf,
                command=f"{cmd_t} {input} {output}",
                type="gen",
                # ordering=f'{len(plan)+1}/?',
            )
        )
        return plan.finalize()
