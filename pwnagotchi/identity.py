from Crypto.Signature import PKCS1_PSS
from Crypto.PublicKey import RSA
import Crypto.Hash.SHA256 as SHA256
import base64
import hashlib
import os
import logging

DefaultPath = "/etc/pwnagotchi/"


class KeyPair(object):
    def __init__(self, path=DefaultPath):
        self.path = path
        self.priv_path = os.path.join(path, "id_rsa")
        self.priv_key = None
        self.pub_path = "%s.pub" % self.priv_path
        self.pub_key = None

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        if not os.path.exists(self.priv_path) or not os.path.exists(self.pub_path):
            logging.info("generating %s ..." % self.priv_path)
            os.system("/usr/bin/ssh-keygen -t rsa -m PEM -b 4096 -N '' -f '%s'" % self.priv_path)

        with open(self.priv_path) as fp:
            self.priv_key = RSA.importKey(fp.read())

        with open(self.pub_path) as fp:
            self.pub_key = RSA.importKey(fp.read())
            self.pub_key_pem = self.pub_key.exportKey('PEM').decode("ascii")
            # python is special
            if 'RSA PUBLIC KEY' not in self.pub_key_pem:
                self.pub_key_pem = self.pub_key_pem.replace('PUBLIC KEY', 'RSA PUBLIC KEY')

        pem = self.pub_key_pem.encode("ascii")

        self.pub_key_pem_b64 = base64.b64encode(pem).decode("ascii")
        self.fingerprint = hashlib.sha256(pem).hexdigest()

    def sign(self, message):
        hasher = SHA256.new(message.encode("ascii"))
        signer = PKCS1_PSS.new(self.priv_key, saltLen=16)
        signature = signer.sign(hasher)
        signature_b64 = base64.b64encode(signature).decode("ascii")
        return signature, signature_b64