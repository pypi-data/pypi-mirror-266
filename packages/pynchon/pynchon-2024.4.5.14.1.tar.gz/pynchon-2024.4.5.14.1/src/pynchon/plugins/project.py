""" pynchon.plugins.project
"""

from fleks.util import tagging  # noqa

from pynchon import abcs, config, constants, models

from pynchon.cli import common, options  # noqa
from pynchon.util import files, lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


class ProjectConfig(abcs.Config):
    """ """

    config_key: typing.ClassVar[str] = "project"
    shell_aliases: typing.Dict[str, str] = typing.Field(default={})
    subproject_patterns: typing.List[str] = typing.Field(default=[])

    exclude_patterns: typing.List[str] = typing.Field()

    # @tagging.tagged_property(conflict_strategy="override")
    @property
    def exclude_patterns(self):
        from pynchon.config import globals

        # globals = plugin_util.get_plugin("globals").get_current_config()
        global_ex = globals.exclude_patterns
        my_ex = self.__dict__.get("exclude_patterns", [])
        return list(set(global_ex + my_ex + ["**/pynchon/templates/includes/**"]))

    @property
    def name(self) -> typing.StringMaybe:
        """ """
        repo_name = config.git.repo_name
        return repo_name or abcs.Path(".").name

    @property
    def _workdir(self):
        return abcs.Path(".").absolute()

    @property
    def root(self) -> str:
        """ """
        git = config.GIT
        return constants.PYNCHON_ROOT or (git and git.root) or self._workdir

    @property
    def subproject(self) -> typing.Dict:
        """ """
        if constants.PYNCHON_ROOT:
            return {}
        git = config.GIT
        git_root = git["root"]
        r1 = self._workdir
        r2 = git_root and git_root.absolute()
        if r2 and (r1 != r2):
            rel_name = r1.relative_to(r2)
            LOGGER.debug(f"subproject detected: {rel_name}")
            # LOGGER.warning(f"subproject detected:\n\t({r1} != git[root] @ {r2})")
            return dict(name=self._workdir.name, root=self._workdir)
        return {}


class Project(models.Manager):
    """Meta-plugin for managing this project"""

    name = "project"
    priority = 2
    config_class = ProjectConfig

    @tagging.tags(click_aliases=["ls"])
    def list(self):
        """List subprojects associated with this project"""
        default = self[:"project"]
        proj_conf = self[:"project.subproject":default]
        project_root = proj_conf.get("root", None) or self[:"git.root":"."]
        # project_root = proj_conf.get("root", None) or '.'
        globs = [
            abcs.Path(project_root).joinpath("**/.pynchon.json5"),
        ]
        self.logger.warning(f"search patterns are {globs}")
        result = files.find_globs(globs)
        self.logger.debug(f"found {len(result)} subprojects (pre-filter)")
        excludes = self["exclude_patterns"]
        self.logger.debug(f"filtering search with {len(excludes)} excludes")
        result = [p for p in result if not p.match_any_glob(excludes)]
        result = [
            dict(
                name=str(p.relative_to(abcs.Path(".").absolute()).parent), config_file=p
            )
            for p in result
        ]
        result = [r for r in result if r["name"] != "."]
        self.logger.debug(f"found {len(result)} subprojects (post-filter)")
        return result

    # @common.kommand(
    #     name="version",
    #     parent=parent,
    #     formatters=dict(markdown=constants.T_VERSION_METADATA),
    #     options=[
    #         # FIXME: options.output_with_default('docs/VERSION.md'),
    #         options.format_markdown,
    #         options.output,
    #         options.header,
    #     ],
    # )
    # def project_version(format, output, header) -> None:
    #     """
    #     Describes version details for this package (and pynchon itself).
    #     """
    #     # from pynchon.api import python #, git
    #     import pynchon
    #     from pynchon.config import git, python
    #
    #     return dict(
    #         pynchon_version=pynchon.__version__,
    #         package_version=python.package.version,
    #         git_hash=git.hash,
    #     )
