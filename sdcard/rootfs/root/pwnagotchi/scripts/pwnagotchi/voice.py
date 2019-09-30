import random


def default():
    return 'ZzzzZZzzzzZzzz'


def on_starting():
    return random.choice([ \
        'Hi, I\'m Pwnagotchi!\nStarting ...',
        'New day, new hunt,\nnew pwns!',
        'Hack the Planet!'])


def on_ai_ready():
    return random.choice([
        'AI ready.',
        'The neural network\nis ready.'])


def on_normal():
    return random.choice([ \
        '',
        '...'])


def on_free_channel(channel):
    return 'Hey, channel %d is\nfree! Your AP will\nsay thanks.' % channel


def on_bored():
    return random.choice([ \
        'I\'m bored ...',
        'Let\'s go for a walk!'])


def on_motivated(reward):
    return 'This is the best\nday of my life!'


def on_demotivated(reward):
    return 'Shitty day :/'


def on_sad():
    return random.choice([ \
        'I\'m extremely bored ...',
        'I\'m very sad ...',
        'I\'m sad',
        '...'])


def on_excited():
    return random.choice([ \
        'I\'m living the life!',
        'I pwn therefore I am.',
        'So many networks!!!',
        'I\'m having so much\nfun!',
        'My crime is that of\ncuriosity ...'])


def on_new_peer(peer):
    return random.choice([ \
        'Hello\n%s!\nNice to meet you.' % peer.name(),
        'Unit\n%s\nis nearby!' % peer.name()])


def on_lost_peer(peer):
    return random.choice([ \
        'Uhm ...\ngoodbye\n%s' % peer.name(),
        '%s\nis gone ...' % peer.name()])


def on_miss(who):
    return random.choice([ \
        'Whops ...\n%s\nis gone.' % who,
        '%s\nmissed!' % who,
        'Missed!'])


def on_lonely():
    return random.choice([ \
        'Nobody wants to\nplay with me ...',
        'I feel so alone ...',
        'Where\'s everybody?!'])


def on_napping(secs):
    return random.choice([ \
        'Napping for %ds ...' % secs,
        'Zzzzz',
        'ZzzZzzz (%ds)' % secs])


def on_awakening():
    return random.choice(['...', '!'])


def on_waiting(secs):
    return random.choice([ \
        'Waiting for %ds ...' % secs,
        '...',
        'Looking around (%ds)' % secs])


def on_assoc(ap):
    ssid, bssid = ap['hostname'], ap['mac']
    what = ssid if ssid != '' and ssid != '<hidden>' else bssid
    return random.choice([ \
        'Hey\n%s\nlet\'s be friends!' % what,
        'Associating to\n%s' % what,
        'Yo\n%s!' % what])


def on_deauth(sta):
    return random.choice([ \
        'Just decided that\n%s\nneeds no WiFi!' % sta['mac'],
        'Deauthenticating\n%s' % sta['mac'],
        'Kickbanning\n%s!' % sta['mac']])


def on_handshakes(new_shakes):
    s = 's' if new_shakes > 1 else ''
    return 'Cool, we got %d\nnew handshake%s!' % (new_shakes, s)


def on_rebooting():
    return "Ops, something\nwent wrong ...\nRebooting ..."


def on_log(log):
    status = 'Kicked %d stations\n' % log.deauthed
    status += 'Made %d new friends\n' % log.associated
    status += 'Got %d handshakes\n' % log.handshakes
    if log.peers == 1:
        status += 'Met 1 peer'
    elif log.peers > 0:
        status += 'Met %d peers' % log.peers
    return status


def on_log_tweet(log):
    return 'I\'ve been pwning for %s and kicked %d clients! I\'ve also met %d new friends and ate %d handshakes! #pwnagotchi #pwnlog #pwnlife #hacktheplanet #skynet' % ( \
        log.duration_human,
        log.deauthed,
        log.associated,
        log.handshakes)
