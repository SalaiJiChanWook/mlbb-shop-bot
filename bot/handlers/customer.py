import os
import re
import uuid
from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery, 
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    BufferedInputFile
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from config.settings import settings
from database.connection import async_session_maker
from database.models import User, Order, DiamondPackage, OrderStatus
from services.qr_service import payment_qr_service

router = Router(name="customer_router")

class OrderStates(StatesGroup):
    register_phone = State()
    choosing_package = State()
    entering_mlbb_id = State()
    choosing_payment = State()
    awaiting_slip = State()

def get_main_menu_keyboard():
    """အောက်ခြေတွင် အမြဲတမ်း ပေါ်နေမည့် Main Menu ခလုတ်များ"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💎 စိန်ဝယ်ယူမည် (/buy)")],
            [KeyboardButton(text="📞 Admin သို့ ဆက်သွယ်ရန်")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )

def get_packages_markup():
    # ID များကို 1 မှ 24 အထိ သီးသန့်စီ သတ်မှတ်ထားပါသည်
    packages = [
        {"id": 1, "name": "Weekly Diamond Pass", "price": "7,000 Ks", "amount": 210},
        {"id": 2, "name": "14 Diamonds", "price": "1,200 Ks", "amount": 14},
        {"id": 3, "name": "28 Diamonds", "price": "2,400 Ks", "amount": 28},
        {"id": 4, "name": "86 Diamonds", "price": "5,800 Ks", "amount": 86},
        {"id": 5, "name": "172 Diamonds", "price": "11,800 Ks", "amount": 172},
        {"id": 6, "name": "257 Diamonds", "price": "17,000 Ks", "amount": 257},
        {"id": 7, "name": "343 Diamonds", "price": "22,300 Ks", "amount": 343},
        {"id": 8, "name": "429 Diamonds", "price": "27,600 Ks", "amount": 429},
        {"id": 9, "name": "514 Diamonds", "price": "32,600 Ks", "amount": 514},
        {"id": 10, "name": "600 Diamonds", "price": "38,200 Ks", "amount": 600},
        {"id": 11, "name": "706 Diamonds", "price": "43,600 Ks", "amount": 706},
        {"id": 12, "name": "878 Diamonds", "price": "54,000 Ks", "amount": 878},
        {"id": 13, "name": "1049 Diamonds", "price": "64,500 Ks", "amount": 1049},
        {"id": 14, "name": "1135 Diamonds", "price": "70,000 Ks", "amount": 1135},
        {"id": 15, "name": "1412 Diamonds", "price": "86,000 Ks", "amount": 1412},
        {"id": 16, "name": "2195 Diamonds", "price": "129,000 Ks", "amount": 2195},
        {"id": 17, "name": "3688 Diamonds", "price": "234,500 Ks", "amount": 3688},
        {"id": 18, "name": "5100 Diamonds", "price": "305,000 Ks", "amount": 5100},
        {"id": 19, "name": "5532 Diamonds", "price": "334,000 Ks", "amount": 5532},
        {"id": 20, "name": "9288 Diamonds", "price": "548,000 Ks", "amount": 9288},
        {"id": 21, "name": "50+50 Diamonds", "price": "3,700 Ks", "amount": 100},
        {"id": 22, "name": "150+150 Diamonds", "price": "10,800 Ks", "amount": 300},
        {"id": 23, "name": "250+250 Diamonds", "price": "17,600 Ks", "amount": 500},
        {"id": 24, "name": "500+500 Diamonds", "price": "35,900 Ks", "amount": 1000},
    ]
    keyboard = []
    # ခလုတ် ၂ ခုစီ ဘေးချင်းကပ် ပြသခြင်း (UI သပ်ရပ်စေရန်)
    row = []
    for pkg in packages:
        btn = InlineKeyboardButton(text=f"{pkg['name']} - {pkg['price']}", callback_data=f"buy_pkg_{pkg['id']}_{pkg['price']}")
        row.append(btn)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    async with async_session_maker() as session:
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        user = (await session.execute(stmt)).scalar_one_or_none()
        
        if not user or not user.phone_number:
            contact_btn = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="📱 ဖုန်းနံပါတ် ပေးပို့မည် (Share Contact)", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            await message.answer(
                f"မင်္ဂလာပါ {message.from_user.first_name} ခင်ဗျာ။\n\n"
                "MLBB Diamond Shop မှ ကြိုဆိုပါသည်။ ပုံမှန်ဝယ်ယူသူများအတွက် Promotion များနှင့် အော်ဒါမှတ်တမ်းများ မှတ်သားထားနိုင်ရန် "
                "အောက်ပါခလုတ်ကို နှိပ်ပြီး **ဖုန်းနံပါတ် အတည်ပြုပေးပါခင်ဗျာ**။",
                reply_markup=contact_btn
            )
            await state.set_state(OrderStates.register_phone)
            return

    await message.answer(
        f"မင်္ဂလာပါ {message.from_user.first_name} ခင်ဗျာ။\n"
        "စိန်ဝယ်ယူလိုပါက အောက်ပါခလုတ်ကို နှိပ်ပါခင်ဗျာ။",
        reply_markup=get_main_menu_keyboard()
    )

@router.message(OrderStates.register_phone, F.contact)
async def handle_contact_register(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"

    async with async_session_maker() as session:
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        user = (await session.execute(stmt)).scalar_one_or_none()
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name or "Customer",
                phone_number=phone
            )
            session.add(user)
        else:
            user.phone_number = phone
            user.username = message.from_user.username
        await session.commit()

    await state.clear()
    await message.answer(
        f"✅ ဖုန်းနံပါတ် ({phone}) အား မှတ်ပုံတင်ပြီးပါပြီခင်ဗျာ!\n\n"
        "ယခု စိန်စတင်ဝယ်ယူရန် အောက်ပါခလုတ်ကို နှိပ်နိုင်ပါပြီ။",
        reply_markup=get_main_menu_keyboard()
    )

@router.message(F.text.in_(["/buy", "💎 စိန်ဝယ်ယူမည် (/buy)"]))
async def start_buy(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("ဝယ်ယူလိုသော Package ကို ရွေးချယ်ပါ-", reply_markup=get_packages_markup())
    await state.set_state(OrderStates.choosing_package)

@router.message(F.text == "📞 Admin သို့ ဆက်သွယ်ရန်")
async def contact_admin(message: Message):
    await message.answer(
        "အကူအညီ လိုအပ်ပါက သို့မဟုတ် မရှင်းလင်းသည်များ ရှိပါက ဆိုင် Admin(@Israel123466) ထံ တိုက်ရိုက် ဆက်သွယ် မေးမြန်းနိုင်ပါသည်ခင်ဗျာ။"
    )

@router.callback_query(OrderStates.choosing_package, F.data.startswith("buy_pkg_"))
async def pkg_chosen(callback: CallbackQuery, state: FSMContext):
    _, _, pkg_id, price = callback.data.split("_")
    await state.update_data(package_id=int(pkg_id), price=price)
    
    await callback.message.edit_text(
        "ကျေးဇူးပြု၍ သင်၏ **MLBB User ID** နှင့် **Zone ID** ကို ရိုက်ပို့ပေးပါခင်ဗျာ။\n\n"
        "👉 ပုံစံ: `12345678 (1234)` သို့မဟုတ် `12345678 1234`",
        parse_mode="Markdown"
    )
    await state.set_state(OrderStates.entering_mlbb_id)
    await callback.answer()

@router.message(OrderStates.entering_mlbb_id, F.text)
async def process_mlbb_id(message: Message, state: FSMContext):
    match = re.search(r"^(\d{6,12})[\s\(\[\{]+(\d{3,6})[\)\]\}]?$", message.text.strip())
    if not match:
        await message.answer("⚠️ Game ID ပုံစံ မမှန်ကန်ပါ။ ဥပမာ - `12345678 (1234)` အတိုင်း ပြန်လည်ရိုက်ထည့်ပေးပါ။")
        return
        
    user_id, zone_id = match.groups()
    await state.update_data(mlbb_user_id=user_id, mlbb_zone_id=zone_id)
    data = await state.get_data()

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="KBZPay", callback_data="pay_KPay"),
            InlineKeyboardButton(text="WavePay", callback_data="pay_WavePay")
        ],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_order")]
    ])

    await message.answer(
        f"📝 **အချက်အလက် စစ်ဆေးပါ**\n\n"
        f"• MLBB ID: `{user_id}`\n"
        f"• Zone ID: `({zone_id})`\n"
        f"• ကျသင့်ငွေ: `{data.get('price')}`\n\n"
        "ငွေပေးချေမည့် နည်းလမ်းကို ရွေးချယ်ပေးပါ-",
        parse_mode="Markdown",
        reply_markup=markup
    )
    await state.set_state(OrderStates.choosing_payment)

@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("❌ Order အား ပယ်ဖျက်လိုက်ပါပြီခင်ဗျာ။", reply_markup=get_main_menu_keyboard())
    await callback.answer()

@router.callback_query(OrderStates.choosing_payment, F.data.startswith("pay_"))
async def payment_step(callback: CallbackQuery, state: FSMContext):
    method = "KBZPay" if "KPay" in callback.data else "WavePay"
    phone = settings.KPAY_PHONE if method == "KBZPay" else settings.WAVEPAY_PHONE
    name = settings.KPAY_NAME if method == "KBZPay" else settings.WAVEPAY_NAME
    
    order_uuid = str(uuid.uuid4())[:8].upper()
    data = await state.get_data()
    amount_text = data.get("price", "N/A")

    await state.update_data(payment_method=method, order_uuid=order_uuid)

    qr_bytes = payment_qr_service.generate_payment_qr(
        method=method,
        order_uuid=order_uuid,
        amount_text=amount_text,
        phone=phone,
        acc_name=name
    )
    photo_file = BufferedInputFile(qr_bytes, filename=f"pay_{order_uuid}.png")

    caption = (
        f"💳 **{method} ဖြင့် ငွေပေးချေရန် QR Code**\n\n"
        f"• အကောင့်နံပါတ်: `{phone}`\n"
        f"• အမည်: **{name}**\n"
        f"• ကျသင့်ငွေ: **{amount_text}**\n"
        f"• Order No (Note): `#{order_uuid}`\n\n"
        "💡 **ငွေလွှဲရန် ညွှန်ကြားချက်:**\n"
        "၁။ အထက်ပါ QR Code အား Scan ဖတ်၍ သို့မဟုတ် ဖုန်းနံပါတ်သို့ တိုက်ရိုက် ငွေလွှဲပေးပါ။\n"
        "၂။ ဖုန်းနံပါတ်သို့ တိုက်ရိုက်လွှဲမည်ဆိုပါက Note (မှတ်ချက်) တွင် `#{order_uuid}` ကို ထည့်သွင်းပေးပါ။\n"
        "၃။ ငွေလွှဲပြီးပါက အောင်မြင်ကြောင်းပြသည့် **Screenshot (ပြေစာ)** ကို ဤနေရာသို့ ပို့ပေးပါခင်ဗျာ။"
    )

    await callback.message.delete()
    await callback.message.answer_photo(
        photo=photo_file,
        caption=caption,
        parse_mode="Markdown"
    )
    await state.set_state(OrderStates.awaiting_slip)
    await callback.answer()

@router.message(OrderStates.awaiting_slip, F.photo)
async def handle_slip_upload(message: Message, state: FSMContext, bot: Bot):
    photo = message.photo[-1]
    data = await state.get_data()
    order_uuid = data.get("order_uuid")

    await message.answer("🔄 ပြေစာလက်ခံရရှိပါပြီ၊ စနစ်မှ အတည်ပြုချက် ရယူနေပါသည်...")

    os.makedirs("storage/slips", exist_ok=True)
    local_file_path = f"storage/slips/slip_{order_uuid}.jpg"
    file_info = await bot.get_file(photo.file_id)
    await bot.download_file(file_info.file_path, destination=local_file_path)

    async with async_session_maker() as session:
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        user = (await session.execute(stmt)).scalar_one_or_none()
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name or "Customer"
            )
            session.add(user)
            await session.flush()

        pkg_id = data.get("package_id", 1)
        pkg_check = await session.get(DiamondPackage, pkg_id)
        if not pkg_check:
            # diamond_amount တိကျစွာ ထည့်သွင်းပြီး Auto Create လုပ်ပေးခြင်း
            default_pkg = DiamondPackage(
                id=pkg_id,
                name="Diamond Package",
                diamond_amount=86,
                price_mmk=4200.0,
                is_active=True
            )
            session.add(default_pkg)
            await session.flush()

        new_order = Order(
            order_uuid=order_uuid,
            user_id=user.id,
            package_id=pkg_id,
            mlbb_user_id=data.get("mlbb_user_id", "Unknown"),
            mlbb_zone_id=data.get("mlbb_zone_id", "Unknown"),
            payment_method=data.get("payment_method", "KBZPay"),
            slip_file_id=photo.file_id,
            transaction_id=None,
            status=OrderStatus.WAITING_APPROVAL
        )
        session.add(new_order)
        await session.commit()
        print(f"✅ DEBUG: Saved Order #{order_uuid} to database.")

    admin_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"adm_appr_{order_uuid}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"adm_rej_{order_uuid}")
        ]
    ])
    admin_text = (
        f"🚨 **New Order Received**\n\n"
        f"Order: `#{order_uuid}`\n"
        f"User: {message.from_user.full_name} (`{message.from_user.id}`)\n"
        f"MLBB: `{data.get('mlbb_user_id')} ({data.get('mlbb_zone_id')})`\n"
        f"Status: စစ်ဆေးရန် စောင့်ဆိုင်းနေပါသည်"
    )

    for admin_id in set(settings.ADMIN_IDS):
        try:
            await bot.send_photo(
                chat_id=admin_id,
                photo=photo.file_id,
                caption=admin_text,
                reply_markup=admin_markup,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Failed to send to admin {admin_id}: {e}")

    await message.answer(
        f"✅ ပြေစာလက်ခံရရှိပါပြီခင်ဗျာ။ Order No `#{order_uuid}` အား Admin မှ စစ်ဆေးပြီး မကြာမီ စိန်ထည့်သွင်းပေးပါမည်။\n\n"
        "ထပ်မံဝယ်ယူလိုပါက အောက်ပါခလုတ်ကို နှိပ်ပါ-",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()