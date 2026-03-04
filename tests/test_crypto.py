from datachain.crypto import Signer, Verifier
from nacl.exceptions import BadSignatureError
import pytest

def test_sign():
    signer = Signer()
    signed = signer.sign(dict(teste=True))

    verifier = signer.verifier
    verifier.verify(signed)

    pubkey = str(verifier)

    new_verifier = Verifier(pubkey)
    new_verifier.verify(signed)
    

    with pytest.raises(BadSignatureError):
        modified_signed = {**signed}
        modified_signed['_sign'] = [c for c in modified_signed['_sign']]
        for i in range(len(modified_signed['_sign'])):
            if modified_signed['_sign'][0] != modified_signed['_sign'][i + 1]: 
                modified_signed['_sign'][0] = modified_signed['_sign'][i+1]
                break
        modified_signed['_sign'] = "".join(modified_signed['_sign'])
        signer.verifier.verify(modified_signed)
