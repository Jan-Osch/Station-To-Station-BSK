import math


def is_prime(number):
    return number > 1 and all([number % divisor != 0
                               for divisor in range(2, int(math.sqrt(number)) + 1)])
