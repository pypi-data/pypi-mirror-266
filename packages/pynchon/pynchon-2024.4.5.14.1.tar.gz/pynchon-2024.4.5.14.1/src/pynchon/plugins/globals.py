""" pynchon.plugins.globals """

from pynchon import abcs, models

from pynchon.util import lme, typing  # noqa


class Globals(models.Provider):
    """Context for pynchon globals"""

    class config_class(abcs.Config):
        """ """

        config_key: typing.ClassVar[str] = "globals"
        exclude_patterns: typing.List[str] = typing.Field(default=[])

    priority = 2
    name = "globals"
