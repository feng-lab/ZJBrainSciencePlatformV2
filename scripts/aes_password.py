"""加密或解密密码
$ pip install pycryptodome
"""

import argparse
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

AUTH_AES_KEY: bytes = b"#030doH2<FIb#b88"
aes_cipher = AES.new(AUTH_AES_KEY, AES.MODE_ECB)


def encrypt_password(data: str) -> str:
    pad_data = pad(data.encode("UTF-8"), AES.block_size, style="pkcs7")
    enc_data = aes_cipher.encrypt(pad_data)
    base64_enc_data = base64.b64encode(enc_data).decode("ASCII")
    return base64_enc_data


def decrypt_password(data: str) -> str:
    enc_data = base64.b64decode(data.encode("ASCII"))
    pad_data = aes_cipher.decrypt(enc_data)
    data = unpad(pad_data, AES.block_size, style="pkcs7").decode("UTF-8")
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["enc", "dec"], help="encrypt or decrypt")
    parser.add_argument("data", help="data to encrypt or decrypt")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    match args.action:
        case "enc":
            print(encrypt_password(args.data))
        case "dec":
            print(decrypt_password(args.data))
        case _:
            print("invalid action")
