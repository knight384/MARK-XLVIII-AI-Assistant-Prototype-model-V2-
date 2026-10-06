from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable, Optional, List, Dict
from enum import Enum
from dataclasses import dataclass, field
import time
import uuid

class ChannelType(Enum):
    TEXT = "text"
    VOICE = "voice"
    WEBSOCKET = "websocket"
    TERMINAL = "terminal"
    MULTIMODAL = "multimodal"

class ContentType(Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO_FRAME = "video_frame"
    SCREEN_FRAME = "screen_frame"
    OCR_TEXT = "ocr_text"
    EVENT = "event"

class PrivacyClassification(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    SENSITIVE = "sensitive"

@dataclass
class MultimodalContext:
    text: List[str] = field(default_factory=list)
    images: List[bytes] = field(default_factory=list) # Raw or ref
    audio_transcripts: List[str] = field(default_factory=list)
    screen_context: List[Any] = field(default_factory=list)
    timestamps: List[float] = field(default_factory=list)
    source: str = "unknown"
    confidence: float = 1.0
    privacy_classification: PrivacyClassification = PrivacyClassification.PRIVATE

@dataclass
class ChannelMessage:
    content: Any # string for text, bytes/reference for binary
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # New Multimodal fields
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    channel_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    content_type: ContentType = ContentType.TEXT
    correlation_id: Optional[str] = None
    sequence_number: Optional[int] = None
    privacy: PrivacyClassification = PrivacyClassification.PRIVATE
    
    # Helper to enforce bounds
    def validate_bounds(self, max_size_bytes: int):
        if isinstance(self.content, bytes) and len(self.content) > max_size_bytes:
            raise ValueError(f"Message payload exceeds max size {max_size_bytes}")

class ChannelEvent:
    def __init__(self, event_type: str, data: Any):
        self.event_type = event_type
        self.data = data

class Channel(ABC):
    def __init__(self, channel_id: str, channel_type: ChannelType):
        self.channel_id = channel_id
        self.channel_type = channel_type
        self._on_message_callback: Optional[Callable[[ChannelMessage], Awaitable[None]]] = None

    def set_on_message(self, callback: Callable[[ChannelMessage], Awaitable[None]]):
        self._on_message_callback = callback

    async def _emit_message(self, msg: ChannelMessage):
        if self._on_message_callback:
            msg.channel_id = self.channel_id
            await self._on_message_callback(msg)

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    @abstractmethod
    async def send_text(self, text: str):
        pass

    @abstractmethod
    async def send_audio(self, audio_data: bytes):
        pass
        
    @abstractmethod
    async def send_event(self, event: ChannelEvent):
        pass
