import os
from datetime import datetime
import shutil
from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# Define base directory and database paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'messages.db')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

def backup_database():
    """Create a timestamped backup of the database"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f'messages_{timestamp}.db')
    
    # Only backup if the database exists
    if os.path.exists(DATABASE_PATH):
        shutil.copy2(DATABASE_PATH, backup_path)
        return backup_path
    return None

def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Database setup
def init_db():
    """Initialize the database and create tables if they don't exist"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            content TEXT NOT NULL,
                            likes INTEGER DEFAULT 0,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                          )''')
        conn.commit()
    
    # Create initial backup after initialization
    backup_database()

# Initialize the database
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_message():
    content = request.form.get('content')
    if not content or len(content.strip()) == 0:
        return jsonify({'error': 'Message content cannot be empty.'}), 400

    if len(content) > 100:
        return jsonify({'error': 'Message content exceeds the 100-character limit.'}), 400

    # Basic content moderation
    inappropriate_words = ['badword1', 'badword2']  # Add more as needed
    if any(word in content.lower() for word in inappropriate_words):
        return jsonify({'error': 'Inappropriate content detected.'}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (content) VALUES (?)', (content,))
        conn.commit()

    return jsonify({'message': 'Message submitted successfully!'}), 201

@app.route('/like/<int:note_id>', methods=['POST'])
def like_note(note_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE messages SET likes = likes + 1 WHERE id = ?', (note_id,))
        conn.commit()
        cursor.execute('SELECT likes FROM messages WHERE id = ?', (note_id,))
        result = cursor.fetchone()

    if result:
        return jsonify({'likes': result[0]}), 200
    else:
        return jsonify({'error': 'Note not found.'}), 404

@app.route('/random', methods=['GET'])
def get_random_message():
    with get_db() as conn:
        cursor = conn.cursor()
        # First try to get a random message that's different from the last one
        last_note_id = request.args.get('last_id')
        if last_note_id:
            cursor.execute('SELECT id, content, likes FROM messages WHERE id != ? ORDER BY RANDOM() LIMIT 1', (last_note_id,))
        else:
            cursor.execute('SELECT id, content, likes FROM messages ORDER BY RANDOM() LIMIT 1')
        result = cursor.fetchone()

    if result:
        return jsonify({'id': result[0], 'message': result[1], 'likes': result[2]}), 200
    else:
        return jsonify({'message': 'No messages available.'}), 404

@app.route('/leave-note')
def leave_note():
    return render_template('leave_note.html')

@app.route('/receive-note')
def receive_note():
    return render_template('receive_note.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)