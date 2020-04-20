from pwnagotchi.ui.hw.inky import Inky
from pwnagotchi.ui.hw.papirus import Papirus
from pwnagotchi.ui.hw.oledhat import OledHat
from pwnagotchi.ui.hw.lcdhat import LcdHat
from pwnagotchi.ui.hw.dfrobot1 import DFRobotV1
from pwnagotchi.ui.hw.dfrobot2 import DFRobotV2
from pwnagotchi.ui.hw.waveshare1 import WaveshareV1
from pwnagotchi.ui.hw.waveshare2 import WaveshareV2
from pwnagotchi.ui.hw.waveshare27inch import Waveshare27inch
from pwnagotchi.ui.hw.waveshare29inch import Waveshare29inch
from pwnagotchi.ui.hw.waveshare144lcd import Waveshare144lcd
from pwnagotchi.ui.hw.waveshare154inch import Waveshare154inch
from pwnagotchi.ui.hw.waveshare213d import Waveshare213d
from pwnagotchi.ui.hw.waveshare213bc import Waveshare213bc
from pwnagotchi.ui.hw.spotpear24inch import Spotpear24inch

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

    if config['ui']['display']['type'] == 'dfrobot_1':
        return DFRobotV1(config)

    if config['ui']['display']['type'] == 'dfrobot_2':
        return DFRobotV2(config)

    elif config['ui']['display']['type'] == 'waveshare_1':
        return WaveshareV1(config)

    elif config['ui']['display']['type'] == 'waveshare_2':
        return WaveshareV2(config)

    elif config['ui']['display']['type'] == 'waveshare27inch':
        return Waveshare27inch(config)

    elif config['ui']['display']['type'] == 'waveshare29inch':
        return Waveshare29inch(config)

    elif config['ui']['display']['type'] == 'waveshare144lcd':
        return Waveshare144lcd(config)

    elif config['ui']['display']['type'] == 'waveshare154inch':
        return Waveshare154inch(config)

    elif config['ui']['display']['type'] == 'waveshare213d':
        return Waveshare213d(config)

    elif config['ui']['display']['type'] == 'waveshare213bc':
        return Waveshare213bc(config)

    elif config['ui']['display']['type'] == 'spotpear24inch':
        return Spotpear24inch(config)
