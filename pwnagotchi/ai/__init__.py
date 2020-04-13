import os
import time
import logging

# https://stackoverflow.com/questions/40426502/is-there-a-way-to-suppress-the-messages-tensorflow-prints/40426709
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}


def load(config, agent, epoch, from_disk=True):
    config = config['ai']
    if not config['enabled']:
        logging.info("ai disabled")
        return False

    try:
        begin = time.time()

        logging.info("[ai] bootstrapping dependencies ...")

        start = time.time()
        from stable_baselines import A2C
        logging.debug("[ai] A2C imported in %.2fs" % (time.time() - start))

        start = time.time()
        from stable_baselines.common.policies import MlpLstmPolicy
        logging.debug("[ai] MlpLstmPolicy imported in %.2fs" % (time.time() - start))

        start = time.time()
        from stable_baselines.common.vec_env import DummyVecEnv
        logging.debug("[ai] DummyVecEnv imported in %.2fs" % (time.time() - start))

        start = time.time()
        import pwnagotchi.ai.gym as wrappers
        logging.debug("[ai] gym wrapper imported in %.2fs" % (time.time() - start))

        env = wrappers.Environment(agent, epoch)
        env = DummyVecEnv([lambda: env])

        logging.info("[ai] creating model ...")

        start = time.time()
        a2c = A2C(MlpLstmPolicy, env, **config['params'])
        logging.debug("[ai] A2C created in %.2fs" % (time.time() - start))

        if from_disk and os.path.exists(config['path']):
            logging.info("[ai] loading %s ..." % config['path'])
            start = time.time()
            a2c.load(config['path'], env)
            logging.debug("[ai] A2C loaded in %.2fs" % (time.time() - start))
        else:
            logging.info("[ai] model created:")
            for key, value in config['params'].items():
                logging.info("      %s: %s" % (key, value))

        logging.debug("[ai] total loading time is %.2fs" % (time.time() - begin))

        return a2c
    except Exception as e:
        logging.exception("error while starting AI (%s)", e)

    logging.warning("[ai] AI not loaded!")
    return False
