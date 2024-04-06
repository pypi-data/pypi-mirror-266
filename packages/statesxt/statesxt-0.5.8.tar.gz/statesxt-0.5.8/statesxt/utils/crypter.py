from cryptography.fernet import Fernet


class Crypter:
    """Simply to encrypt and decrypt"""

    def decrypt(self, key, encryptedMessage):
        return key.decrypt(encryptedMessage).decode()

    def encrypt(self, key, message):
        return key.encrypt(message.encode())

    def generateKey(self):
        return Fernet(Fernet.generate_key())
