NumChannels = 140
NumChannelsExt = 165  # see https://github.com/evilsocket/pwnagotchi/issues/583


def freq_to_channel(freq):
    if freq <= 2472:
        return int(((freq - 2412) / 5) + 1)
    elif freq == 2484:
        return int(14)
    elif 5035 <= freq <= 5865:
        return int(((freq - 5035) / 5) + 7)
    else:
        return 0
