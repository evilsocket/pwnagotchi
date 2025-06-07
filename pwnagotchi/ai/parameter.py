from gym import spaces


class Parameter(object):
    def __init__(self, name, value=0.0, min_value=0, max_value=2, meta=None, trainable=True):
        self.name = name
        self.trainable = trainable
        self.meta = meta
        self.value = value
        self.min_value = min_value

        # Determine the actual maximum value for the parameter
        # For channel parameters, this is 5 (weights 0-5).
        # For other parameters, it's the passed max_value (defaulting to 2).
        current_actual_max_value = 5 if name.startswith('_channel_') else max_value

        # self.max_value is used internally to define the size of the gym.spaces.Discrete space.
        # If min_value is 0, Discrete(N) gives values [0, ..., N-1].
        # So N should be actual_max_value + 1.
        # e.g., for channels (0-5), N = 5 + 1 = 6. Discrete(6) -> [0,1,2,3,4,5].
        # e.g., for default boolean (0-1), actual_max_value=1 (if max_value=1 passed), N = 1 + 1 = 2. Discrete(2) -> [0,1].
        # The original code's `max_value=2` (default) means actual values 0,1,2. So N = 2+1 = 3. Discrete(3) -> [0,1,2].
        self.max_value = current_actual_max_value + 1

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
