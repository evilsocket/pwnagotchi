import os
import logging
import threading

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.hw as hw
from pwnagotchi.ui.view import View


class Display(View):
    def __init__(self, config, state={}):
        super(Display, self).__init__(config, hw.display_for(config), state)
        config = config['ui']['display']

        self._enabled = config['enabled']
        self._rotation = config['rotation']

        self.init_display()

        self._canvas_next_event = threading.Event()
        self._canvas_next = None
        self._render_thread_instance = threading.Thread(
            target=self._render_thread,
            daemon=True
        )
        self._render_thread_instance.start()

    def is_inky(self):
        return self._implementation.name == 'inky'

    def is_papirus(self):
        return self._implementation.name == 'papirus'

    def is_waveshare_v1(self):
        return self._implementation.name == 'waveshare_1'

    def is_waveshare_v2(self):
        return self._implementation.name == 'waveshare_2'

    def is_waveshare27inch(self):
        return self._implementation.name == 'waveshare27inch'

    def is_waveshare29inch(self):
        return self._implementation.name == 'waveshare29inch'

    def is_oledhat(self):
        return self._implementation.name == 'oledhat'

    def is_lcdhat(self):
        return self._implementation.name == 'lcdhat'

    def is_dfrobot_v1(self):
        return self._implementation.name == 'dfrobot_v1'

    def is_dfrobot_v2(self):
        return self._implementation.name == 'dfrobot_v2'

    def is_waveshare144lcd(self):
        return self._implementation.name == 'waveshare144lcd'

    def is_waveshare154inch(self):
        return self._implementation.name == 'waveshare154inch'

    def is_waveshare213d(self):
        return self._implementation.name == 'waveshare213d'

    def is_waveshare213bc(self):
        return self._implementation.name == 'waveshare213bc'

    def is_spotpear24inch(self):
        return self._implementation.name == 'spotpear24inch'

    def is_waveshare_any(self):
        return self.is_waveshare_v1() or self.is_waveshare_v2()

    def init_display(self):
        if self._enabled:
            self._implementation.initialize()
            plugins.on('display_setup', self._implementation)
        else:
            logging.warning("display module is disabled")
        self.on_render(self._on_view_rendered)

    def clear(self):
        self._implementation.clear()

    def image(self):
        img = None
        if self._canvas is not None:
            img = self._canvas if self._rotation == 0 else self._canvas.rotate(-self._rotation)
        return img

    def _render_thread(self):
        """Used for non-blocking screen updating."""

        while True:
            self._canvas_next_event.wait()
            self._canvas_next_event.clear()
            self._implementation.render(self._canvas_next)

    def _on_view_rendered(self, img):
        try:
            if self._config['ui']['web']['on_frame'] != '':
                os.system(self._config['ui']['web']['on_frame'])
        except Exception as e:
            logging.error("%s" % e)

        if self._enabled:
            self._canvas = (img if self._rotation == 0 else img.rotate(self._rotation))
            if self._implementation is not None:
                self._canvas_next = self._canvas
                self._canvas_next_event.set()
