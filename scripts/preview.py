#!/usr/bin/env python3

import sys
import os
import time
import argparse
from http.server import HTTPServer
import shutil
import logging
import yaml

sys.path.insert(0,
                os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             '../sdcard/rootfs/root/pwnagotchi/scripts/'))

from pwnagotchi.ui.display import Display, VideoHandler


class CustomDisplay(Display):

    def _http_serve(self):
        if self._video_address is not None:
            self._httpd = HTTPServer((self._video_address, self._video_port),
                                     CustomVideoHandler)
            logging.info("ui available at http://%s:%d/" % (self._video_address,
                                                        self._video_port))
            self._httpd.serve_forever()
        else:
            logging.info("could not get ip of usb0, video server not starting")

    def _on_view_rendered(self, img):
        CustomVideoHandler.render(img)

        if self._enabled:
            self.canvas = (img if self._rotation == 0 else img.rotate(self._rotation))
            if self._render_cb is not None:
                self._render_cb()


class CustomVideoHandler(VideoHandler):

    @staticmethod
    def render(img):
        with CustomVideoHandler._lock:
            try:
                img.save("/tmp/pwnagotchi-{rand}.png".format(rand=id(CustomVideoHandler)), format='PNG')
            except BaseException:
                logging.exception("could not write preview")

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            try:
                self.wfile.write(
                    bytes(
                        self._index %
                        ('localhost', 1000), "utf8"))
            except BaseException:
                pass

        elif self.path.startswith('/ui'):
            with self._lock:
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                try:
                    with open("/tmp/pwnagotchi-{rand}.png".format(rand=id(CustomVideoHandler)), 'rb') as fp:
                        shutil.copyfileobj(fp, self.wfile)
                except BaseException:
                    logging.exception("could not open preview")
        else:
            self.send_response(404)


class DummyPeer:
    @staticmethod
    def name():
        return "beta"


def main():
    parser = argparse.ArgumentParser(description="This program emulates\
                                     the pwnagotchi display")
    parser.add_argument('--display', help="Which display to use.",
                        default="waveshare_2")
    parser.add_argument('--port', help="Which port to use",
                        default=8080)
    parser.add_argument('--sleep', type=int, help="Time between emotions",
                        default=2)
    parser.add_argument('--lang', help="Language to use",
                        default="en")
    args = parser.parse_args()

    CONFIG = yaml.load('''
    main:
        lang: {lang}
    ui:
        fps: 0.3
        display:
            enabled: false
            rotation: 180
            color: black
            refresh: 30
            type: {display}
            video:
                enabled: true
                address: "0.0.0.0"
                port: {port}
    '''.format(display=args.display,
               port=args.port,
               lang=args.lang))

    DISPLAY = CustomDisplay(config=CONFIG, state={'name': '%s>' % 'preview'})

    while True:
        DISPLAY.on_starting()
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_ai_ready()
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_normal()
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_new_peer(DummyPeer())
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_lost_peer(DummyPeer())
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_free_channel('6')
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.wait(args.sleep)
        DISPLAY.update()
        DISPLAY.on_bored()
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_sad()
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_motivated(1)
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_demotivated(-1)
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_excited()
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_deauth({'mac': 'DE:AD:BE:EF:CA:FE'})
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_miss('test')
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_lonely()
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_handshakes(1)
        DISPLAY.update()
        time.sleep(args.sleep)
        DISPLAY.on_rebooting()
        DISPLAY.update()
        time.sleep(args.sleep)


if __name__ == '__main__':
    SystemExit(main())
