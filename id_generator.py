import random

def generate_random_number(num_digits):
    # Calculate the range within which the random number should fall
    min_value = 10 ** (num_digits - 1)
    max_value = (10 ** num_digits) - 1

    # Generate a random integer within the specified range
    random_number = random.randint(min_value, max_value)

    return random_number


