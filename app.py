from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from db import get_db_connection

app = Flask(__name__)
CORS(app)

openai.api_key = "你的 OpenAI API Key"

@app.route('/todos', methods=['GET'])
def get_todos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()
    conn.close()
    return jsonify(todos)

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todos (task) VALUES (%s)", (data['task'],))
    conn.commit()
    conn.close()
    return jsonify({"message": "新增成功"}), 201

@app.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "刪除成功"})

@app.route('/generate-todo', methods=['POST'])
def generate_todo():
    data = request.json
    prompt = data.get("prompt", "幫我生成一些待辦事項")

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一個待辦事項助理，請提供實用的待辦清單"},
            {"role": "user", "content": prompt}
        ]
    )

    ai_response = response["choices"][0]["message"]["content"]
    todos = ai_response.split("\n")

    conn = get_db_connection()
    cursor = conn.cursor()
    for task in todos:
        if task.strip():
            cursor.execute("INSERT INTO todos (task) VALUES (%s)", (task,))
    conn.commit()
    conn.close()

    return jsonify({"message": "AI 產生的待辦事項已存入資料庫"}), 201

if __name__ == '__main__':
    app.run(debug=True)
