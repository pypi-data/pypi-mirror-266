from cryptography.fernet import Fernet
import uuid


def encrypt_message(message, key):
    f = Fernet(key)
    return f.encrypt(message.encode())


def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    return f.decrypt(encrypted_message).decode()


def generate_uuid4():
    return uuid.uuid4()