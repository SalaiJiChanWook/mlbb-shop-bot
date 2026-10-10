import json
import logging
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from config.settings import settings

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def verify_slip(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Gemini Vision ကိုသုံးပြီး KBZPay / WavePay Screenshot ပြေစာမှ
        Transaction ID နှင့် Amount တို့ကို ထုတ်ယူစစ်ဆေးပေးခြင်း
        """
        prompt = (
            "Analyze this Myanmar digital payment receipt (KBZPay or WavePay). "
            "Extract the transaction details strictly in JSON format with keys: "
            "'is_valid_slip' (boolean), 'provider' (KBZPay or WavePay or Unknown), "
            "'transaction_id' (string or null), 'amount' (number or null), "
            "'timestamp' (string or null). Return ONLY raw JSON without markdown code fences."
        )
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt
                ]
            )
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(raw_text)
            return data
        except Exception as e:
            logger.error(f"OCR Parsing Error: {e}")
            return {
                "is_valid_slip": False,
                "provider": "Unknown",
                "transaction_id": None,
                "amount": None,
                "error": str(e)
            }

ocr_service = OCRService()