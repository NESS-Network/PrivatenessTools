from NessKeys.CryptorMaker import CryptorMaker
from NessKeys.PasswordCryptor import PasswordCryptor
from NessKeys.BlockCryptor import BlockCryptor
from NessKeys.ConsoleOutput import ConsoleOutput
from Crypto.Random import get_random_bytes
import random
import uuid
import os
from base64 import b64encode
from base64 import b64decode

def files_same(file1, file2): 
    with open(file1, "rb") as one: 
        with open(file2, "rb") as two: 
            chunk = other = True 
            while chunk or other: 
                chunk = one.read(1000) 
                other = two.read(1000) 
                if chunk != other: 
                    return False 
    
    return True 

print("==ENCRYPTION==")

password = "12345"

def rand_text(dup: int = 10):
    return  str(uuid.uuid4()) * dup

text = rand_text(100)

cryptor = CryptorMaker.make('salsa20')
pc = PasswordCryptor(cryptor, password)
enc_text = b64encode(pc.encrypt(bytes(text, 'utf8'))).decode('utf-8')
crc = b64encode(pc.crc(bytes(text, 'utf8'))).decode('utf-8')

dec_text = pc.decrypt( b64decode(enc_text), b64decode(crc) ).decode('utf-8')

print("Salsa20", text == dec_text)


def rand_text(dup: int = 10):
    return  str(uuid.uuid4()) * dup

text = rand_text(100)

cryptor = CryptorMaker.make('aes')
pc = PasswordCryptor(cryptor, password)
enc_text = b64encode(pc.encrypt(bytes(text, 'utf8'))).decode('utf-8')
crc = b64encode(pc.crc(bytes(text, 'utf8'))).decode('utf-8')

dec_text = pc.decrypt( b64decode(enc_text), b64decode(crc) ).decode('utf-8')

print("AES", text == dec_text)




cryptor = CryptorMaker.make('salsa20')
# block_size = 1024**2
block_size = 1024 * 32
filename = os.path.dirname(__file__) + '/sample.jpg'
filename_enc = os.path.dirname(__file__) + '/sample.enc'
filename_dec = os.path.dirname(__file__) + '/smpl.jpg'
cipher = get_random_bytes(32)

bc = BlockCryptor(cryptor, cipher[:cryptor.getBlockSize()], ConsoleOutput(), block_size)
bc.encrypt(filename, filename_enc)
bc.decrypt(filename_enc, filename_dec)

print("Salsa20 file ecryption ", files_same(filename, filename_dec))


cryptor = CryptorMaker.make('aes')
# block_size = 1024**2
block_size = 1024 * 32
filename = os.path.dirname(__file__) + '/sample.jpg'
filename_enc = os.path.dirname(__file__) + '/sample.enc'
filename_dec = os.path.dirname(__file__) + '/smpl.jpg'
cipher = get_random_bytes(32)

bc = BlockCryptor(cryptor, cipher[:cryptor.getBlockSize()], ConsoleOutput(), block_size)
bc.encrypt(filename, filename_enc)
bc.decrypt(filename_enc, filename_dec)

print("AES file ecryption ", files_same(filename, filename_dec))