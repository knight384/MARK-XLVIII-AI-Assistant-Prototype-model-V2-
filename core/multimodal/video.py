from core.multimodal.limits import MultimodalLimits

class ScreenCaptureError(Exception):
    pass

class ScreenAdapter:
    """Bounded screen capture adapter with privacy controls."""
    
    @classmethod
    def capture_frame(cls, monitor_id: int, is_enabled: bool) -> bytes:
        if not is_enabled:
            raise ScreenCaptureError("Screen capture is disabled by privacy policy.")
            
        # Simulate capture - no actual GUI bindings required since environment is headless
        # Just return dummy data to fulfill architectural boundaries
        return b"simulated_screen_frame_data"

class VideoAdapter:
    """Bounded video extraction adapter."""
    
    @classmethod
    def extract_frames(cls, video_bytes: bytes, max_frames: int = MultimodalLimits.MAX_VIDEO_FRAMES_PER_SESSION):
        # Enforce limits
        if len(video_bytes) > MultimodalLimits.MAX_IMAGE_FILE_SIZE * 5: # e.g. 50MB max video
            raise ValueError("Video payload too large")
            
        # Simulate extraction returning up to max_frames
        return [b"frame_data"] * min(3, max_frames)
