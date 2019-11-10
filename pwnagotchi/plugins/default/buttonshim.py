import logging
import RPi.GPIO as GPIO
import subprocess
import pwnagotchi.plugins as plugins
import signal
import smbus
import time
from threading import Thread
import atexit
from colorsys import hsv_to_rgb


try:
    import queue
except ImportError:
    import Queue as queue

ADDR = 0x3f

#adapted from version 0.0.2
__version__ = '0.0.2x'

_bus = None

LED_DATA = 7
LED_CLOCK = 6

REG_INPUT = 0x00
REG_OUTPUT = 0x01
REG_POLARITY = 0x02
REG_CONFIG = 0x03

NUM_BUTTONS = 5

BUTTON_A = 0
"""Button A"""
BUTTON_B = 1
"""Button B"""
BUTTON_C = 2
"""Button C"""
BUTTON_D = 3
"""Button D"""
BUTTON_E = 4
"""Button E"""

NAMES = ['A', 'B', 'C', 'D', 'E']
"""Sometimes you want to print the plain text name of the button that's triggered.

You can use::

    buttonshim.NAMES[button_index]

To accomplish this.

"""

ERROR_LIMIT = 10

FPS = 60

LED_GAMMA = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2,
    2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5,
    6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 11, 11,
    11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18,
    19, 19, 20, 21, 21, 22, 22, 23, 23, 24, 25, 25, 26, 27, 27, 28,
    29, 29, 30, 31, 31, 32, 33, 34, 34, 35, 36, 37, 37, 38, 39, 40,
    40, 41, 42, 43, 44, 45, 46, 46, 47, 48, 49, 50, 51, 52, 53, 54,
    55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
    71, 72, 73, 74, 76, 77, 78, 79, 80, 81, 83, 84, 85, 86, 88, 89,
    90, 91, 93, 94, 95, 96, 98, 99, 100, 102, 103, 104, 106, 107, 109, 110,
    111, 113, 114, 116, 117, 119, 120, 121, 123, 124, 126, 128, 129, 131, 132, 134,
    135, 137, 138, 140, 142, 143, 145, 146, 148, 150, 151, 153, 155, 157, 158, 160,
    162, 163, 165, 167, 169, 170, 172, 174, 176, 178, 179, 181, 183, 185, 187, 189,
    191, 193, 194, 196, 198, 200, 202, 204, 206, 208, 210, 212, 214, 216, 218, 220,
    222, 224, 227, 229, 231, 233, 235, 237, 239, 241, 244, 246, 248, 250, 252, 255]

# The LED is an APA102 driven via the i2c IO expander.
# We must set and clear the Clock and Data pins
# Each byte in _reg_queue represents a snapshot of the pin state

_reg_queue = []
_update_queue = []
_brightness = 0.5

_led_queue = queue.Queue()

_t_poll = None

_running = False

_states = 0b00011111


class Handler():
    plugin = None
    def __init__(self, plugin):
        self.press = None
        self.release = None

        self.hold = None
        self.hold_time = 0

        self.repeat = False
        self.repeat_time = 0

        self.t_pressed = 0
        self.t_repeat = 0
        self.hold_fired = False
        self.plugin = plugin

_handlers = [None,None,None,None,None]


