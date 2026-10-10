from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: Union[List[int], str]
    OWNER_ID: int
    
    GEMINI_API_KEY: str
    
    KPAY_PHONE: str
    KPAY_NAME: str
    WAVEPAY_PHONE: str
    WAVEPAY_NAME: str
    
    RATE_LIMIT_SECONDS: float = 2.0
    AI_RATE_LIMIT_PER_MINUTE: int = 4
    DATABASE_URL: str = "sqlite+aiosqlite:///storage/database.sqlite3"
    
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("ADMIN_IDS", mode="after")
    def parse_admin_ids(cls, v) -> List[int]:
        if isinstance(v, list):
            return [int(x) for x in v]
        if isinstance(v, str):
            # ကော်မာ ခံထားတာတွေကို ခွဲထုတ်ပြီး int အဖြစ် ပြောင်းပေးခြင်း
            clean_str = v.strip("[]")
            return [int(x.strip()) for x in clean_str.split(",") if x.strip()]
        if isinstance(v, int):
            return [v]
        return []

settings = Settings()