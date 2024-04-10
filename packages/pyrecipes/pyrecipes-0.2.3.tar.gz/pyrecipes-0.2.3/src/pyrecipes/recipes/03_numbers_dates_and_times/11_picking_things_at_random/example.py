"""
You want to pick random items out of a sequence or generate random numbers.
"""
import random


def main():
    random.seed(0)
    values = [1, 2, 3, 4, 5, 6]
    print("values:", values)

    print("\npick a random value from values")
    for _ in range(5):
        print(random.choice(values))

    print("\npick a random sample of values from values")
    for _ in range(5):
        print(random.sample(values, 3))

    print("\nrandomly shuffle values")
    for _ in range(5):
        random.shuffle(values)
        print(values)

    print("\npick a random integer")
    for _ in range(5):
        print(random.randint(0, 10))

    print("\npick a random floating-point between 0-1")
    for _ in range(5):
        print(random.random())

    print("\nget N random bits expressed as an integer")
    for _ in range(5):
        print(random.getrandbits(200))


if __name__ == "__main__":
    main()
