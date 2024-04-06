""" pynchon.plugins.pattern

    See also:
        https://github.com/cookiecutter/cookiecutter/issues/784
"""

import os

from fleks import cli, tagging

from pynchon import abcs, constants, models
from pynchon.api import render
from pynchon.util import lme, text, typing
from pynchon.util.os import invoke
from pynchon.util.files.diff import str_diff

LOGGER = lme.get_logger(__name__)

FNAME_ADVICE = ".scaffold.advice.json5"
PETR = abcs.Path(constants.PYNCHON_EMBEDDED_TEMPLATES_ROOT)


class RenderResult(abcs.Config):
    before: typing.Optional[str] = typing.Field(default=None)
    after: typing.Optional[str] = typing.Field(default=None)
    diff: typing.Optional[str] = typing.Field(default=None)
    src: typing.Union[str, abcs.Path] = typing.Field(required=True)
    dest: typing.Union[str, abcs.Path] = typing.Field(default=None)

    @property
    def diff(self):
        return str_diff(self.after, self.before)

    def __str__(self):
        return f"<RenderResult {self.src}>"


class ScaffoldAdvice(abcs.Config):
    file: typing.Union[str, abcs.Path] = typing.Field(required=True)
    loaded: bool = typing.Field(default=False)
    inherits: typing.List[str] = typing.Field(default=[])

    @property
    def inherits(self):
        if self.loaded:
            return self.__dict__["inherits"]
        else:
            return self.load().inherits

    def exists(self):
        return abcs.Path(self.file).exists()

    def load(self):
        cadvice = abcs.Path(self.file).read()
        adv = text.loads.json5(cadvice)
        self.__dict__.update(loaded=True, **adv)
        return self

    def __str__(self):
        return f"<ScaffoldAdvice {id(self)}>"


class Scaffold(abcs.Config):
    root: typing.Union[str, abcs.Path] = typing.Field(required=True)
    files: typing.List[str] = typing.Field(default=[])
    dirs: typing.List[str] = typing.Field(default=[])
    kind: str = typing.Field(required=True)

    def sync(self, goals=[], **kwargs):
        """ """
        # LOGGER.critical(f"sync: {kwargs}")
        self.sync_scaffold_dirs(goals=goals, **kwargs)
        self.sync_scaffold_files(goals=goals, **kwargs)
        for p in self.get_parents():
            p.sync(goals=goals, **kwargs)
        return goals

    def sync_scaffold_dirs(
        self,
        plugin=None,
        should_plan: bool = False,
        dest=None,
        goals=[],
        context: dict = {},
    ):
        """ """
        LOGGER.info(f"sync_scaffold_dirs: {dest}")
        for pdir in self.dirs:
            tmp = pdir.relative_to(self.root)
            if render.is_templated(str(tmp)):
                msg = f"detected `{tmp}` is templated, "
                tmp = abcs.Path(
                    render.get_template_from_string(str(tmp)).render(**context)
                )
                msg += f"rendered it as {tmp}"
                LOGGER.critical(msg)
            LOGGER.critical(f"sync_scaffold_dirs:: {dest} {tmp}")
            if tmp.exists():
                LOGGER.info(f"directory already exists @ `{tmp}`")
            else:
                goals.append(
                    models.Goal(
                        type="create",
                        label=f"dir-creation required by {self.kind}",
                        resource=tmp,
                        command=f"mkdir -p {tmp}",
                    )
                )

    def sync_scaffold_files(
        self,
        plugin=None,
        dest=None,
        goals=[],
        should_plan: bool = False,
        context: typing.Dict = {},
    ) -> models.Plan:
        """ """
        assert plugin
        # ctx_f = ".tmp.pattern.ctx"
        # dumpf.json(context, file=ctx_f)
        for src in self.files:
            dst = src.relative_to(self.root)
            plugin.render_file(
                goals=goals,
                kind=self.kind,
                context=context,
                src=src,
                dest=dst,
                should_plan=should_plan,
            )
            # Pattern.siblings['jinja'].render(
            #     src=src, dest=dest,
            #     should_plan=should_plan))
            # if not dst.exists():
            #     # goals.append(
            #     #     models.Goal(
            #     #         type="create",
            #     #         label=f"file-creation required by scaffold @ `{self.kind}`",
            #     #         resource=dst,
            #     #         command=f"cp {src} {dst}",
            #     #     )
            #     # )
            # else:
            #     LOGGER.critical(f"modifies?: {dest}")
            #     if should_plan:
            #         # goals.append(
            #         #     self.siblings['jinja'].render(
            #         #         src=src, dest=dest,
            #         #         should_plan=should_plan))
            #         goals.append(models.Goal(
            #         type='render',
            #         label=f"rendering template @ `{dst}`",
            #         resource=dst,
            #         command=f"pynchon jinja render {src} {dst}",
            #     ))

    def get_parents(self):
        """ """
        out = []
        parents = self.advice.inherits if self.advice else []
        for kind in parents:
            pfolder = PETR / "scaffolds" / kind
            scaf = Scaffold(kind=kind, root=pfolder)
            out.append(scaf)
        return out

    def get_inherited_files(self):
        """ """
        out = []
        for scaf in self.get_parents():
            out += scaf.files
        return out

    def get_inherited_dirs(self):
        """ """
        out = []
        for scaf in self.get_parents():
            out += scaf.dirs
        return out

    @property
    def has_advice(self) -> bool:
        return self.advice is not None

    @property
    def advice(self):
        fadvice = ScaffoldAdvice(file=self.root / FNAME_ADVICE)
        if not fadvice.exists():
            return None
        else:
            return fadvice

    @property
    def files(self) -> typing.List[str]:
        folder = self.root
        base_files = list(
            {x for x in folder.glob("*") if not x.is_dir() and x.name != FNAME_ADVICE}
        )
        return base_files  # +self.get_inherited_files()

    @property
    def dirs(self) -> typing.List:
        base_dirs = list(
            [x for x in self.root.glob("**/") if x.is_dir() and not x == self.root]
        )
        return base_dirs  # +self.get_inherited_dirs()

    def __str__(self):
        return f"<Scaffold@`{self.kind}`>"

    __repr__ = __str__


