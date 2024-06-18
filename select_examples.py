import random

def generate_random_numbers(minimum, maximum, count):
    # get random numbers within specified range
    result = random.sample(range(minimum, maximum + 1), count)
    result.sort()
    return result

min_number = 6
max_number = 15
num_examples = 8

random_numbers = generate_random_numbers(min_number, max_number, num_examples)

print("Number of examples:", num_examples)
print("Random numbers:", random_numbers)