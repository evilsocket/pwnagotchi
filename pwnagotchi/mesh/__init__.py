import os

from Crypto.PublicKey import RSA
import hashlib

def new_session_id():
    return ':'.join(['%02x' % b for b in os.urandom(6)])


def get_identity(config):
    pubkey = None
    with open(config['main']['pubkey']) as fp:
        pubkey = RSA.importKey(fp.read())
    return pubkey, hashlib.sha256(pubkey.exportKey('DER')).hexdigest()
