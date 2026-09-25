"""
Tests for Security & Network Protocol Framing
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aether.core.security import SecurityEngine
from aether.network.protocol import AetherFrame, MessageType


def test_security_encryption():
    sec = SecurityEngine("test-secret-key-123")
    plain = b"Aether P2P Encrypted Data Payload"
    encrypted = sec.encrypt(plain)
    decrypted = sec.decrypt(encrypted)

    assert decrypted == plain


def test_frame_serialization():
    frame = AetherFrame(
        message_type=MessageType.TASK_SUBMIT,
        sender_id="client-001",
        payload={"data": [1, 2, 3]}
    )
    serialized = frame.serialize()
    deserialized = AetherFrame.deserialize(serialized)

    assert deserialized.message_type == MessageType.TASK_SUBMIT
    assert deserialized.sender_id == "client-001"
    assert deserialized.payload == {"data": [1, 2, 3]}
