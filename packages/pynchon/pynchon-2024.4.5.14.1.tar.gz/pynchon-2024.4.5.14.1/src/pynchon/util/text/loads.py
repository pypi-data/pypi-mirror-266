""" pynchon.util.text.loads

    Helpers for loading data structures from strings
"""

import json as json_mod

import yaml as modyaml
import pyjson5 as modjson5

from pynchon.util import lme, typing

LOGGER = lme.get_logger(__name__)


def ini(content: str) -> typing.StringMaybe:
    """
    Parses `content` as ini-file.
    :param content: str:
    """
    raise NotImplementedError()


def yaml(content: str) -> typing.StringMaybe:
    """Parses `content` as yaml.

    :param content: str:
    """
    # try:
    return modyaml.safe_load(content)
    # except yaml.YAMLError as exc:
    #     print(exc)


def toml(content: str) -> typing.StringMaybe:
    """Parses `content` as toml.

    :param content: str:

    """
    raise NotImplementedError()


def json(content: str = "") -> typing.StringMaybe:
    """Parses `content` as JSON (strict).
    For most things, you're better using `loads.json5()`,
    since that's just a JSON superset with a more relaxed parser.

    :param content: str:  (Default value = '')
    """
    return json_mod.loads(content)


def json5(content: str = "", quiet=True) -> typing.Dict:
    """Parses `content` as JSON5.
    This tries to give a better error message than defaults.

    :param content: str:  (Default value = '')
    :param quiet: Default value = True)
    """
    try:
        return modjson5.loads(content)
    except (ValueError,) as exc:
        LOGGER.critical("Cannot parse json5 from literal!")
        quiet or LOGGER.critical(content)
        content_lines = content.split("\n")
        if "at column" in exc.args[0]:
            line_no = exc.args[0].split()[0].split(":")[-1]
            line_no = int(line_no)
            err_lines = "\n".join(content_lines[line_no - 3 : line_no + 3])
        else:
            err_lines = None
            line_no = None
        LOGGER.warning(f"error: {exc}")
        err_lines and LOGGER.warning(f"lines nearby:\n\n {err_lines}")
        raise
