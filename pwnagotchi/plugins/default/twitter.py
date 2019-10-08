__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'twitter'
__license__ = 'GPL3'
__description__ = 'This plugin creates tweets about the recent activity of pwnagotchi'

import logging
from pwnagotchi.voice import Voice

OPTIONS = dict()

def on_loaded():
    logging.info("twitter plugin loaded.")


# called in manual mode when there's internet connectivity
def on_internet_available(ui, keypair, config, log):
    if log.is_new() and log.handshakes > 0:
        try:
            import tweepy
        except ImportError:
            logging.error("Couldn't import tweepy")
            return

        logging.info("detected a new session and internet connectivity!")

        picture = '/dev/shm/pwnagotchi.png'

        ui.on_manual_mode(log)
        ui.update(force=True)
        ui.image().save(picture, 'png')
        ui.set('status', 'Tweeting...')
        ui.update(force=True)

        try:
            auth = tweepy.OAuthHandler(OPTIONS['consumer_key'], OPTIONS['consumer_secret'])
            auth.set_access_token(OPTIONS['access_token_key'], OPTIONS['access_token_secret'])
            api = tweepy.API(auth)

            tweet = Voice(lang=config['main']['lang']).on_log_tweet(log)
            api.update_with_media(filename=picture, status=tweet)
            log.save_session_id()

            logging.info("tweeted: %s" % tweet)
        except Exception as e:
            logging.exception("error while tweeting")
