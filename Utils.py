import math


def is_prime(number):
    return number > 1 and all([number % divisor != 0
                               for divisor in range(2, int(math.sqrt(number)) + 1)])


class Cipher(object):
    def __init__(self, key):
        self.key = key

    def decrypt(self, message):
        return ''.join([self.decrypt_character(char, self.key) for char in message])

    @staticmethod
    def decrypt_character(char, key):
        return chr((ord(char) - key + 256) % 256)

    def encrypt(self, message):
        return ''.join([self.encode_character(char, self.key) for char in str(message)])

    @staticmethod
    def encode_character(char, key):
        return chr((ord(char) + key) % 256)


class RSA(object):
    def __init__(self, p, q, e):
        self.p = p
        self.q = q
        self.e = e
        self.n = p * q
        self.d = self.generate_private_key()

    def generate_private_key(self):
        phi = (self.p - 1) * (self.q - 1)
        candidate = extended_euclidean(phi, self.e)
        return candidate if candidate > 0 else candidate + phi

    def sign(self, m):
        return ':'.join([str(mod_pow(number, self.d, self.n)) for number in m])


def extended_euclidean(number, remainder):
    current = 1
    last = 0
    original_number = number
    original_remainder = remainder
    while remainder:
        number, quotient, remainder = remainder, number // remainder, number % remainder
        last, current = current - quotient * last, last
    return (1 - current * original_number) // original_remainder


def mod_pow(a, m, p):
    return a ** m % p
