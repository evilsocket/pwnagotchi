import pwnagotchi.ui.fonts as fonts


class DisplayImpl(object):
    def __init__(self, config, name):
        self.name = name
        self.config = config['ui']['display']
        self._layout = {
            'width': 0,
            'height': 0,
            'face': (0, 0),
            'name': (0, 0),
            'channel': (0, 0),
            'aps': (0, 0),
            'uptime': (0, 0),
            'line1': (0, 0),
            'line2': (0, 0),
            'friend_face': (0, 0),
            'friend_name': (0, 0),
            'shakes': (0, 0),
            'mode': (0, 0),
            # status is special :D
            'status': {
                'pos': (0, 0),
                'font': fonts.status_font(fonts.Medium),
                'max': 20
            }
        }

    def layout(self):
        raise NotImplementedError

    def initialize(self):
        raise NotImplementedError

    def render(self, canvas):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError
