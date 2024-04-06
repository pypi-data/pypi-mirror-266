""" {{pkg}}.util.classproperty
"""

from . import typing


@typing.validate_arguments
def new_in_class(name: str, kls: typing.Type):
    """

    :param name: str:
    :param kls: typing.Type:
    :param name: str:
    :param kls: typing.Type:

    """
    return name in dir(kls) and not any([name in dir(base) for base in kls.__bases__])


def is_subclass(x, y, strict=True):
    """

    :param x: param y:
    :param strict: Default value = True)
    :param y:

    """
    if isinstance(x, (typing.Type)) and issubclass(x, y):
        if strict and x == y:
            return False
        return True
    return False


class classproperty:
    """ """

    def __init__(self, fxn):
        self.fxn = fxn

    def __get__(self, obj, owner) -> typing.OptionalAny:
        return self.fxn(owner)


class classproperty_cached(classproperty):
    """ """

    CLASSPROP_CACHES = {}

    def __get__(self, obj, owner) -> typing.OptionalAny:
        result = self.__class__.CLASSPROP_CACHES.get(self.fxn, self.fxn(owner))
        self.__class__.CLASSPROP_CACHES[self.fxn] = result
        return self.__class__.CLASSPROP_CACHES[self.fxn]
