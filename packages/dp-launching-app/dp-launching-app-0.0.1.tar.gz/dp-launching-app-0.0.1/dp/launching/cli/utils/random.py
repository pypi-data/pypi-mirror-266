import random
import string


def get_random_str(len: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=len))
