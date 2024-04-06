""" pynchon.util.text.dumpf

    Helpers for loading data structures from files
"""

import sys

from pynchon import cli

from pynchon.util import lme, text, typing  # noqa

LOGGER = lme.get_logger(__name__)


@cli.click.argument("file", default="/dev/stdin")
def json(obj, file=None, **kwargs) -> None:
    """ """
    with open(file, "w") as fhandle:
        fhandle.write(text.dumps.json(obj, **kwargs))


@cli.click.argument("file", default="/dev/stdin")
def yaml(file=None, output=None, **kwargs):
    """
    Parse JSON input and writes YAML
    """
    file = "/dev/stdin" if file == "-" else file
    content = text.dumps.yaml(file=file, **kwargs)
    fhandle = open(output, "w") if output else sys.stdout
    content = f"{content}\n"
    fhandle.write(content)
    fhandle.close()