@tagging.tags(click_aliases=["pat"])
class Pattern(models.ResourceManager):
    """
    Tools for working with file/directory patterns
    """

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "pattern"
        include_patterns: typing.List[str] = typing.Field(default=["*/", "*/*/"])

        @property
        def root(self):
            tmp = PETR / "scaffolds"
            assert tmp.exists(), tmp
            return tmp

    name = "pattern"
    cli_name = "pattern"

    @property
    def patterns(self) -> typing.Dict:
        tmp = super(self.__class__, self).list()
        tmp = [[str(x.relative_to(self.config.root)), x.glob("**/*")] for x in tmp]
        tmp = dict(tmp)
        keep = [x for x in tmp if not any([k.startswith(f"{x}/") for k in tmp])]
        tmp = dict(list([[k, list(v)] for k, v in tmp.items() if k in keep]))
        return tmp

    @property
    def pattern_folder(self):
        return self["root"]

    @property
    def pattern_names(self):
        tmp = self.patterns
        tmp = [abcs.Path(x) for x in tmp.keys()]
        tmp = [x.parents[0] if (self.config.root / x).is_file() else x for x in tmp]
        tmp = map(str, tmp)
        return list(tmp)

    @tagging.tags(click_aliases=["ls"])
    def list(self) -> typing.List:
        """
        Describe templates we can cut patterns from
        """
        return self.pattern_names

    @cli.click.command("open")
    @cli.click.argument("kind", nargs=1)
    def _open(self, kind):
        """open pattern in editor"""
        pfolder = self.pattern_folder / kind
        ed = self[:"pynchon.editor":"atom"]
        invoke(f"{ed} {pfolder}&", system=True)

    @cli.options.plan
    @cli.click.option("--kind")
    @cli.click.argument("dest", nargs=1)
    @cli.click.argument("src", nargs=1)
    def render_file(
        self,
        kind: str = None,
        name: str = None,
        should_plan: bool = False,
        src: str = None,
        dest: str = None,
        goals: typing.List = [],
        context: typing.Dict = {},
    ):
        """Render a single file @ DEST from KIND"""
        pconf = Pattern.project_config.dict()
        context = context or dict(name=name or self[:"project.name":], **pconf)
        context.update(__template__=dest)
        pattern = Scaffold(kind=kind, root=self.pattern_folder / kind)
        dest = abcs.Path(dest)
        try:
            src_content = abcs.Path(src).read()
        except (Exception,) as exc:
            LOGGER.critical(f"error reading '{src}':\n\n{exc}")
            src_content = None
        src_templated = render.is_templated(src_content)
        if dest.exists():
            if src_templated:
                LOGGER.critical(f"render_file: {[src, dest]}")
                before = src_content
                tmpl = render.get_template_from_string(src_content)
                after = tmpl.render(**context)
                tmp = RenderResult(before=before, after=after, src=src, dest=dest)
                if tmp.diff:
                    LOGGER.critical("render_file: diff present")
                    LOGGER.critical(f"\n{tmp.diff}")
                    nsrc = abcs.Path(os.path.relpath(src, "."))
                    tmpf = dest.name.replace(os.path.sep, "_")
                    tmpf = abcs.Path(f".tmp.pattern.rendered.{tmpf}")
                    tmpf.write(after)
                    goal = models.Goal(
                        type="sync",
                        label="sync existing file",
                        resource=dest,
                        owner=Pattern.__name__,
                        udiff=tmp.diff,
                        command=f"cp {tmpf} {dest}",
                    )
                    goals.append(goal)
                else:
                    LOGGER.critical("render_file: no diff")
            else:
                LOGGER.critical("render_file: destination is missing (templated)")
        else:
            goals.append(
                models.Goal(
                    type="sync",
                    label="sync new file",
                    resource=dest,
                    command=f"cp '{src}' {dest}",
                )
            )
        if should_plan:
            return goals
        else:
            return self.apply(plan=goals)

    @cli.click.option("--name", default=None)
    @cli.click.argument("kind", nargs=1)
    @cli.click.argument("dest", nargs=1)
    @cli.options.plan
    def sync(
        self,
        dest: str = None,
        kind: str = None,
        name: str = None,
        should_plan: bool = False,
        context: typing.Dict = {},
    ):
        """Synchronizes DEST from scaffold KIND"""
        LOGGER.critical(f'Synchronizing "{dest}" from `{kind}`')
        tmp = self.pattern_names
        if kind not in tmp:
            LOGGER.critical(f"Unrecognized pattern `{kind}`; expected one of {tmp}")
            raise SystemExit(1)
        plan = super(self.__class__, self).plan()
        destp = abcs.Path(dest)

        pattern = Scaffold(kind=kind, root=self.pattern_folder / kind)

        LOGGER.warning(f"found pattern:\n\t{pattern}")
        LOGGER.warning(f"tentatively rendering {pattern} to `{destp}`")
        patterns = [pattern] + pattern.get_parents()
        folder = abcs.Path(dest).absolute()
        pconf = Pattern.project_config.dict()
        context = context or dict(name=name or self[:"project.name":], **pconf)
        for pattern in patterns:
            LOGGER.critical(f"running sync for: {pattern}")
            goals = pattern.sync(
                plugin=self,
                dest=destp,
                goals=plan,
                context=context,
                should_plan=should_plan,
            )
        if should_plan:
            LOGGER.critical(plan)
            return plan
        else:
            return self.apply(plan=plan)

    @cli.click.argument("name", nargs=1)
    @cli.click.argument("kind", nargs=1)
    @cli.options.plan
    def new(
        self,
        kind: str = None,
        name: str = None,
        should_plan: bool = False,
    ):
        """Instantiates PATTERN to NAME"""
        oname = name
        name = self[:"project.name":name]
        pfolder = self.pattern_folder / kind
        if not pfolder.exists():
            choices = set(self.list().keys())
            tmp = pfolder.relative_to(abcs.Path(".").absolute())
            LOGGER.critical(
                f'KIND @ "{name}" suggests pattern-folder @ "{tmp}", but folder does not exist!'
            )
            LOGGER.critical(f"Choices are: {choices}")
        else:
            plan = super(self.__class__, self).plan()
            dest = abcs.Path(name).absolute()
            if dest.exists():
                LOGGER.warning(f"{dest} already exists!")
            fadvice = ScaffoldAdvice(file=pfolder / ".scaffold.advice.json5")
            if fadvice.exists():
                fadvice.load()
                inherits = fadvice.inherits
            else:
                inherits = []
            inherits += [pfolder / "*"] if pfolder not in inherits else []
            LOGGER.warning(f"{kind} inherits {len(inherits)} patterns")
            dest = dest.relative_to(abcs.Path(".").absolute())
            dest2 = oname if oname == "." else dest
            # raise Exception(dest)
            for parent in inherits:
                # parent = parent.relative_to(abcs.Path(".").absolute())
                plan.append(
                    self.goal(
                        command=f"cp -rfv {parent} {dest2}",
                        resource=dest,
                        type="copy",
                    )
                )

            plan.append(
                self.goal(
                    command=f"{self.click_entry.name} {self.cli_name} render {dest}",
                    resource=dest.absolute(),
                    type="recursive-render",
                )
            )
            if should_plan:
                return plan
            else:
                result = self.apply(plan)
                return result.ok
