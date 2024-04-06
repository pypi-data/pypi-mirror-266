'''
Module for easy encryption and decryption of secrets. Allows us to
securely use credentials within code.
'''

from cryptography.fernet import Fernet


def _load_secret_key(path: str) -> str:
    '''
    Helper function to load a secret key from the given path
    '''

    with open(path, 'rb') as file_object:
        for line in file_object:
            secret_key = line
    return secret_key


def get_secret(path: str) -> str:
    '''
    Returns the encrypted secret from the given path using the key
    located in ./keys/
    '''

    f = Fernet(_load_secret_key('./keys/data_collection.bin'))
    with open(path, 'rb') as file_object:
        for line in file_object:
            encrypted_password = line
    return bytes.decode(f.decrypt(encrypted_password))


def write_encrypted_secret(path: str, secret: str):
    '''
    Writes the given secret to the given path using the key
    located in ./keys/
    '''
    
    f = Fernet(_load_secret_key('./keys/data_collection.bin'))
    with open(path, 'wb') as file_object:
        file_object.write(f.encrypt(secret.encode('ascii')))
