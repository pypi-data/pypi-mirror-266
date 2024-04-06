""" pynchon.abcs.path
"""

import os
from fnmatch import fnmatch

from fleks.models import JSONEncoder

from pynchon.util import lme, typing

LOGGER = lme.get_logger(__name__)


class Path(typing.PathType):
    """ """

    def write(self, content: str) -> None:
        """ """
        with open(str(self), "w") as fhandle:
            fhandle.write(content)

    def read(self) -> str:
        """ """
        if not self.exists():
            raise ValueError(f"Cannot read nonexistant file @ {str(self)}")
        # LOGGER.critical(f'opening "{self}" for read..')
        with open(str(self)) as fhandle:
            content = fhandle.read()
        return content

    def endswith(self, other) -> bool:
        return str(self).endswith(other)

    def startswith(self, other) -> bool:
        return str(self).startswith(other)

    def path_truncated(self):
        """ """
        return self.parents[0] / self.stem_truncated()

    def full_extension(self):
        """no extension truncation, i.e. `.tar.gz`"""
        return self.name[self.name.find(".") :]

    def stem_truncated(self):
        """truncated stem"""
        return self.name[: self.name.rfind(self.full_extension())]

    def siblings(self):
        return self.parents[0].list()

    def match_any_glob(self, exclude_patterns: typing.List[str], quiet: bool = True):
        for exclude in exclude_patterns:
            match = self.match_glob(exclude)
            if match:
                quiet or LOGGER.info(f"{self} matches exclude @{match}")
                return match

    def match_glob(self, pattern):
        """

        :param pattern:

        """
        return fnmatch(str(self), str(pattern)) and pattern

    def has_file(self, fname) -> bool:
        """

        :param fname:

        """
        return self.absolute() in [p.absolute() for p in Path(fname).parents]

    def list(self) -> typing.List[str]:
        return [x for x in os.listdir(str(self))]


JSONEncoder.register_encoder(type=Path, fxn=str)
