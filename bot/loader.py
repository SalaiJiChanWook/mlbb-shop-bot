from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import settings

# 1. Bot Instance (Markdown/HTML Default Parse mode သတ်မှတ်ခြင်း)
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)

# 2. Dispatcher Instance (FSM Storage အတွက် MemoryStorage အသုံးပြုခြင်း)
# မှတ်ချက်- အကယ်၍ Production တွင် Server Restart ချသည့်အခါ State မပျောက်စေလိုပါက RedisStorage သို့ အလွယ်တကူ ပြောင်းလဲနိုင်ပါသည်
dp = Dispatcher(storage=MemoryStorage())