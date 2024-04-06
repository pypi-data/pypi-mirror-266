""" pynchon.util.text.normalize """

import re

from pynchon.util import typing


def snake_case(name: str) -> str:
    """

    :param name: str:
    :param name: str:

    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


DEFAULT_NORMALIZATION_RULES = {" ": "_", "/": "_", "-": "_"}


def normalize(
    txt: str = "",
    post: typing.List[typing.Callable] = [
        lambda _: _.lower(),
        lambda _: re.sub("_+", "_", _),
    ],
    rules: typing.List[typing.Callable] = DEFAULT_NORMALIZATION_RULES,
) -> str:
    """normalizes input text, with support for parametric rules/post-processing

    :param txt: str:  (Default value = "")
    :param post: typing.List[typing.Callable]:  (Default value = [lambda _: _.lower())
    :param lambda: _: re.sub('_+':
    :param txt: str:  (Default value = "")
    :param post: typing.List[typing.Callable]:  (Default value = [lambda _: _.lower())
    :param lambda _: re.sub('_+':
    :param '_':
    :param _):
    :param ]:
    :param rules: typing.List[typing.Callable]:  (Default value = DEFAULT_NORMALIZATION_RULES)

    """
    tmp = txt
    for k, v in rules.items():
        tmp = tmp.replace(k, v)
    for fxn in post:
        tmp = fxn(tmp)
    return tmp
