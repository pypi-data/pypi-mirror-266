"""The common module contains common functions and classes used by the other modules.
"""

def hello_world():
    """Prints "Hello World!" to the console.
    """
    print("Hello World!")


def calculate_average(sequence):
    """
    Calculate the average value of a sequence.

    Args:
        sequence (list or tuple): The sequence of numbers.

    Returns:
        float: The average value of the sequence.
    """
    if not sequence:
        return None  # Return None for empty sequence

    total = sum(sequence)
    average = total / len(sequence)
    return average

# Given sequence
number = (1, 5, 5, 6, 7)

# Calculating the mean
mean_value = calculate_average(number)
print("Mean:", mean_value)
