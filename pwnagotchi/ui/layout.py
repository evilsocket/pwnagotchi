import pwnagotchi.ui.fonts as fonts


def inkyphat(config, layout):
    fonts.setup(10, 8, 10, 28)

    layout['width'] = 212
    layout['height'] = 104
    layout['face'] = (0, 37)
    layout['name'] = (5, 18)
    layout['channel'] = (0, 0)
    layout['aps'] = (25, 0)
    layout['uptime'] = (layout['width'] - 65, 0)
    layout['line1'] = [0, int(layout['height'] * .12), layout['width'], int(layout['height'] * .12)]
    layout['line2'] = [0, layout['height'] - int(layout['height'] * .12), layout['width'],
                       layout['height'] - int(layout['height'] * .12)]
    layout['friend_face'] = (0, (layout['height'] * 0.88) - 15)
    layout['friend_name'] = (40, (layout['height'] * 0.88) - 13)
    layout['shakes'] = (0, layout['height'] - int(layout['height'] * .12) + 1)
    layout['mode'] = (layout['width'] - 25, layout['height'] - int(layout['height'] * .12) + 1)
    layout['status'] = {
        'pos': (102, 18),
        'font': fonts.Small,
        'max': 20
    }
    return layout


def papirus(config, layout):
    fonts.setup(10, 8, 10, 23)

    layout['width'] = 200
    layout['height'] = 96
    layout['face'] = (0, int(layout['height'] / 4))
    layout['name'] = (5, int(layout['height'] * .15))
    layout['channel'] = (0, 0)
    layout['aps'] = (25, 0)
    layout['uptime'] = (layout['width'] - 65, 0)
    layout['line1'] = [0, int(layout['height'] * .12), layout['width'], int(layout['height'] * .12)]
    layout['line2'] = [0, layout['height'] - int(layout['height'] * .12), layout['width'],
                       layout['height'] - int(layout['height'] * .12)]
    layout['friend_face'] = (0, (layout['height'] * 0.88) - 15)
    layout['friend_name'] = (40, (layout['height'] * 0.88) - 13)
    layout['shakes'] = (0, layout['height'] - int(layout['height'] * .12) + 1)
    layout['mode'] = (layout['width'] - 25, layout['height'] - int(layout['height'] * .12) + 1)
    layout['status'] = {
        'pos': (85, int(layout['height'] * .15)),
        'font': fonts.Medium,
        'max': (layout['width'] - 100) // 6
    }
    return layout


def oledhat(config, layout):
    fonts.setup(8, 8, 8, 8)

    layout['width'] = 128
    layout['height'] = 64
    layout['face'] = (0, 32)
    layout['name'] = (0, 10)
    layout['channel'] = (0, 0)
    layout['aps'] = (25, 0)
    layout['uptime'] = (70, 0)
    layout['line1'] = [0, 9, 128, 9]
    layout['line2'] = [0, 53, 128, 53]
    layout['friend_face'] = (0, (layout['height'] * 0.88) - 15)
    layout['friend_name'] = (40, (layout['height'] * 0.88) - 13)
    layout['shakes'] = (0, 53)
    layout['mode'] = (103, 10)
    layout['status'] = {
        'pos': (30, 18),
        'font': fonts.Small,
        'max': (20) // 6
    }
    return layout


def waveshare(config, layout):
    if config['ui']['display']['color'] == 'black':
        fonts.setup(10, 9, 10, 35)

        layout['width'] = 250
        layout['height'] = 122
        layout['face'] = (0, 40)
        layout['name'] = (5, 20)
        layout['channel'] = (0, 0)
        layout['aps'] = (28, 0)
        layout['uptime'] = (layout['width'] - 65, 0)
        layout['line1'] = [0, int(layout['height'] * .12), layout['width'], int(layout['height'] * .12)]
        layout['line2'] = [0, layout['height'] - int(layout['height'] * .12), layout['width'],
                           layout['height'] - int(layout['height'] * .12)]
        layout['friend_face'] = (0, (layout['height'] * 0.88) - 15)
        layout['friend_name'] = (40, (layout['height'] * 0.88) - 13)
        layout['shakes'] = (0, layout['height'] - int(layout['height'] * .12) + 1)
        layout['mode'] = (layout['width'] - 25, layout['height'] - int(layout['height'] * .12) + 1)

    else:
        fonts.setup(10, 8, 10, 25)

        layout['width'] = 212
        layout['height'] = 104
        layout['face'] = (0, int(layout['height'] / 4))
        layout['name'] = (5, int(layout['height'] * .15))
        layout['channel'] = (0, 0)
        layout['aps'] = (28, 0)
        layout['status'] = (int(layout['width'] / 2) - 15, int(layout['height'] * .15))
        layout['uptime'] = (layout['width'] - 65, 0)
        layout['line1'] = [0, int(layout['height'] * .12), layout['width'], int(layout['height'] * .12)]
        layout['line2'] = [0, layout['height'] - int(layout['height'] * .12), layout['width'],
                           layout['height'] - int(layout['height'] * .12)]
        layout['friend_face'] = (0, (layout['height'] * 0.88) - 15)
        layout['friend_name'] = (40, (layout['height'] * 0.88) - 13)
        layout['shakes'] = (0, layout['height'] - int(layout['height'] * .12) + 1)
        layout['mode'] = (layout['width'] - 25, layout['height'] - int(layout['height'] * .12) + 1)

    layout['status'] = {
        'pos': (125, 20),
        'font': fonts.Medium,
        'max': (layout['width'] - 125) // 6
    }
    return layout


def for_display(config):
    layout = {
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
            'font': fonts.Medium,
            'max': 20
        }
    }

    if config['ui']['display']['type'] in ('inky', 'inkyphat'):
        layout = inkyphat(config, layout)

    elif config['ui']['display']['type'] in ('papirus', 'papi'):
        layout = papirus(config, layout)

    if config['ui']['display']['type'] in ('oledhat'):
        layout = oledhat(config, layout)

    elif config['ui']['display']['type'] in ('ws_1', 'ws1', 'waveshare_1', 'waveshare1',
                                             'ws_2', 'ws2', 'waveshare_2', 'waveshare2'):
        layout = waveshare(config, layout)

    return layout
