import time
from typing import Optional
from core.multimodal.limits import MultimodalLimits
from core.channels.base import ChannelMessage, ContentType, PrivacyClassification

class AudioSessionError(Exception):
    pass

class BoundedAudioSession:
    """Manages an audio session ensuring limits are respected."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = time.time()
        self.buffer_size = 0
        self.is_active = True
        
    def add_chunk(self, size_bytes: int):
        if not self.is_active:
            raise AudioSessionError("Session is not active.")
            
        elapsed = time.time() - self.start_time
        if elapsed > MultimodalLimits.MAX_AUDIO_DURATION_SECONDS:
            self.is_active = False
            raise AudioSessionError(f"Maximum audio duration ({MultimodalLimits.MAX_AUDIO_DURATION_SECONDS}s) exceeded.")
            
        if self.buffer_size + size_bytes > MultimodalLimits.MAX_AUDIO_BUFFER_BYTES:
            self.is_active = False
            raise AudioSessionError(f"Maximum audio buffer ({MultimodalLimits.MAX_AUDIO_BUFFER_BYTES} bytes) exceeded.")
            
        self.buffer_size += size_bytes
        
    def close(self):
        self.is_active = False
