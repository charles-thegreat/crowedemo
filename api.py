# app.py
from flask import Flask, request, jsonify
from agent import chat
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Conversation history storage
def init_db():
    conn = sqlite3.connect('conversations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, conversation_id TEXT, 
                  role TEXT, content TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_history(conversation_id):
    conn = sqlite3.connect('conversations.db')
    c = conn.cursor()
    c.execute('SELECT role, content FROM messages WHERE conversation_id=? ORDER BY timestamp',
              (conversation_id,))
    messages = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return messages

def save_message(conversation_id, role, content):
    conn = sqlite3.connect('conversations.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages VALUES (NULL, ?, ?, ?, ?)',
              (conversation_id, role, content, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    message = data.get('message')
    conversation_id = data.get('conversation_id', 'default')

    history = get_history(conversation_id)
    
    response = chat(message, history)
    
    save_message(conversation_id, 'user', message)
    save_message(conversation_id, 'assistant', response)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)