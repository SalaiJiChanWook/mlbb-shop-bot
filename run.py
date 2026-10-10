import asyncio
import logging
import sys
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile
from aiogram.types import MenuButtonCommands

from config.settings import settings
from database.connection import init_db
from bot.loader import bot, dp
from bot.middlewares.auth import AuthMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.handlers import customer, admin, developer
from services.excel_service import excel_service

logger = logging.getLogger(__name__)

async def auto_daily_scheduler(bot: Bot):
    """ညစဉ် ၁၁:၅၉ အချိန်တွင် Excel Auto-export ပြုလုပ်ပေးမည့် Scheduler"""
    while True:
        now = datetime.now()
        # ည ၁၁ နာရီ ၅၉ မိနစ်တွင် အလိုအလျောက် execute လုပ်ခြင်း
        if now.hour == 23 and now.minute == 59:
            try:
                logger.info("Executing Midnight Sales Auto-export...")
                file_path = await excel_service.export_daily_sales(now.date())
                
                # Admin များထံ နေ့စဉ်စာရင်း Auto ပို့ပေးခြင်း
                for admin_id in settings.ADMIN_IDS:
                    try:
                        await bot.send_document(
                            chat_id=admin_id,
                            document=FSInputFile(file_path),
                            caption=f"🌙 **{now.strftime('%Y-%m-%d')} နေ့စဉ် အရောင်းစာရင်း အကျဉ်းချုပ်**"
                        )
                    except Exception:
                        pass
                # မိနစ်ထပ်မံ မထပ်စေရန် စက္ကန့် ၆၀ ခေတ္တအနားယူခြင်း
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Scheduler Error: {e}")
        
        await asyncio.sleep(30)  # စက္ကန့် ၃၀ လျှင် တစ်ကြိမ် စစ်ဆေးခြင်း

async def main():
    logger.info("Initializing SQLite Database...")
    await init_db()

    dp.message.middleware(ThrottlingMiddleware())
    dp.message.outer_middleware(AuthMiddleware())
    dp.callback_query.outer_middleware(AuthMiddleware())

    dp.include_router(developer.router)
    dp.include_router(admin.router)
    dp.include_router(customer.router)

    # Background Scheduler Task ကို Event Loop ထဲ တင်ပေးခြင်း
    asyncio.create_task(auto_daily_scheduler(bot))

    logger.info("Starting Telegram Bot (Polling Mode on Local Laptop)...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot Stopped Gracefully.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("storage/bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Initializing SQLite Database...")
    await init_db()

    # Middleware များ အဆင့်ဆင့် တပ်ဆင်ခြင်း
    # ၁။ Anti-Spam / Rate-Limiter စစ်ဆေးခြင်း
    dp.message.middleware(ThrottlingMiddleware())
    
    # ၂။ Security / Role-Based Access Control စစ်ဆေးခြင်း
    dp.message.outer_middleware(AuthMiddleware())
    dp.callback_query.outer_middleware(AuthMiddleware())

    # Routers ချိတ်ဆက်ခြင်း
    dp.include_router(developer.router)
    dp.include_router(admin.router)
    dp.include_router(customer.router)

    logger.info("Starting Telegram Bot (Polling Mode on Local Laptop)...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot Stopped Gracefully.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("storage/bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Initializing SQLite Database...")
    await init_db()

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware Registration
    dp.message.middleware(ThrottlingMiddleware())

    # Router Registration
    dp.include_router(developer.router)
    dp.include_router(admin.router)
    dp.include_router(customer.router)

    logger.info("Starting Telegram Bot (Polling Mode on Local Laptop)...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    # 1. /buy command ကို Telegram စနစ်ထဲ မှတ်ပုံတင်ခြင်း
    await bot.set_my_commands([
        BotCommand(command="buy", description="💎 စိန်ဝယ်ယူမည်"),
        BotCommand(command="start", description="🔄 စတင်အသုံးပြုမည်")
    ])

    # 2. အောက်ခြေ ဘယ်ဘက်ထောင့်တွင် Floating Menu Button အမြဲပေါ်နေစေခြင်း
    await bot.set_chat_menu_button(
        menu_button=MenuButtonCommands()
    )

    logger.info("Starting Telegram Bot (Polling Mode on Local Laptop)...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot Stopped Gracefully.")