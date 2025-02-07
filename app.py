from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from db import get_db_connection
from db import execute_query
import mysql.connector
from mysql.connector import Error
import logging
import openai

load_dotenv()

# 設置日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def validate_env():
    required_vars = [
        'MYSQL_HOST',
        'MYSQL_USER',
        'MYSQL_PASSWORD',
        'MYSQL_DATABASE',
        'MYSQL_PORT',
        'OPENAI_API_KEY'
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

validate_env()

# 設置 OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 添加錯誤處理
@app.errorhandler(Exception)
def handle_error(error):
    app.logger.error(f"An error occurred: {error}")
    return jsonify({"error": str(error)}), 500

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route("/", methods=["GET"])
def home():
    try:
        return jsonify({"message": "API is running", "status": "success"})
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/todos', methods=['GET'])
def get_todos():
    logger.info("Received request for /todos")
    try:
        todos = execute_query("SELECT * FROM todos")
        logger.info(f"Successfully retrieved {len(todos)} todos")
        return jsonify(todos)
    except Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            "error": "Server error",
            "message": str(e)
        }), 500

@app.route('/todos', methods=['POST'])
def add_todo():
    try:
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({"error": "Missing task"}), 400
            
        execute_query(
            "INSERT INTO todos (task) VALUES (%s)",
            (data['task'],)
        )
        return jsonify({"message": "Todo added successfully"}), 201
    except Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    try:
        result = execute_query(
            "DELETE FROM todos WHERE id = %s",
            (id,)
        )
        if result == 0:
            return jsonify({"error": "Todo not found"}), 404
        return jsonify({"message": "Todo deleted successfully"})
    except Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(500)
def handle_500(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500

@app.route('/generate-todo', methods=['POST'])
def generate_todo():
    try:
        logger.info("收到 AI 生成請求")
        data = request.get_json()
        prompt = data.get("prompt", "幫我生成一些待辦事項")

        # 使用 OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一個待辦事項助理，請提供實用的待辦清單"},
                {"role": "user", "content": prompt}
            ]
        )

        # 處理 AI 回應
        ai_response = response.choices[0].message.content
        logger.info(f"AI 回應: {ai_response}")

        # 將回應拆分成個別待辦事項
        todos = [task.strip().replace('- ', '') for task in ai_response.split('\n') if task.strip()]

        # 將待辦事項存入資料庫
        connection = get_db_connection()
        cursor = connection.cursor()
        
        for task in todos:
            if task:  # 確保任務不是空字串
                cursor.execute("INSERT INTO todos (task) VALUES (%s)", (task,))
        
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "AI 待辦事項已生成並儲存"}), 201

    except Exception as e:
        logger.error(f"生成待辦事項時發生錯誤: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5001,
        debug=True
    )