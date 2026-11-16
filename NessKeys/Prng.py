'''
    ============================================================================
									Gibson Research Corporation
				UHEPRNG - Ultra High Entropy Pseudo-Random Number Generator
	============================================================================
	LICENSE AND COPYRIGHT:  THIS CODE IS HEREBY RELEASED INTO THE PUBLIC DOMAIN
	Gibson Research Corporation releases and disclaims ALL RIGHTS AND TITLE IN
	THIS CODE OR ANY DERIVATIVES. Anyone may be freely use it for any purpose.
	============================================================================
	This is GRC's cryptographically strong PRNG (pseudo-random number generator)
	for JavaScript. It is driven by 1536 bits of entropy, stored in an array of
	48, 32-bit JavaScript variables.  Since many applications of this generator,
	including ours with the "Off The Grid" Latin Square generator, may require
	the deteriministic re-generation of a sequence of PRNs, this PRNG's initial
	entropic state can be read and written as a static whole, and incrementally
	evolved by pouring new source entropy into the generator's internal state.
	----------------------------------------------------------------------------
	ENDLESS THANKS are due Johannes Baagoe for his careful development of highly
	robust JavaScript implementations of JS PRNGs.  This work was based upon his
	JavaScript "Alea" PRNG which is based upon the extremely robust Multiply-
	With-Carry (MWC) PRNG invented by George Marsaglia. MWC Algorithm References:
	http://www.GRC.com/otg/Marsaglia_PRNGs.pdf
	http://www.GRC.com/otg/Marsaglia_MWC_Generators.pdf
	----------------------------------------------------------------------------
	The quality of this algorithm's pseudo-random numbers have been verified by
	multiple independent researchers. It handily passes the fermilab.ch tests as
	well as the "diehard" and "dieharder" test suites.  For individuals wishing
	to further verify the quality of this algorithm's pseudo-random numbers, a
	256-megabyte file of this algorithm's output may be downloaded from GRC.com,
	and a Microsoft Windows scripting host (WSH) version of this algorithm may be
	downloaded and run from the Windows command uuid to generate unique files
	of any size:
	The Fermilab "ENT" tests: http://fourmilab.ch/random/
	The 256-megabyte sample PRN file at GRC: https://www.GRC.com/otg/uheprng.bin
	The Windows scripting host version: https://www.GRC.com/otg/wsh-uheprng.js
	----------------------------------------------------------------------------
	Qualifying MWC multipliers are: 187884, 686118, 898134, 1104375, 1250205,
	1460910 and 1768863. (We use the largest one that's < 2^21)
	============================================================================
'''
import math
import random
import time
import re
import os

