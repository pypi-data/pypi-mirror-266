""" pynchon.models.validators

    FIXME: ntuple struct for vdata
"""

import fleks

from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)


# @validator
def require_conf_key(
    kls,
    self=None,
    vdata=None,
    strict: bool = True,
):
    """ """
    pconf_kls = getattr(kls, "config_class", None)
    conf_key = getattr(pconf_kls, "config_key", kls.name.replace("-", "_"))
    if not conf_key:
        msg = f"failed to determine conf-key for {kls}"
        LOGGER.critical(msg)
        if strict:
            # raise vdata.error_class(msg)
            raise fleks.meta.ClassMalformed(msg)
    return vdata


def warn_config_kls(kls, self=None, vdata=None):
    """
    :param vdata=None:
    :param self=None:
    :param kls:
    """
    """ """
    """ """
    pconf_kls = getattr(kls, "config_class", "NOTSET")
    if pconf_kls == "NOTSET":
        vdata.warnings["`config_class` not set!"].append(kls)
    return vdata
