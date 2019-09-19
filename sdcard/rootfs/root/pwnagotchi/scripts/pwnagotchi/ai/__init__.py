import os

# https://stackoverflow.com/questions/40426502/is-there-a-way-to-suppress-the-messages-tensorflow-prints/40426709
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
import warnings

# https://stackoverflow.com/questions/15777951/how-to-suppress-pandas-future-warning
warnings.simplefilter(action='ignore', category=FutureWarning)

import core


def load(config, agent, epoch, from_disk=True):
    config = config['ai']
    if not config['enabled']:
        core.log("ai disabled")
        return False

    core.log("[ai] bootstrapping dependencies ...")

    from stable_baselines import A2C
    from stable_baselines.common.policies import MlpLstmPolicy
    from stable_baselines.common.vec_env import DummyVecEnv

    import pwnagotchi.ai.gym as wrappers

    env = wrappers.Environment(agent, epoch)
    env = DummyVecEnv([lambda: env])

    core.log("[ai] bootstrapping model ...")

    a2c = A2C(MlpLstmPolicy, env, **config['params'])

    if from_disk and os.path.exists(config['path']):
        core.log("[ai] loading %s ..." % config['path'])
        a2c.load(config['path'], env)
    else:
        core.log("[ai] model created:")
        for key, value in config['params'].items():
            core.log("      %s: %s" % (key, value))

    return a2c
