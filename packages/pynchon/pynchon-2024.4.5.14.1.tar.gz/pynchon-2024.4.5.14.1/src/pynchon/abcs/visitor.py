""" pynchon.abcs.visitor
"""

import copy
from types import MappingProxyType

import pydash

from pynchon import abcs
from pynchon.util import lme

LOGGER = lme.get_logger(__name__)


class Visitor:
    def __init__(
        self,
        filter_path=lambda _: True,
        filter_value=lambda _: True,
        trigger=lambda p, v: (p, v),
        paths=[],
        obj=None,
        **kwargs,
    ):
        self.conf = kwargs
        self.filter_path = filter_path
        self.filter_value = filter_value
        self.trigger = trigger

    def matched(self, path=None, value=None):
        """
        :param path: Default value = None)
        :param value: Default value = None)
        """
        default = self.trigger(path, value)
        if "accumulate_paths" in self.conf:
            return path
        elif "accumulate_values" in self.conf:
            return value
        else:
            return default

    def __call__(
        self,
        path=None,
        value=None,
    ):
        """
        :param path: Default value = None)
        :param value: Default value = None)
        """
        if all([self.filter_path(path), self.filter_value(value)]):
            return self.matched(path=path, value=value)


def traverse(obj, visitor=None, visitor_kls=None, visitor_kwargs={}):
    """# example `visitor`:
    #
    # def visit(value=None, path=None):
    #     LOGGER.debug(f"[{path}: {value}]")
    #     return value

    :param obj: param visitor:  (Default value = None)
    :param visitor_kls: Default value = None)
    :param visitor_kwargs: Default value = {})
    :param visitor:  (Default value = None)

    """
    assert bool(visitor) ^ bool(visitor_kls) ^ bool(visitor_kwargs)
    paths = []

    def travel(arg=obj, path="", paths=[]):
        if isinstance(arg, (list, tuple)):
            for i, item in enumerate(arg):
                path_key = f"{path}.{i}"
                paths += [path_key]
                travel(item, path=path_key)
        if isinstance(arg, (dict,)):
            for k, v in arg.items():
                path_key = f"{path}.{k}"
                paths += [path_key]
                travel(v, path=path_key)
        paths = sorted(list(set(paths)))
        return paths

    paths = travel()
    result = dict(paths=paths, obj=obj)
    if visitor_kwargs and not visitor_kls:
        visitor_kls = Visitor
    if visitor_kls:
        assert not visitor
        visitor = visitor_kls(**{**result, **visitor_kwargs})
    visits = []
    if visitor is not None:
        for path in paths:
            visitation = visitor(path=path, value=pydash.get(obj, path))
            visitation and visits.append(visitation)
    result.update(
        # visitor=visitor,
        visits=visits
    )
    result = abcs.AttrDict(**result)
    return result


class TemplatedDict(dict):
    """ """

    def __init__(self, dct):
        """

        :param dct:

        """
        super().__init__(dct.copy())
        self.logger = lme.get_logger(self.__class__.__name__)

    def get_path(self, path):
        """

        :param path:

        """
        return pydash.get(self, path)

    def set_path(self, path, val):
        """

        :param path: param val:
        :param val:

        """
        return pydash.set_with(self, path, val)

    @property
    def traversal(self):
        """ """
        traversed = traverse(
            self,
            visitor_kwargs=dict(filter_value=self.is_templated, accumulate_paths=True),
        )
        return traversed

    @property
    def unresolved(self):
        """ """
        return self.traversal.visits


import jinja2

# from pynchon.api.render import UndefinedError


class JinjaDict(TemplatedDict):
    """ """

    def render(self, ctx={}):
        """
        :param ctx: Default value = {})
        """
        tmp = copy.deepcopy(self)
        while tmp.unresolved:
            templated = tmp.unresolved
            self.logger.debug(f"remaining unresolved: {len(templated)}")
            for i, path in enumerate(templated):
                templated.pop(i)
                val = self.get_path(path)
                try:
                    x = tmp.render_path(path, ctx=ctx)
                    rspec = dict(resolution=x, path=path, value=val)
                    LOGGER.info(rspec)
                except (jinja2.exceptions.UndefinedError,) as exc:
                    self.logger.debug(f"resolution for {path}@`{val}` failed ({exc})")
                    self.logger.debug(exc)
                    # self.logger.debug(f"self: {tmp}")
                    # self.logger.debug(f"ctx: {ctx}")
                    templated.append(path)
                else:
                    break
            else:
                break
        return MappingProxyType(tmp)

    def render_path(self, path, ctx={}, strict=False):
        """

        :param path: param ctx:  (Default value = {})
        :param strict: Default value = False)
        :param ctx:  (Default value = {})

        """
        # from pynchon.api import render
        from pynchon.util.text import render

        strict and True
        value = self.get_path(path)
        resolved = render.jinja(
            text=value,
            context={**self, **ctx},
            # includes=[],
        )
        self.set_path(path, resolved)
        return resolved

    def is_templated(self, v):
        """

        :param v:

        """
        return isinstance(v, (str,)) and "{{" in v
