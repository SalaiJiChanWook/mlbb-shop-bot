# ⚡ MLBB Diamond Top-up Automation Engine

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/) [![aiogram 3.x](https://img.shields.io/badge/Framework-aiogram_3.x-2CA5E0?style=flat&logo=telegram&logoColor=white)](https://docs.aiogram.dev/) [![SQLAlchemy 2.0](https://img.shields.io/badge/ORM-SQLAlchemy_2.0_\(Async\)-D71F00?style=flat)](https://www.sqlalchemy.org/) [![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/) [![CI Pipeline](https://img.shields.io/badge/CI-Passing-brightgreen?style=flat&logo=githubactions&logoColor=white)](https://github.com/)

An asynchronous, event-driven enterprise e-commerce automation system designed for digital game credit distribution (Mobile Legends: Bang Bang Diamonds) in Myanmar. Built with **Role-Based Access Control (RBAC)**, **Non-blocking In-Memory QR Generation**, **Fail-safe Payment Processing**, and **Automated Financial Reconciliation**.

> **Live Production Bot:** [@Riku\_Mllb\_Diamond\_mm\_bot](https://t.me/Riku_Mllb_Diamond_mm_bot)

---

## 🏛 System Architecture

The application adopts Clean Architecture principles, completely decoupling Telegram presentation handlers from business services and data persistence layers.

```
                     [ Telegram Clients (Mobile/Desktop) ]
                                       │
                                       ▼ (Long Polling / Webhook)
                          ┌───────────────────────────┐
                          │    aiogram 3.x Engine     │
                          ├───────────────────────────┤
                          │ • Sliding-window Throttler│
                          │ • RBAC Auth Middlewares   │
                          └─────────────┬─────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
   [ Customer Layer ]           [ Admin Layer ]             [ Developer Layer ]
   • FSM Order Pipeline         • 1-Click Approval Queue    • System Diagnostics
   • Native Contact Ingestion   • Rejection & Escalation    • Hot Database Snapshots
   • Dynamic In-Memory QR       • Top Customer Analytics    • Midnight Schedulers
           │                            │                            │
           └────────────────────────────┼────────────────────────────┘
                                        ▼
                       ┌───────────────────────────────┐
                       │    Asynchronous Services      │
                       ├───────────────────────────────┤
                       │ • Dynamic QR Synthesis (PIL)  │
                       │ • Excel Financial Reporting   │
                       │ • Gemini AI Support Agent     │
                       └───────────────┬───────────────┘
                                       ▼
                       ┌───────────────────────────────┐
                       │   SQLAlchemy 2.0 (Async)      │
                       │ SQLite Engine / AioSQLite DB  │
                       └───────────────────────────────┘
```

&nbsp;

---

## 🚀 Key Engineering Highlights

### 1\. Zero-Disk-Thrashing Dynamic QR Synthesis

- Generates contextual dynamic payment QR codes (KBZPay / WavePay) on demand.  
- Encodes transaction metadata, localized Burmese headers, and unique Order UUIDs directly inside a non-blocking `io.BytesIO` memory stream, eliminating SSD disk wear on host servers.

### 2\. Enterprise Security & Anti-Fraud Protection

- **Idempotency & Replay Attack Defense:** Transaction IDs extracted from receipts are cryptographically unique and indexed in SQLite to prohibit duplicate submissions.  
- **Hardware-Level RBAC:** Middleware validates incoming events against protected Environment IDs to isolate Super Admin and Developer capabilities from standard users.  
- **Privacy Enforcement:** Bot does not capture arbitrary user numbers; leverages Telegram Native Contact Sharing (`request_contact=True`) for verified user registration.

### 3\. Automated Daily Financial Reconciliation

- Background task automatically triggers every night at 23:59 (Asia/Yangon), queries completed transactions, compiles formatted Excel spreadsheets (`.xlsx`) via OpenPyXL, and dispatches audited books directly to store administrators.

---

## 📂 Project Directory Structure

```
mlbb-shop-bot/
├── .github/workflows/ci.yml     # Automated Linting & Testing Workflow
├── config/
│   └── settings.py              # Pydantic v2 Settings Management
├── database/
│   ├── connection.py            # Async Engine & Session Factory
│   └── models.py                # Normalized Database Models
├── services/
│   ├── ai_service.py            # Sandboxed Gemini Assistant Service
│   ├── excel_service.py         # OpenPyXL Financial Reporting Engine
│   ├── ocr_service.py           # Gemini Vision Receipt Parser
│   └── qr_service.py            # In-Memory Dynamic QR Generator
├── bot/
│   ├── handlers/                # Customer, Admin & Developer Routers
│   ├── middlewares/             # Security RBAC & Throttling
│   └── loader.py                # Bot Factory Instance
├── storage/                     # Persistent Volumes (DB, Logs, Slips)
├── Dockerfile                   # Multi-stage Container Spec
├── docker-compose.yml           # Container Orchestration
├── requirements.txt             # Locked Dependencies
└── run.py                       # Application Entry Point
```

&nbsp;

---

## 🛠 Quickstart Guide

### Option 1: Docker Compose Deployment (Recommended)

```sh
# 1. Clone repository
git clone https://github.com/<your-username>/mlbb-shop-bot.git
cd mlbb-shop-bot

# 2. Configure Environment
cp .env.example .env
# Fill in your BOT_TOKEN, ADMIN_IDS, OWNER_ID

# 3. Spin up container
docker compose up -d --build

# 4. View logs
docker compose logs -f
```

&nbsp;

### Option 2: Local Python Environment

```sh
# 1. Create Virtualenv
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start engine
python run.py
```

&nbsp;

---

## 👨‍💻 Author

**Automation & Systems Engineer**

- Telegram: [@Riku\_Mllb\_Diamond\_mm\_bot](https://t.me/Riku_Mllb_Diamond_mm_bot)


# 📱 MLBB Telegram Bot \- Functions & Commands Guide

ဤလက်စွဲစာအုပ်သည် Bot တွင် ပါဝင်သော လုပ်ဆောင်ချက်အားလုံးကို **Customer**၊ **Admin** နှင့် **Developer/Owner** စသည့် Role ၃ ခုအလိုက် လိုရင်းတိုရှင်း စုစည်းဖော်ပြထားခြင်း ဖြစ်ပါသည်။

---

## 👤 ၁။ Customer (ဖောက်သည်များအတွက်)

| Function / Action | အသုံးပြုပုံ | အသေးစိတ် ရှင်းလင်းချက် |
| :---- | :---- | :---- |
| **စတင်အသုံးပြုခြင်း** | `/start` | Bot ကို စတင်နှိုးပြီး အကောင့်ဖွင့်ခြင်း။ အသစ်ဖြစ်ပါက ဖုန်းနံပါတ် တောင်းခံမည်။ |
| **ဖုန်းနံပါတ် အတည်ပြုခြင်း** | `[📱 ဖုန်းနံပါတ် ပေးပို့မည်]` | Telegram Contact မှတစ်ဆင့် စစ်မှန်သော ဖုန်းနံပါတ်ကို စနစ်ထဲ သို့ အလိုအလျောက် မှတ်ပုံတင်ခြင်း။ |
| **စိန်ဝယ်ယူခြင်း** | `/buy` | MLBB Package များ (Diamonds, Weekly Pass) ကို ရွေးချယ်၍ အော်ဒါတင်ခြင်း။ |
| **Game ID ထည့်သွင်းခြင်း** | စာရိုက်ပို့ခြင်း (FSM) | `12345678 (1234)` ပုံစံဖြင့် User ID နှင့် Zone ID ရိုက်ပို့ပြီး အတည်ပြုခြင်း။ |
| **Payment နည်းလမ်း ရွေးခြင်း** | `[KBZPay]` သို့မဟုတ် `[WavePay]` | မိမိ ပေးချေမည့် ဘဏ်အကောင့်ကို ရွေးချယ်ခြင်း။ |
| **Dynamic QR ရယူခြင်း** | အလိုအလျောက် ပြသမည် | Order No နှင့် ပမာဏ ပါဝင်သော QR Code ပုံ ထွက်လာမည်။ |
| **ငွေလွှဲပြေစာ ပေးပို့ခြင်း** | ပုံ (Photo) ပို့ခြင်း | ငွေလွှဲ Screenshot ပို့၍ Admin ထံ အတည်ပြုချက် တောင်းခံခြင်း။ |
| **အော်ဒါ ပယ်ဖျက်ခြင်း** | `[❌ Cancel]` | မဝယ်ယူမီ အချိန်မရွေး အော်ဒါကို ဖျက်သိမ်းခြင်း။ |
| **AI Helpdesk မေးမြန်းခြင်း** | သာမန် စာရိုက်ပို့ခြင်း | Game ID ရှာနည်း၊ ဈေးနှုန်း၊ ငွေလွှဲနည်းများကို မြန်မာလို အချိန်မရွေး မေးမြန်းခြင်း။ |

&nbsp;

---

## 🛡️ ၂။ Shop Admin (အရောင်းဝန်ထမ်းများအတွက်)

*(Protected by `ADMIN_IDS` in `.env`)*

| Command / Action | အသုံးပြုပုံ | အသေးစိတ် ရှင်းလင်းချက် |
| :---- | :---- | :---- |
| **New Order Alerts** | အလိုအလျောက် ရောက်ရှိမည် | ဝယ်သူ Slip ပို့သည်နှင့် ပြေစာပုံ၊ MLBB ID၊ Txn ID တို့ပါသော စာလွှာ ရောက်လာမည်။ |
| **အော်ဒါ အတည်ပြုခြင်း** | `[✅ Approve]` | စိန်ထည့်ပြီးပါက နှိပ်ရုံဖြင့် Order အောင်မြင်ပြီး ဝယ်သူထံ အလိုအလျောက် စာပို့ပေးခြင်း။ |
| **အော်ဒါ ငြင်းပယ်ခြင်း** | `[❌ Reject]` | Slip အတုဖြစ်ပါက ပယ်ဖျက်ပြီး ဝယ်သူထံ အကြောင်းကြားစာ ပို့ပေးခြင်း။ |
| **အရောင်းစာရင်း ထုတ်ယူခြင်း** | `/export_today` | ယနေ့ ရောင်းချရငွေနှင့် စာရင်းအားလုံးကို Excel (`.xlsx`) ဖိုင်အဖြစ် တိုက်ရိုက်ဆွဲယူခြင်း။ |
| **ဖောက်သည်ဟောင်းများ စစ်ဆေးခြင်း** | `/customers` | အများဆုံး ဝယ်ယူထားသော Top 10 ဖောက်သည်များ (ဖုန်းနံပါတ်၊ Username၊ ဝယ်ယူမှုအကြိမ်) ကြည့်ရှုခြင်း။ |

&nbsp;

---

## 👑 ၃။ Server Owner / Developer (စနစ်ပိုင်ရှင်အတွက်)

*(Protected by `OWNER_ID` in `.env` \- Super Admin)*

| Command / Action | အသုံးပြုပုံ | အသေးစိတ် ရှင်းလင်းချက် |
| :---- | :---- | :---- |
| **Master Control Panel** | `/owner` | လုပ်ဆောင်ချက်အားလုံးကို ခလုတ်များဖြင့် စီမံနိုင်သော Inline Dashboard ခေါ်ယူခြင်း။ |
| **Server ကျန်းမာရေး စစ်ဆေးခြင်း** | `[🖥 Server Status]` သို့မဟုတ် `/server_status` | Laptop ၏ CPU %, RAM %, Disk Space % ကို Live စစ်ဆေးခြင်း။ |
| **Database Backup ဆွဲယူခြင်း** | `[📦 DB Backup]` သို့မဟုတ် `/backup_db` | `database.sqlite3` Snapshot ဖိုင်ကို Telegram ထဲသို့ တိုက်ရိုက် ရယူသိမ်းဆည်းခြင်း။ |
| **မပြီးပြတ်သေးသော အော်ဒါများ** | `[⏳ Pending Orders]` | စိန်မထည့်ရသေးဘဲ စောင့်ဆိုင်းနေသော Orders စာရင်းကို အသေးစိတ် စစ်ဆေးခြင်း။ |
| **အရောင်းစာရင်း Excel ရယူခြင်း** | `[📊 Export Excel]` | Excel အရောင်းစာရင်းကို Dashboard မှတစ်ဆင့် ဆွဲထုတ်ခြင်း။ |
| **ညစဉ် Auto Report (Task)** | နေ့စဉ် ည ၁၁:၅၉ (Auto) | Laptop တွင် Excel ဖိုင် auto သိမ်းဆည်းပြီး Admin/Owner ထံသို့ စာရင်းအလိုအလျောက် ပို့ပေးခြင်း။ |
| **Super Admin Access** | အားလုံး အကျုံးဝင်သည် | Admin Command များ ဖြစ်သော Approve/Reject များကိုလည်း တိုက်ရိုက် လုပ်ပိုင်ခွင့်ရှိခြင်း။ |

&nbsp;

---

## ⚙️ Summary of Workflow

```
[Customer: /buy] 
       ⬇
[MLBB ID Input] 
       ⬇
[Choose Pay Method] 
       ⬇
[Scan Dynamic QR & Upload Slip] 
       ⬇
[Admin Notification Push] 
       ⬇
[Admin: Click Approve] 
       ⬇
[Customer: Received Diamonds Notification 🎉]
```

&nbsp;