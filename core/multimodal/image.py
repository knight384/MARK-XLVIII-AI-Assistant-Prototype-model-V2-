from core.multimodal.limits import MultimodalLimits

class ImageValidationError(Exception):
    pass

class ImageAdapter:
    """Bounded image processing adapter."""
    
    @classmethod
    def validate_image_metadata(cls, size_bytes: int, mime_type: str, width: int = 0, height: int = 0):
        if size_bytes > MultimodalLimits.MAX_IMAGE_FILE_SIZE:
            raise ImageValidationError(f"Image size {size_bytes} exceeds limit {MultimodalLimits.MAX_IMAGE_FILE_SIZE}")
            
        if mime_type not in MultimodalLimits.SUPPORTED_IMAGE_FORMATS:
            raise ImageValidationError(f"Unsupported image format: {mime_type}")
            
        if width > MultimodalLimits.MAX_IMAGE_WIDTH or height > MultimodalLimits.MAX_IMAGE_HEIGHT:
            raise ImageValidationError(f"Image dimensions {width}x{height} exceed maximum {MultimodalLimits.MAX_IMAGE_WIDTH}x{MultimodalLimits.MAX_IMAGE_HEIGHT}")
            
        return True
