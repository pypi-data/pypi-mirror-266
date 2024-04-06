""" pynchon.util.os
"""

# from . import models

from shil import invoke

# def invoke(cmd: str, **kwargs):
#     """
#     Dependency-free replacement for the `invoke` module,
#     which fixes annoyances with subprocess.POpen and os.system.
#     """
#     invoc = models.Invocation(cmd=cmd, **kwargs)
#     result = invoc()
#     result.__rich__()
#     return result


def slurp_json(cmd: str, **kwargs):
    """ """
    result = invoke(f"{cmd} > .tmp.{id(cmd)}")
    assert result.succeeded
    from pynchon.util.text import loadf

    return loadf.json(f".tmp.{id(cmd)}")
