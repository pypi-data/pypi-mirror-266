""" pynchon.cli.common:
    Common options/arguments and base classes for CLI
"""

import json
import functools

import shimport
from fleks.cli import click

from pynchon.util import lme, text, typing  # noqa

LOGGER = lme.get_logger(__name__)


def load_groups_from_children(root=None, parent=None):
    """ """
    shimport.wrap(root).filter_folder(include_main=True).prune(
        name_is="entry",  # default
    ).map(
        lambda ch: [
            ch.name.replace(".__main__", "").split(".")[-1],
            ch.namespace["entry"],
        ]
    ).starmap(
        lambda name, fxn: [
            setattr(fxn, "name", name),
            click.group_merge(fxn, parent),
        ]
    )


def entry_for(
    name,
):
    """ """
    # from pynchon import shimport
    import importlib

    unf = importlib.import_module(name)
    mdoc = unf.__doc__

    def entry() -> typing.NoneType:
        pass

    entry.__doc__ = (mdoc or "").lstrip().split("\n")[0]

    class Groop(click.Group):
        pass

    entry = click.group(name.split(".")[-1], cls=Groop)(entry)
    return entry


class kommand:
    """ """

    is_group = False

    def __init__(
        self,
        name=None,
        parent=None,
        arguments=[],
        alias=None,
        options=[],
        transformers=[],
        handlers=[],
        formatters={},
        cls=None,
        help=None,
        **click_kwargs,
    ):
        self.name = name
        self.alias = alias
        self.parent = parent or click
        self.options = options
        self.arguments = arguments
        self.click_kwargs = click_kwargs
        self.formatters = {**formatters, **dict(json=self.format_json)}
        self.transformers = sorted(
            transformers,
            key=lambda t: t.priority,
        )
        self.handlers = sorted(
            handlers
            + [
                # output_handler(parent=self),
                # stdout_handler(parent=self),
            ],
            key=lambda h: h.priority,
        )
        cls and click_kwargs.update(cls=cls)
        help and click_kwargs.update(help=help.lstrip())
        if not self.is_group:
            self.cmd = self.parent.command(self.name, **click_kwargs)
        else:
            self.cmd = self.parent.group(self.name, **click_kwargs)
        self.cmd.alias = alias
        self.logger = lme.get_logger(f"cmd[{name}]")

    def format_json(self, result):
        """ """
        self.logger.debug("Formatter for: `json`")
        return json.dumps(result, indent=2)

    def wrapper(self, *args, **call_kwargs):
        assert self.fxn

        @functools.wraps(self.fxn)
        def newf(*args, **call_kwargs):
            self.logger.info(f"Wrapping invocation: {self.parent.name}.{self.name}")
            call_kwargs and self.logger.debug(f" with: {call_kwargs}")
            result = self.fxn(*args, **call_kwargs)
            if result is not None:
                result and LOGGER.info(f"json conversion for type: {type(result)}")
                import rich

                tmp = text.to_json(result)
                # raise Exception('bonk')
                rich.print(tmp)
            return result

        return newf

    def __call__(self, fxn: typing.Callable):
        self.fxn = fxn
        assert fxn, "function cannot be None!"

        f = self.cmd(self.wrapper())
        tmp = [x.strip() for x in (f.help or fxn.__doc__ or "").split("\n")]
        f.help = " ".join(tmp).lstrip()

        for opt in self.options:
            f = opt(f)
        for arg in self.arguments:
            f = arg(f)
        return f


def create_command(_name: str, fxn: typing.Callable, entry=None):
    """
    FIXME: move to fleks?
    WARNING: do not change signature.  this function is used
    with `shimport.wrapper().map(...)` so it must accept
    (key,value) style arguments.
    """
    from fleks.util.tagging import tags

    out = []
    aliases = tags[fxn].get("click_aliases", []) + [fxn.__name__]
    for alias in aliases:
        out.append(
            kommand(
                name=alias.replace("_", "-"),
                parent=entry,
                help=(
                    fxn.__doc__
                    if alias == fxn.__name__
                    else f"Alias for `{fxn.__name__}`"
                ),
            )(fxn)
        )
    return out


class groop(kommand):
    """# class BetterGroup(click.Group):
    #     def format_usage(self,ctx,formatter):
    #         super(BetterGroup,self).format_usage(ctx,formatter)
    #     def format_epilog(self,ctx,formatter):
    #         return super(BetterGroup,self).format_epilog(ctx,formatter)
    #     def format_help(self, ctx, formatter):
    #         super(BetterGroup,self).format_help(ctx,formatter)
    #     def format_options(self,ctx,formatter):
    #         super(BetterGroup,self).format_options(ctx,formatter)
    #     def format_help_text(self,ctx,formatter):
    #         super(BetterGroup,self).format_help_text(ctx,formatter)
    """

    is_group = True