def _run():
    global _running, _states
    _running = True
    _last_states = 0b00011111
    _errors = 0

    while _running:
        led_data = None

        try:
            led_data = _led_queue.get(False)
            _led_queue.task_done()

        except queue.Empty:
            pass

        try:
            if led_data:
                for chunk in _chunk(led_data, 32):
                    _bus.write_i2c_block_data(ADDR, REG_OUTPUT, chunk)

            _states = _bus.read_byte_data(ADDR, REG_INPUT)

        except IOError:
            _errors += 1
            if _errors > ERROR_LIMIT:
                _running = False
                raise IOError("More than {} IO errors have occurred!".format(ERROR_LIMIT))

        for x in range(NUM_BUTTONS):
            last = (_last_states >> x) & 1
            curr = (_states >> x) & 1
            handler = _handlers[x]

            # If last > curr then it's a transition from 1 to 0
            # since the buttons are active low, that's a press event
            if last > curr:
                handler.t_pressed = time.time()
                handler.hold_fired = False

                if callable(handler.press):
                    handler.t_repeat = time.time()
                    Thread(target=handler.press, args=(x, True, handler.plugin)).start()

                continue

            if last < curr and callable(handler.release):
                Thread(target=handler.release, args=(x, False, handler.plugin)).start()
                continue

            if curr == 0:
                if callable(handler.hold) and not handler.hold_fired and (time.time() - handler.t_pressed) > handler.hold_time:
                    Thread(target=handler.hold, args=(x,)).start()
                    handler.hold_fired = True

                if handler.repeat and callable(handler.press) and (time.time() - handler.t_repeat) > handler.repeat_time:
                    _handlers[x].t_repeat = time.time()
                    Thread(target=_handlers[x].press, args=(x, True, handler.plugin)).start()

        _last_states = _states

        time.sleep(1.0 / FPS)


def _quit():
    global _running

    if _running:
        _led_queue.join()
        set_pixel(0, 0, 0)
        _led_queue.join()

    _running = False
    _t_poll.join()


def setup():
    global _t_poll, _bus

    if _bus is not None:
        return

    _bus = smbus.SMBus(1)

    _bus.write_byte_data(ADDR, REG_CONFIG, 0b00011111)
    _bus.write_byte_data(ADDR, REG_POLARITY, 0b00000000)
    _bus.write_byte_data(ADDR, REG_OUTPUT, 0b00000000)

    _t_poll = Thread(target=_run)
    _t_poll.daemon = True
    _t_poll.start()

    set_pixel(0, 0, 0)

    atexit.register(_quit)


def _set_bit(pin, value):
    global _reg_queue

    if value:
        _reg_queue[-1] |= (1 << pin)
    else:
        _reg_queue[-1] &= ~(1 << pin)


def _next():
    global _reg_queue

    if len(_reg_queue) == 0:
        _reg_queue = [0b00000000]
    else:
        _reg_queue.append(_reg_queue[-1])


def _enqueue():
    global _reg_queue

    _led_queue.put(_reg_queue)

    _reg_queue = []


def _chunk(l, n):
    for i in range(0, len(l)+1, n):
        yield l[i:i + n]


def _write_byte(byte):
    for x in range(8):
        _next()
        _set_bit(LED_CLOCK, 0)
        _set_bit(LED_DATA, byte & 0b10000000)
        _next()
        _set_bit(LED_CLOCK, 1)
        byte <<= 1


def on_hold(buttons, handler=None, hold_time=2):
    """Attach a hold handler to one or more buttons.

    This handler is fired when you hold a button for hold_time seconds.

    When fired it will run in its own Thread.

    It will be passed one argument, the button index::

        @buttonshim.on_hold(buttonshim.BUTTON_A)
        def handler(button):
            # Your code here

    :param buttons: A single button, or a list of buttons
    :param handler: Optional: a function to bind as the handler
    :param hold_time: Optional: the hold time in seconds (default 2)

    """
    setup()

    if buttons is None:
        buttons = [BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_D, BUTTON_E]

    if isinstance(buttons, int):
        buttons = [buttons]

    def attach_handler(handler):
        for button in buttons:
            _handlers[button].hold = handler
            _handlers[button].hold_time = hold_time

    if handler is not None:
        attach_handler(handler)
    else:
        return attach_handler


def on_press(buttons, handler=None, repeat=False, repeat_time=0.5):
    """Attach a press handler to one or more buttons.

    This handler is fired when you press a button.

    When fired it will be run in its own Thread.

    It will be passed two arguments, the button index and a
    boolean indicating whether the button has been pressed/released::

        @buttonshim.on_press(buttonshim.BUTTON_A)
        def handler(button, pressed):
            # Your code here

    :param buttons: A single button, or a list of buttons
    :param handler: Optional: a function to bind as the handler
    :param repeat: Optional: Repeat the handler if the button is held
    :param repeat_time: Optional: Time, in seconds, after which to repeat

    """
    setup()

    if buttons is None:
        buttons = [BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_D, BUTTON_E]

    if isinstance(buttons, int):
        buttons = [buttons]

    def attach_handler(handler):
        for button in buttons:
            _handlers[button].press = handler
            _handlers[button].repeat = repeat
            _handlers[button].repeat_time = repeat_time

    if handler is not None:
        attach_handler(handler)
    else:
        return attach_handler


