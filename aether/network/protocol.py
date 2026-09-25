"""
Frame Protocol & Message Schema for Aether P2P Streaming
"""

import json
from enum import Enum
from typing import Dict, Any, Optional


class MessageType(str, Enum):
    HANDSHAKE_INIT = "HANDSHAKE_INIT"
    HANDSHAKE_ACK = "HANDSHAKE_ACK"
    TELEMETRY_SYNC = "TELEMETRY_SYNC"
    TASK_SUBMIT = "TASK_SUBMIT"
    TASK_STREAM_CHUNK = "TASK_STREAM_CHUNK"
    TASK_COMPLETE = "TASK_COMPLETE"
    ERROR = "ERROR"
    PING = "PING"
    PONG = "PONG"


class AetherFrame:
    def __init__(
        self,
        message_type: MessageType,
        sender_id: str,
        recipient_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        encrypted: bool = False,
        encrypted_payload: Optional[str] = None
    ):
        self.message_type = message_type
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.payload = payload or {}
        self.encrypted = encrypted
        self.encrypted_payload = encrypted_payload

    def serialize(self) -> str:
        return json.dumps({
            "message_type": self.message_type.value if isinstance(self.message_type, Enum) else self.message_type,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "payload": self.payload,
            "encrypted": self.encrypted,
            "encrypted_payload": self.encrypted_payload
        })

    @classmethod
    def deserialize(cls, json_str: str) -> "AetherFrame":
        data = json.loads(json_str)
        return cls(
            message_type=MessageType(data["message_type"]),
            sender_id=data["sender_id"],
            recipient_id=data.get("recipient_id"),
            payload=data.get("payload", {}),
            encrypted=data.get("encrypted", False),
            encrypted_payload=data.get("encrypted_payload")
        )
