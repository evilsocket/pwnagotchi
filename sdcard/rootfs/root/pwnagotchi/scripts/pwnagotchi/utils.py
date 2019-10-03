import yaml
import os

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