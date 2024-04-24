import json
import sys

from nacl.encoding import HexEncoder
from nacl.signing import SigningKey, VerifyKey

class Verifier:
    def __init__(self, verify_key):
        if isinstance(verify_key, VerifyKey):
            self.key = verify_key
        elif isinstance(verify_key, str):
            self.key = VerifyKey(verify_key.encode('utf-8'), encoder=HexEncoder)
        else:
            raise ValueError()

    def verify(self, item):
        assert isinstance(item, dict)
        item_to_sign = {**item, '_sign': None}
        item_bytes = json.dumps(item_to_sign, sort_keys=True).encode('utf-8')
        return self.key.verify(item_bytes, HexEncoder.decode(item['_sign'].encode('utf-8')))

    def __str__(self):
        return self.key.encode(HexEncoder).decode('utf-8')

class Signer:
    def __init__(self, key=None):
        if key is None:
            self.key = SigningKey.generate()
        elif isinstance(key, SigningKey):
            self.key = key
        elif isinstance(key, bytes):
            self.key = SigningKey(key)
        else:
            key_path = str(key)
            with open(key_path, 'rb') as f:
                self.key = SigningKey(f.read())
    @property
    def verifier(self):
        return Verifier(self.key.verify_key)

    @property
    def save(self, location):
        with open(str(location), 'wb') as f:
             f.write(self.key.encode())

    def sign(self, item):
        assert isinstance(item, dict)
        item_to_sign = {**item, '_sign': None}
        item_bytes = json.dumps(item_to_sign, sort_keys=True).encode('utf-8')
        signature = self.key.sign(item_bytes)
        signature = signature[:64]
        signature = HexEncoder.encode(signature)
        signature = signature.decode('utf-8')
        print('signature', len(signature), signature, file=sys.stderr)
        return {
            **item_to_sign,
            '_sign': signature
        }

