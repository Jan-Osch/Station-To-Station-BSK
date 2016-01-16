import random
import threading

from Utils import is_prime, Cipher, mod_pow


class Client(threading.Thread):
    def __init__(self, name, g, p, input_queue, output_queue, rsa_obj, keys, server_id):
        super(Client, self).__init__()
        self.finished_successfully = None
        self.p = p
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.rsa_obj = rsa_obj
        self.keys = keys
        self.server_id = server_id
        self.g = g
        self.name = name

    def create_private_key(self):
        candidate = random.randint(0, self.p - 2)
        while not is_prime(candidate):
            candidate = random.randint(0, self.p - 2)
        return candidate

    def send_final_message(self):
        pass

    def run(self):
        alpha = self.create_private_key()
        own_number = mod_pow(self.g, alpha, self.p)

        self.output_queue.put(own_number)
        message_from_server = self.input_queue.get(timeout=1000)

        if self.is_message_valid(message_from_server):
            server_number, encrypted_message = message_from_server
            shared_key = mod_pow(alpha, server_number, self.p)
            cipher = Cipher(shared_key)

            if self.is_encrypted_message_valid(own_number, server_number, encrypted_message, cipher):
                self.output_queue.put(self.prepare_final_message(own_number, server_number, cipher))
                self.finished_successfully = True
                return
        self.finished_successfully = False

    @staticmethod
    def is_message_valid(message_from_server):
        try:
            return message_from_server != 'ERROR' or len(message_from_server) == 2
        except:
            return False

    def prepare_final_message(self, own_number, server_number, cipher):
        signed_message = self.rsa_obj.sign((own_number, server_number))
        return cipher.encrypt(signed_message)

    def is_encrypted_message_valid(self, own_number, server_number, encrypted_message, cipher):
        try:
            first, second = cipher.decrypt(encrypted_message).split(':')
            server_public_key, server_n = self.keys.get(self.server_id)
            return self.is_signature_valid(first, own_number, server_public_key, server_n) and \
                   self.is_signature_valid(second, server_number, server_public_key, server_n)
        except:
            return False

    @staticmethod
    def is_signature_valid(signed_message, expected_content, public_key, n):
        try:
            actual_content = mod_pow(int(signed_message), public_key, n)
            return actual_content == expected_content
        except:
            return False
