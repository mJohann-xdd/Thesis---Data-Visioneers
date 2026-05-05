import os
import mysql.connector
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        # Cloud-ready: Support for PostgreSQL (common on Heroku/Render)
        result = urlparse(db_url)
        return psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
    
    # Default to MySQL
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "thesis_finance"),
        port=int(os.getenv("DB_PORT", 3306))
    )
