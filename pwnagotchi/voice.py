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
        return random.choice([
            self._('Hi, I\'m Pwnagotchi! Starting ...'),
            self._('New day, new hunt, new pwns!'),
            self._('Hack the Planet!')])

    def on_ai_ready(self):
        return random.choice([
            self._('AI ready.'),
            self._('The neural network is ready.')])

    def on_normal(self):
        return random.choice([
            '',
            '...'])

    def on_free_channel(self, channel):
        return self._('Hey, channel {channel} is free! Your AP will say thanks.').format(channel=channel)

    def on_bored(self):
        return random.choice([
            self._('I\'m bored ...'),
            self._('Let\'s go for a walk!')])

    def on_motivated(self, reward):
        return self._('This is the best day of my life!')

    def on_demotivated(self, reward):
        return self._('Shitty day :/')

    def on_sad(self):
        return random.choice([
            self._('I\'m extremely bored ...'),
            self._('I\'m very sad ...'),
            self._('I\'m sad'),
            '...'])

    def on_excited(self):
        return random.choice([
            self._('I\'m living the life!'),
            self._('I pwn therefore I am.'),
            self._('So many networks!!!'),
            self._('I\'m having so much fun!'),
            self._('My crime is that of curiosity ...')])

    def on_new_peer(self, peer):
        return random.choice([
            self._('Hello {name}! Nice to meet you. {name}').format(name=peer.name()),
            self._('Unit {name} is nearby! {name}').format(name=peer.name())])

    def on_lost_peer(self, peer):
        return random.choice([
            self._('Uhm ... goodbye {name}').format(name=peer.name()),
            self._('{name} is gone ...').format(name=peer.name())])

    def on_miss(self, who):
        return random.choice([
            self._('Whoops ... {name} is gone.').format(name=who),
            self._('{name} missed!').format(name=who),
            self._('Missed!')])

    def on_lonely(self):
        return random.choice([
            self._('Nobody wants to play with me ...'),
            self._('I feel so alone ...'),
            self._('Where\'s everybody?!')])

    def on_napping(self, secs):
        return random.choice([
            self._('Napping for {secs}s ...').format(secs=secs),
            self._('Zzzzz'),
            self._('ZzzZzzz ({secs}s)').format(secs=secs)])

    def on_shutdown(self):
        return random.choice([
            self._('Good night.'),
            self._('Zzz')])

    def on_awakening(self):
        return random.choice(['...', '!'])

    def on_waiting(self, secs):
        return random.choice([
            self._('Waiting for {secs}s ...').format(secs=secs),
            '...',
            self._('Looking around ({secs}s)').format(secs=secs)])

    def on_assoc(self, ap):
        ssid, bssid = ap['hostname'], ap['mac']
        what = ssid if ssid != '' and ssid != '<hidden>' else bssid
        return random.choice([
            self._('Hey {what} let\'s be friends!').format(what=what),
            self._('Associating to {what}').format(what=what),
            self._('Yo {what}!').format(what=what)])

    def on_deauth(self, sta):
        return random.choice([
            self._('Just decided that {mac} needs no WiFi!').format(mac=sta['mac']),
            self._('Deauthenticating {mac}').format(mac=sta['mac']),
            self._('Kickbanning {mac}!').format(mac=sta['mac'])])

    def on_handshakes(self, new_shakes):
        s = 's' if new_shakes > 1 else ''
        return self._('Cool, we got {num} new handshake{plural}!').format(num=new_shakes, plural=s)

    def on_rebooting(self):
        return self._("Ops, something went wrong ... Rebooting ...")

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

    def hhmmss(self, count, fmt):
        if count > 1:
            # plural
            if fmt == "h":
                return self._("hours")
            if fmt == "m":
                return self._("minutes")
            if fmt == "s":
                return self._("seconds")
        else:
            # sing
            if fmt == "h":
                return self._("hour")
            if fmt == "m":
                return self._("minute")
            if fmt == "s":
                return self._("second")
        return fmt
