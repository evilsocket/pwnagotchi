import os
import glob
import _thread
import threading
import importlib, importlib.util
import logging



default_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "default")
loaded = {}
database = {}
locks = {}


class Plugin:
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        global loaded, locks

        plugin_name = cls.__module__.split('.')[0]
        plugin_instance = cls()
        logging.debug("loaded plugin %s as %s" % (plugin_name, plugin_instance))
        loaded[plugin_name] = plugin_instance

        for attr_name in plugin_instance.__dir__():
            if attr_name.startswith('on_'):
                cb = getattr(plugin_instance, attr_name, None)
                if cb is not None and callable(cb):
                    locks["%s::%s" % (plugin_name, attr_name)] = threading.Lock()


def toggle_plugin(name, enable=True):
    """
    Load or unload a plugin

    returns True if changed, otherwise False
    """
    import pwnagotchi
    from pwnagotchi.ui import view
    from pwnagotchi.utils import save_config

    global loaded, database

    if pwnagotchi.config:
        if not name in pwnagotchi.config['main']['plugins']:
            pwnagotchi.config['main']['plugins'][name] = dict()
        pwnagotchi.config['main']['plugins'][name]['enabled'] = enable
        save_config(pwnagotchi.config, '/etc/pwnagotchi/config.toml')

    if not enable and name in loaded:
        if getattr(loaded[name], 'on_unload', None):
            loaded[name].on_unload(view.ROOT)
        del loaded[name]

        return True

    if enable and name in database and name not in loaded:
        load_from_file(database[name])
        if name in loaded and pwnagotchi.config and name in pwnagotchi.config['main']['plugins']:
            loaded[name].options = pwnagotchi.config['main']['plugins'][name]
        one(name, 'loaded')
        if pwnagotchi.config:
            one(name, 'config_changed', pwnagotchi.config)
        one(name, 'ui_setup', view.ROOT)
        one(name, 'ready', view.ROOT._agent)
        return True

    return False


def on(event_name, *args, **kwargs):
    for plugin_name in loaded.keys():
        one(plugin_name, event_name, *args, **kwargs)


def locked_cb(lock_name, cb, *args, **kwargs):
    global locks

    if lock_name not in locks:
        locks[lock_name] = threading.Lock()

    with locks[lock_name]:
        cb(*args, *kwargs)


def one(plugin_name, event_name, *args, **kwargs):
    global loaded

    if plugin_name in loaded:
        plugin = loaded[plugin_name]
        cb_name = 'on_%s' % event_name
        callback = getattr(plugin, cb_name, None)
        if callback is not None and callable(callback):
            try:
                lock_name = "%s::%s" % (plugin_name, cb_name)
                locked_cb_args = (lock_name, callback, *args, *kwargs)
                _thread.start_new_thread(locked_cb, locked_cb_args)
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
    global loaded, database
    logging.debug("loading plugins from %s - enabled: %s" % (path, enabled))
    for filename in glob.glob(os.path.join(path, "*.py")):
        plugin_name = os.path.basename(filename.replace(".py", ""))
        database[plugin_name] = filename
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
    on('config_changed', config)
