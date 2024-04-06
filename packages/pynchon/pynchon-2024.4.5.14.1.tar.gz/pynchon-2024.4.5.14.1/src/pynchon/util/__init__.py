""" pynchon.util
"""

from pynchon import constants

from . import lme

LOGGER = lme.get_logger(__name__)


def get_root(path: str = ".") -> str:
    """

    :param path: str:  (Default value = ".")
    :param path: str:  (Default value = ".")

    """
    import os

    from pynchon.abcs import Path

    path = Path(path).absolute()
    if (path / ".git").exists():
        return path.relative_to(os.getcwd())
    elif not path:
        return None
    else:
        return get_root(path.parents[0])


def is_python_project() -> bool:
    """ """
    import os

    from pynchon.api import git

    return os.path.exists(os.path.join(git.get_root(), constants.PYNCHON_CONFIG_FILE))


def find_src_root(config: dict) -> str:
    """

    :param config: dict:
    :param config: dict:

    """
    from pynchon.abcs import Path

    pconf = config.get("project", {})
    LOGGER.debug(f"project config: {pconf}")
    src_root = Path(pconf.get("src_root", "."))
    src_root = src_root if src_root.is_dir() else None
    return src_root.relative_to(".")
