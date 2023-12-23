from Crypto.Signature import PKCS1_PSS
from Crypto.PublicKey import RSA
import Crypto.Hash.SHA256 as SHA256
import base64
import hashlib
import os
import logging
import shutil

DefaultPath = "/etc/pwnagotchi/"


class KeyPair(object):
    def __init__(self, path=DefaultPath, view=None):
        self.path = path
        self.priv_path = os.path.join(path, "id_rsa")
        self.priv_key = None
        self.pub_path = "%s.pub" % self.priv_path
        self.pub_key = None
        self.fingerprint_path = os.path.join(path, "fingerprint")
        self._view = view

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        while True:
            # first time, generate new keys
            if not os.path.exists(self.priv_path) or not os.path.exists(self.pub_path):
                if os.path.exists(f'{self.priv_path}.original') and os.path.exists(f'{self.pub_path}.original') and os.path.exists(f'{self.fingerprint_path}.original'):
                    logging.warning('laoding backup')
                    shutil.copy(f'{self.priv_path}.original', self.priv_path)
                    shutil.copy(f'{self.pub_path}.original', self.pub_path)
                else:
                    self._view.on_keys_generation()
                    logging.info("generating %s ..." % self.priv_path)
                    os.system("pwngrid -generate -keys '%s'" % self.path)

            # load keys: they might be corrupted if the unit has been turned off during the generation, in this case
            # the exception will remove the files and go back at the beginning of this loop.
            try:
                with open(self.priv_path) as fp:
                    self.priv_key = RSA.importKey(fp.read())

                with open(self.pub_path) as fp:
                    self.pub_key = RSA.importKey(fp.read())
                    self.pub_key_pem = self.pub_key.exportKey('PEM').decode("ascii")
                    # python is special
                    if 'RSA PUBLIC KEY' not in self.pub_key_pem:
                        self.pub_key_pem = self.pub_key_pem.replace('PUBLIC KEY', 'RSA PUBLIC KEY')

                pem_ascii = self.pub_key_pem.encode("ascii")

                self.pub_key_pem_b64 = base64.b64encode(pem_ascii).decode("ascii")
                self.fingerprint = hashlib.sha256(pem_ascii).hexdigest()

                with open(self.fingerprint_path, 'w+t') as fp:
                    fp.write(self.fingerprint)

                # no exception, keys loaded correctly.
                self._view.on_starting()
                if not os.path.exists(f'{self.priv_path}.original'):
                    shutil.copy(self.priv_path, f'{self.priv_path}.original')
                if not os.path.exists(f'{self.pub_path}.original'):
                    shutil.copy(self.pub_path, f'{self.pub_path}.original')
                if not os.path.exists(f'{self.fingerprint_path}.original'):
                    shutil.copy(self.fingerprint_path, f'{self.fingerprint_path}.original')
                return

            except Exception as e:
                # if we're here, loading the keys broke something ...
                logging.exception("error loading keys, maybe corrupted, deleting and regenerating ...")
                try:
                    os.remove(self.priv_path)
                    os.remove(self.pub_path)
                except:
                    pass

    def sign(self, message):
        hasher = SHA256.new(message.encode("ascii"))
        signer = PKCS1_PSS.new(self.priv_key, saltLen=16)
        signature = signer.sign(hasher)
        signature_b64 = base64.b64encode(signature).decode("ascii")
        return signature, signature_b64
