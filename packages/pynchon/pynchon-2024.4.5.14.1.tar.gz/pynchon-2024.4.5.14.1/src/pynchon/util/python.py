""" pynchon.api.python
"""

import functools

from pynchon.util import files, lme, text

LOGGER = lme.get_logger(__name__)


@functools.lru_cache(maxsize=None)
def is_package(folder: str) -> bool:
    """slightly better than just looking for setup.py-
    we try to use it to get the current version-string

    :param folder: str:
    """
    from pynchon.util.os import invoke

    cmd = invoke(
        f"cd {folder} && python setup.py --version 2>/dev/null", log_command=False
    )
    return cmd.succeeded


def load_setupcfg(file: str = "", folder: str = ""):
    """

    :param file: str:  (Default value = "")
    :param folder: str:  (Default value = "")
    :param file: str:  (Default value = "")
    :param folder: str:  (Default value = "")

    """
    if not file:
        folder = folder or files.get_git_root().parents[0]
        file = folder / "setup.cfg"
    return text.loadf.ini(file)


from pynchon.util import typing


def load_entrypoints(config: dict = None) -> typing.List[typing.Dict]:
    """
    loads entrypoints from setup.cfg style configuration
    """
    if not config:
        LOGGER.critical("no config provided!")
        return {}
    try:
        console_scripts = config["options.entry_points"]["console_scripts"]
    except (KeyError,) as exc:
        LOGGER.warning(
            f'could not load config["options.entry_points"]["console_scripts"] from {config}'
        )
        return {}
    console_scripts = [x for x in console_scripts.split("\n") if x]
    package = config["metadata"]["name"]
    entrypoints = []
    for c in console_scripts:
        tmp = dict(
            package=package,
            bin_name=c.split("=")[0].strip(),
            module=c.split("=")[1].strip().split(":")[0],
            entrypoint=c.split("=")[1].strip().split(":")[1],
        )
        abs_entrypoint = tmp["module"] + ":" + tmp["entrypoint"]
        tmp["setuptools_entrypoint"] = abs_entrypoint
        entrypoints.append(tmp)
    return entrypoints
    # return dict(package=package,entrypoints=entrypoints,)
