""" {{pkg}}.util.types

This module collects common imports and annotation-types, i.e.
various optional/composite types used in type-hints, underneath
one convenient namespace.
"""

import typing
from pathlib import Path as BasePath

from fleks.util.typing import *  # noqa

validate = validate_arguments


def bind_method(func, instance, as_name=None):
    """
    Binds the function *func* to *instance*, with either provided name *as_name*
    or the existing name of *func*. The provided *func* should accept the
    instance as the first argument, i.e. "self".

    :param instance: param func:
    :param as_name: Default value = None)
    :param func:
    """
    assert isinstance(func, (FunctionType,))
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method


OptionalAny = typing.Optional[typing.Any]
PathType = type(BasePath())

Bool = bool
NoneType = type(None)
BoolMaybe = typing.Optional[bool]
StringMaybe = typing.Optional[str]
CallableMaybe = typing.Optional[typing.Callable]
DictMaybe = typing.Optional[typing.Dict]
TagDict = typing.Dict[str, str]


Namespace = typing.Dict[str, typing.Any]
CallableNamespace = typing.Dict[str, typing.Callable]

# i.e. `obj,created = model.objects.get_or_create()`
GetOrCreateResult = typing.Tuple[object, bool]
