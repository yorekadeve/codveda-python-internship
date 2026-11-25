import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import InvalidToken

from file_encryption import decrypt_file, encrypt_file

PASSWORD = "correct horse battery"


class FileEncryptionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.original = self.folder / "notes.txt"
        self.original.write_text("Secret line one\nSecret line two\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_round_trip_restores_the_original_text(self):
        encrypted = encrypt_file(self.original, PASSWORD)
        self.assertEqual(encrypted.name, "notes.txt.enc")
        decrypted = decrypt_file(encrypted, PASSWORD)
        self.assertEqual(decrypted.name, "notes.decrypted.txt")
        self.assertEqual(
            decrypted.read_text(encoding="utf-8"),
            self.original.read_text(encoding="utf-8"),
        )

    def test_encrypted_file_does_not_contain_the_plain_text(self):
        encrypted = encrypt_file(self.original, PASSWORD)
        self.assertNotIn(b"Secret line one", encrypted.read_bytes())

    def test_wrong_password_is_refused(self):
        encrypted = encrypt_file(self.original, PASSWORD)
        with self.assertRaises(InvalidToken):
            decrypt_file(encrypted, "wrong password")

    def test_tampered_file_is_refused(self):
        encrypted = encrypt_file(self.original, PASSWORD)
        data = bytearray(encrypted.read_bytes())
        data[-5] ^= 1
        encrypted.write_bytes(bytes(data))
        with self.assertRaises(InvalidToken):
            decrypt_file(encrypted, PASSWORD)

    def test_same_password_gives_different_encrypted_files(self):
        first = encrypt_file(self.original, PASSWORD).read_bytes()
        (self.folder / "notes.txt.enc").unlink()
        second = encrypt_file(self.original, PASSWORD).read_bytes()
        self.assertNotEqual(first, second)

    def test_plain_file_is_not_accepted_for_decryption(self):
        with self.assertRaises(ValueError):
            decrypt_file(self.original, PASSWORD)

    def test_existing_output_is_never_overwritten(self):
        encrypt_file(self.original, PASSWORD)
        with self.assertRaises(FileExistsError):
            encrypt_file(self.original, PASSWORD)

    def test_missing_file_is_reported(self):
        with self.assertRaises(FileNotFoundError):
            encrypt_file(self.folder / "nope.txt", PASSWORD)


if __name__ == "__main__":
    unittest.main()