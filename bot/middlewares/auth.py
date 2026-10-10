import logging
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy import select

from config.settings import settings
from database.connection import async_session_maker
from database.models import User, UserRole

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Event ပေးပို့သူ (User) အချက်အလက် ထုတ်ယူခြင်း
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        telegram_id = user.id

        # 1. Role သတ်မှတ်ခြင်း (Hardcoded Security Check)
        if telegram_id == settings.OWNER_ID:
            current_role = UserRole.DEVELOPER
        elif telegram_id in settings.ADMIN_IDS:
            current_role = UserRole.ADMIN
        else:
            current_role = UserRole.CUSTOMER

        # 2. Database ရှိ User Status (Ban စာရင်း) ကို စစ်ဆေးခြင်း
        async with async_session_maker() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            db_user = (await session.execute(stmt)).scalar_one_or_none()

            # အကယ်၍ Database ထဲတွင် User ရှိပြီး Ban ခံထားရပါက အားလုံးကို Drop လုပ်ခြင်း
            if db_user and db_user.is_banned:
                logger.warning(f"Blocked banned user attempt: {telegram_id}")
                if isinstance(event, Message):
                    await event.answer("⛔ သင်၏ အကောင့်သည် စနစ်အား အသုံးပြုခွင့် ပိတ်ပင် (Ban) ခံထားရပါသည်။")
                elif isinstance(event, CallbackQuery):
                    await event.answer("⛔ သင်၏ အကောင့်အား ပိတ်ပင်ထားပါသည်!", show_alert=True)
                return

        # 3. Handler များအတွင်း တိုက်ရိုက်ယူသုံးနိုင်ရန် Context Data ထဲသို့ Inject ပြုလုပ်ပေးခြင်း
        data["user_role"] = current_role
        data["is_admin"] = current_role in [UserRole.ADMIN, UserRole.DEVELOPER]
        data["is_owner"] = (current_role == UserRole.DEVELOPER)

        return await handler(event, data)