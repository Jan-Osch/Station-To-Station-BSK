import threading
import unittest

from mock import MagicMock

from Client import Client
from Utils import is_prime


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.client = Client(name='name',
                             g='generator',
                             p='size',
                             input_queue='input_queue',
                             output_queue='output_queue',
                             rsa_obj='rsa-objc',
                             keys='keys',
                             server_id='server_id')

    def test_is_instance_of_thread(self):
        self.assertTrue(isinstance(self.client, threading.Thread))

    def test_create_private_key_returns_a_random_number_smaller_than_p_minus_two(self):
        p = 100
        self.client.p = p
        probe_size = 100
        result = all([0 <= self.client.create_private_key() <= p - 2 for _ in range(probe_size)])

        self.assertTrue(result)

    def test_create_private_key_returns_a_prime_number(self):
        p = 100
        self.client.p = p
        probe_size = 100
        flag = all([is_prime(self.client.create_private_key()) for _ in range(probe_size)])
        self.assertTrue(flag)

    def test_has_a_finished_successfully_property_set_to_None(self):
        self.assertTrue(hasattr(self.client, 'finished_successfully'))
        self.assertEqual(self.client.finished_successfully, None)

    def test_has_send_final_message_method(self):
        self.client.send_final_message()

    def test_run_creates_alpha_by_calling_create_private_key(self):
        value = 'mock_value'
        self.client.create_private_key = MagicMock(return_value=value)
        self.client.run()
        self.assertEqual(self.client.alpha, value)

    def test_send_initial_message_returns_correct_number(self):
        p = 4121
        self.client.p = p
        g = 123
        self.client.g = g
        alpha = 231
        self.client.alpha = alpha
        expected = g ** alpha % p

        actual = self.client.send_initial_message()

        self.assertEqual(actual, expected)

    def test_decode_message_method_returns_exchanged_key_as_first_argument(self):
        p = 41
        self.client.p = p
        alpha = 17
        self.client.alpha = alpha
        message = 16
        expected = alpha ** message % p

        result = self.client.decode_message(message, 'encrypted')

        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
