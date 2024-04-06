""" pynchon.app
"""

import sys
import atexit

import enlighten
from fleks import app as fleks_app
from fleks.app import AppBase, Console, Text, Theme
from memoized_property import memoized_property

from pynchon import events
from pynchon.util import lme

# from fleks.app import (AppBase, AppEvents)

LOGGER = lme.get_logger(__name__)


class AppEvents(AppBase):
    def __init__(self, **kwargs):
        """ """
        self.events = events


class AppConsole(fleks_app.AppBase):
    Text = Text
    Theme = Theme
    # docs = manager.term.link(
    #     'https://python-enlighten.readthedocs.io/en/stable/examples.html',
    #     'Read the Docs')

    def __init__(self, **kwargs):
        """ """
        self.console = Console()

    # # FIXME: use multi-dispatch over kwargs and define `lifecyle` repeatedly
    # def lifecycle_stage(self, sender, stage=None, **kwargs):
    #     """ """
    #     if stage:
    #         tmp = getattr(sender, '__name__', str(sender))
    #         # LOGGER.critical(f"STAGE ({tmp}): {stage}")
    #         self.status_bar.update(stage=stage)

    @memoized_property
    def status_bar(self):
        """ """
        tmp = self.manager.status_bar(
            status_format="{app}{fill}{stage}{fill}{elapsed}",
            color="bold_underline_bright_white_on_lightslategray",
            justify=enlighten.Justify.LEFT,
            app="Pynchon",
            stage="...",
            autorefresh=True,
            min_delta=0.1,
        )

        # atexit.register(
        #     lambda: self.events.lifecycle.send(
        #         self, stage=r"\o/" if not self.exc else "❌", msg=""
        #     )
        # )  # noqa: W605
        return tmp

    #
    # @memoized_property
    # def lifecycle_bar(self):
    #     """ """
    #     tmp = self.manager.status_bar(
    #         status_format=u'{fill}{msg}{fill}',
    #         color='bold_underline_bright_red_on_lightslategray',
    #         justify=enlighten.Justify.CENTER,
    #         msg='222',
    #         autorefresh=True,
    #         min_delta=0.1,
    #     )
    #
    #     atexit.register(
    #         lambda: self.events.lifecycle.send(self, msg="\o/")
    #     )  # noqa: W605
    #     return tmp

    @memoized_property
    def manager(self):
        tmp = enlighten.get_manager()
        atexit.register(lambda: self.manager.stop())
        return tmp


class AppExitHooks(fleks_app.AppBase):
    """ """

    exc = None
    hooks_installed = False
    # https://stackoverflow.com/questions/9741351/how-to-find-exit-code-or-reason-when-atexit-callback-is-called-in-python

    # def uninstall(self):
    def install_exit_hooks(self) -> None:
        if not self.hooks_installed:
            msg = "Installing exit handlers"
            LOGGER.critical(msg)
            self.events.lifecycle.send(self, msg=msg)
            self._sys_exit = sys.exit
            self._orig_exc_handler = sys.excepthook
            sys.exit = self.exit
            sys.excepthook = self.exc_handler
            atexit.register(self.exit_handler)
            self.hooks_installed = True

    def exit(self, code=0):
        self.exit_code = code
        self._sys_exit(code)

    def exc_handler(self, exc_type, exc, *args):
        self.exception = exc
        # import sys
        # ex_type, ex_value, traceback = sys.exc_info()
        # raise ex_type(ex_value)
        tmp = f"death by exc: ({self.exc})"
        self.events.lifecycle.send(self, stage=tmp)
        return self._orig_exc_handler(exc_type, exc, *args)

    def sys_exit_handler(self):
        if self.exit_code is not None and not self.exit_code == 0:
            tmp = f"death by sys.exit({self.exit_code})"
            self.events.lifecycle.send(self, stage=tmp)
            return True

    def exit_handler(self):
        """ """
        handled = self.sys_exit_handler()
        handled = handled or self.exc_exit_handler()
        handled = handled or self.default_exit_handler()
        return handled

    def exc_exit_handler(self):
        """ """
        if self.exception is not None:
            text = f"exc_exit_handler: {self.exception}"
            LOGGER.critical(text)
            text = self.Text(text)
            text.stylize("bold red", 0, 6)
            self.console.print(text)
            self.events.lifecycle.send(self, stage="❌")
            return True

    def default_exit_handler(self):
        """ """
        exc = self.exception
        if exc:
            LOGGER.critical(f"default_exit_handler: encountered exception: {exc}")
            self.events.lifecycle.send(self, stage="❌")
        else:
            pass
            # LOGGER.critical(f"default_exit_handler: "+r"\o/")
            # self.events.lifecycle.send(self, stage=r"\o/")
            # self.status_bar.update(stage=r"\o/", msg="", force=True)
            # import IPython; IPython.embed()
            # LOGGER.critical("exit ok")
        return True


class App(AppConsole, AppEvents, AppExitHooks):
    def __init__(self, **kwargs):
        """ """
        AppConsole.__init__(self, **kwargs)
        AppEvents.__init__(self, **kwargs)
        self.exit_code = None
        self.exception = None
        self.install_exit_hooks()
        # self.logger = ..


app = App()
