import pathlib
import typing

from pycspr.types.crypto import KeyAlgorithm
from pycspr.types.crypto import PrivateKey
from pycspr.types.crypto import PublicKey
from pycspr.crypto import get_key_pair_from_bytes
from pycspr.crypto import get_key_pair_from_pem_file


def create_private_key(algo: KeyAlgorithm, pvk: bytes, pbk: bytes) -> PrivateKey:
    """Returns an account holder's private key.

    :param algo: ECC key algorithm identifier.
    :param pvk: ECC private key.
    :param pbk: ECC public key.

    """
    if isinstance(algo, str):
        algo = KeyAlgorithm[algo]

    return PrivateKey(pvk, pbk, algo)


def create_public_key(algo: KeyAlgorithm, pbk: bytes) -> PublicKey:
    """Returns an account holder's public key.

    :param algo: ECC key algorithm identifier.
    :param pbk: ECC public key raw bytes.

    """
    return PublicKey(algo, pbk)


def create_public_key_from_account_key(account_key: bytes) -> PublicKey:
    """Returns an account holder's public key.

    :param account_key: Account key asociated with account;s public key.
    :returns: A public key.

    """
    return create_public_key(KeyAlgorithm(account_key[0]), account_key[1:])


def parse_private_key(
    fpath: pathlib.Path,
    algo: typing.Union[str, KeyAlgorithm] = KeyAlgorithm.ED25519
) -> PrivateKey:
    """Returns on-chain account information deserialised from a secret key held on file system.

    :param fpath: Path to secret key pem file associated with the account.
    :param algo: ECC key algorithm identifier.
    :returns: On-chain account information wrapper.

    """
    algo = KeyAlgorithm[algo] if isinstance(algo, str) else algo
    (pvk, pbk) = get_key_pair_from_pem_file(fpath, algo)

    return create_private_key(algo, pvk, pbk)


def parse_private_key_bytes(
    pvk: bytes,
    algo: typing.Union[str, KeyAlgorithm] = KeyAlgorithm.ED25519
) -> PrivateKey:
    """Returns a user's private key deserialised from a secret key.

    :param pvk: A private key.
    :param algo: ECC key algorithm identifier.
    :returns: Private key wrapper.

    """
    algo = KeyAlgorithm[algo] if isinstance(algo, str) else algo
    (pvk, pbk) = get_key_pair_from_bytes(pvk, algo)

    return create_private_key(algo, pvk, pbk)


def parse_public_key(fpath: pathlib.Path) -> PublicKey:
    """Returns an account holder's public key.

    :param fpath: Path to public key hex file associated with the account.
    :returns: An account holder's public key.

    """
    with open(fpath) as fstream:
        account_key = bytes.fromhex(fstream.read())

    return create_public_key_from_account_key(account_key)


def parse_public_key_bytes(
    pbk: bytes,
    algo: typing.Union[str, KeyAlgorithm]
) -> PublicKey:
    """Returns an account holder's public key.

    :param pbk: A public key.
    :param algo: ECC key algorithm identifier.
    :returns: A public key.

    """
    algo = KeyAlgorithm[algo] if isinstance(algo, str) else algo

    return create_public_key(algo, pbk)
