import os
import sys
import yaml

from pathlib import Path

from cryptography.hazmat.primitives.serialization import load_pem_private_key, Encoding # noqa
from cryptography.hazmat.primitives.serialization import BestAvailableEncryption  # noqa
from cryptography.hazmat.primitives.serialization import PrivateFormat, NoEncryption  # noqa
from cryptography.hazmat.primitives import hashes


def get_config_file(cfgfile):
    try:
        with open(cfgfile, "r") as fconf:
            try:
                conf_var = yaml.safe_load(fconf)
            except yaml.scanner.ScannerError:
                print('Keyvault config file error: Scanner Error')
                sys.exit(-1)
    except (OSError, IOError) as e:
        print('Keyvault config file error: '+e.strerror)
        sys.exit(-1)

    return conf_var


def create_key_hash(name):
    k_hash = hashes.Hash(hashes.SHA256())
    k_hash.update(name.encode())
    key = k_hash.finalize()
    return key.hex()


def select_keyfile(keyfile):
    (_, i_file) = os.path.split(keyfile)
    cryptkeyfile = kv_conf_book['keyfolder']+'/'+i_file  # type: ignore
    p = Path(cryptkeyfile)
    if p.exists() and p.is_file():
        return (True)
    return (False)


def store_keyfile(keyfile, newkeyfile=None):

    (_, i_file) = os.path.split(keyfile)

    if newkeyfile is None:
        cryptkeyfile = kv_conf_book['keyfolder']+'/'+i_file  # type: ignore
        pwd = create_key_hash(i_file)
    else:
        cryptkeyfile = kv_conf_book['keyfolder']+'/'+newkeyfile  # type: ignore
        pwd = create_key_hash(newkeyfile)

    try:
        with open(keyfile, 'r') as f:
            key = f.read().encode('utf-8')
        p_key0 = load_pem_private_key(key, password=None)
    except ValueError:
        return (False)

    p_key1 = p_key0.private_bytes(Encoding.PEM,
                                  PrivateFormat.PKCS8,
                                  BestAvailableEncryption(pwd.encode()))

    with open(cryptkeyfile, 'w') as f:
        f.write(p_key1.decode())

    return (True)


def recover_keyfile(keyfile):

    if select_keyfile(keyfile):
        (_, i_file) = os.path.split(keyfile)
        pwd = create_key_hash(i_file)
        cryptkeyfile = kv_conf_book['keyfolder']+'/'+i_file  # type: ignore

        try:
            with open(cryptkeyfile, 'r') as f:
                key = f.read().encode('utf-8')
            p_key0 = load_pem_private_key(key, password=pwd.encode())
        except ValueError:
            return (None)

        return (p_key0.private_bytes(Encoding.PEM,
                                     PrivateFormat.TraditionalOpenSSL,
                                     NoEncryption()))
    return (None)


def stream_keyfile(keyfile, pwd):

    if select_keyfile(keyfile):
        (_, i_file) = os.path.split(keyfile)
        pwd = create_key_hash(i_file)
        cryptkeyfile = kv_conf_book['keyfolder']+'/'+i_file  # type: ignore

        try:
            with open(cryptkeyfile, 'r') as f:
                key = f.read().encode('utf-8')
            p_key0 = load_pem_private_key(key, password=pwd.encode())
        except ValueError:
            return (None)

        return (p_key0.private_bytes(Encoding.PEM,
                                     PrivateFormat.PKCS8,
                                     BestAvailableEncryption(pwd.encode())))

    return (None)


kv_conf_book = get_config_file('server-config.yml')

if __name__ == "__main__":
    kv_conf_book = get_config_file('server-config.yml')
