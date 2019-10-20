import os
import shutil
import yaml
import pwnagotchi
from pwnagotchi.utils import RWLock
from pwnagotchi.utils import deep_merge


class SharedConfig:
    """
    This class holds the pwnagotchi config.
    It safes all configs on - class level (_data) - which means,
    that each instance of this class will have the same config.

    It uses a read-write-lock to be thread safe.
    """

    _instance = None
    _data = dict()
    _lock = RWLock()

    @staticmethod
    def copy():
        """
        Returns a copy of the internal dict
        """
        return SharedConfig._data.copy()

    @staticmethod
    def get_instance():
        """
        Return the created instance of the config
        """
        return SharedConfig._instance

    def __init__(self, *args, **kwargs):
        """
        This will clean the whole config (if clear=True)
        and use the given values
        """
        with SharedConfig._lock.write():
            SharedConfig._data.clear()
            for arg in args:
                if isinstance(arg, dict):
                    for key, value in arg.items():
                        SharedConfig._data[key] = value

            if kwargs:
                for key, value in kwargs.items():
                    SharedConfig._data[key] = value

    def __getattr__(self, attr):
        with SharedConfig._lock.read():
            return SharedConfig._data.get(attr)

    def __setattr__(self, key, value):
        with SharedConfig._lock.write():
            SharedConfig._data.__setitem__(key, value)

    def __setitem__(self, key, value):
        with SharedConfig._lock.write():
            SharedConfig._data.__setitem__(key, value)

    def __delattr__(self, item):
        with SharedConfig._lock.write():
            SharedConfig._data.__delitem__(item)

    def __delitem__(self, key):
        with SharedConfig._lock.write():
            SharedConfig._data.__delitem__(key)

    def __getitem__(self, key):
        with SharedConfig._lock.read():
            return SharedConfig._data.__getitem__(key)

    def __str__(self):
        with SharedConfig._lock.read():
            return SharedConfig._data.__str__()

    def __repr__(self):
        with SharedConfig._lock.read():
            return SharedConfig._data.__repr__()

    @staticmethod
    def load_from_args(args):
        default_config_path = os.path.dirname(args.config)
        if not os.path.exists(default_config_path):
            os.makedirs(default_config_path)

        ref_defaults_file = os.path.join(os.path.dirname(pwnagotchi.__file__), 'defaults.yml')
        ref_defaults_data = None

        # check for a config.yml file on /boot/
        if os.path.exists("/boot/config.yml"):
            # logging not configured here yet
            print("installing /boot/config.yml to %s ...", args.user_config)
            # https://stackoverflow.com/questions/42392600/oserror-errno-18-invalid-cross-device-link
            shutil.move("/boot/config.yml", args.user_config)

        # if not config is found, copy the defaults
        if not os.path.exists(args.config):
            print("copying %s to %s ..." % (ref_defaults_file, args.config))
            shutil.copy(ref_defaults_file, args.config)
        else:
            # check if the user messed with the defaults
            with open(ref_defaults_file) as fp:
                ref_defaults_data = fp.read()

            with open(args.config) as fp:
                defaults_data = fp.read()

            if ref_defaults_data != defaults_data:
                print("!!! file in %s is different than release defaults, overwriting !!!" % args.config)
                shutil.copy(ref_defaults_file, args.config)

        # load the defaults
        with open(args.config) as fp:
            config = yaml.safe_load(fp)

        # load the user config
        if os.path.exists(args.user_config):
            with open(args.user_config) as fp:
                user_config = yaml.safe_load(fp)
                # if the file is empty, safe_load will return None and merge_config will boom.
                if user_config:
                    config = deep_merge(user_config, config)

        # the very first step is to normalize the display name so we don't need dozens of if/elif around
        if config['ui']['display']['type'] in ('inky', 'inkyphat'):
            config['ui']['display']['type'] = 'inky'

        elif config['ui']['display']['type'] in ('papirus', 'papi'):
            config['ui']['display']['type'] = 'papirus'

        elif config['ui']['display']['type'] in ('oledhat'):
            config['ui']['display']['type'] = 'oledhat'

        elif config['ui']['display']['type'] in ('ws_1', 'ws1', 'waveshare_1', 'waveshare1'):
            config['ui']['display']['type'] = 'waveshare_1'

        elif config['ui']['display']['type'] in ('ws_2', 'ws2', 'waveshare_2', 'waveshare2'):
            config['ui']['display']['type'] = 'waveshare_2'
        elif config['ui']['display']['type'] in ('ws_27inch', 'ws27inch', 'waveshare_27inch', 'waveshare27inch'):
            config['ui']['display']['type'] = 'waveshare27inch'
        else:
            print("unsupported display type %s" % config['ui']['display']['type'])
            exit(1)

        print("Effective Configuration:")
        print(yaml.dump(config, default_flow_style=False))

        SharedConfig._instance = SharedConfig(config)

        return SharedConfig.get_instance()
