import os
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

# Constants and environment setup
HOME = Path.home()
APPS_DIR = os.getenv("APPS_DIR")
APPLICATION_SUPPORT_DIR = Path("~/Library/Application Support").expanduser()
CRYPTEX_DIR = Path(".").parent.parent
CRYPTEX_DATA_DIR = APPLICATION_SUPPORT_DIR / "Cryptex"
CRYPTEX_ARCHIVE_DIR = CRYPTEX_DATA_DIR / "En"
CRYPTEX_ORIGINS_DIR = CRYPTEX_DATA_DIR / "De"


# Ensure necessary directories exist

if not Path(CRYPTEX_DATA_DIR).exists():
    print("Could not locate `Cryptex` data directory.")
    print("Creating it now...")
    cryptex_data_directory = APPLICATION_SUPPORT_DIR / "cryptex"
    archive_directory = cryptex_data_directory / "archive"
    origins_directory = cryptex_data_directory / "origins"
    Path.mkdir(cryptex_data_directory, parents=True, exist_ok=True)
    Path.mkdir(archive_directory)
    Path.mkdir(origins_directory)


# Function to generate a key from the passphrase
def generate_key_from_passphrase(passphrase, salt=b"salt_"):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
    return key


# Function to encrypt or decrypt data
def process_file(input_file_path, output_file_path, passphrase, is_encryption):
    key = generate_key_from_passphrase(passphrase)
    fernet = Fernet(key)

    with open(input_file_path, "rb") as file:
        data = file.read()

    if is_encryption:
        processed_data = fernet.encrypt(data)
    else:
        try:
            processed_data = fernet.decrypt(data)
        except:
            print("Decryption failed. Please double-check your key and try again.")
            return

    output_directory = os.path.dirname(output_file_path)
    if not Path(output_directory).exists():
        os.makedirs(output_directory, exist_ok=True)

    with open(output_file_path, "wb") as file:
        file.write(processed_data)

    if is_encryption:
        print("Encryption complete. File saved to:", output_file_path)
    else:
        print("Decryption complete. File saved to:", output_file_path)


def en(input_file_path, passphrase):
    base_name = os.path.basename(input_file_path)
    encrypted_file_name = (
        base_name.replace(".txt", ".crypt")
        if ".txt" in base_name
        else base_name + ".crypt"
    )
    output_directory = CRYPTEX_ARCHIVE_DIR
    output_file_path = os.path.join(output_directory, encrypted_file_name)
    process_file(input_file_path, output_file_path, passphrase, is_encryption=True)


def de(input_file_path, passphrase):
    base_name = os.path.basename(input_file_path)
    decrypted_file_name = (
        base_name.replace(".crypt", ".txt")
        if ".crypt" in base_name
        else base_name + ".txt"
    )
    output_directory = CRYPTEX_ORIGINS_DIR
    output_file_path = os.path.join(output_directory, decrypted_file_name)
    process_file(input_file_path, output_file_path, passphrase, is_encryption=False)
