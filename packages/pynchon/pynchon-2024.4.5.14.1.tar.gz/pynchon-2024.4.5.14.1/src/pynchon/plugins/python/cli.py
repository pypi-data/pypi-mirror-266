""" pynchon.plugins.python.cli
"""

import glob
import importlib

import shimport
from fleks import cli, tagging
from fleks.util.click import click_recursive_help
from memoized_property import memoized_property

from pynchon import abcs, api
from pynchon.models.python import EntrypointMetadata

from .common import PythonPlanner

from pynchon.util import lme, typing  # noqa


config_mod = shimport.lazy(
    "pynchon.config",
)
LOGGER = lme.get_logger(__name__)
import click


def _check_click(fxn=None, path=None) -> bool:
    """ """
    from pynchon.util.oop import is_subclass

    if path is not None:
        with open(str(path)) as fhandle:
            return "click" in fhandle.read()
    else:
        return any(
            [isinstance(fxn, (x,)) for x in [click.Group, click.Command]]
        ) or any([is_subclass(fxn, x) for x in [click.Group, click.Command]])


class PythonCliConfig(abcs.Config):
    """ """

    config_key: typing.ClassVar[str] = "python_cli"
    src_root: str = typing.Field(help="")
    # entrypoints: typing.List[typing.Dict] = typing.Field(help="")
    hooks: typing.List[str] = typing.Field(
        help="applicable hook names",
        default=["open-after-apply"],
    )

    @property
    def root(self):
        tmp = self.__dict__.get("root")
        if tmp:
            return tmp
        else:
            from pynchon import config

            return abcs.Path(config.docs.root) / "cli"

    @property
    def src_root(self) -> abcs.Path:
        """ """
        src_root = config_mod.src["root"]
        # FIXME: support for subprojects
        # # src_root = abcs.Path(
        # # config_mod.project.get(
        # #     "src_root", config_mod.pynchon.get("src_root")
        # # )).absolute()
        return abcs.Path(src_root)

    @property
    def console_script_entrypoints(self) -> typing.List[EntrypointMetadata]:
        """ """
        from pynchon.config import python  # noqa

        package_entrypoints = python.package.console_scripts
        out = []
        for dct in package_entrypoints:
            bin_name = dct["bin_name"]
            module_name, fxn_name = dct["setuptools_entrypoint"].split(":")
            dotpath = ".".join([module_name, fxn_name])
            module = shimport.import_module(module_name)
            fxn = getattr(module, fxn_name, None)
            file = module.__file__
            try:
                abcs.Path(file).relative_to(self.src_root)
                inside_src_root = True
            except (ValueError,) as exc:
                # ValueError: ... is not in the subpath of .. OR one path is relative and the other is absolute.
                LOGGER.critical(
                    f"script-entrypoint file @ `{file}` is not relative to source root at `{self.src_root}`!"
                )
                LOGGER.critical(
                    "make sure you've installed this package in development mode with `pip install -e ..`"
                )
                inside_src_root = False
            emd = EntrypointMetadata(
                is_click=_check_click(fxn=fxn),
                is_package_entrypoint=True,
                file=file,
                bin_name=bin_name,
                inside_src_root=inside_src_root,
                help_command=f"{bin_name} --help",
                path=abcs.Path(file),
                resource=self.root / f"script-{bin_name}.md",
                src_root=self.src_root,
                is_module=False,
                dotpath=dotpath,
            )
            assert bin_name
            out.append(emd)
        return out

    @property
    def module_entrypoints(self) -> typing.List[typing.Dict]:
        """ """
        src_root = self.src_root
        pat = src_root / "**" / "__main__.py"
        excludes = config_mod.src["exclude_patterns"]
        matches = glob.glob(str(pat), recursive=True)
        LOGGER.info(f"{len(matches)} matches for `entrypoints` filter")
        # LOGGER.info(f"filtering with `excludes`: {excludes}")
        matches = list(
            filter(lambda x: not abcs.Path(x).match_any_glob(excludes), matches)
        )
        # LOGGER.info(f"{len(matches)} matches survived filter")
        matches = [[x, {}] for x in matches]
        matches = dict(matches)
        pkg_name = (
            "unknown"  # self.siblings['python']['package'].get("name") or "unknown"
        )
        for f, meta in matches.items():
            LOGGER.info(f"found entry-point: {f}")
            dotpath = abcs.Path(f).relative_to(src_root)
            dotpath = ".".join(str(dotpath).split("/")[:-1])
            rsrc = self.root / f"{dotpath}.md"
            matches[f] = {
                **matches[f],
                **dict(
                    click=_check_click(path=f),
                    dotpath=dotpath,
                    file=f,
                    path=abcs.Path(f),
                    main_entrypoint=f.endswith("__main__.py"),
                    # package_entrypoint=False,
                    resource=rsrc,
                ),
            }
        result = list(matches.values())
        result = [EntrypointMetadata(src_root=self.src_root, **x) for x in result]
        return result


