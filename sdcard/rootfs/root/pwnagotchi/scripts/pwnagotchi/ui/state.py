from threading import Lock


class State(object):
    def __init__(self, state={}):
        self._state = state
        self._lock = Lock()
        self._listeners = {}

    def add_element(self, key, elem):
        self._state[key] = elem

    def add_listener(self, key, cb):
        with self._lock:
            self._listeners[key] = cb

    def items(self):
        with self._lock:
            return self._state.items()

    def get(self, key):
        with self._lock:
            return self._state[key].value if key in self._state else None

    def set(self, key, value):
        with self._lock:
            if key in self._state:
                prev = self._state[key].value
                self._state[key].value = value
                if key in self._listeners and self._listeners[key] is not None and prev != value:
                    self._listeners[key](prev, value)
