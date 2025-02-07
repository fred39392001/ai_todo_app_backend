import mysql.connector
from mysql.connector import Error
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host': 'junction.proxy.rlwy.net',
    'user': 'root',
    'password': 'ZefBrcXDxTewSwSIXYwOWwIsFDedGsne',
    'database': 'railway',
    'port': 39237,
    'connect_timeout': 30,
    'use_pure': True
}

def get_db_connection():
    try:
        logger.info("嘗試連接到資料庫...")
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            logger.info("資料庫連接成功！")
            return connection
    except Error as e:
        logger.error(f"資料庫連接錯誤：{e}")
        raise

def execute_query(query, params=None):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if query.lower().startswith('select'):
            result = cursor.fetchall()
            return result
        else:
            connection.commit()
            return cursor.rowcount
            
    except Error as e:
        logger.error(f"查詢執行錯誤：{e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()