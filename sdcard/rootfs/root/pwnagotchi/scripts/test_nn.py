#!/usr/bin/python3
import os

# https://stackoverflow.com/questions/40426502/is-there-a-way-to-suppress-the-messages-tensorflow-prints/40426709
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}

import warnings

# https://stackoverflow.com/questions/15777951/how-to-suppress-pandas-future-warning
warnings.simplefilter(action='ignore', category=FutureWarning)

import time
import random

print("loading dependencies ...")

start = time.time()

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import A2C

quit()

import pwnagotchi.mesh.wifi as wifi
import pwnagotchi.ai.gym as wrappers

print("deps loaded in %ds" % (time.time() - start))
print()


class EpochMock(object):
    def __init__(self):
        self.epoch = 0

    def wait_for_epoch_data(self, timeout=None):
        duration = random.randint(5, 60)
        slept = random.randint(0, duration)

        tot_epochs = self.epoch + 1

        num_active = random.randint(0, tot_epochs)
        num_inactive = tot_epochs - num_active

        tot_interactions = random.randint(0, 100)
        missed = random.randint(0, int(tot_interactions / 10))
        num_deauth = random.randint(0, tot_interactions - missed)
        num_assocs = tot_interactions - num_deauth

        # time.sleep(duration)

        data = {
            'aps_histogram': [random.random() for c in range(0, wifi.NumChannels)],
            'sta_histogram': [random.random() for c in range(0, wifi.NumChannels)],
            'peers_histogram': [random.random() for c in range(0, wifi.NumChannels)],

            'duration_secs': duration,
            'slept_for_secs': slept,
            'blind_for_epochs': random.randint(0, 5),
            'inactive_for_epochs': num_inactive,
            'active_for_epochs': num_active,
            'missed_interactions': missed,
            'num_hops': random.randint(1, wifi.NumChannels),
            'num_deauths': num_deauth,
            'num_associations': num_assocs,
            'num_handshakes': random.randint(0, tot_interactions),
            'cpu_load': .5 + random.random(),
            'mem_usage': .5 + random.random(),
            'temperature': random.randint(40, 60)
        }

        self.epoch += 1
        return data


epoch_mock = EpochMock()
env = wrappers.Environment(epoch_mock)
env = DummyVecEnv([lambda: env])

print("learning from random data ...")

model = A2C(MlpPolicy, env, verbose=1)
model.learn(total_timesteps=10)

model.save("test.nn")

print("running ...")
obs = env.reset()
for i in range(1000):
    env.render()
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()

"""
memory = Memory()

state = env.reset()

for i in range(0, 10):
    env.render()
    policy = env.action_space.sample()

    next_state, reward, done, info = env.step(policy)

    if done:
        next_state = np.zeros(state.shape)
        memory.add((state, policy, reward, next_state))

        env.reset()

        state, reward, done, info = env.step(env.action_space.sample())
    else:
        memory.add((state, policy, reward, next_state))
        state = next_state
"""

"""
import numpy as np

import pwnagotchi.ai.nn as nn


def on_epoch(epoch, epoch_time, train_accu, valid_accu):
    print("epoch:%d duration:%f t_accu:%f v_accu:%f" % (epoch, epoch_time, train_accu, valid_accu))
    if valid_accu >= 0.98:
        return True


x = []
y = []

with open('nn-data.csv', 'rt') as fp:
    for line in fp:
        line = line.strip()
        if line != "":
            v = np.asarray(list(map(float, line.split(','))))
            x.append(v[1:])
            y.append(v[0])

x = np.asarray(x)
y = np.asarray(y)

num_inputs = len(x[0])
num_outputs = 2
valid_perc = 0.1
tot_samples = len(x)
valid_samples = int(tot_samples * valid_perc)
train_samples = tot_samples - valid_samples

print("loaded %d samples (inputs:%d train:%d validation:%d)" % (tot_samples, num_inputs, train_samples, valid_samples))

x_train = x[:train_samples]
y_train = y[:train_samples]
x_val = x[train_samples:]
y_val = y[train_samples:]

print("training ...")

net = nn.ANN(layers=(
    nn.Dense(num_inputs, 150),
    nn.ReLU(),
    nn.Dense(150, 150),
    nn.ReLU(),
    nn.Dense(150, 150),
    nn.ReLU(),
    nn.Dense(150, num_outputs),
    nn.ReLU(),
))

net.train(x_train, y_train, x_val, y_val, 1000, epoch_cbs=(on_epoch,))

net.save("test-nn.pkl")
# def train(self, x_train, y_train, x_val, y_val, epochs, batch_size=32, epoch_cbs=()):
# if cb(epoch, epoch_time, train_accu, valid_accu) is True:
"""
