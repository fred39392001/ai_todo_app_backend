import mysql.connector
import logging
from db import DB_CONFIG

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def init_database():
    connection = None
    cursor = None
    try:
        logger.info("連接到資料庫...")
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 創建 todos 表格
            create_table_query = """
            CREATE TABLE IF NOT EXISTS todos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            cursor.execute(create_table_query)
            connection.commit()
            logger.info("todos 表格創建成功！")
            
            # 插入一些測試數據
            insert_query = """
            INSERT INTO todos (task) VALUES 
            ('測試待辦事項 1'),
            ('測試待辦事項 2')
            """
            
            cursor.execute(insert_query)
            connection.commit()
            logger.info("測試數據插入成功！")
            
    except Exception as e:
        logger.error(f"資料庫初始化錯誤：{e}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            logger.info("資料庫連接已關閉")

if __name__ == "__main__":
    init_database()