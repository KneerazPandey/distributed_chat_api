import random

class RandomGenerator:
    @staticmethod
    def generate_otp(length=6):
         return str(random.randint(100000, 999999))
        