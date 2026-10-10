import os
import psutil
from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from config.settings import settings
from database.connection import async_session_maker
from database.models import Order, OrderStatus
from services.excel_service import excel_service

router = Router(name="developer_router")

def is_owner(user_id: int) -> bool:
    return user_id == settings.OWNER_ID

@router.message(F.text == "/owner")
async def owner_panel(message: Message):
    """Owner အတွက် Master Control Dashboard"""
    if not is_owner(message.from_user.id):
        return

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🖥 Server Status", callback_data="own_status"),
            InlineKeyboardButton(text="📦 DB Backup", callback_data="own_backup")
        ],
        [
            InlineKeyboardButton(text="⏳ Pending Orders", callback_data="own_pending"),
            InlineKeyboardButton(text="📊 Export Excel", callback_data="own_excel")
        ]
    ])

    await message.answer(
        "👑 **Owner Master Control Panel**\n\n"
        "စနစ်တစ်ခုလုံးကို စီမံရန် အောက်ပါ ခလုတ်များမှ ရွေးချယ်နိုင်ပါသည်-",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "own_status")
async def callback_status(callback):
    if not is_owner(callback.from_user.id): return
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    await callback.message.answer(
        f"🖥 **Server Diagnostics**\n\n• CPU: `{cpu}%`\n• RAM: `{ram}%`\n• Disk: `{disk}%`",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "own_backup")
async def callback_backup(callback):
    if not is_owner(callback.from_user.id): return
    db_path = "storage/database.sqlite3"
    if os.path.exists(db_path):
        await callback.message.answer_document(FSInputFile(db_path), caption="📦 Database Snapshot")
    await callback.answer()

@router.callback_query(F.data == "own_excel")
async def callback_excel(callback):
    if not is_owner(callback.from_user.id): return
    path = await excel_service.export_daily_sales()
    await callback.message.answer_document(FSInputFile(path), caption="📊 Sales Report Excel")
    await callback.answer()

@router.callback_query(F.data == "own_pending")
async def callback_pending(callback):
    """အတည်ပြုရန် ကျန်နေသော Pending Orders များကို စစ်ဆေးခြင်း"""
    if not is_owner(callback.from_user.id): return
    async with async_session_maker() as session:
        stmt = select(Order).where(Order.status == OrderStatus.WAITING_APPROVAL)
        orders = (await session.execute(stmt)).scalars().all()

        if not orders:
            await callback.message.answer("✅ လက်ရှိတွင် အတည်ပြုရန် ကျန်နေသော Order မရှိပါခင်ဗျာ။")
        else:
            text = f"⏳ **Pending Orders စုစုပေါင်း ({len(orders)}) ခု:**\n\n"
            for o in orders:
                text += f"• Order `#{o.order_uuid}` | MLBB: `{o.mlbb_user_id}` | Pay: `{o.payment_method}`\n"
            await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()