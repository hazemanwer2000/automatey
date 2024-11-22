
import string
import random

def getRandomString(n=8):
    characterPool = string.ascii_letters + string.digits
    randomString = ''.join(random.choices(characterPool, k=n))
    return randomString.upper()