def on_release(buttons=None, handler=None):
    """Attach a release handler to one or more buttons.

    This handler is fired when you let go of a button.

    When fired it will be run in its own Thread.

    It will be passed two arguments, the button index and a
    boolean indicating whether the button has been pressed/released::

        @buttonshim.on_release(buttonshim.BUTTON_A)
        def handler(button, pressed):
            # Your code here

    :param buttons: A single button, or a list of buttons
    :param handler: Optional: a function to bind as the handler

    """
    setup()

    if buttons is None:
        buttons = [BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_D, BUTTON_E]

    if isinstance(buttons, int):
        buttons = [buttons]

    def attach_handler(handler):
        for button in buttons:
            _handlers[button].release = handler

    if handler is not None:
        attach_handler(handler)
    else:
        return attach_handler


def set_brightness(brightness):
    global _brightness

    setup()

    if not isinstance(brightness, int) and not isinstance(brightness, float):
        raise ValueError("Brightness should be an int or float")

    if brightness < 0.0 or brightness > 1.0:
        raise ValueError("Brightness should be between 0.0 and 1.0")

    _brightness = brightness


def set_pixel(r, g, b):
    """Set the Button SHIM RGB pixel

    Display an RGB colour on the Button SHIM pixel.

    :param r: Amount of red, from 0 to 255
    :param g: Amount of green, from 0 to 255
    :param b: Amount of blue, from 0 to 255

    You can use HTML colours directly with hexadecimal notation in Python. EG::

        buttonshim.set_pixel(0xFF, 0x00, 0xFF)

    """
    setup()

    if not isinstance(r, int) or r < 0 or r > 255:
        raise ValueError("Argument r should be an int from 0 to 255")

    if not isinstance(g, int) or g < 0 or g > 255:
        raise ValueError("Argument g should be an int from 0 to 255")

    if not isinstance(b, int) or b < 0 or b > 255:
        raise ValueError("Argument b should be an int from 0 to 255")

    r, g, b = [int(x * _brightness) for x in (r, g, b)]

    _write_byte(0)
    _write_byte(0)
    _write_byte(0b11101111)
    _write_byte(LED_GAMMA[b & 0xff])
    _write_byte(LED_GAMMA[g & 0xff])
    _write_byte(LED_GAMMA[r & 0xff])
    _write_byte(0)
    _write_byte(0)
    _enqueue()

def runCommand(button, pressed, plugin):
    logging.debug(f"Button Pressed! Loading command from slot '{button}'")
    command = plugin.commands[button]
    logging.debug(f"Button Pressed! Running command: {command}")
    process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
    procfess.wait()

class Buttonshim(plugins.Plugin):
    __author__ = 'gon@o2online.de'
    __version__ = '0.0.1'
    __license__ = 'GPL3'
    __description__ = 'Pimoroni Button Shim GPIO Button and RGB LED support plugin based on the pimoroni-buttonshim-lib and the pwnagotchi-gpio-buttons-plugin'

    def __init__(self):
        self.running = False
        self.options = dict()
        self.commands = ['', '', '', '', '']
        global _handlers
        _handlers = [Handler(self) for x in range(NUM_BUTTONS)]
        on_press([BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_D, BUTTON_E], runCommand)

    def on_loaded(self):
        i = 0
        for b in self.options['buttons']:
            self.commands[i] = b
            logging.debug(f"Loaded command '{b}' into slot '{i}'.")
            i=i+1
        logging.info("Button Shim GPIO Button plugin loaded.")
        self.running = True
