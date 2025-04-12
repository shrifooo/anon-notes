# Wholesome Anonymous Notes

A platform to spread positivity and kindness through anonymous messages. Share and receive uplifting notes with others while maintaining anonymity.

## Features
- Leave anonymous uplifting messages
- Receive random messages from others
- Like messages that brighten your day
- Clean, modern UI with smooth animations

## Tech Stack
- Backend: Python/Flask
- Database: Supabase
- Frontend: HTML, TailwindCSS, JavaScript

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your Supabase credentials
3. Run the application:
   ```bash
   python main.py
   ```

## Deployment on Render
1. Fork/clone this repository
2. Connect your repository to Render
3. Create a new Web Service with:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
4. Add these environment variables in Render:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

## Development
- The application uses Supabase for persistent storage
- Messages are stored with content and like counts
- Local development uses environment variables from `.env`