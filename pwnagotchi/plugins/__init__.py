import os
import glob
import _thread
import importlib, importlib.util
import logging

default_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "default")
loaded = {}


class Plugin:
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        global loaded
        plugin_name = cls.__module__.split('.')[0]
        plugin_instance = cls()
        logging.debug("loaded plugin %s as %s" % (plugin_name, plugin_instance))
        loaded[plugin_name] = plugin_instance


def on(event_name, *args, **kwargs):
    for plugin_name, plugin in loaded.items():
        one(plugin_name, event_name, *args, **kwargs)


def one(plugin_name, event_name, *args, **kwargs):
    global loaded
    if plugin_name in loaded:
        plugin = loaded[plugin_name]
        cb_name = 'on_%s' % event_name
        callback = getattr(plugin, cb_name, None)
        if callback is not None and callable(callback):
            try:
                _thread.start_new_thread(callback, (*args, *kwargs))
            except Exception as e:
                logging.error("error while running %s.%s : %s" % (plugin_name, cb_name, e))
                logging.error(e, exc_info=True)


def load_from_file(filename):
    logging.debug("loading %s" % filename)
    plugin_name = os.path.basename(filename.replace(".py", ""))
    spec = importlib.util.spec_from_file_location(plugin_name, filename)
    instance = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(instance)
    return plugin_name, instance


def load_from_path(path, enabled=()):
    global loaded
    logging.debug("loading plugins from %s - enabled: %s" % (path, enabled))
    for filename in glob.glob(os.path.join(path, "*.py")):
        plugin_name = os.path.basename(filename.replace(".py", ""))
        if plugin_name in enabled:
            try:
                load_from_file(filename)
            except Exception as e:
                logging.warning("error while loading %s: %s" % (filename, e))
                logging.debug(e, exc_info=True)

    return loaded


def load(config):
    enabled = [name for name, options in config['main']['plugins'].items() if
               'enabled' in options and options['enabled']]

    # load default plugins
    load_from_path(default_path, enabled=enabled)

    # load custom ones
    custom_path = config['main']['custom_plugins'] if 'custom_plugins' in config['main'] else None
    if custom_path is not None:
        load_from_path(custom_path, enabled=enabled)

    # propagate options
    for name, plugin in loaded.items():
        plugin.options = config['main']['plugins'][name]

    on('loaded')
