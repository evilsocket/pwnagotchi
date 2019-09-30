import _thread
import threading
import time
import random
import os
import json

import core

import pwnagotchi.ai as ai
from pwnagotchi.ai.epoch import Epoch


class Stats(object):
    def __init__(self, path, events_receiver):
        self._lock = threading.Lock()
        self._receiver = events_receiver

        self.path = path
        self.born_at = time.time()
        # total epochs lived (trained + just eval)
        self.epochs_lived = 0
        # total training epochs
        self.epochs_trained = 0

        self.worst_reward = 0.0
        self.best_reward = 0.0

        self.load()

    def on_epoch(self, data, training):
        best_r = False
        worst_r = False
        with self._lock:
            reward = data['reward']
            if reward < self.worst_reward:
                self.worst_reward = reward
                worst_r = True

            elif reward > self.best_reward:
                best_r = True
                self.best_reward = reward

            self.epochs_lived += 1
            if training:
                self.epochs_trained += 1

        self.save()

        if best_r:
            self._receiver.on_ai_best_reward(reward)
        elif worst_r:
            self._receiver.on_ai_worst_reward(reward)

    def load(self):
        with self._lock:
            if os.path.exists(self.path) and os.path.getsize(self.path) > 0:
                core.log("[ai] loading %s" % self.path)
                with open(self.path, 'rt') as fp:
                    obj = json.load(fp)

                self.born_at = obj['born_at']
                self.epochs_lived, self.epochs_trained = obj['epochs_lived'], obj['epochs_trained']
                self.best_reward, self.worst_reward = obj['rewards']['best'], obj['rewards']['worst']

    def save(self):
        with self._lock:
            core.log("[ai] saving %s" % self.path)
            with open(self.path, 'wt') as fp:
                json.dump({
                    'born_at': self.born_at,
                    'epochs_lived': self.epochs_lived,
                    'epochs_trained': self.epochs_trained,
                    'rewards': {
                        'best': self.best_reward,
                        'worst': self.worst_reward
                    }
                }, fp)


class AsyncTrainer(object):
    def __init__(self, config):
        self._config = config
        self._model = None
        self._epoch = Epoch(config)
        self._is_training = False
        self._training_epochs = 0
        self._nn_path = self._config['ai']['path']
        self._stats = Stats("%s.json" % os.path.splitext(self._nn_path)[0], self)

    def set_training(self, training, for_epochs=0):
        self._is_training = training
        self._training_epochs = for_epochs

    def is_training(self):
        return self._is_training

    def training_epochs(self):
        return self._training_epochs

    def start_ai(self):
        _thread.start_new_thread(self._ai_worker, ())

    def _save_ai(self):
        core.log("[ai] saving model to %s ..." % self._nn_path)
        self._model.save(self._nn_path)

    def on_ai_step(self):
        self._model.env.render()

        if self._is_training:
            self._save_ai()

        self._stats.on_epoch(self._epoch.data(), self._is_training)

    def on_ai_training_step(self, _locals, _globals):
        self._model.env.render()

    def on_ai_policy(self, new_params):
        core.log("[ai] setting new policy:")
        for name, value in new_params.items():
            if name in self._config['personality']:
                curr_value = self._config['personality'][name]
                if curr_value != value:
                    core.log("[ai] ! %s: %s -> %s" % (name, curr_value, value))
                    self._config['personality'][name] = value
            else:
                core.log("[ai] param %s not in personality configuration!" % name)

        self.run('set wifi.ap.ttl %d' % self._config['personality']['ap_ttl'])
        self.run('set wifi.sta.ttl %d' % self._config['personality']['sta_ttl'])
        self.run('set wifi.rssi.min %d' % self._config['personality']['min_rssi'])

    def on_ai_best_reward(self, r):
        core.log("[ai] best reward so far: %s" % r)
        self._view.on_motivated(r)

    def on_ai_worst_reward(self, r):
        core.log("[ai] worst reward so far: %s" % r)
        self._view.on_demotivated(r)

    def _ai_worker(self):
        self._model = ai.load(self._config, self, self._epoch)

        if self._model:
            self.on_ai_ready()

            epochs_per_episode = self._config['ai']['epochs_per_episode']

            obs = None
            while True:
                self._model.env.render()
                # enter in training mode?
                if random.random() > self._config['ai']['laziness']:
                    core.log("[ai] learning for %d epochs ..." % epochs_per_episode)
                    try:
                        self.set_training(True, epochs_per_episode)
                        self._model.learn(total_timesteps=epochs_per_episode, callback=self.on_ai_training_step)
                    except Exception as e:
                        core.log("[ai] error while training: %s" % e)
                    finally:
                        self.set_training(False)
                        obs = self._model.env.reset()
                # init the first time
                elif obs is None:
                    obs = self._model.env.reset()

                # run the inference
                action, _ = self._model.predict(obs)
                obs, _, _, _ = self._model.env.step(action)
