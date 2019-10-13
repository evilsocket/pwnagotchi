"""Inky pHAT e-Ink Display Driver."""
from . import inkyfast


class InkyPHATFast(inkyfast.InkyFast):
    """Inky wHAT e-Ink Display Driver."""

    WIDTH = 212
    HEIGHT = 104

    WHITE = 0
    BLACK = 1
    RED = 2
    YELLOW = 2

    def __init__(self, colour):
        """Initialise an Inky pHAT Display.

        :param colour: one of red, black or yellow, default: black

        """
        inkyfast.InkyFast.__init__(
            self,
            resolution=(self.WIDTH, self.HEIGHT),
            colour=colour,
            h_flip=False,
            v_flip=False)