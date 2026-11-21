import os
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("DB_PASSWORD", ""),
    "database": "smart_ai_library"
}