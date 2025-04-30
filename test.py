from Crypto.Hash import SHA3_256
from base64 import b32encode
from base64 import b32decode
import textwrap

data = b'eb5606b44d2ef77af3753904a8139450-17-millions.mp4'

h_obj = SHA3_256.new()
h_obj.update(data)
print(h_obj.hexdigest())
hashstring = b32encode(h_obj.digest()).decode('utf-8')
print(hashstring)

print(' '.join(textwrap.wrap(hashstring, 4)))