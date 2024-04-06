""" pynchon.models.planning
"""

import typing
import collections
import concurrent.futures

import shil
from fleks import app
from fleks.models import BaseModel

from pynchon import abcs
from pynchon.app import app as pynchon_app
from pynchon.util.os import invoke

from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(" ")

RED_X = "❌"
RED_BALL = "🔴"
YELLOW_BALL = "🟡"


class BaseModel(BaseModel):
    @property
    def _action_summary(self):
        """ """
        if self.command:
            return shil.fmt(self.command)
        else:
            return f"{self.owner}.{self.callable.__name__}(..)"

    @property
    def rel_resource(self) -> str:
        return (
            abcs.Path(self.resource).absolute().relative_to(abcs.Path(".").absolute())
        )


class Action(BaseModel):
    """ """

    type: str = typing.Field(default="unknown_action_type")
    ok: bool = typing.Field(default=None)
    error: typing.StringMaybe = typing.Field(default="")
    changed: bool = typing.Field(default=False)
    resource: abcs.ResourceType = typing.Field(default="??")
    command: str = typing.Field(default="echo")
    callable: typing.CallableMaybe = typing.Field(help="", default=None)
    owner: typing.StringMaybe = typing.Field(
        help="Name of the plugin that owns this Action", default=None
    )
    ordering: typing.StringMaybe = typing.Field(
        default=None,
        help="human-friendly string describing the sort order for this action inside plan",
    )

    def __rich__(self) -> str:
        """ """
        # indicator = RED_BALL if self.changed else YELLOW_BALL

        indicator = (
            app.Text(
                "modified",
                justify="right",
                style="red",
            )
            if self.changed
            else None
        )
        ind = (
            app.Text(
                "process: failed",
                # justify='right',
                style="red",
            )
            if not self.ok
            else None
        )
        err = (
            (
                app.Text(
                    "error: ",
                    # justify='right',
                    style="red",
                )
                + app.Text(self.error, justify="center")
            )
            if not self.ok
            else None
        )
        sibs = [
            app.Text(
                f"target: {self.rel_resource}",
            ),
            app.Text(f"action: {self._action_summary}"),
            indicator,
            ind,
            err,
        ]
        sibs = app.Group(*filter(None, sibs))
        ordering = f" ({self.ordering.strip()})"
        return app.Panel(
            sibs,
            title=app.Text(f"{ordering} ", style="dim underline")
            + app.Text(
                f"{self.type}", style=f"dim bold {'red' if self.changed else 'green'}"
            ),
            title_align="left",
            # style=app.Style(
            #     dim=True,
            #     # color='green',
            #     bgcolor="black",
            #     frame=False,
            # ,
            subtitle=app.Text(f"{self.owner}", style="dim"),
        )

    @property
    def status_string(self):
        if self.ok is None:
            tmp = "pending"
        elif self.ok:
            tmp = "ok"
        else:
            tmp = "failed"
        return tmp

    def __str__(self):
        return f"<[{self.type}]@{self.resource}: {self.status_string}>"


class Goal(BaseModel):
    """ """

    # FIXME: validation-- command OR callable must be set

    class Config(BaseModel.Config):
        exclude: typing.Set[str] = {"udiff", "callable"}
        # arbitrary_types_allowed = True
        # json_encoders = {typing.MethodType: lambda c: str(c)}

    resource: abcs.ResourceType = typing.Field(default="?r", required=False)
    command: typing.StringMaybe = typing.Field(default=None)
    callable: typing.MethodType = typing.Field(default=None)
    type: typing.StringMaybe = typing.Field(default=None, required=False)
    owner: typing.StringMaybe = typing.Field(
        help="Name of the plugin that owns this Goal", default=None
    )
    label: typing.StringMaybe = typing.Field(default=None)
    udiff: typing.StringMaybe = typing.Field(default=None)
    ordering: typing.StringMaybe = typing.Field(
        default=None,
        help="human-friendly string describing the sort order for this action inside plan",
    )

    def act(goal, git=None, plugin_name="?", ordering="?"):
        """ """
        pynchon_app.status_bar.update(
            app="Pynchon::APPLY",
            stage=f"{plugin_name} plugin {ordering}",
        )
        invocation = invoke(goal.command, interactive=goal.type == "interactive")
        success = invocation.succeeded
        action = dict(
            ok=success,
            ordering=goal.ordering,
            error="" if success else invocation.stderr,
            # log=invocation.succeeded and invocation.stderr else None,
            owner=goal.owner,
            command=goal.command,
            resource=goal.resource,
            type=goal.type,
        )
        rsrc_path = abcs.Path(goal.resource).absolute()
        current_changes = (
            [] if git is None else [path.absolute() for path in git.modified]
        )
        # prev_changes = git.modified
        changed = all(
            [
                rsrc_path in current_changes,
                # rsrc_path not in prev_changes,
            ]
        )
        action.update(ordering=ordering, changed=changed)
        return Action(**action)

    def __rich__(self) -> str:
        """ """
        ordering = f" ({self.ordering.strip()})" if self.ordering else ""

        if self.udiff:
            sibs = [app.Markdown(f"```diff\n{self.udiff}\n```")]
        else:
            sibs = [
                app.Syntax(
                    f"  {self._action_summary}",
                    "bash",
                    line_numbers=False,
                    word_wrap=True,
                )
            ]

        return app.Panel(
            app.Group(*sibs),
            title=app.Text(f"{ordering} ", style="dim underline")
            + app.Text(f"{self.type}", style="dim bold yellow"),
            title_align="left",
            style=app.Style(
                dim=True,
                bgcolor="black",
                frame=False,
            ),
            subtitle=app.Text(f"{self.label or self.owner}", style="dim"),
            # + app.Text(" rsrc=", style="bold italic")
            # + app.Text(f"{self.rel_resource}", style="dim italic"),
        )


