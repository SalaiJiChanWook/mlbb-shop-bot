import io
import qrcode
from PIL import Image, ImageDraw, ImageFont
from config.settings import settings

class PaymentQRService:
    @staticmethod
    def generate_payment_qr(
        method: str, 
        order_uuid: str, 
        amount_text: str, 
        phone: str, 
        acc_name: str
    ) -> bytes:
        """
        KPay / WavePay အတွက် Dynamic Note/Order ID ပါဝင်သော 
        Payment QR Card ပုံကို Generate ပြုလုပ်ပေးခြင်း
        """
        # 1. QR Payload ဖန်တီးခြင်း
        # (Customer အနေဖြင့် မည်သည့် QR Scanner ဖြင့် scan ဖတ်သည်ဖြစ်စေ အချက်အလက်များ တိကျစွာ ပြသနိုင်စေရန်)
        payload = (
            f"PAY TO: {acc_name}\n"
            f"ACCOUNT: {phone}\n"
            f"METHOD: {method}\n"
            f"ORDER_NO: #{order_uuid}\n"
            f"AMOUNT: {amount_text}"
        )

        # 2. QR Code matrix generate ပြုလုပ်ခြင်း
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(payload)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr_w, qr_h = qr_img.size

        # 3. Canvas Card တစ်ခု ဖန်တီးခြင်း (Header, QR Code, Footer ပါဝင်သော ကတ်ပြား)
        card_w = qr_w + 60
        card_h = qr_h + 160
        bg_color = (255, 255, 255)
        card = Image.new("RGB", (card_w, card_h), bg_color)
        draw = ImageDraw.Draw(card)

        # 4. Color Themes (KBZPay: Deep Blue / WavePay: Golden Yellow/Orange)
        theme_color = (0, 91, 170) if "KPAY" in method.upper() else (237, 140, 0)

        # Top Header Banner
        draw.rectangle([(0, 0), (card_w, 45)], fill=theme_color)
        
        # Default Font Fallback
        font = ImageFont.load_default()

        # Banner Title
        banner_title = f"{method} Quick Scan & Pay"
        draw.text((20, 15), banner_title, fill=(255, 255, 255), font=font)

        # QR Code အား Canvas အလယ်သို့ ကူးထည့်ခြင်း
        card.paste(qr_img, (30, 55))

        # Bottom Text Information
        info_y = qr_h + 65
        line1 = f"Account: {phone} ({acc_name})"
        line2 = f"Amount: {amount_text}"
        line3 = f"Transfer Note: #{order_uuid}"

        draw.text((25, info_y), line1, fill=(30, 30, 30), font=font)
        draw.text((25, info_y + 20), line2, fill=(0, 128, 0), font=font)
        draw.text((25, info_y + 40), line3, fill=theme_color, font=font)

        # In-Memory Buffer ထဲသို့ သိမ်းဆည်းပြီး Bytes အဖြစ် ပြန်ထုတ်ပေးခြင်း
        output_buffer = io.BytesIO()
        card.save(output_buffer, format="PNG")
        output_buffer.seek(0)
        return output_buffer.getvalue()

payment_qr_service = PaymentQRService()