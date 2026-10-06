import pytest
import asyncio
import time
from core.channels.base import ChannelMessage, ContentType, PrivacyClassification, MultimodalContext
from core.multimodal.limits import MultimodalLimits
from core.multimodal.audio import BoundedAudioSession, AudioSessionError
from core.multimodal.image import ImageAdapter, ImageValidationError
from core.multimodal.ocr import OCRAdapter

def test_multimodal_message_bounds():
    # Construct a valid message
    msg = ChannelMessage(
        content=b'x' * 1024,
        source="camera1",
        content_type=ContentType.IMAGE
    )
    # Validate against limits
    msg.validate_bounds(MultimodalLimits.MAX_IMAGE_FILE_SIZE)
    
    # Exceed limits
    msg.content = b'x' * (MultimodalLimits.MAX_IMAGE_FILE_SIZE + 1)
    with pytest.raises(ValueError):
        msg.validate_bounds(MultimodalLimits.MAX_IMAGE_FILE_SIZE)

def test_audio_session_bounds():
    session = BoundedAudioSession("test_session")
    session.add_chunk(1024 * 1024)
    assert session.buffer_size == 1024 * 1024
    
    with pytest.raises(AudioSessionError):
        session.add_chunk(MultimodalLimits.MAX_AUDIO_BUFFER_BYTES)
        
    assert not session.is_active

def test_audio_session_timeout():
    session = BoundedAudioSession("test_session_2")
    session.start_time = time.time() - (MultimodalLimits.MAX_AUDIO_DURATION_SECONDS + 1)
    with pytest.raises(AudioSessionError):
        session.add_chunk(1024)
        
def test_image_adapter_bounds():
    ImageAdapter.validate_image_metadata(
        size_bytes=1024, mime_type="image/jpeg", width=1920, height=1080
    )
    
    with pytest.raises(ImageValidationError):
        ImageAdapter.validate_image_metadata(
            size_bytes=1024, mime_type="image/gif", width=1920, height=1080
        )
        
    with pytest.raises(ImageValidationError):
        ImageAdapter.validate_image_metadata(
            size_bytes=1024, mime_type="image/jpeg", width=4000, height=4000
        )

def test_ocr_untrusted_input():
    text = OCRAdapter.process_image(b'fake_image_data')
    assert "Simulated" in text
