"""
End-to-End Encryption & Pairing Security Engine
Implements AES-GCM 256 encryption (or stdlib HMAC-SHA256 fallback) for P2P payload transfers and secure pairing.
"""

import os
import base64
import hashlib
import hmac

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


class SecurityEngine:
    def __init__(self, secret_key: str):
        self.raw_secret = secret_key
        self.key = hashlib.sha256(secret_key.encode("utf-8")).digest()
        if HAS_CRYPTO:
            self.cipher = AESGCM(self.key)

    def encrypt(self, plain_bytes: bytes) -> str:
        """Encrypts bytes using AES-256-GCM (or HMAC-xor fallback)."""
        if HAS_CRYPTO:
            nonce = os.urandom(12)
            ciphertext = self.cipher.encrypt(nonce, plain_bytes, None)
            payload = nonce + ciphertext
            return base64.b64encode(payload).decode("utf-8")
        else:
            nonce = os.urandom(12)
            key_stream = hashlib.pbkdf2_hmac('sha256', self.key, nonce, 100, dklen=len(plain_bytes))
            ciphertext = bytes([p ^ k for p, k in zip(plain_bytes, key_stream)])
            signature = hmac.new(self.key, nonce + ciphertext, hashlib.sha256).digest()
            payload = nonce + signature + ciphertext
            return base64.b64encode(payload).decode("utf-8")

    def decrypt(self, encoded_payload: str) -> bytes:
        """Decrypts base64 payload."""
        raw_payload = base64.b64decode(encoded_payload.encode("utf-8"))
        if HAS_CRYPTO:
            if len(raw_payload) < 13:
                raise ValueError("Invalid payload length")
            nonce = raw_payload[:12]
            ciphertext = raw_payload[12:]
            return self.cipher.decrypt(nonce, ciphertext, None)
        else:
            if len(raw_payload) < 44:
                raise ValueError("Invalid payload length")
            nonce = raw_payload[:12]
            signature = raw_payload[12:44]
            ciphertext = raw_payload[44:]

            expected_sig = hmac.new(self.key, nonce + ciphertext, hashlib.sha256).digest()
            if not hmac.compare_digest(signature, expected_sig):
                raise ValueError("Authentication signature verification failed")

            key_stream = hashlib.pbkdf2_hmac('sha256', self.key, nonce, 100, dklen=len(ciphertext))
            return bytes([c ^ k for c, k in zip(ciphertext, key_stream)])

    @staticmethod
    def generate_pairing_code() -> str:
        raw = base64.b32encode(os.urandom(5)).decode("utf-8")
        return raw[:6].upper()
