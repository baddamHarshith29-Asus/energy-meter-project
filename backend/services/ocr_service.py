import easyocr
import re
import os

class OCRService:
    def __init__(self):
        # We initialize the reader only when needed to avoid blocking server startup
        self.reader = None

    def scan_bill(self, image_path):
        """
        Scans an image of an energy bill and extracts key metrics.
        Returns a dictionary with extracted data.
        """
        try:
            if not self.reader:
                print("Initializing OCR model (this may take a moment on first run)...")
                self.reader = easyocr.Reader(['en'], gpu=False)

            results = self.reader.readtext(image_path)
            full_text = " ".join([res[1] for res in results]).lower()
            
            # Simple heuristic extraction
            units = self._extract_value(full_text, r'(\d+\.?\d*)\s*(?:kwh|units|consumption)')
            cost = self._extract_value(full_text, r'(?:\$|usd|total|amount)\s*(\d+\.?\d*)')
            
            # If cost not found with prefix, try common patterns
            if not cost:
                cost = self._extract_value(full_text, r'amount\s*due\s*[^\d]*(\d+\.?\d*)')

            return {
                "units": units,
                "cost": cost,
                "confidence": "low" if not (units or cost) else "high",
                "extracted_text_preview": str(full_text)[:200]
            }
        except Exception as e:
            print(f"OCR Error: {e}")
            return {"error": str(e)}

    def _extract_value(self, text, pattern):
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except:
                pass
        return None
