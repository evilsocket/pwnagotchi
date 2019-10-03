import random
import gettext
import os


class Voice:
    def __init__(self, lang):
        localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
        translation = gettext.translation(
            'voice', localedir,
            languages=[lang],
            fallback=True,
        )
        translation.install()
        self._ = translation.gettext

    def default(self):
        return self._('ZzzzZZzzzzZzzz')

    def on_starting(self):
        return random.choice([ \
            self._('Hi, I\'m Pwnagotchi!\nStarting ...'),
            self._('New day, new hunt,\nnew pwns!'),
            self._('Hack the Planet!')])

    def on_ai_ready(self):
        return random.choice([
            self._('AI ready.'),
            self._('The neural network\nis ready.')])

    def on_normal(self):
        return random.choice([ \
            '',
            '...'])

    def on_free_channel(self, channel):
        return self._('Hey, channel {channel} is\nfree! Your AP will\nsay thanks.').format(channel=channel)

    def on_bored(self):
        return random.choice([ \
            self._('I\'m bored ...'),
            self._('Let\'s go for a walk!')])

    def on_motivated(self, reward):
        return self._('This is the best\nday of my life!')

    def on_demotivated(self, reward):
        return self._('Shitty day :/')

    def on_sad(self):
        return random.choice([ \
            self._('I\'m extremely bored ...'),
            self._('I\'m very sad ...'),
            self._('I\'m sad'),
            '...'])

    def on_excited(self):
        return random.choice([ \
            self._('I\'m living the life!'),
            self._('I pwn therefore I am.'),
            self._('So many networks!!!'),
            self._('I\'m having so much\nfun!'),
            self._('My crime is that of\ncuriosity ...')])

    def on_new_peer(self, peer):
        return random.choice([ \
            self._('Hello\n{name}!\nNice to meet you. {name}').format(name=peer.name()),
            self._('Unit\n{name}\nis nearby! {name}').format(name=peer.name())])

    def on_lost_peer(self, peer):
        return random.choice([ \
            self._('Uhm ...\ngoodbye\n{name}').format(name=peer.name()),
            self._('{name}\nis gone ...').format(name=peer.name())])

    def on_miss(self, who):
        return random.choice([ \
            self._('Whoops ...\n{name}\nis gone.').format(name=who),
            self._('{name}\nmissed!').format(name=who),
            self._('Missed!')])

    def on_lonely(self):
        return random.choice([ \
            self._('Nobody wants to\nplay with me ...'),
            self._('I feel so alone ...'),
            self._('Where\'s everybody?!')])

    def on_napping(self, secs):
        return random.choice([ \
            self._('Napping for {secs}s ...').format(secs=secs),
            self._('Zzzzz'),
            self._('ZzzZzzz ({secs}s)').format(secs=secs)])

    def on_awakening(self):
        return random.choice(['...', '!'])

    def on_waiting(self, secs):
        return random.choice([ \
            self._('Waiting for {secs}s ...').format(secs=secs),
            '...',
            self._('Looking around ({secs}s)').format(secs=secs)])

    def on_assoc(self, ap):
        ssid, bssid = ap['hostname'], ap['mac']
        what = ssid if ssid != '' and ssid != '<hidden>' else bssid
        return random.choice([ \
            self._('Hey\n{what}\nlet\'s be friends!').format(what=what),
            self._('Associating to\n{what}').format(what=what),
            self._('Yo\n{what}!').format(what=what)])

    def on_deauth(self, sta):
        return random.choice([ \
            self._('Just decided that\n{mac}\nneeds no WiFi!').format(mac=sta['mac']),
            self._('Deauthenticating\n{mac}').format(mac=sta['mac']),
            self._('Kickbanning\n{mac}!').format(mac=sta['mac'])])

    def on_handshakes(self, new_shakes):
        s = 's' if new_shakes > 1 else ''
        return self._('Cool, we got {num}\nnew handshake{plural}!').format(num=new_shakes, plural=s)

    def on_rebooting(self):
        return self._("Ops, something\nwent wrong ...\nRebooting ...")

    def on_log(self, log):
        status = self._('Kicked {num} stations\n').format(num=log.deauthed)
        status += self._('Made {num} new friends\n').format(num=log.associated)
        status += self._('Got {num} handshakes\n').format(num=log.handshakes)
        if log.peers == 1:
            status += self._('Met 1 peer')
        elif log.peers > 0:
            status += self._('Met {num} peers').format(num=log.peers)
        return status

    def on_log_tweet(self, log):
        return self._(
            'I\'ve been pwning for {duration} and kicked {deauthed} clients! I\'ve also met {associated} new friends and ate {handshakes} handshakes! #pwnagotchi #pwnlog #pwnlife #hacktheplanet #skynet').format(
            duration=log.duration_human,
            deauthed=log.deauthed,
            associated=log.associated,
            handshakes=log.handshakes)

    def custom(self, text):
        return self._(text)
