import threading
import unittest
from Queue import Queue

from mock import MagicMock, patch

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

    def test_create_initial_message_returns_correct_number(self):
        p = 4121
        self.client.p = p
        g = 123
        self.client.g = g
        alpha = 231
        self.client.alpha = alpha
        expected = g ** alpha % p

        actual = self.client.generate_own_number()

        self.assertEqual(actual, expected)

    def test_decode_message_method_returns_exchanged_key_as_first_argument(self):
        p = 41
        self.client.p = p
        alpha = 17
        self.client.alpha = alpha
        message = 16
        expected = alpha ** message % p

        result = self.client.generate_shared_key(message)

        self.assertEqual(result, expected)

    @patch('Client.Cipher')
    def test_run_creates_alpha_by_calling_create_private_key(self, mock_cipher):
        self.client.output_queue = MagicMock()
        MagicMock().attach_mock(self.client.output_queue, 'put')
        value = 'mock_value'
        self.client.create_private_key = MagicMock(return_value=value)
        self.client.generate_own_number = MagicMock()
        self.client.input_queue = MagicMock()
        self.client.rsa_obj = MagicMock()

        self.client.run()

        self.assertEqual(self.client.alpha, value)

    @patch('Client.Cipher')
    def test_run_creates_initial_message_saves_it_and_puts_on_output_queue(self, mock_cipher):
        self.client.create_private_key = MagicMock()
        self.client.output_queue = MagicMock()
        MagicMock().attach_mock(self.client.output_queue, 'put')
        mock_message = 'mock_message'
        self.client.generate_own_number = MagicMock(return_value=('%s' % mock_message))
        self.client.input_queue = MagicMock()
        self.client.rsa_obj = MagicMock()

        self.client.run()

        self.client.output_queue.put.assert_called_once_with(mock_message)
        self.assertEqual(self.client.own_number, mock_message)

    @patch('Client.Cipher')
    def test_run_calls_get_on_input_queue_and_sets_finish_flag_to_false_for_error(self, mock_cipher):
        self.client.create_private_key = MagicMock()
        self.client.output_queue = MagicMock()
        MagicMock().attach_mock(self.client.output_queue, 'put')
        self.client.generate_own_number = MagicMock()
        self.client.input_queue = MagicMock()
        error_signal = 'ERROR'
        self.client.input_queue.get = MagicMock(return_value=error_signal)
        self.client.rsa_obj = MagicMock()

        self.client.run()

        timeout = 1000
        self.client.input_queue.get.assert_called_once_with(timeout=timeout)
        self.assertIsNotNone(self.client.finished_successfully)
        self.assertFalse(self.client.finished_successfully)

    @patch('Client.Cipher')
    def test_if_message_does_not_match_sets_finish_flag_to_false(self, mock_cipher):
        mock_cipher.return_value = MagicMock()
        different_value = 'different_value'
        mock_cipher.decode.return_value = different_value

        self.client.create_private_key = MagicMock()
        self.client.output_queue = MagicMock()
        MagicMock().attach_mock(self.client.output_queue, 'put')
        self.client.generate_own_number = MagicMock()
        self.client.input_queue = MagicMock()
        response = [123123, 'some_value']
        self.client.input_queue.get = MagicMock(return_value=response)
        self.client.rsa_obj = MagicMock()
        self.client.rsa_obj.sign.return_value = different_value

        self.client.run()

        self.assertIsNotNone(self.client.finished_successfully)
        self.assertFalse(self.client.finished_successfully)

    @patch('Client.Cipher')
    def test_run_will_create_a_cipher_object_from_shared_key(self, mock_cipher):
        different_value = 'different_value'
        mock_cipher.decode.return_value = different_value

        self.client.create_private_key = MagicMock()
        self.client.output_queue = MagicMock()
        MagicMock().attach_mock(self.client.output_queue, 'put')
        self.client.generate_own_number = MagicMock()
        self.client.input_queue = MagicMock()
        self.client.generate_shared_key = MagicMock(return_value='shared_key')
        response = [123123, 'some_value']
        self.client.input_queue.get = MagicMock(return_value=response)
        self.client.rsa_obj = MagicMock()
        self.client.rsa_obj.sign.return_value = different_value

        self.client.run()

        mock_cipher.assert_called_once_with('shared_key')

    @patch('Client.Cipher')
    def test_run_will_set_finish_flag_to_true_when_signature_matches(self, mock_cipher):
        different_value = 'different_value'
        mocksToCreate = [MagicMock()]
        mocksToCreate[0].decode.return_value = different_value
        mock_cipher.side_effect = mocksToCreate

        self.client.create_private_key = MagicMock()
        self.client.output_queue = MagicMock()
        MagicMock().attach_mock(self.client.output_queue, 'put')
        self.client.generate_own_number = MagicMock()
        self.client.input_queue = MagicMock()
        self.client.generate_shared_key = MagicMock(return_value='shared_key')
        response = [123123, 'some_value']
        self.client.input_queue.get = MagicMock(return_value=response)
        self.client.rsa_obj = MagicMock()
        self.client.rsa_obj.sign.return_value = different_value

        self.client.run()

        self.assertIsNotNone(self.client.finished_successfully)
        self.assertTrue(self.client.finished_successfully)




if __name__ == '__main__':
    unittest.main()
