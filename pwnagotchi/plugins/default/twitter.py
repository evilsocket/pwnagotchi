__author__ = '33197631+dadav@users.noreply.github.com'
__version__ = '1.0.0'
__name__ = 'twitter'
__license__ = 'GPL3'
__description__ = 'This plugin creates tweets about the recent activity of pwnagotchi'

import logging
from pwnagotchi.voice import Voice
import pwnagotchi.ui.faces as faces

OPTIONS = dict()

def on_loaded():
    logging.info("twitter plugin loaded.")


# called in manual mode when there's internet connectivity
def on_internet_available(agent):
    config = agent.config()
    display = agent.view()
    last_session = agent.last_session
    faces.load_from_config(config['ui']['faces'])

    if last_session.is_new() and last_session.handshakes > 0:
        try:
            import tweepy
        except ImportError:
            logging.error("Couldn't import tweepy")
            return

        logging.info("detected a new session and internet connectivity!")

        picture = '/dev/shm/pwnagotchi.png'

        display.on_manual_mode(last_session)
        display.update(force=True)
        display.image().save(picture, 'png')
        display.set('face', faces.EXCITED)
        display.set('status', 'Tweeting...')
        display.update(force=True)

        try:
            auth = tweepy.OAuthHandler(OPTIONS['consumer_key'], OPTIONS['consumer_secret'])
            auth.set_access_token(OPTIONS['access_token_key'], OPTIONS['access_token_secret'])
            api = tweepy.API(auth)

            tweet = Voice(lang=config['main']['lang']).on_last_session_tweet(last_session)
            api.update_with_media(filename=picture, status=tweet)
            last_session.save_session_id()

            logging.info("tweeted: %s" % tweet)
        except Exception as e:
            logging.exception("error while tweeting")
