mlbb-shop-bot/
├── .env.example
├── requirements.txt
├── run.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── database/
│   ├── __init__.py
│   ├── connection.py
│   └── models.py
├── services/
│   ├── __init__.py
│   ├── ai_service.py
│   └── ocr_service.py
├── bot/
│   ├── __init__.py
│   ├── loader.py
│   ├── middlewares/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── throttling.py
│   └── handlers/
│       ├── __init__.py
│       ├── customer.py
│       ├── admin.py
│       └── developer.py
└── storage/
    ├── database.sqlite3
    └── slips/