SignatureAddress = 'de:ad:be:ef:de:ad'
BroadcastAddress = 'ff:ff:ff:ff:ff:ff'
Dot11ElemID_Whisper = 222
NumChannels = 140

def freq_to_channel(freq):
    if freq <= 2472:
        return int(((freq - 2412) / 5) + 1)
    elif freq == 2484:
        return int(14)
    elif 5035 <= freq <= 5865:
        return int(((freq - 5035) / 5) + 7)
    else:
        return 0


def encapsulate(payload, addr_from, addr_to=BroadcastAddress):
    from scapy.all import Dot11, Dot11Beacon, Dot11Elt, RadioTap

    radio = RadioTap()
    dot11 = Dot11(type=0, subtype=8, addr1=addr_to, addr2=SignatureAddress, addr3=addr_from)
    beacon = Dot11Beacon(cap='ESS')
    frame = radio / dot11 / beacon

    data_size = len(payload)
    data_left = data_size
    data_off = 0
    chunk_size = 255

    while data_left > 0:
        sz = min(chunk_size, data_left)
        chunk = payload[data_off: data_off + sz]
        frame /= Dot11Elt(ID=Dot11ElemID_Whisper, info=chunk, len=sz)
        data_off += sz
        data_left -= sz

    return frame
