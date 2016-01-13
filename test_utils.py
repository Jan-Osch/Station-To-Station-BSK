import unittest

from Utils import is_prime


class UtilsTest(unittest.TestCase):
    def test_is_prime_returns_false_for_one_and_zero(self):
        self.assertFalse(is_prime(1))
        self.assertFalse(is_prime(0))

    def test_is_prime_returns_true_for_two_and_three(self):
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(3))

    def test_is_prime_returns_false_for_four(self):
        self.assertFalse(is_prime(4))

    def test_is_prime_works_for_a_couple_of_numbers(self):
        self.assertFalse(is_prime(256))
        self.assertFalse(is_prime(133))
        self.assertTrue(is_prime(5))
        self.assertTrue(is_prime(7))
        self.assertTrue(is_prime(11))
        self.assertTrue(is_prime(13))


if __name__ == '__main__':
    unittest.main()
