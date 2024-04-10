"""The common module contains common functions and classes used by the other modules.
"""

def hello_world():
    """Prints "Hello World!" to the console.
    """
    print("Hello World!")

def random_number():
    """Returns a random number between 1 and 100.
    """
    import random
    return random.randint(1, 100)