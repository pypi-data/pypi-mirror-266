import random


class GenerateRandomString:
    def __init__(self):
        self.alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'g', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                         't', 'u', 'v', 'w', 'x', 'y', 'z']
        self.alphabet_upper = [i.upper() for i in self.alphabet]
        self.nums = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    def random(self, length=32):
        sorts = self.alphabet + self.alphabet_upper + self.nums
        return "".join(random.choices(sorts, k=length))

    def alphabet_random(self, length=32, ignore=False):
        sorts = self.alphabet + self.alphabet_upper
        if ignore: sorts = self.alphabet
        return "".join(random.choices(sorts, k=length))

    def num_random(self, length=32):
        return "".join(random.choices(self.nums, k=length))
