import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from supabase import create_client
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def init_db():
    """Initialize the database if needed"""
    try:
        # Check if table exists by attempting to select from it
        supabase.table('messages').select('*').limit(1).execute()
    except:
        # If table doesn't exist, create it
        supabase.table('messages').insert({
            'content': 'Welcome to Wholesome Notes! 💌',
            'likes': 0
        }).execute()

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

    try:
        result = supabase.table('messages').insert({
            'content': content,
            'likes': 0
        }).execute()
        
        return jsonify({'message': 'Message submitted successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/like/<int:note_id>', methods=['POST'])
def like_note(note_id):
    try:
        # First get current likes
        result = supabase.table('messages').select('likes').eq('id', note_id).execute()
        if not result.data:
            return jsonify({'error': 'Note not found.'}), 404
        
        current_likes = result.data[0]['likes']
        
        # Update likes count
        result = supabase.table('messages').update({
            'likes': current_likes + 1
        }).eq('id', note_id).execute()
        
        return jsonify({'likes': result.data[0]['likes']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/random', methods=['GET'])
def get_random_message():
    try:
        last_note_id = request.args.get('last_id')
        
        # Get all messages
        result = supabase.table('messages').select('*').execute()
        messages = result.data
        
        if not messages:
            return jsonify({'message': 'No messages available.'}), 404
            
        # Filter out the last note if specified
        if last_note_id:
            messages = [m for m in messages if m['id'] != int(last_note_id)]
            
        if not messages:
            # If no other messages available, return any message
            result = supabase.table('messages').select('*').execute()
            messages = result.data
            
        # Select a random message
        message = random.choice(messages)
        return jsonify({
            'id': message['id'],
            'message': message['content'],
            'likes': message['likes']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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