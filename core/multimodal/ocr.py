class OCRAdapter:
    """Bounded OCR Adapter."""
    
    @classmethod
    def process_image(cls, image_bytes: bytes) -> str:
        # Mock OCR integration - standard library only per instructions
        # Any real OCR would require pytesseract, easyocr, or cloud APIs
        # which would need to be approved dependencies.
        # As per the rules: "Do not add dependencies merely because they are popular."
        # We will stub this to prove the untrusted input architecture.
        return "[Simulated OCR Text]"
