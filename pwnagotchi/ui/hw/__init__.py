from pwnagotchi.ui.hw.inky import Inky
from pwnagotchi.ui.hw.papirus import Papirus
from pwnagotchi.ui.hw.oledhat import OledHat
from pwnagotchi.ui.hw.lcdhat import LcdHat
from pwnagotchi.ui.hw.waveshare1 import WaveshareV1
from pwnagotchi.ui.hw.waveshare2 import WaveshareV2
from pwnagotchi.ui.hw.waveshare27inch import Waveshare27inch


def display_for(config):
    # config has been normalized already in utils.load_config
    if config['ui']['display']['type'] == 'inky':
        return Inky(config)

    elif config['ui']['display']['type'] == 'papirus':
        return Papirus(config)

    if config['ui']['display']['type'] == 'oledhat':
        return OledHat(config)

    if config['ui']['display']['type'] == 'lcdhat':
        return LcdHat(config)

    elif config['ui']['display']['type'] == 'waveshare_1':
        return WaveshareV1(config)

    elif config['ui']['display']['type'] == 'waveshare_2':
        return WaveshareV2(config)

    elif config['ui']['display']['type'] == 'waveshare27inch':
        return Waveshare27inch(config)
    
    elif config['ui']['display']['type'] == 'waveshare29inch':
        return Waveshare29inch(config)
    
