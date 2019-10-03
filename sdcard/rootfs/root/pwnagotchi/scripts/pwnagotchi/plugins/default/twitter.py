__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'twitter'
__license__ = 'GPL3'
__description__ = 'This plugin creates tweets about the recent activity of pwnagotchi'
__enabled__ = True

import logging
from pwnagotchi.voice import Voice

UI = None


def on_loaded():
    logging.info("Twitter plugin loaded.")


# called in manual mode when there's internet connectivity
def on_internet_available(config, log):
    if config['twitter']['enabled'] and log.is_new() and log.handshakes > 0 and UI:
        try:
            import tweepy
        except ImportError:
            logging.error("Couldn't import tweepy")
            return

        logging.info("detected a new session and internet connectivity!")

        picture = '/dev/shm/pwnagotchi.png'

        UI.on_manual_mode(log)
        UI.update(force=True)
        UI.image().save(picture, 'png')
        UI.set('status', 'Tweeting...')
        UI.update(force=True)

        try:
            auth = tweepy.OAuthHandler(config['twitter']['consumer_key'], config['twitter']['consumer_secret'])
            auth.set_access_token(config['twitter']['access_token_key'], config['twitter']['access_token_secret'])
            api = tweepy.API(auth)

            tweet = Voice(lang=config['main']['lang']).on_log_tweet(log)
            api.update_with_media(filename=picture, status=tweet)
            log.save_session_id()

            logging.info("tweeted: %s" % tweet)
        except Exception as e:
            logging.exception("error while tweeting")


def on_ui_setup(ui):
    # need that object
    global UI
    UI = ui
