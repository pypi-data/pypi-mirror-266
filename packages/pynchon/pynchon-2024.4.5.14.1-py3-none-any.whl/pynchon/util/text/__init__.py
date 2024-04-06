""" pynchon.util.text
    Utilities for parsing, generating or manipulating text
"""

from . import dumps, loadf, loads  # noqa

jsonify = to_json = dumps.json  # noqa


def indent(txt: str, level: int = 2) -> str:
    """
    indents text, or if given an object, stringifies and then indents

    :param txt: str:
    :param level: int:  (Default value = 2)
    """
    import pprint

    if not isinstance(txt, (str, bytes)):
        txt = pprint.pformat(txt)
    return "\n".join([(" " * level) + line for line in txt.split("\n") if line.strip()])
