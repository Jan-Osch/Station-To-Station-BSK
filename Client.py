from Server import AbstractEntity
from Utils import Cipher, mod_pow


class Client(AbstractEntity):
    def __init__(self, name, g, p, input_queue, output_queue, rsa_obj, keys, server_id):
        super(Client, self).__init__(name, g, p, input_queue, output_queue, rsa_obj, keys)
        self.server_id = server_id
        self.name = name

    def run(self):
        alpha = self.create_private_key()
        own_number = mod_pow(self.g, alpha, self.p)
        self.output_queue.put(own_number, timeout=self.timeout)

        message_from_server = self.input_queue.get(timeout=self.timeout)
        if self.is_message_valid(message_from_server, intended_length=2):
            server_number, encrypted_message = message_from_server
            self.K = mod_pow(server_number, alpha, self.p)
            cipher = Cipher(self.K)
            if self.is_encrypted_message_valid(client_number=own_number,
                                               server_number=server_number,
                                               encrypted_message=encrypted_message,
                                               cipher=cipher,
                                               partner_id=self.server_id):
                self.output_queue.put(self.prepare_encrypted_message(own_number, server_number, cipher),
                                      timeout=self.timeout)
                self.finished_successfully = True
                return

        self.finished_successfully = False
