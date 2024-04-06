import unittest

import fracas.crypto


class TestCrypto(unittest.TestCase):
    def test_encrypt(self):
        s = "When in the course of human events"
        pw = "my terrible password"
        fracas.crypto.genkey(pw)
        enc = fracas.crypto.encrypt(s)
        dec = fracas.crypto.decrypt(enc, pw)
        self.assertEqual(dec, s)


if __name__ == "__main__":
    unittest.main()
