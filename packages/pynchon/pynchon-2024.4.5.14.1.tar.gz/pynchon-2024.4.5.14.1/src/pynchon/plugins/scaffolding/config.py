""" pynchon.plugins.scaffolding
"""

import os

from pynchon import abcs
from pynchon.util import lme, typing

LOGGER = lme.get_logger(__name__)


class ScaffoldingItem(abcs.AttrDict):
    warnings = []

    def __init__(
        self, name="unnamed scaffold", scope="*", pattern=None, src=None, **kwargs
    ):
        assert pattern is not None
        assert src is not None
        super().__init__(
            name=name,
            scope=scope,
            src=abcs.Path(os.path.expanduser(src)),
            pattern=pattern,
            **kwargs,
        )
        self.validate()

    @property
    def exists(self) -> typing.Bool:
        return os.path.exists(self.src)

    def validate(self):
        if not self.exists and self.src not in ScaffoldingItem.warnings:
            LOGGER.critical(f"Scaffolding source @ {self.src} does not exist!")
            ScaffoldingItem.warnings.append(self.src)


class ScaffoldingConfig(abcs.Config):
    """ """

    config_key: typing.ClassVar[str] = "scaffolding"

    # def scaffolds(self):
    #     return dict([
    #         [scaffold_pattern,scaffold_meta]
    #         for k,v in self.items()])
