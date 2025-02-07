import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'port': int(os.getenv('MYSQL_PORT')),
    # 添加連接設定
    'connect_timeout': 60,        # 增加連接超時時間
    'read_timeout': 30,          # 讀取超時
    'write_timeout': 30,         # 寫入超時
    'auth_plugin': 'mysql_native_password',  # 使用原生密碼認證
    'ssl_disabled': True         # 禁用 SSL
}