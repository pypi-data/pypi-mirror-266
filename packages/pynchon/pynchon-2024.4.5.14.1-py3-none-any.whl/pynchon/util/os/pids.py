""" pynchon.util.os.pids
"""

import shimport

from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)

psutil = shimport.lazy("psutil")


def filter_pids(cmdline__contains: str = None, **kwargs):
    """ """
    procs = []
    for p in psutil.pids():
        try:
            procs.append(psutil.Process(p))
        except (psutil.NoSuchProcess,) as exc:
            LOGGER.critical(exc)
    survivors = []
    for p in procs:
        try:
            # special filters
            if cmdline__contains:
                cmdline = " ".join(p.cmdline())
                if cmdline__contains not in cmdline:
                    continue
            # normal filters
            for k, v in kwargs.items():
                tmp = getattr(p, k)
                if callable(tmp):
                    tmp = tmp()
                if v != tmp:
                    break
            else:
                survivors.append(p)
        except (psutil.AccessDenied,):
            continue
        except (psutil.NoSuchProcess,):
            continue
    return survivors
