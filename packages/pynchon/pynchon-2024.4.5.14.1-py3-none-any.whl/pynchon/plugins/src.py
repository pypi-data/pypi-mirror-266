""" pynchon.plugins.src
"""

import fnmatch

from pynchon import abcs, api, cli, events, models  # noqa
from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)

EXT_MAP = {
    ".ini": dict(
        template="pynchon/plugins/src/header/ini.j2", pre=["#", "###"], post="###"
    ),
    ".j2": dict(
        template="pynchon/plugins/src/header/jinja.j2", pre=["{#", "<!--"], post="#}"
    ),
    "*.md.j2": dict(
        template="pynchon/plugins/src/header/jinja-md.md.j2",
        pre=["{#", "<!--"],
        post="#}",
    ),
    ".json5": dict(
        template="includes/pynchon/src/json5-header.j2", pre=["//", "///"], post="///"
    ),
    ".py": dict(
        # template='includes/pynchon/src/python-header.j2',
        template="pynchon/plugins/src/header/python.j2",
        pre=['"""', '"', "'"],
        post='""""',
    ),
    ".sh": dict(
        template="pynchon/plugins/src/header/sh.j2", pre=["#", "###"], post="###"
    ),
}


class SourceMan(models.ResourceManager):
    """Management tool for project source"""

    class config_class(abcs.Config):
        config_key: typing.ClassVar[str] = "src"
        goals: typing.List[str] = typing.Field(default=[])
        include_patterns: typing.List[str] = typing.Field(default=[])
        exclude_patterns: typing.List[str] = typing.Field(default=[])
        root: typing.Union[str, abcs.Path, None] = typing.Field(default=None)
        sorted: bool = typing.Field(
            default=False, description="Whether to sort source code"
        )

    name = "src"
    cli_name = "src"
    priority = 0

    # @tagging.tagged_property(conflict_strategy="override")
    # @property
    # def exclude_patterns(self):
    #     from pynchon.plugins import util as plugin_util
    #
    #     globals = plugin_util.get_plugin("globals").get_current_config()
    #     global_ex = globals["exclude_patterns"]
    #     my_ex = self.get("exclude_patterns", [])
    #     return list(set(global_ex + my_ex + ["**/pynchon/templates/includes/**"]))

    # @tagging.tagged_property(conflict_strategy='override')
    # def exclude_patterns(self):
    #     globals = plugin_util.get_plugin('globals').get_current_config()
    #     global_ex = globals['exclude_patterns']
    #     my_ex = self.get('exclude_patterns', [])
    #     return list(set( global_ex+my_ex))

    # def list(self):
    #     """ """
    #     # config = api.project.get_config()
    #     # src_root = config.pynchon['src_root']
    #     include_patterns = self.config.get('include_patterns', ["**"])
    #     return files.find_globs(include_patterns)
    def list_modified(self):
        """
        Lists modified files
        """
        raise NotImplementedError()

    def _get_meta(self, rsrc):
        tmp = rsrc.full_extension()
        try:
            ext_meta = EXT_MAP[tmp]
        except (KeyError,) as exc:
            for x in EXT_MAP:
                if fnmatch.fnmatch(tmp, x):
                    ext_meta = EXT_MAP[x]
                    break
            else:
                LOGGER.warning(f"no match for {x}")
                return
        return ext_meta

    def _get_missing_headers(self, resources):
        """
        :param resources:
        """
        result = dict(extensions=set(), files=[])
        for p_rsrc in resources:
            if not p_rsrc.is_file() or not p_rsrc.exists():
                continue
            # ext_info = self._rsrc_ext_info(p_rsrc)
            tmp = p_rsrc.full_extension()
            ext_meta = self._get_meta(p_rsrc)
            if ext_meta is None:
                continue
            preamble_patterns = ext_meta["pre"]
            assert isinstance(preamble_patterns, (list,))
            with p_rsrc.open("r") as fhandle:
                content = fhandle.read().lstrip()
                if any([content.startswith(pre.lstrip()) for pre in preamble_patterns]):
                    # we detected expected comment at the top of the file,
                    # so the appropriate header *might* be present; skip it
                    continue
                else:
                    # no header at all
                    result["files"].append(p_rsrc)
                    result["extensions"] = result["extensions"].union(
                        {p_rsrc.full_extension()}
                    )
        result.update(extensions=list(result["extensions"]))
        return result

    def _plan_empties(self, resources):
        """
        :param resources:
        """
        result = []
        return result

    def _render_header_file(self, rsrc: abcs.Path = None):
        """
        :param rsrc: abcs.Path:  (Default value = None)
        """
        ext = rsrc.full_extension()
        templatef = self._get_meta(rsrc)["template"]
        tpl = api.render.get_template(templatef)
        abs = rsrc.absolute()
        src_root = abcs.Path(self.config["root"]).absolute()
        try:
            relf = abs.relative_to(src_root)
        except ValueError:
            relf = abs.relative_to(abcs.Path(".").absolute())
        relf = relf.path_truncated()
        module_dotpath = str(relf).replace("/", ".")
        tmp2 = __name__.replace(".", "-")
        fname = f".tmp.src-header.{module_dotpath}{ext}"
        result = tpl.render(
            module_dotpath=module_dotpath,
            template=templatef,
            filename=str(abs),
            relative_filename=relf,
        )
        if not result:
            err = f'header for extension "{ext}" rendered to "{fname}" from {templatef}'
            self.logger.warning(err)
        with open(fname, "w") as fhandle:
            fhandle.write(result)
        LOGGER.warning(f"wrote {fname}")
        return fname

    @cli.click.group("open")
    def _open(self):
        """Helper for opening project source files"""

    @_open.command("recent")
    def open_recent(self):
        """Opens recently changed files"""

    @_open.command("changed")
    def open_changed(self):
        """opens changed files"""

    def plan(self, config=None):
        """Describe plan for this plugin"""
        plan = super().plan(config=config)
        resources = [abcs.Path(fsrc) for fsrc in self.list()]
        self.logger.warning("Adding user-provided goals")
        for g in self["goals"]:
            plan.append(self.goal(command=g, resource="?", type="user-config"))

        self.logger.warning("Adding file-header related goals")
        cmd_t = "python -mpynchon.util.files prepend --clean "
        loop = self._get_missing_headers(resources)
        for rsrc in loop["files"]:
            if rsrc.match_any_glob(self["exclude_patterns"::[]]):
                continue
            ext = rsrc.full_extension()
            ext = ext[1:] if ext.startswith(".") else ext
            # fhdr = header_files[ext]
            fhdr = self._render_header_file(rsrc)
            plan.append(
                self.goal(
                    resource=rsrc,
                    type="change",
                    label=f"Adding file header for '{ext}'",
                    command=f"{cmd_t} {fhdr} {rsrc}",
                )
            )
        return plan

    #
    # def find(self):
    #     """file finder"""
    #
    # def header(self):
    #     """creates file headers for source in {src_root}"""
    #
    # def map(self):
    #     """file mapper"""
