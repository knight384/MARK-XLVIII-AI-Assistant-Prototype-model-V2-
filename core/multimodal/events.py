class MultimodalEventType:
    AUDIO_STARTED = "AUDIO_STARTED"
    AUDIO_FRAME = "AUDIO_FRAME"
    TRANSCRIPT_PARTIAL = "TRANSCRIPT_PARTIAL"
    TRANSCRIPT_FINAL = "TRANSCRIPT_FINAL"
    IMAGE_RECEIVED = "IMAGE_RECEIVED"
    VIDEO_FRAME = "VIDEO_FRAME"
    SCREEN_FRAME = "SCREEN_FRAME"
    OCR_COMPLETE = "OCR_COMPLETE"
    VISION_ANALYSIS_COMPLETE = "VISION_ANALYSIS_COMPLETE"
    TTS_STARTED = "TTS_STARTED"
    TTS_COMPLETED = "TTS_COMPLETED"
    
class PrivacyControls:
    def __init__(self):
        self.microphone_enabled = False
        self.camera_enabled = False
        self.screen_enabled = False
        self.persist_raw_media = False
