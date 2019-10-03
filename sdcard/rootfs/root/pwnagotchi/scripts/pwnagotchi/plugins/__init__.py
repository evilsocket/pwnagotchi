import os
import glob
import importlib, importlib.util

default_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "default")
loaded = {}


def dummy_callback():
    pass


def on(event_name, *args, **kwargs):
    global loaded
    cb_name = 'on_%s' % event_name
    for _, plugin in loaded.items():
        if cb_name in plugin.__dict__:
            # print("calling %s %s(%s)" %(cb_name, args, kwargs))
            plugin.__dict__[cb_name](*args, **kwargs)


def load_from_file(filename):
    plugin_name = os.path.basename(filename.replace(".py", ""))
    spec = importlib.util.spec_from_file_location(plugin_name, filename)
    instance = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(instance)
    return plugin_name, instance


def load_from_path(path):
    global loaded

    for filename in glob.glob(os.path.join(path, "*.py")):
        name, plugin = load_from_file(filename)
        if name in loaded:
            raise Exception("plugin %s already loaded from %s" % (name, plugin.__file__))
        elif not plugin.__enabled__:
            # print("plugin %s is not enabled" % name)
            pass
        else:
            loaded[name] = plugin

    return loaded
