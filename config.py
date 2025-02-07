import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),  # 預設值應該是字串
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'test_db'),
    'port': int(os.getenv('MYSQL_PORT', 3306))  # 這裡轉換為整數
}

