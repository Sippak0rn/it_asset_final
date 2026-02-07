# config.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:1234@127.0.0.1:3306/it_assets_db?charset=utf8mb4"
    )

    # ปิด CSRF แบบถาวร
    WTF_CSRF_ENABLED = False