class ApplyResults(typing.BaseModel):
    # typing.List[Action], metaclass=meta.namespace):
    """ """
    goals: typing.List[Goal] = typing.Field(default=[])
    actions: typing.List[Action] = typing.Field(default=[])

    @property
    def finished(self):
        """ """
        return len(self.goals) == len(self.actions)

    @property
    def ok(self) -> bool:
        return self.finished and all([a.ok for a in self])

    @property
    def action_types(self):
        tmp = list({g.type for g in self})
        return {k: [] for k in tmp}

    @property
    def _dict(self):
        """ """
        result = collections.OrderedDict()
        result["ok"] = self.ok
        result["resources"] = list({a.resource for a in self})
        result["actions"] = [
            g.command if g.command else self.callable.__name__ for g in self
        ]
        result["action_types"] = self.action_types
        result["changed"] = list({a.resource for a in self if a.changed})
        for g in self:
            result["action_types"][g.type].append(g.resource)
        return result

    def __iter__(self):
        return iter(self.actions)

    def __len__(self):
        return len(self.actions)

    def __str__(self):
        return f"<{self.__class__.__name__}[{len(self)} actions]>"


class Plan(typing.BaseModel):
    """ """

    goals: typing.List[Goal] = typing.Field(default=[])
    owner: typing.StringMaybe = typing.Field(
        help="Name of the plugin that owns this Plan", default=None
    )

    def apply(self, parallelism: int = 0, fail_fast: bool = True, git=None):
        """ """
        goals = self.goals
        total = len(goals)

        jobs = []
        results = []
        if parallelism:
            LOGGER.warning(f"parallel execution enabled (workers={parallelism})")
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=parallelism
            ) as executor:
                for i, goal in enumerate(goals):
                    ordering = f"  {i+1}/{total}"
                    jobs.append(
                        executor.submit(
                            goal.act,
                            git=git,
                            plugin_name=self.__class__.__name__,
                            ordering=ordering,
                        )
                    )
            for i, future in enumerate(concurrent.futures.as_completed(jobs)):
                # LOGGER.debug(f' waiting for {i+1} / {total}')
                action = future.result()
                results.append(action)
                lme.CONSOLE.print(action)
                if fail_fast and not action.ok:
                    msg = f"fail-fast is set, so exiting early.  exception follows\n\n{action.error}"
                    LOGGER.critical(msg)
                    break
        else:
            LOGGER.warning(f"parallel execution disabled (workers={parallelism})")
            for i, goal in enumerate(goals):
                ordering = f"  {i+1}/{total}"
                lme.CONSOLE.print(goal)
                action = goal.act(
                    git=git,
                    plugin_name=self.__class__.__name__,
                    ordering=ordering,
                )
                # lme.CONSOLE.print(action)
                results.append(action)
                if fail_fast and not action.ok:
                    msg = f"fail-fast is set, so exiting early.  exception follows\n\n{action.error}"
                    LOGGER.critical(msg)
                    break
        results = ApplyResults(actions=results, goals=goals)
        return results

    def finalize(self):
        """
        When a plan is finished being appended to,
        it can be "finalized" to set the `ordering` value
        for individual goals.
        """
        plan_length = len(self.goals)
        self.goals = [
            g.copy(update=dict(ordering=f"{i+1}/{plan_length}"))
            for i, g in enumerate(self.goals)
        ]
        return self

    def __rich__(self) -> str:
        """ """
        syntaxes = []
        for g in self.goals:
            if hasattr(g, "__rich__"):
                syntaxes.append(g.__rich__())
            else:
                syntaxes.append(str(g))

        table = app.Table.grid(
            # title=f'{__name__} ({len(self)} items)',
            # subtitle='...',
            # box=box.MINIMAL_DOUBLE_HEAD,
            expand=True,
            # border_style='dim italic yellow'
            # border_style='bold dim',
        )
        [
            [
                table.add_row(x),
                # table.add_row(app.Align(app.Emoji("gear"), align='right')),
            ]
            for i, x in enumerate(syntaxes)
        ]

        panel = app.Panel(
            table,
            title=app.Text(
                f"{self.__class__.__name__}", justify="left", style="italic"
            ),
            title_align="left",
            padding=1,
            style=app.Style(
                dim=True,
                # color='green',
                bgcolor="black",
                frame=False,
            ),
            subtitle=f"(Planned {len(self)} items)",  # subtitle=Text("✔", style='green')
        )
        return panel

    def append(self, other: Goal):
        """ """
        if other in self:
            return
        elif isinstance(other, (Goal,)):
            self.goals += [other]
        elif isinstance(other, (Plan,)):
            self.goals += other.dict()["goals"]
        elif isinstance(
            other,
            (
                list,
                # tuple,
            ),
        ):
            self.goals += other
        else:
            raise NotImplementedError(type(other))

    def __contains__(self, g):
        return g in self.goals

    def __len__(self):
        return len(self.goals)

    def __add__(self, other):
        """ """
        if isinstance(other, (Goal,)):
            return Plan(goals=self.goals + [other])
        elif isinstance(other, (Plan,)):
            return Plan(goals=self.goals + other.goals)
        elif isinstance(
            other,
            (
                list,
                tuple,
            ),
        ):
            return Plan(goals=self.goals + list(other))
        else:
            raise NotImplementedError(type(other))

    __iadd__ = __add__
