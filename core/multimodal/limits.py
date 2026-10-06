class MultimodalLimits:
    # Audio Limits
    MAX_AUDIO_DURATION_SECONDS = 300  # 5 minutes
    MAX_AUDIO_BUFFER_BYTES = 5 * 1024 * 1024  # 5 MB
    
    # Image/Camera Limits
    MAX_IMAGE_WIDTH = 3840  # 4K
    MAX_IMAGE_HEIGHT = 2160 # 4K
    MAX_IMAGE_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    SUPPORTED_IMAGE_FORMATS = ["image/jpeg", "image/png", "image/webp"]
    
    # Video/Screen Limits
    MAX_VIDEO_FRAMES_PER_SESSION = 600
    MAX_SCREEN_CAPTURE_FPS = 5
    
    # OCR Limits
    MAX_OCR_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
    
    # WebSocket payload limits
    MAX_WEBSOCKET_PAYLOAD = 1 * 1024 * 1024  # 1 MB (already in api.py)
