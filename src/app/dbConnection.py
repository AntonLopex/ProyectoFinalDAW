from dotenv import load_dotenv
import os
from utils.utils import inject_year

load_dotenv()

SQL_USER = os.getenv("MYSQL_USER")
SQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
SQL_HOST = os.getenv("MYSQL_HOST")
SQL_PORT = os.getenv("MYSQL_PORT")
SQL_DB = os.getenv("MYSQL_DB")


class Config:

    SECRET_KEY = os.getenv("SEC_KEY")
    # print(f"SECRET_KEY: {SECRET_KEY}")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}:{SQL_PORT}/{SQL_DB}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = os.getenv("DEBUG", "False") == "True"
    
 # ── Mail ──────────────────────────────────────────────────
    MAIL_SERVER         = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT           = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS        = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME       = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD       = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = (os.getenv("MAIL_SENDER_NAME") + inject_year()['SHORT_YEAR'], os.getenv("MAIL_USERNAME"))