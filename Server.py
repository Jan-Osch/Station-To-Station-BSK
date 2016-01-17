import random
import threading

from Utils import is_prime, mod_pow, Cipher


class AbstractEntity(threading.Thread):
    def __init__(self, name, g, p, input_queue, output_queue, rsa_obj, keys):
        super(AbstractEntity, self).__init__()
        self.p = p
        self.g = g
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.rsa_obj = rsa_obj
        self.keys = keys
        self.name = name

        self.finished_successfully = None
        self.K = None
        self.timeout = 1

    def create_private_key(self):
        candidate = random.randint(0, self.p - 2)
        while not is_prime(candidate):
            candidate = random.randint(0, self.p - 2)
        return candidate

    @staticmethod
    def is_message_valid(message, intended_length):
        try:
            if intended_length > 1:
                return len(message) == intended_length and message != 'ERROR'
            return message != 'ERROR'
        except:
            return False

    def run(self):
        raise NotImplementedError

    @staticmethod
    def is_signature_valid(signed_message, expected_content, public_key, n):
        try:
            actual_content = mod_pow(int(signed_message), public_key, n)
            return actual_content == expected_content
        except:
            return False

    def prepare_encrypted_message(self, first_number, second_number, cipher):
        signed_message = self.rsa_obj.sign((first_number, second_number))
        return cipher.encrypt(signed_message)

    def is_encrypted_message_valid(self, client_number, server_number, encrypted_message, cipher, partner_id):
        try:
            first, second = cipher.decrypt(encrypted_message).split(':')
            partner_public_key, partner_n = self.keys.get(partner_id)
            if self.is_signature_valid(signed_message=first,
                                       expected_content=client_number,
                                       public_key=partner_public_key,
                                       n=partner_n):
                return self.is_signature_valid(signed_message=second,
                                               expected_content=server_number,
                                               public_key=partner_public_key,
                                               n=partner_n)
        except:
            pass
        return False


class Server(AbstractEntity):
    def __init__(self, name, g, p, input_queue, output_queue, rsa_obj, keys, client_id):
        super(Server, self).__init__(name, g, p, input_queue, output_queue, rsa_obj, keys)
        self.client_id = client_id
        self.name = name

    def run(self):
        try:
            client_number = self.input_queue.get(timeout=self.timeout)

            if self.is_message_valid(client_number, intended_length=1):
                beta = self.create_private_key()
                own_number = mod_pow(self.g, beta, self.p)
                self.K = mod_pow(client_number, beta, self.p)
                cipher = Cipher(self.K)
                self.output_queue.put((own_number,
                                       self.prepare_encrypted_message(first_number=client_number,
                                                                      second_number=own_number,
                                                                      cipher=cipher)),
                                      timeout=self.timeout)

                client_message = self.input_queue.get(timeout=self.timeout)

                if self.is_message_valid(client_message, intended_length=1):
                    if self.is_encrypted_message_valid(client_number=client_number,
                                                       server_number=own_number,
                                                       encrypted_message=client_message,
                                                       cipher=cipher,
                                                       partner_id=self.client_id):
                        self.finished_successfully = True
                        return
        except:
            pass
        self.finished_successfully = False
