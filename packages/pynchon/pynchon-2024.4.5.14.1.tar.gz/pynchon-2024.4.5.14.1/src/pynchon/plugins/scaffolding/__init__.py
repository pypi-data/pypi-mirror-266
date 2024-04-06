""" pynchon.plugins.scaffolding
"""

from fleks import tagging

from pynchon import models
from pynchon.util import files, lme, typing
from pynchon.util.os import invoke

from .config import ScaffoldingConfig, ScaffoldingItem

tags = tagging.tags
LOGGER = lme.get_logger(__name__)


class Scaffolding(models.ShyPlanner):
    """Management tool for project boilerplate"""

    contribute_plan_apply = False
    priority = 3
    name = "scaffolding"
    cli_name = "scaffold"
    cli_label = "Manager"
    config_class = ScaffoldingConfig

    def match(self, pattern=None):
        """
        returns files that match for all scaffolds
        """
        if pattern:
            return files.find_globs([pattern], quiet=True)
        else:
            matches = []
            for scaffold in self.scaffolds:
                LOGGER.debug(
                    f"scaffold @ `{scaffold.pattern}` with scope {scaffold.scope}:"
                )
                matched_scaffold = ScaffoldingItem(
                    **{**scaffold, **dict(matches=self.match(pattern=scaffold.pattern))}
                )
                matches.append(matched_scaffold)
            return matches

    @property
    def matches(self):
        return self.match()

    @tags(click_aliases=["st", "status"])
    def stat(self):
        """status of current scaffolding"""
        ignore_keys = "diff".split()
        diff = self.diff(quiet=True)
        modified = [
            {k: v for k, v in s.items() if k not in ignore_keys}
            for s in diff["modified"]
        ]
        return dict(errors=diff["errors"], modified=modified)

    @property
    def scaffolds(self):
        """ """
        result = self.plugin_config.get("scaffolds", [])
        return [ScaffoldingItem(**x) for x in result]

    @tags(
        click_aliases=[
            "ls",
        ]
    )
    def list(self):
        """list available scaffolds"""
        return self.scaffolds

    def diff(self, quiet: bool = False):
        """diff with known scaffolding

        :param quiet: bool:  (Default value = False)
        :param quiet: bool:  (Default value = False)

        """
        result = dict(errors=[], modified=[])
        for matched_scaffold in self.matches:
            for fname in matched_scaffold.matches:
                if matched_scaffold.exists:
                    diff = invoke(f"diff {fname} {matched_scaffold.src}")
                    if diff.succeeded:
                        LOGGER.debug(f"no diff detected for {fname}")
                    else:
                        this_diff = files.diff(matched_scaffold.src, fname)
                        percent_diff = files.diff_percent(matched_scaffold.src, fname)
                        result["modified"].append(
                            dict(
                                src=matched_scaffold.src,
                                fname=fname,
                                percent_diff=f"{percent_diff}%",
                                # diff=this_diff,
                                # diff=diff.stdout
                            )
                        )
                        files.diff_report(this_diff, logger=LOGGER.debug)
                else:
                    result["errors"].append(fname)
        return result

    def plan(self, config=None) -> typing.List[str]:
        """

        :param config: Default value = None)

        """
        config or self.plugin_config
        plan = super().plan(config)
        for delta in self.diff()["modified"]:
            plan.append(
                models.Goal(
                    type="scaffold",
                    resource=delta["fname"],
                    command=f"cp {delta['src']} {delta['fname']}",
                )
            )
        return plan
