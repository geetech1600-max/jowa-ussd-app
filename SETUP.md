# Development Setup Guide

## Local Development
1. Clone repository: `git clone https://github.com/your-username/jowa-ussd-app.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Initialize database: `python init_database.py`
5. Run app: `python app.py`

## Deployment
1. Push code to GitHub
2. Connect repository to Render.com
3. Set environment variables in Render dashboard
4. Deploy automatically

## Database Setup
Uses Supabase (PostgreSQL). See database configuration in `app.py`.