@tagging.tags(click_aliases=["pc"])
class PythonCLI(PythonPlanner):
    """Generators for Python CLI docs"""

    name = "python-cli"
    cli_name = "python-cli"
    config_class = PythonCliConfig

    @cli.click.group
    def gen(self):
        """Generates CLI docs for python packages"""

    @cli.click.flag("--changes")
    def list(self, changes: bool = False) -> typing.List[str]:
        """list related targets/resources"""
        if changes:
            out = []
            git = self.siblings["git"]
            git_changes = git.list(changes=True)
            for emeta in self.config.module_entrypoints:
                p = abcs.Path(emeta["path"]).absolute()
                if p in git_changes:
                    out.append(p)
            return out
        else:
            return [
                abcs.Path(emeta["path"]).absolute()
                for emeta in self.config.module_entrypoints
            ]

    @memoized_property
    def console_script_entrypoints(self) -> typing.List[EntrypointMetadata]:
        """ """
        return self.config.console_script_entrypoints

    @gen.command("toc")
    @cli.options.header
    @cli.options.output
    def toc(
        self,
        # format, file, stdout,
        output,
        header,
    ) -> None:
        """
        Generate table-of-contents for all project entrypoints
        """
        output = output or self.root / "README.md"
        LOGGER.warning(f"writing toc to file: {output}")
        cse = self.console_script_entrypoints
        cme = self.config.module_entrypoints
        LOGGER.warning(f"found {len(cse)} console-script-entrypoints")
        LOGGER.warning(f"found {len(cme)} module-entrypoints")
        entrypoints = cse + cme
        # import IPython; IPython.embed()
        cfg = {**self.config.dict(), **dict(entrypoints=entrypoints)}
        cfg = {**api.project.get_config().dict(), **{self.config_class.config_key: cfg}}
        templatef = self.plugin_templates_root / "TOC.md.j2"
        tmpl = api.render.get_template(templatef)
        result = tmpl.render(
            # package_entrypoints=python_cli.entrypoints,
            package_entrypoints=[e for e in entrypoints if e.is_package_entrypoint],
            main_entrypoints=[e for e in entrypoints if e.is_module],
            **cfg,
        )
        with open(str(output), "w") as fhandle:
            fhandle.write(result)

    def _click_recursive_help(
        self, resource=None, path=None, module=None, dotpath=None, name=None, **kwargs
    ):
        """ """

        result = []
        if name and not module:
            module, name = name.split(":")
        if module and name:
            try:
                mod = importlib.import_module(module)
                entrypoint = getattr(mod, name)
            except (Exception,) as exc:
                LOGGER.critical(exc)
                return []
        else:
            err = "No entrypoint found"
            LOGGER.warning(err)
            raise Exception(err)
        LOGGER.debug(f"Recursive help for `{module}:{name}`")
        # raise Exception(dir())
        result = click_recursive_help(
            entrypoint,
            parent=None,
            path=path,
            dotpath=dotpath,
            module=module,
        ).values()
        git_root = self.siblings["git"]["root"]
        result = [
            {
                **v,
                **dict(
                    module=module,
                    resource=resource or self.root / f"{v['dotpath']}.md",
                    package=module.split(".")[0],
                    entrypoint=name,
                    dotpath=dotpath,
                    help="???",
                    # help=shil.invoke(
                    #     f"python -m{v['help_invocation']} --help", strict=True
                    # ).stdout,
                    # src_url=self.get_src_url(path),
                ),
            }
            for v in result
        ]
        return result

    #     """
    #     Generates help for every entrypoint
    #     """
    #     conf = util.python.load_entrypoints(util.python.load_setupcfg(path=file))
    #     entrypoints = conf.get("entrypoints", {})
    #     if not entrypoints:
    #         LOGGER.warning(f"failed loading entrypoints from {file}")
    #         return []
    #     docs = {}
    #     for e in entrypoints:
    #         bin_name = str(e["bin_name"])
    #         epoint = e["setuptools_entrypoint"]
    #         fname = os.path.join(output_dir, bin_name)
    #         fname = f"{fname}.md"
    #         LOGGER.debug(f"{epoint}: -> `{fname}`")
    #         docs[fname] = {**_click_recursive_help(name=e["setuptools_entrypoint"]), **e}
    #
    #     for fname in docs:
    #         with open(fname, "w") as fhandle:
    #             fhandle.write(constants.T_DETAIL_CLI.render(docs[fname]))
    #         LOGGER.debug(f"wrote: {fname}")
    #     return list(docs.keys())

    def get_entrypoint_metadata(
        self, file: str = None, console_script: bool = False
    ) -> EntrypointMetadata:
        """ """
        if console_script:
            LOGGER.warning(f"looking up console-script metadata for '{file}'")
            filtered = self.console_script_entrypoints
        else:
            LOGGER.warning(f"looking up module-entrypoint metadata for '{file}'")
            filtered = self.config["module_entrypoints"]
        found = False
        file = abcs.Path(file)
        for emd in filtered:
            if str(emd.path) == str(file):
                if console_script:
                    pass  # raise Exception(emd.dict())
                else:
                    # raise Exception(emd.module)
                    module = shimport.import_module(emd.module)
                    wrapped = shimport.wrapper(module)
                    click_entries = wrapped.filter(
                        only_functions=True, filter_vals=[_check_click]
                    )
                    click_entry = (
                        list(click_entries.items())[0] if click_entries else None
                    )
                    if click_entry is None:
                        LOGGER.critical(
                            f"exception retrieving help programmatically: {file}"
                        )
                        # LOGGER.critical(
                        #     f"error retrieving help via system CLI: {emd.help_invocation}"
                        # )
                        recursive_help = {}
                    else:
                        name, fxn = click_entry
                        recursive_help = self._click_recursive_help(
                            module=emd.module,
                            name="entry",
                            # resource=self.root / f"{emd.dotpath}.md",
                            resource=emd.resource,
                            dotpath=emd.dotpath,
                            path=emd.path,
                            file=emd.file,
                        )
                # try:
                # emd.update(entrypoints=tmp)
                # except (AttributeError,) as exc:
                # else:
                # rsrc = self.root / f"{emd.dotpath}.md"
                # docs_url = rsrc.relative_to(self.docs_root.parent)
                # emd.update(
                #     is_click=True,
                #     # help_invocation=help_invocation,
                #     docs_url=docs_url,
                #     # src_url='/'+str(src_url),
                #     # src_url=src_url,
                #     resource=rsrc,
                #     # entrypoints=sub_entrypoints,
                # )
                # metadata.update(**get_cmd_output(help_invocation))
                # import IPython; IPython.embed()
                # raise Exception(sub_entrypoints)
                found = True
                break
        if not found:
            LOGGER.critical(f"missing {file}")
            return {}
        return emd

    @property
    def docs_root(self):
        return abcs.Path(self[:"docs.root":])

    @memoized_property
    def src_root(self):
        return abcs.Path(self[:"src.root":])

    @property
    def root(self):
        return self.config.root

    @gen.command("module-doc-gen")
    @cli.options.stdout
    @cli.options.file
    @cli.options.header
    @cli.options.output_file
    def module_doc_gen(
        self,
        file,
        output,
        stdout,
        header,
    ):  # noqa
        """
        Autogenenerate docs for py modules using `__main__`
        """
        assert abcs.Path(file).exists(), f"input file @ {file} does not exist"
        metadata = self.get_entrypoint_metadata(file=file)
        output = abcs.Path(output) if output else self.root / f"{metadata.dotpath}.md"
        output_dir = output.parents[0]
        assert output_dir.exists(), f"{output_dir} does not exist"
        tmpl = api.render.get_template(self.plugin_templates_root / "main.module.md.j2")
        config = {
            **api.project.get_config().dict(),
            **{self.config_class.config_key: {**self.config.dict(), **dict()}},
        }
        result = tmpl.render(
            entrypoints=[metadata],
            **config,
        )
        LOGGER.critical(result)
        LOGGER.critical(f"Writing output to: {output}")
        with open(str(output), "w") as fhandle:
            fhandle.write(result)

    @gen.command("script-doc-gen")
    @cli.options.file
    @cli.options.output_file
    def script_doc_gen(self, file, output):
        """
        Autogenenerates docs for py files mentioned in `console_scripts`.
        (Not for direct usage; let the planner determine invocation)
        """
        assert abcs.Path(file).exists(), f"input file @ {file} does not exist"
        metadata = self.get_entrypoint_metadata(file, console_script=True)
        output = (
            abcs.Path(output) if output else self.root / f"script-{metadata.dotpath}.md"
        )
        output_dir = output.parents[0]
        assert output_dir.exists(), f"{output_dir} does not exist"
        tmpl_f = self.plugin_templates_root / "script.console.md.j2"
        tmpl = api.render.get_template(tmpl_f)
        result = tmpl.render(entrypoints=[metadata])
        LOGGER.critical(result)
        LOGGER.critical(f"Writing output to: {output}")
        with open(str(output), "w") as fhandle:
            fhandle.write(result)

    @property
    def plugin_invocation(self):
        return f"{self.click_entry.name} {self.cli_name}"

    def plan(self):
        """Describe plan for this plugin"""
        plan = super(self.__class__, self).plan()

        plan.append(
            self.goal(command=f"mkdir -p {self.root}", type="mkdir", resource=self.root)
        )

        rsrc = self.root / "README.md"
        cmd = f"{self.plugin_invocation} toc " f"--output {rsrc}"
        plan.append(self.goal(command=cmd, type="gen", resource=rsrc))

        script_entrypoints = self.console_script_entrypoints
        module_entrypoints = self.config.module_entrypoints
        if not script_entrypoints:
            LOGGER.warning("no script_entrypoints found..")
        if not module_entrypoints:
            LOGGER.warning("no module_entrypoints found..")
        for entrypoint_metadata in script_entrypoints:
            rsrc = entrypoint_metadata.resource
            plan.append(
                self.goal(
                    command=(
                        f"{self.plugin_invocation} script-doc-gen "
                        f"--file {entrypoint_metadata.file} "
                        f"--output {rsrc} "
                    ),
                    type="gen",
                    resource=rsrc,
                )
            )
        for entrypoint_metadata in module_entrypoints:
            entrypoint_metadata = self.get_entrypoint_metadata(entrypoint_metadata.file)
            inp = entrypoint_metadata.path
            rsrc = entrypoint_metadata.resource
            if not rsrc:
                raise Exception(entrypoint_metadata)
            plan.append(
                self.goal(
                    command=(
                        f"{self.plugin_invocation} module-doc-gen "
                        f"--file {inp} --output {rsrc}"
                    ),
                    type="gen",
                    resource=rsrc,
                )
            )
        return plan.finalize()