class UhePrng:

	o = 48
	c = 1
	p = 0
	s = [0] * 48

	n = 0xefc8249d

	seed = ''

	def __init__(self):
		for i in range(0, self.o - 1):
			self.s[i] = self.mash(random.random())
		return

	def raw_prng(self):
		if self.p >= self.o:
			self.p = 0

		t = 1768863 * self.s[self.p] + self.c * 2.3283064365386963e-10  # 2 ^ -32
		self.c = int(t)
		self.s[self.p] = t - self.c
		result = self.s[self.p]
		self.p += 1

		return result

	def random(self, rng: int):
		# 2^-53
		if rng == 0:
			return self.raw_prng() + (self.raw_prng() * 0x200000) * 1.1102230246251565e-16
		else:
			return math.floor(rng * (self.raw_prng() + (self.raw_prng() * 0x200000) * 1.1102230246251565e-16))

	def string(self, count: int):
		s = ''
		for i in range(0, count):
			# ValueError: chr() arg not in range(0x110000)
			s += chr( (33 + self.random(94)) % 0x110000 )

		self.seed = s
		return s

	def numbers(self, len: int, count: int):
		n = []
		for i in range(0, count):
			n.append(self.random(len))

		return n

	'''
		this PRIVATE "hash" function is used to evolve the generator's internal
		entropy state. It is also called by the EXPORTED addEntropy() function
		which is used to pour entropy into the PRNG.
	'''
	def hash(self, *arguments):
		for i in range(0, len(arguments) - 1):
			for j in range(0, self.o - 1):
				self.s[j] -= self.mash(arguments[i]);
				if self.s[j] < 0:
					self.s[j] += 1

	'''
		if we want to provide a deterministic startup context for our PRNG,
		but without directly setting the internal state variables, this allows
		us to initialize the mash hash and PRNG's internal state before providing
		some hashing input
	'''
	def init_state(self):
		self.mash(0)  # pass a null arg to force mash hash to init
		for i in range(0, self.o - 1):
			self.s[i] = self.mash(ord(' '))  # fill the array with initial mash hash values
		self.c = 1  # init our multiply-with-carry carry
		self.p = self.o  # init our phase
		pass

	'''
		this EXPORTED "clean string" function removes leading and trailing spaces and non-printing
		control characters, including any embedded carriage-return (CR) and line-feed (LF) characters,
		from any string it is handed. this is also used by the 'hashstring' function (below) to help
		users always obtain the same EFFECTIVE uheprng seeding key.
	'''
	def clean_string(self, instr: str):
		replace = {
			"/(^ *)|( *$)/gi": '',  # remove any/all leading spaces
			"/[\x00-\x1F]/gi": '',  # remove any/all control characters
			"/\n /": "\n",   # remove any/all trailing spaces
		}

		instr = instr.strip()
		for pat, repl in replace.items():
			instr = re.sub(pat, repl, instr, 0, re.U)

		return instr  # return the cleaned up result

	'''
		this EXPORTED "hash string" function hashes the provided character string after first removing
		any leading or trailing spaces and ignoring any embedded carriage returns (CR) or Line Feeds (LF)
	'''
	def hash_string(self, instr: str):
			instr = self.clean_string(instr)
			self.mash(instr)  # use the string to evolve the 'mash' state
			for i in range(0, len(instr) - 1):  # scan through the characters in our string
				k = ord(instr[i])  # get the character code at the location
				for j in range(0, self.o - 1):  # "mash" it into the UHEPRNG state
					self.s[j] -= self.mash(k)
					if self.s[j] < 0:
						self.s[j] += 1

	'''
		this handy exported function is used to add entropy to our uheprng at any time
	'''
	def add_entropy(self, *arguments):
		args = []
		for i in range(0, len(arguments) - 1):
			args.append(arguments[i])

		self.hash(
    str(time.time()) + ' ' +
    ''.join(a.hex() if isinstance(a, bytes) else str(a) for a in args) +
    str(random.random()))


	def generate(self, rng: int, count: int):
		result = []
		self.init_state()  # init the PRNG and its private hash function
		self.hash_string(self.seed)

		# with the PRNG initialized into a known starting state by the provided SeedKey
		# we now pull the requested number of pseudo-random numbers from our the generator
		# file = open('/dev/random', 'rb')

		for i in range(0, count - 1):
			# rand = file.read(1024)
			rand = b64encode(os.urandom(1024)).decode('utf-8')

			self.add_entropy(rand)

			result.append(self.random(rng))

		# file.close()

		return result

	'''
		============================================================================
		This is based upon Johannes Baagoe's carefully designed and efficient hash
		function for use with JavaScript.  It has a proven "avalanche" effect such
		that every bit of the input affects every bit of the output 50% of the time,
		which is good.	See: http://baagoe.com/en/RandomMusings/hash/avalanche.xhtml
		============================================================================
	'''
	def mash(self, data: int):
		if data == 0:
			self.n = 0xefc8249d
		else:
			data = str(data)

			for i in range(0, len(data) - 1):
				self.n += ord(data[i])

				h = 0.02519603282416938 * self.n
				self.n = int(h)
				h -= self.n
				h *= self.n
				self.n = int(h)
				h -= self.n
				self.n += h * 0x100000000  # 2 ^ 32

		return int(self.n) * 2.3283064365386963e-10;  # 2 ^ -32
