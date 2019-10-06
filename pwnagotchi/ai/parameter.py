from gym import spaces


class Parameter(object):
    def __init__(self, name, value=0.0, min_value=0, max_value=2, meta=None, trainable=True):
        self.name = name
        self.trainable = trainable
        self.meta = meta
        self.value = value
        self.min_value = min_value
        self.max_value = max_value + 1

        # gym.space.Discrete is within [0, 1, 2, ..., n-1]
        if self.min_value < 0:
            self.scale_factor = abs(self.min_value)
        elif self.min_value > 0:
            self.scale_factor = -self.min_value
        else:
            self.scale_factor = 0

    def space_size(self):
        return self.max_value + self.scale_factor

    def space(self):
        return spaces.Discrete(self.max_value + self.scale_factor)

    def to_param_value(self, policy_v):
        self.value = policy_v - self.scale_factor
        assert self.min_value <= self.value <= self.max_value
        return int(self.value)
