from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from django.conf import settings


def encode(data):
    return bytes(data, "raw_unicode_escape")


def decode(data):
    return str(data, "raw_unicode_escape")


def encrypt(value):
    return decode(f.encrypt(encode(value)))


def decrypt(value):
    try:
        return decode(f.decrypt(encode(value)))
    except InvalidToken:
        return "Invalid Token"


def decrypt_by_key(value, key):
    try:
        f = Fernet(encode(key))
        return decode(f.decrypt(encode(value)))
    except InvalidToken:
        return "Invalid Token"


def is_encrypted(value):
    return value.startswith("gAAAAA")


if hasattr(settings, "ENCRYPTION_KEY"):
    f = Fernet(encode(settings.ENCRYPTION_KEY))
