from Crypto.Hash import SHA3_256
from base64 import b32encode
from base64 import b32decode
import textwrap

data = b'SHA-3 is the latest member of the Secure Hash Algorithm family of standards, released by NIST on August 5, 2015.'

h_obj = SHA3_256.new()
h_obj.update(data)
print(h_obj.hexdigest())
hashstring = b32encode(h_obj.digest()).decode('utf-8')
print(hashstring)

print(' '.join(textwrap.wrap(hashstring, 4)))