import pickle
from typing import List, Tuple

from nacl.public import SealedBox, PublicKey, PrivateKey

from src.constants import EncryptedData, Data


def generate_keys() -> Tuple[PrivateKey, PublicKey]:
    """
    Generate a new key pair.

    :return: the key pair
    """
    private_key = PrivateKey.generate()
    public_key = private_key.public_key
    return private_key, public_key


def encrypt_data_rows(anonymized_rows: Data, central_pk: PublicKey) -> EncryptedData:
    """
    Encrypt data rows rowwise.

    :param anonymized_rows: the data rows
    :param central_pk: the required public key
    :return: the encrypted data rows
    """
    result: List[bytes] = []
    sealed_box = SealedBox(central_pk)
    for row in anonymized_rows:
        serialized_row = pickle.dumps(row)
        encrypted_row = sealed_box.encrypt(serialized_row)
        result.append(encrypted_row)
    return result


def decrypt_result(encrypted_data_rows: EncryptedData, private_key: PrivateKey) -> Data:
    """
    Decrypt encrypted data rows rowwise.

    :param encrypted_data_rows: the encrypted rows
    :param private_key: the required private key
    :return: the decrypted data rows
    """
    anonymized_result = []
    unseal_box = SealedBox(private_key)
    for row in encrypted_data_rows:
        decrypted_encoded_row = unseal_box.decrypt(row)
        decrypted_row = pickle.loads(decrypted_encoded_row)
        anonymized_result.append(decrypted_row)
    return anonymized_result
