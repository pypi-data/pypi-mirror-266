""" pynchon.util.events """

import functools
import collections

EventType = collections.namedtuple("Event", "type msg data")
LifeCycle = functools.partial(EventType, type="app-lifecycle")
ConfigFinalized = functools.partial(EventType, type="config-finalized")
PluginFinalized = functools.partial(EventType, type="plugin-finalized")


class Engine:
    """ """

    def push(self, **kwargs):
        event = EventType(**kwargs)
        raise NotImplementedError(event)

    def subscribe(self, fxn, type: str = None):
        """

        :param fxn: param type: str:  (Default value = None)
        :param type: str:  (Default value = None)

        """


DEFAULT_ENGINE = Engine()
push = DEFAULT_ENGINE.push
