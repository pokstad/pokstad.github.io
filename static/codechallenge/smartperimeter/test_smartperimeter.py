#!/usr/local/Cellar/python/2.7.12/bin/python

import unittest
import smartperimeter as sp
import json
from random import choice
from string import ascii_uppercase

"""
Copyright Paul Okstad 2016
pokstad@icloud.com
http://pokstad.com/codechallenge/smartperimeter/challenge_response.html

Tests based on requirements:

1. String input of up to 250 characters
2. Returns a JSON response compliant to the schema defined below
3. Generate a public/private RSA keypair
4. Keypair should persist on the filesystem
5. Subsequent invocations of your application should read from the same files
"""

def random_string(char_count):
    return ''.join(choice(ascii_uppercase) for i in range(char_count))

class TestSigning(unittest.TestCase):

    def test_input_length(self):
        # random string inputs of up to 250 characters should be signable
        for i in range(0,250):
            testMessage = random_string(i)
            with sp.MessageSigner(testMessage) as testMS:
                sig = testMS.signature
                # valid signatures are 344 base64 chars long
                self.assertEqual(len(sig), 344, "Unexpected base64 signature length")

    def test_persistence(self):
        # The same key should be used between invocations via filesystem persistence:
        pubkey = None
        testMessage = "theAnswerIs42"
        with sp.MessageSigner(testMessage) as firstInvocation:
            pubkey = firstInvocation.pubkey
        # now the second invocation should use the same file
        with sp.MessageSigner(testMessage) as secondInvocation:
            self.assertEqual(secondInvocation.pubkey, pubkey, "Different public keys between invocations")

    def test_json_response(self):
        # we are required to have 3 JSON fields with string values
        testMessage = "theAnswerIs42"
        with sp.MessageSigner(testMessage) as testMS:
            response = json.loads(testMS.json_response)
            for i in ['message','pubkey','signature']:
                self.failUnless(response.has_key(i), "Missing JSON property %s" % (i))
                # each corresponding value should be a string
                self.failUnless(
                    isinstance(response[i], basestring),
                    "JSON value must be string, instead got: %s" % (response))

if __name__ == '__main__':
    unittest.main()