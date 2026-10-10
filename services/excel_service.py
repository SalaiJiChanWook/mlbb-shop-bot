import os
from datetime import datetime, date
from sqlalchemy import select
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from database.connection import async_session_maker
from database.models import Order, User, DiamondPackage, OrderStatus

EXPORT_DIR = "storage/daily_reports"
os.makedirs(EXPORT_DIR, exist_ok=True)

class ExcelReportService:
    @staticmethod
    async def export_daily_sales(target_date: date = None) -> str:
        """
        သတ်မှတ်ထားသော ရက်စွဲအတွက် အောင်မြင်သည့် Order များကို 
        Excel ဖိုင်အဖြစ် storage/daily_reports ထဲတွင် သိမ်းဆည်းပေးခြင်း
        """
        if target_date is None:
            target_date = datetime.now().date()

        date_str = target_date.strftime("%Y-%m-%d")
        file_path = os.path.join(EXPORT_DIR, f"Sales_Report_{date_str}.xlsx")

        async with async_session_maker() as session:
            # 1. သက်ဆိုင်ရာ ရက်စွဲ၏ Completed Orders များကို Query လုပ်ခြင်း
            stmt = (
                select(Order, User, DiamondPackage)
                .join(User, Order.user_id == User.id)
                .join(DiamondPackage, Order.package_id == DiamondPackage.id)
                .where(Order.status == OrderStatus.COMPLETED)
                .order_by(Order.created_at.asc())
            )
            result = await session.execute(stmt)
            records = result.all()

        # 2. Excel Workbook စတင်ဖန်တီးခြင်း
        wb = Workbook()
        ws = wb.active
        ws.title = f"Sales_{date_str}"

        # 3. Headers Styling
        headers = [
            "Order ID", "Date Time", "Customer Name", "Telegram ID",
            "MLBB User ID", "Zone ID", "Package", "Amount (MMK)",
            "Payment Method", "Transaction ID"
        ]
        ws.append(headers)

        header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
        header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
        center_align = Alignment(horizontal="center", vertical="center")
        thin_border = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9')
        )

        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align

        # 4. Rows ဒေတာများ ထည့်သွင်းခြင်း
        total_revenue = 0.0
        row_idx = 2

        for order, user, pkg in records:
            # ရက်စွဲ တိုက်စစ်ခြင်း (ယနေ့ရက်စွဲ ဟုတ်မဟုတ်)
            if order.created_at and order.created_at.date() == target_date:
                ws.append([
                    f"#{order.order_uuid}",
                    order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    user.full_name,
                    user.telegram_id,
                    order.mlbb_user_id,
                    order.mlbb_zone_id,
                    pkg.name,
                    pkg.price_mmk,
                    order.payment_method,
                    order.transaction_id or "N/A"
                ])
                total_revenue += pkg.price_mmk

                for c in range(1, len(headers) + 1):
                    ws.cell(row=row_idx, column=c).border = thin_border
                row_idx += 1

        # 5. Total Summary Row ထည့်သွင်းခြင်း
        ws.append([""] * (len(headers) - 3) + ["စုစုပေါင်း ရောင်းရငွေ", total_revenue, ""])
        summary_cell = ws.cell(row=row_idx, column=len(headers) - 1)
        summary_cell.font = Font(name="Arial", size=11, bold=True, color="008000")
        
        # 6. Column Widths အလိုအလျောက် ချိန်ညှိခြင်း
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        wb.save(file_path)
        return file_path

excel_service = ExcelReportService()