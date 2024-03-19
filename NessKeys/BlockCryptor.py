import NessKeys.interfaces.Cryptor as Cryptor
from NessKeys.interfaces.output import output as ioutput
import os, math
import time

from framework.GLOBAL import GLOBAL

class BlockCryptor:
    def __init__(self, cryptor: Cryptor, key: bytes, output: ioutput, block_size = 1048576):
        self.block_size = block_size
        self.cryptor = cryptor
        self.output = output
        self.key = key

    def encrypt(self, filename_in: str, filename_out: str):
        filesize = os.path.getsize(filename_in)
        rbc = self.block_size - self.cryptor.getBlockAddition()
        blocks = math.ceil(filesize / rbc)
        
        f_in = open(filename_in, "rb")
        f_out = open(filename_out, "ab")

        filesize = os.path.getsize(filename_out)
        blocks_start = math.ceil(filesize / self.block_size)

        f_in.seek(rbc * blocks_start)

        for i in range(blocks_start, blocks):
            if GLOBAL.halt:
                f_in.close()
                f_out.close()
                print("* Encryption stopped *")
                GLOBAL.fn_halt()
                exit()

            if GLOBAL.fn_paused():
                f_in.close()
                f_out.close()
                print("* Encryption paused *")
                exit()

            block = f_in.read(rbc)
            encrypted_block = self.cryptor.encrypt(block, self.key)
            f_out.write(encrypted_block)

            if i > 0:
                GLOBAL.fn_progress(round(i*100/blocks))

            # time.sleep(1)

        f_in.close()
        f_out.close()

        GLOBAL.fn_progress(100)


    def decrypt(self, filename_in: str, filename_out: str):
        filesize = os.path.getsize(filename_in)
        blocks = math.ceil(filesize / self.block_size)
        
        f_in = open(filename_in, "rb")
        f_out = open(filename_out, "ab")

        filesize = os.path.getsize(filename_out)
        rbc = self.block_size - self.cryptor.getBlockAddition()
        blocks_start = math.ceil(filesize / rbc)

        f_in.seek(self.block_size * blocks_start)

        for i in range(blocks_start, blocks):
            if GLOBAL.halt:
                f_in.close()
                f_out.close()
                print("* Decryption stopped *")
                GLOBAL.fn_halt()
                exit()

            if GLOBAL.fn_paused():
                f_in.close()
                f_out.close()
                print("* Decryption paused *")
                exit()

            block = f_in.read(self.block_size)
            decrypted_block = self.cryptor.decrypt(block, self.key)
            f_out.write(decrypted_block)
            if i > 0:
                GLOBAL.fn_progress(round(i*100/blocks))

            # time.sleep(1)

        f_in.close()
        f_out.close()

        GLOBAL.fn_progress(100)