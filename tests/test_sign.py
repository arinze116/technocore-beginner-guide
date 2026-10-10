"""Regression tests for signing-key handling and Ed25519 signatures."""

import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import sign


class SigningKeyTests(unittest.TestCase):
    def test_accepts_exactly_32_bytes_of_hex_seed(self):
        seed = "01" * 32
        key, returned_seed = sign.load_key(seed)
        self.assertEqual(returned_seed, seed)
        self.assertIsInstance(key, Ed25519PrivateKey)

    def test_rejects_passphrase_instead_of_hashing_it(self):
        with self.assertRaisesRegex(SystemExit, "Passphrases are not accepted"):
            sign.load_key("a human-memorable passphrase")

    def test_rejects_64_character_non_hex_seed(self):
        with self.assertRaisesRegex(SystemExit, "64 hexadecimal characters"):
            sign.load_key("z" * 64)

    def test_signature_verifies_for_canonical_message(self):
        seed = "ab" * 32
        key, _ = sign.load_key(seed)
        message = "lobby|12345|hello world"
        encoded = sign.signature(key, message)
        import base64

        raw_signature = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        key.public_key().verify(raw_signature, message.encode("utf-8"))

    def test_did_is_derived_from_seed(self):
        seed = "cd" * 32
        first, _ = sign.load_key(seed)
        second, _ = sign.load_key(seed)
        self.assertEqual(sign.did_of(first), sign.did_of(second))
        self.assertTrue(sign.did_of(first).startswith("did:key:z6Mk"))


if __name__ == "__main__":
    unittest.main()
