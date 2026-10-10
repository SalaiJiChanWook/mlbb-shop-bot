from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, FSInputFile
from sqlalchemy import select, func

from config.settings import settings
from database.connection import async_session_maker
from database.models import Order, OrderStatus, User, DiamondPackage
from services.excel_service import excel_service

router = Router(name="admin_router")

# 1. Admin Security Guard ကို ထိပ်ဆုံးတွင် ထားရှိခြင်း
def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS or user_id == settings.OWNER_ID

@router.message(F.text == "/customers")
async def show_top_customers(message: Message):
    """ဝယ်ယူမှု အများဆုံး ဖောက်သည်များ စာရင်း ကြည့်ခြင်း"""
    if not is_admin(message.from_user.id):
        return

    async with async_session_maker() as session:
        stmt = (
            select(
                User.full_name,
                User.username,
                User.phone_number,
                func.count(Order.id).label("total_orders")
            )
            .join(Order, User.id == Order.user_id)
            .where(Order.status == OrderStatus.COMPLETED)
            .group_by(User.id)
            .order_by(func.count(Order.id).desc())
            .limit(10)
        )
        results = (await session.execute(stmt)).all()

        if not results:
            await message.answer("လက်ရှိတွင် အောင်မြင်သော ဝယ်ယူသူမှတ်တမ်း မရှိသေးပါခင်ဗျာ။")
            return

        report = "🏆 **ထိပ်တန်း ဝယ်ယူသူများ စာရင်း (Top 10 Loyal Customers)**\n\n"
        for idx, (name, username, phone, count) in enumerate(results, 1):
            uname = f"@{username}" if username else "No Username"
            phone_str = phone or "No Phone"
            report += (
                f"{idx}️⃣ **{name}** ({uname})\n"
                f"   • Phone: `{phone_str}`\n"
                f"   • ဝယ်ယူမှုအကြိမ်: **{count} ကြိမ်**\n\n"
            )

        report += "💡 *ဤဖောက်သည်များထံသို့ Promotion ကူပွန်များ ပေးပို့နိုင်ပါသည်ခင်ဗျာ။*"
        await message.answer(report, parse_mode="Markdown")

@router.callback_query(F.data.startswith("adm_appr_"))
async def approve_order(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ သင်သည် Admin မဟုတ်ပါ!", show_alert=True)
        return

    order_uuid = callback.data.replace("adm_appr_", "").replace("#", "").strip()

    async with async_session_maker() as session:
        stmt = (
            select(Order, User, DiamondPackage)
            .join(User, Order.user_id == User.id)
            .join(DiamondPackage, Order.package_id == DiamondPackage.id)
            .where(Order.order_uuid == order_uuid)
        )
        res = await session.execute(stmt)
        record = res.first()

        if not record:
            await callback.answer("Order ရှာမတွေ့ပါ!", show_alert=True)
            return

        order, user, package = record
        order.status = OrderStatus.COMPLETED
        await session.commit()

        # Customer ထံ အကြောင်းကြားစာ ပို့ခြင်း
        try:
            await bot.send_message(
                chat_id=user.telegram_id,
                text=(
                    f"🎉 **သင့် Order အောင်မြင်ပါပြီ!**\n\n"
                    f"• Order No: `#{order_uuid}`\n"
                    f"• Package: **{package.name}**\n"
                    f"• MLBB ID: `{order.mlbb_user_id} ({order.mlbb_zone_id})`\n\n"
                    "Diamond များကို ဂိမ်းအကောင့်ထဲသို့ ထည့်သွင်းပေးလိုက်ပါပြီခင်ဗျာ။ ကျေးဇူးတင်ပါသည်။"
                ),
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.message.edit_caption(
        caption=f"{callback.message.caption}\n\n✅ **Approved by Admin: {callback.from_user.first_name}**",
        reply_markup=None
    )
    await callback.answer("Order အောင်မြင်စွာ အတည်ပြုပြီးပါပြီ။")

@router.callback_query(F.data.startswith("adm_rej_"))
async def reject_order(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ သင်သည် Admin မဟုတ်ပါ!", show_alert=True)
        return

    order_uuid = callback.data.replace("adm_rej_", "").replace("#", "").strip()

    async with async_session_maker() as session:
        stmt = select(Order, User).join(User, Order.user_id == User.id).where(Order.order_uuid == order_uuid)
        res = await session.execute(stmt)
        record = res.first()

        if not record:
            await callback.answer("Order ရှာမတွေ့ပါ!", show_alert=True)
            return

        order, user = record
        order.status = OrderStatus.REJECTED
        await session.commit()

        try:
            await bot.send_message(
                chat_id=user.telegram_id,
                text=f"⚠️ **သင့် Order ပယ်ဖျက်ခံရပါသည်**\n\nOrder No: `#{order_uuid}` ငွေလွှဲပြေစာ မမှန်ကန်ပါသဖြင့် ငြင်းပယ်လိုက်ပါသည်။ လိုအပ်ပါက ဆိုင် Admin ထံ တိုက်ရိုက်ဆက်သွယ်ပါ။",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.message.edit_caption(
        caption=f"{callback.message.caption}\n\n❌ **Rejected by Admin: {callback.from_user.first_name}**",
        reply_markup=None
    )
    await callback.answer("Order အား ငြင်းပယ်လိုက်ပါပြီ။")

@router.message(F.text == "/export_today")
async def export_today_sales(message: Message):
    """Admin အနေဖြင့် ယနေ့အရောင်းစာရင်း Excel ဆွဲယူခြင်း"""
    if not is_admin(message.from_user.id):
        return

    wait_msg = await message.answer("📊 Excel စာရင်း ဖန်တီးနေပါသည်၊ ခေတ္တစောင့်ပေးပါ...")

    try:
        file_path = await excel_service.export_daily_sales()
        excel_doc = FSInputFile(file_path)

        await message.answer_document(
            document=excel_doc,
            caption="✅ **ယနေ့အတွက် အရောင်းစာရင်း Excel File**\nLaptop ၏ `storage/daily_reports/` ထဲတွင်လည်း အလိုအလျောက် သိမ်းဆည်းပြီးပါပြီ။",
            parse_mode="Markdown"
        )
    except Exception as e:
        await message.answer(f"⚠️ Excel ဖန်တီးရာတွင် အမှားဖြစ်ပွားပါသည်: {e}")
    finally:
        await wait_msg.delete()