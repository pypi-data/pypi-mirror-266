""" pynchon.models.planner """

import typing

from fleks import tagging
from memoized_property import memoized_property
from fleks.util.tagging import tags

from pynchon import abcs, cli
from pynchon.app import app

from . import planning
from .plugins import BasePlugin

from pynchon.util import files, lme, typing  # noqa


LOGGER = lme.get_logger(" ")


@tags(cli_label="Planner")
class AbstractPlanner(BasePlugin):
    """A plugin-type that provides plan/apply basics"""

    cli_label = "Planner"

    def _list(self, use_glob=None, changes=False):
        """
        Lists affected resources for this project
        """
        use_glob = use_glob or getattr(self.config, "file_glob", None)
        assert use_glob
        default = self[:"project"]
        proj_conf = self[:"project.subproject":default]
        project_root = proj_conf.get("root", None) or self[:"git.root":"."]
        globs = [
            abcs.Path(project_root).joinpath(f"**/{use_glob}"),
        ]
        self.logger.debug(f"search patterns are {globs}")
        result = files.find_globs(globs)
        self.logger.debug(f"found {len(result)} {use_glob} files (pre-filter)")
        excludes = self["exclude_patterns"::[]]
        # NB: always honor the global-excludes
        excludes += self.siblings["globals"]["exclude_patterns"::[]]
        self.logger.debug(f"filtering search with {len(excludes)} excludes")
        result = [p for p in result if not p.match_any_glob(excludes)]
        self.logger.debug(f"found {len(result)} {use_glob} files (post-filter)")
        if not result:
            err = f"active, but found no {use_glob} files!"
            self.logger.critical(err)
        return result

    @tags(publish_to_cli=False)
    def goal(self, **kwargs):
        """ """
        return planning.Goal(
            owner=f"{self.__class__.__module__}.{self.__class__.__name__}", **kwargs
        )

    @property
    def Plan(self):
        return planning.Plan

    def plan(
        self,
        config=None,
        goals=[],
    ) -> planning.Plan:
        """
        Creates a plan for this plugin
        """
        # app.manager.status_bar.update(app='PLAN')
        app.status_bar.update(app="Pynchon::PLAN", stage=f"plugin:{self.name}")
        plan = self.Plan(owner=self.name)
        if not goals:
            goals = getattr(self.config, "goals", [])
            goals and LOGGER.critical(f"{self.name} goals from config: {goals}")
            for g in goals:
                _type = g.pop("type", "from-config")
                cmd = g.pop("command", None)
                cmd = cmd and cmd.format(**g)
                g.update(command=cmd, type=_type)
                plan.append(self.goal(**g))
        else:
            self.logger.critical(f"packing  {len(goals)} goals")
            for g in goals:
                plan.append(g)
        app.status_bar.update(app="Pynchon", stage=f"{len(plan)}")
        return plan

    def _dispatch_apply_hooks(self, results: planning.ApplyResults):
        """ """
        # write status event (used by the app-console)
        app.status_bar.update(
            app="Pynchon::HOOKS",
            stage=f"{self.__class__.name}",
        )
        if results.finished:
            hooks = self.apply_hooks
            if hooks:
                LOGGER.warning(
                    f"{self.name}.apply: dispatching {len(hooks)} hooks: {hooks}"
                )
                hook_results = []
                for hook in hooks:
                    hook_results.append(self.run_hook(hook, results))
            else:
                LOGGER.warning(f"{self.name}.apply: no hooks to run.")
        else:
            LOGGER.critical(f"{self.name}: Skipping hooks: ")
            LOGGER.critical(
                f"  {len(results.goals)-len(results.actions)} goals incomplete"
            )

    @cli.options.quiet
    @cli.options.parallelism
    @cli.options.fail_fast
    def apply(
        self,
        plan: planning.Plan = None,
        parallelism: str = "0",
        fail_fast: bool = False,
        quiet: bool = False,
    ) -> planning.ApplyResults:
        """
        Executes the plan for this plugin
        """
        parallelism = int(parallelism)
        # app.status_bar.update(
        #     app="Pynchon::APPLY",
        #     stage=f"plugin:{self.__class__.name}"
        # )
        plan = plan or self.plan()
        LOGGER.critical(
            f"{self.name}.apply ( {len(plan)} goals with {parallelism} workers)"
        )
        results = plan.apply(parallelism=parallelism, git=self.siblings["git"])

        LOGGER.critical(
            f"{self.name}.apply finished ( {len(results.actions)}/{len(results.goals)} goals )"
        )
        self._dispatch_apply_hooks(results)
        if not quiet:
            return results

    def _validate_hooks(self, hooks):
        # FIXME: validation elsewhere
        for x in hooks:
            assert isinstance(x, (str,))
            assert " " not in x
            assert "_" not in x
            assert x.strip()

    @memoized_property
    def apply_hooks(self):
        """ """
        hooks = [x for x in self.hooks if x.split("-")[-1] == "apply"]
        apply_hooks = self["apply_hooks"::[]]
        hooks += [
            x + ("-apply" if not x.endswith("-apply") else "") for x in apply_hooks
        ]
        hooks = list(set(hooks))
        self._validate_hooks(hooks)
        return hooks

    @memoized_property
    def hooks(self):
        """ """
        hooks = self["hooks"::[]]
        self._validate_hooks(hooks)
        return hooks

    def _hook_diff_after_apply(self, result: planning.ApplyResults) -> bool:
        """ """
        self.logger.warning("diff-after-apply not implemented yet")

    def _hook_open_after_apply(self, result: planning.ApplyResults) -> bool:
        """ """
        changes = list({r.resource for r in result})
        changes = [abcs.Path(rsrc) for rsrc in changes]
        changes = [rsrc for rsrc in changes if not rsrc.is_dir()]
        self.logger.warning(f"Opening {len(changes)} changed resources.")
        docs_plugin = self if self.name == "docs" else self.siblings["docs"]
        for ch in changes:
            docs_plugin.open(ch)
        return True

    @typing.validate_arguments
    def run_hook(self, hook_name: str, results: planning.ApplyResults):
        """
        :param hook_name: str:
        :param results: planning.ApplyResults:
        """

        class HookNotFound(Exception):
            pass

        class HookFailed(RuntimeError):
            pass

        norml_hook_name = hook_name.replace("-", "_")
        fxn_name = f"_hook_{norml_hook_name}"
        hook_fxn = getattr(self, fxn_name, None)
        if hook_fxn is None:
            err = [self.__class__, [hook_name, fxn_name]]
            self.logger.critical(err)
            raise HookNotFound(err)
        hook_result = hook_fxn(results)
        self.logger.critical(hook_result)
        return hook_result


