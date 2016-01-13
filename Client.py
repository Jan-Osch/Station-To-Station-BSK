import random
import threading

from Utils import is_prime


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

    def send_initial_message(self):
        return self.g ** self.alpha % self.p

    def decode_message(self, server_number, encrypted_message):
        return self.alpha ** server_number % self.p

    def send_final_message(self):
        pass

    def run(self):
        self.alpha = self.create_private_key()
