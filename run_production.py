# run_production.py
from waitress import serve
from app import app
import os

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"JOWA Production Server running on http://localhost:{port}")
    print("No warnings - using Waitress production server")
    serve(app, host='0.0.0.0', port=port)