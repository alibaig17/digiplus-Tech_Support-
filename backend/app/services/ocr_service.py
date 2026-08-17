"""
🔍 OCR service — extracts text from uploaded screenshots using EasyOCR.

EasyOCR's reader is expensive to initialize (loads a neural net), so we
lazily create a single shared reader instance.
"""
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr

        # English only by default; add more language codes as needed.
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def extract_text(image_path: str) -> str:
    """Run OCR on an image file and return the extracted text (best-effort)."""
    try:
        reader = _get_reader()
        results = reader.readtext(image_path, detail=0, paragraph=True)
        return "\n".join(results)
    except Exception as e:
        print(f"⚠️ OCR failed for {image_path}: {e}")
        return ""
