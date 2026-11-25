import base64
import getpass
import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC = b"SSENC1"
SALT_SIZE = 16
ITERATIONS = 600_000
MIN_PASSWORD_LENGTH = 8


def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def encrypt_file(input_path, password):
    input_path = Path(input_path)
    output_path = input_path.with_name(input_path.name + ".enc")
    if output_path.exists():
        raise FileExistsError(f"{output_path} already exists. Delete or rename it first.")

    data = input_path.read_bytes()
    salt = os.urandom(SALT_SIZE)
    token = Fernet(derive_key(password, salt)).encrypt(data)
    output_path.write_bytes(MAGIC + salt + token)
    return output_path


def decrypt_file(input_path, password):
    input_path = Path(input_path)
    blob = input_path.read_bytes()
    header_size = len(MAGIC) + SALT_SIZE
    if not blob.startswith(MAGIC) or len(blob) <= header_size:
        raise ValueError("This file was not encrypted by this program.")

    salt = blob[len(MAGIC):header_size]
    token = blob[header_size:]
    data = Fernet(derive_key(password, salt)).decrypt(token)

    if input_path.suffix == ".enc":
        original = input_path.with_suffix("")
        output_path = original.with_name(original.stem + ".decrypted" + original.suffix)
    else:
        output_path = input_path.with_name(input_path.name + ".decrypted")
    if output_path.exists():
        raise FileExistsError(f"{output_path} already exists. Delete or rename it first.")

    output_path.write_bytes(data)
    return output_path


def ask_new_password():
    password = getpass.getpass("Choose a password (typing is hidden): ")
    if len(password) < MIN_PASSWORD_LENGTH:
        print(f"Error: The password must be at least {MIN_PASSWORD_LENGTH} characters.")
        return None
    if password != getpass.getpass("Type the password again: "):
        print("Error: The two passwords do not match.")
        return None
    return password


def main():
    print("=== File Encryption and Decryption ===")
    print("1. Encrypt a file")
    print("2. Decrypt a file")
    choice = input("Choose 1 or 2: ").strip()
    if choice not in ("1", "2"):
        print("Error: Please choose 1 or 2.")
        return

    file_path = input("Enter the path of the file: ").strip().strip('"')
    if not file_path:
        print("Error: Please enter a file path.")
        return

    try:
        if choice == "1":
            password = ask_new_password()
            if password is None:
                return
            result = encrypt_file(file_path, password)
            print(f"Encrypted. Saved as: {result}")
        else:
            password = getpass.getpass("Enter the password (typing is hidden): ")
            result = decrypt_file(file_path, password)
            print(f"Decrypted. Saved as: {result}")
    except FileNotFoundError:
        print("Error: File not found. Check the file name and path.")
    except FileExistsError as error:
        print(f"Error: {error}")
    except InvalidToken:
        print("Error: Wrong password, or the file has been changed.")
    except ValueError as error:
        print(f"Error: {error}")
    except OSError:
        print("Error: This file cannot be read. Is it a folder, or do you lack permission?")


if __name__ == "__main__":
    main()