class ShyPlanner(AbstractPlanner):
    """ShyPlanner uses plan/apply workflows, but they must be
    executed directly.  ProjectPlugin (or any other parent plugins)
    won't include this as a sub-plan.
    """

    contribute_plan_apply = False


@tags(cli_label="Manager")
class Manager(ShyPlanner):
    cli_label = "Project Tools"
    cli_description = "Tools for project management"


class ResourceManager(Manager):
    @property
    def changes(self):
        """Set(git_changes).intersection(plugin_resources)"""
        git = self.siblings["git"]
        changes = git.modified
        these_changes = set(changes).intersection(set(self.list(changes=False)))
        return dict(modified=list(these_changes))

    @tagging.tags(click_aliases=["ls"])
    @cli.click.option(
        "--changes",
        "-m",
        "changes",
        is_flag=True,
        default=False,
        help="returns the git-modified subset",
    )
    def list(self, changes: bool = False):
        """Lists resources associated with this plugin"""
        if changes:
            return self.changes["modified"]
        from pynchon import abcs
        from pynchon.util import files

        try:
            include_patterns = self["include_patterns"]
            root = self["root"]
        except (KeyError,) as exc:
            self.logger.critical(
                f"{self.__class__} tried to use self.list(), but does not follow protocol"
            )
            self.logger.critical(
                "self['include_patterns'] and self['root'] must both be defined!"
            )
            raise
        root = abcs.Path(root)
        # proot = self.project_config['pynchon']['root']
        tmp = [p for p in include_patterns if abcs.Path(p).is_absolute()]
        tmp += [root / p for p in include_patterns if not abcs.Path(p).is_absolute()]
        # tmp += [proot / p for p in include_patterns if not abcs.Path(p).is_absolute()]
        return files.find_globs(tmp)


class Planner(ShyPlanner):
    """Planner uses plan/apply workflows, and contributes it's plans
    to ProjectPlugin (or any other parent plugins).
    """

    contribute_plan_apply = True
    cli_description = ""


class RenderingPlugin(Planner):
    cli_label = "Rendering Tools"
    cli_description = ""
