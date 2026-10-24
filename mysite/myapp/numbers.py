from math import isqrt


def is_prime(number):
    if number < 2:
        return False
    for divisor in range(2, isqrt(number) + 1):
        if number % divisor == 0:
            return False
    return True


def select_numbers(start, end, number_type):
    """Обе границы включены; диапазон предварительно проверяется формой."""
    numbers = []
    for number in range(start, end + 1):
        if (number_type == "all"
                or number_type == "even" and number % 2 == 0
                or number_type == "odd" and number % 2 != 0
                or number_type == "prime" and is_prime(number)):
            numbers.append(number)
    return numbers
