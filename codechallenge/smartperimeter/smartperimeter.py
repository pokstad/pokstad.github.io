#!/usr/local/Cellar/python/2.7.12/bin/python

"""
Copyright Paul Okstad 2016
pokstad@icloud.com
http://pokstad.com/codechallenge/smartperimeter/challenge_response.html

This script utilizes the home brew Python version 2.7
along with pyOpenSSL v0.16 on macOS 10.11.5 (El Capitan).
The environment can be set up as follows:

1. Install brew: `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
2. Install python `brew install python`
3. Install pyopenssl `brew install pyopenssl 0.16`

I used pyOpenSSL because it is a very narrow wrapper around OpenSSL
and is included with most Python distros as a standard library. In
order to get the public key dumping functionality, I needed to use
a newer version of the library. By default, macOS uses v0.13 but I
needed v0.16.

A continuous integration service can execute my unit tests by
running the test_smartperimeter.py file.

"""

import json
import argparse
import OpenSSL
from OpenSSL import crypto
import shelve
import base64

# Shelf file location (relative to execution)
PERSISTANCE_FILE = "keypair.shelve"

# Shelf keys
SHELF_PRIVATE_KEY = "private"
SHELF_PUBLIC_KEY = "public"

# Crypto settings
KEY_FILE_TYPE = crypto.FILETYPE_PEM
KEY_CRYPTO_TYPE = crypto.TYPE_RSA
KEY_CRYPTO_LENGTH = 2048
SIGNATURE_DIGEST_ALG = 'sha256'

# Useful when running script directly with options
def setup_parser():
    """Configures command line parser
    inputs: none
    outputs: configured ArgumentParser object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'inputMessage',
        help="The string you wish to sign with your private key.")
    return parser

# MessageSigner is the core of the script. It maintains the state of the message signing.
# The message signing depends on two main things: the private key and the message to sign.
class MessageSigner:
    shelf = None
    pkey = None
    message = None
    file_path = PERSISTANCE_FILE
    
    def __init__(self, message):
        """
        Initialize MessageSigner instance with string message.
        inputs: message is a string object that can range between 1-250 characters
        outputs: none
        """
        self.message = message
        return
        
    def __enter__(self):
        """
        MessageSigner instances are designed to be used within a "with" block.
        inputs: None
        outputs: self
        """
        self.shelf = shelve.open(self.file_path)
        self.load_keypair()
        return self
        
    @property
    def signature(self):
        """
        Signature is a read only property that contains the crypto signature of our message in base64
        inputs: none
        outputs: base64 encoded string of signature of SHA256 digest of message
        """
        return base64.standard_b64encode(crypto.sign(self.pkey, self.message, SIGNATURE_DIGEST_ALG))
    
    @property
    def pubkey(self):
        """
        Pubkey is a read only property that is derived from our private key.
        inputs: none
        outputs: ASCII encoded public key string
        """
        return self.shelf[SHELF_PUBLIC_KEY]
    
    @property
    def json_response(self):
        """
        json_response is a read only property that generates a JSON structure serialized into a string
        inputs: none
        outputs: string representing JSON structure
        """
        return json.dumps({
            'message':self.message,
            'pubkey':self.pubkey,
            'signature':self.signature
        }, sort_keys=True, indent=4)
        
    def load_keypair(self):
        """
        load_keypair attempts to load a private and public keypair from the persistence shelf.
        If no keypair can be found, a new one will be generated.
        inputs: none
        outputs: pyOpenSSL PKey object that can represent an RSA 2048 bit private & public key
        """
        if self.shelf.has_key(SHELF_PRIVATE_KEY):
            self.pkey = crypto.load_privatekey(KEY_FILE_TYPE, self.shelf[SHELF_PRIVATE_KEY])
            return
        # key pair doesn't exist, so generate it and store it
        self.pkey = crypto.PKey()
        self.pkey.generate_key(KEY_CRYPTO_TYPE, KEY_CRYPTO_LENGTH)
        self.shelf[SHELF_PRIVATE_KEY] = crypto.dump_privatekey(KEY_FILE_TYPE, self.pkey)
        self.shelf[SHELF_PUBLIC_KEY] = crypto.dump_publickey(KEY_FILE_TYPE, self.pkey)
        return
        
    def __exit__(self, exception_type, exception_value, traceback):
        """
        This is how we close the shelf at the end of a "with" block.
        """
        self.shelf.close()

def main():
    args = setup_parser().parse_args()
    message = args.inputMessage
    with MessageSigner(message) as ms:
        print(ms.json_response)

if __name__ == '__main__':
	main()
