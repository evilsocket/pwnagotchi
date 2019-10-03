import yaml
import os
import logging


# https://stackoverflow.com/questions/823196/yaml-merge-in-python
def merge_config(user, default):
    if isinstance(user, dict) and isinstance(default, dict):
        for k, v in default.items():
            if k not in user:
                user[k] = v
            else:
                user[k] = merge_config(user[k], v)
    return user


def load_config(args):
    with open(args.config, 'rt') as fp:
        config = yaml.safe_load(fp)

    if os.path.exists(args.user_config):
        with open(args.user_config, 'rt') as fp:
            user_config = yaml.safe_load(fp)
            config = merge_config(user_config, config)

    return config


def setup_logging(args, config):
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    root = logging.getLogger()

    root.setLevel(logging.DEBUG if args.debug else logging.INFO)

    if config['main']['log']:
        file_handler = logging.FileHandler(config['main']['log'])
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)
