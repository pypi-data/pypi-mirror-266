""" pynchon.models.plugins.pynchon """

import collections

import fleks
import shimport
from fleks import tagging

from pynchon.plugins import util as plugins_util

from . import validators

from pynchon import abcs, api, cli, events  # noqa
from pynchon.util import lme, typing  # noqa


LOGGER = lme.get_logger(__name__)
classproperty = fleks.util.typing.classproperty
pydash = shimport.lazy("pydash")
config_mod = shimport.lazy("pynchon.config")


@tagging.tags(cli_label="<<Abstract>>")
class PynchonPlugin(fleks.Plugin):
    """Pynchon-specific plugin-functionality"""

    name = "<<Abstract>>"
    cli_label = "<<Abstract>>"
    cli_description = __doc__

    config_class = None
    __class_validators__ = [
        validators.require_conf_key,
        validators.warn_config_kls,
    ]

    @classproperty
    def siblings(kls) -> collections.OrderedDict:
        """
        Returns a dictionary of other plugins for this runtime
        """
        result = []
        from pynchon.plugins import registry

        for plugin in registry.keys():
            if plugin == kls.name:
                continue
            result.append(plugins_util.get_plugin_obj(plugin))
        result = sorted(result, key=lambda p: p.priority)

        class Siblings(collections.OrderedDict):
            def collect_config_list(self, key):
                """collects the named key across all sibling-plugins"""
                out = []
                for name, plugin_obj in self.items():
                    out += plugin_obj[key::[]]
                return out

            def collect_config_dict(self, key):
                """collects the named key across all sibling-plugins"""
                out = {}
                for name, plugin_obj in self.items():
                    out.update(plugin_obj[key::{}])
                return out

        return Siblings([p.name, p] for p in result)

    @classproperty
    def instance(kls):
        """Returns the (singleton) instance for this plugin"""
        return plugins_util.get_plugin_obj(kls.name)

    @classproperty
    def plugin_templates_prefix(kls):
        return f"pynchon/plugins/{kls.config_class.config_key}"

    @classproperty
    def plugin_templates_root(self):
        """ """
        return abcs.Path(self.plugin_templates_prefix)

    @classproperty
    def project_config(self):
        """
        Returns finalized config for the whole project
        """
        return api.project.get_config()

    @classmethod
    def get_config_key(kls):
        """
        Returns config key or (normalized) class-name
        """
        default = kls.name.replace("-", "_")
        config_kls = getattr(kls, "config_class", None)
        return getattr(config_kls, "config_key", default) or default

    @classmethod
    def get_current_config(kls):
        """
        Get the current config for this plugin
        """
        conf_class = getattr(kls, "config_class", None)
        if conf_class is None:
            return {}
        conf_key = kls.get_config_key()
        result = getattr(config_mod, conf_key)
        return result

    @property
    def project_root(self):
        proj_conf = self[:"project.subproject":{}] or self[:"project":]
        return proj_conf.get("root", None) or self[:"git.root":]

    @property
    def plugin_config(self):
        """ """
        return self.get_current_config()

    @property
    def config(self):
        """ """
        return self.cfg()

    def cfg(self):
        """Shows current config for this plugin"""
        kls = self.__class__
        conf_class = getattr(kls, "config_class", None)
        conf_class_name = conf_class.__name__ if conf_class else "(None)"
        LOGGER.debug(f"config class: {conf_class_name}")
        LOGGER.debug("current config:")
        result = kls.get_current_config()
        return result

    def __getitem__(self, key: str):
        """
        shortcut for accessing local plugin-config
        """
        if isinstance(key, (slice,)):

            start, stop, step = key.start, key.stop, key.step
            try:
                if start:
                    result = self[start]
                if stop:
                    result = self % stop
                result = result if result is not None else step
            except (KeyError,) as exc:
                if step is not None:
                    return step
                else:
                    raise
            else:
                return result
        else:
            try:
                return getattr(self.config, key)
            except (AttributeError,) as exc:
                try:
                    return self.config[key]
                except (KeyError,) as exc:
                    fallback = pydash.get(self.config, key)
                    if fallback:
                        return fallback
                    else:
                        raise

    def __floordiv__(self, key: str, strict=False):
        """

        :param key: str:
        :param strict: Default value = False)
        """
        # return self.__mod__(key, strict=strict)
        from pynchon import api

        assert key
        key = key[1:] if key.startswith("/") else key
        return api.render.get_template(f"{self.plugin_templates_prefix}/{key}")

    def __mod__(self, key: str, strict=True):
        """shortcut for accessing global pynchon-config

        :param key: str:
        :param strict: Default value = True)

        """
        try:
            return self.project_config[key]
        except (KeyError,) as exc:
            fallback = pydash.get(self.project_config, key, None)
            if fallback is not None:
                return fallback
            else:
                if strict:
                    raise
