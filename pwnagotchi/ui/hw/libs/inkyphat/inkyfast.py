from inky.inky import Inky, CS0_PIN, DC_PIN, RESET_PIN, BUSY_PIN


class InkyFast(Inky):

    def __init__(self, resolution=(400, 300), colour='black', cs_pin=CS0_PIN, dc_pin=DC_PIN, reset_pin=RESET_PIN,
                 busy_pin=BUSY_PIN, h_flip=False, v_flip=False):
        super(InkyFast, self).__init__(resolution, colour, cs_pin, dc_pin, reset_pin, busy_pin, h_flip, v_flip)

        self._luts['black'] = [
                0b01001000, 0b10100000, 0b00010000, 0b00010000, 0b00010011, 0b00000000, 0b00000000,
                0b01001000, 0b10100000, 0b10000000, 0b00000000, 0b00000011, 0b00000000, 0b00000000,
                0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000,
                0b01001000, 0b10100101, 0b00000000, 0b10111011, 0b00000000, 0b00000000, 0b00000000,
                0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000,
                # The following timings have been reduced to avoid the fade to black
                0x00, 0x00, 0x00, 0x00, 0x00,
                0x10, 0x04, 0x04, 0x04, 0x04,
                0x04, 0x08, 0x08, 0x10, 0x10,
                0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00,
            ]