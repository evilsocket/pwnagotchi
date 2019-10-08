import os

def new_session_id():
    return ':'.join(['%02x' % b for b in os.urandom(6)])
